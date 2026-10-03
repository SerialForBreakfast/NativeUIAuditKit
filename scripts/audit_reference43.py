"""Audit reference delivery integrity and consumer compatibility; never admit data."""
import argparse
from collections import Counter
import json
from pathlib import Path
from PIL import Image
import human_annotation_review as h
from fixture_owned_pairs import member
from harvest_bundle_validation import validate_bundle
from focus_corrected_transition_audit import validate_case


def verify_files(root):
    manifest = h.read(root / 'artifact-manifest.json')
    h.require(manifest.get('schema_version') == 1, 'manifest_version')
    entries = manifest['files']
    h.require(0 < len(entries) <= 1000, 'member_count')
    names = set()
    for entry in entries:
        name = entry['path']
        h.require(name.casefold() not in names, 'duplicate_member')
        names.add(name.casefold())
        path = member(root, name)
        h.require(path.is_file() and path.stat().st_size == entry['bytes'] and
                  h.sha(path) == entry['sha256'], 'member_integrity')
    actual = {p.relative_to(root).as_posix().casefold() for p in root.rglob('*') if p.is_file()}
    h.require(actual == names | {'artifact-manifest.json'}, 'unlisted_member')
    return len(entries)


def accepted_cases(root):
    audit = h.read(root / 'audit.json')
    rows = audit['rows']
    h.require(len(rows) == audit['pairs'] == 36 and len({r['case_id'] for r in rows}) == 36,
              'accepted_membership')
    completed = {}
    for receipt in sorted(root.glob('campaigns/*/campaign-receipt.json')):
        data = h.read(receipt)
        for key, case in data['case_accounting'].items():
            if case['state'] != 'completed':
                continue
            h.require(key not in completed, 'duplicate_completed_case')
            completed[key] = (receipt.parent.name, case)
    h.require(set(completed) == {r['case_id'] for r in rows}, 'receipt_membership')
    for row in rows:
        campaign, case = completed[row['case_id']]
        h.require(campaign == row['campaign'] and case['split_group'] == 'validation' and
                  row['path'] == f"campaigns/{campaign}/splits/validation/{row['case_id']}",
                  'case_path_or_role')
    return rows


def inspect_image(path, scene):
    with Image.open(path) as image:
        h.require(image.format == 'PNG' and image.width * image.height <= 16_000_000,
                  'image_format_or_size')
        image.load()
        h.require(image.size == (scene['scene_width'], scene['scene_height']), 'scene_dimensions')
    observation = scene['focus_observation']
    h.require(scene['is_settled'] is True and observation['verified'] is True and
              observation['observedID'] == scene['focused_element_id'], 'observed_focus')
    focused = [e['element_id'] for e in scene['elements'] if e['is_focused']]
    h.require(focused == [scene['focused_element_id']], 'focused_membership')
    return h.sha(path)


def run(root, output):
    root, output = h.local(root), h.fresh(output)
    files = verify_files(root)
    rows = accepted_cases(root)
    results, hashes = [], []
    for row in rows:
        base = member(root, row['path'])
        report = dict(caseID=row['case_id'], kind=row['kind'], consumer='blocked')
        results.append(report)
        if row['kind'] == 'appearance':
            meta = h.read(base / 'synth-0_metadata.json')
            target = meta['focused_element_id']
            target_states = []
            for role, key in [('unfocused', 'baseline_scene'), ('focused', 'focused_scene')]:
                scene = meta[key]
                image = base / meta[role + '_png']
                digest = inspect_image(image, scene)
                h.require(digest == meta[role + '_sha256'], 'image_binding')
                hashes.append(digest)
                found = [e for e in scene['elements'] if e['element_id'] == target]
                h.require(len(found) == 1, 'target_missing')
                target_states.append(found[0]['is_focused'])
            h.require(target_states == [False, True], 'appearance_target_states')
            try:
                validate_bundle(base, max_total_bytes=512 * 1024**2)
                report['consumer'] = 'validated'
            except (ValueError, KeyError, TypeError) as error:
                report['reason'] = str(error)
        else:
            data = h.read(base / 'transition-case.json')
            focus = []
            for endpoint in data['endpoints']:
                scene = endpoint['capture_endpoint']['after_scene']
                digest = inspect_image(base / endpoint['image'], scene)
                h.require(digest == endpoint['capture_endpoint']['frame_png_sha256'], 'image_binding')
                hashes.append(digest)
                focus.append(scene['focused_element_id'])
            h.require(len(focus) == 2 and ((focus[0] != focus[1]) == (row['kind'] == 'scroll_moved')),
                      'transition_focus_relation')
            campaign = h.read(root / 'campaigns' / row['campaign'] / 'campaign-manifest.json')
            case = next(c for c in campaign['cases'] if c['case_id'] == row['case_id'])
            try:
                validate_case(root, base / 'transition-case.json', case)
                report['consumer'] = 'validated'
            except (ValueError, KeyError, TypeError) as error:
                report['reason'] = str(error)
        report['imageAndObservedFocusChecks'] = 'passed'
    h.require(len(hashes) == 72 and len(set(hashes)) == 66, 'image_counts')
    result = dict(filesVerified=files, acceptedCases=len(rows), imageEntries=len(hashes),
                  uniqueImageHashes=len(set(hashes)), kinds=dict(Counter(r['kind'] for r in rows)),
                  compatibility=dict(Counter(r['consumer'] for r in results)), cases=results,
                  trainingEligible=False, role='calibration',
                  limitation='Image/focus checks are not complete native bracket, crop or training admission.')
    h.write(output, result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}))
