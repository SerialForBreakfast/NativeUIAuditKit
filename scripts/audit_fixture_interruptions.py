"""Offline diagnostic-only interruption audit; no admission, inference or capture."""
import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path

from PIL import Image
from fixture_rendered_body import validate as body_bounds
from focus_dataset_contract import ROOT, local
from focus_runtime import identity, bounded_batches, invoke
from human_corpus_inventory import metadata_hashes
from photos_focus_pilot import preview


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def member(root, name):
    p = Path(name)
    require(not p.is_absolute() and '..' not in p.parts, 'unsafe_member')
    target = root / p
    require(not any(q.is_symlink() for q in [target, *target.parents]), 'symlink')
    require(target.is_file() and target.stat().st_size <= 32*1024*1024, 'member_limit')
    return target


def integrity(root, protected):
    manifest = json.loads(member(root, 'manifest.json').read_text())
    require(manifest.get('schema_version') == 1, 'manifest_version')
    files = manifest['files']
    require(0 < len(files) <= 512, 'manifest_limit')
    names = [r['path'] for r in files]
    require(len(names) == len(set(names)), 'duplicate_member')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    require(actual == set(names) | {'manifest.json'}, 'manifest_membership')
    for r in files:
        p = member(root, r['path'])
        require(p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'member_integrity')
        require(r['sha256'] not in protected, 'protected_bytes')
    return manifest


def rect(value, size):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value), 'bounds_type')
    x, y, w, h = value
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and
            x+w <= size[0]+.01 and y+h <= size[1]+.01, 'bounds_range')
    return value


def audit_frame(document, size, event_id):
    a, b = document['before'], document['after']
    receipt = document['capture']
    require(receipt.get('state') == 'delivered' and receipt.get('effectStatus') == 'unverified',
            'capture_receipt')
    require(a['monotonic_nanoseconds'] <= b['monotonic_nanoseconds'], 'bracket_time')
    for s in (a, b):
        require((s['scene_width'], s['scene_height']) == size, 'image_size')
    # Exclude only clocks and diagnostic timing; all geometry, semantics, native
    # focus and interruption records must agree across the actual bracket.
    ignore = {'monotonic_nanoseconds', 'timestamp', 'observation_diagnostics'}
    require({k:v for k,v in a.items() if k not in ignore} ==
            {k:v for k,v in b.items() if k not in ignore}, 'bracket_drift')
    interruption = a.get('interruption') or {}
    if interruption:
        require(interruption['event_id'].lower() == event_id.lower(), 'event_mismatch')
        if any(interruption.get(k) for k in ('overlay_bounds', 'action_bounds', 'label_bounds')):
            require(interruption.get('geometry_source') == 'uikit_presentation_layer_window_pixels',
                    'overlay_geometry_source')
    elements = a['elements']
    ids = [e['element_id'] for e in elements]
    require(len(set(ids)) == len(ids), 'duplicate_element')
    obs = a.get('focus_observation') or {}
    generations = {e.get('rendered_body_geometry', {}).get('generation') for e in elements}
    require(len(generations) == 1 and all(type(g) is int for g in generations), 'body_generation')
    generation = next(iter(generations))
    if obs:
        require(obs['generation'] == generation and obs['observedID'] == a.get('focused_element_id'),
                'focus_binding')
    focus = a.get('focused_element_id')
    proposals, exclusions = [], []
    visibility = interruption.get('underlay_visibility') or {}
    overlay = interruption.get('overlay_bounds')
    if overlay:
        rect(overlay, size)
        require(set(visibility) == set(ids), 'visibility_membership')
    for e in elements:
        eid = e['element_id']
        bounds = body_bounds(e.get('rendered_body_geometry'), size, eid, generation)
        state = visibility.get(eid, 'visible' if not overlay else 'unknown')
        require(state in ('visible', 'partially_covered', 'fully_covered', 'unknown'), 'visibility_value')
        reason = 'body_unavailable' if bounds is None else state if state != 'visible' else None
        if reason:
            exclusions.append({'id': eid, 'reason': reason})
            continue
        # No ordinary-focus label is manufactured while an overlay owns focus.
        proposals.append({'id': eid, 'bounds': bounds, 'role': 'rendered_control_body',
                          'state': 'unknown' if not obs else 'focused' if eid == focus else 'unfocused'})
    if interruption.get('action_bounds'):
        proposals.append({'id': 'interruption.continue', 'role': 'interruption_action',
                          'bounds': rect(interruption['action_bounds'], size),
                          'state': 'focused' if interruption.get('observed_focus_id') ==
                                   'interruption.continue' else 'unknown'})
    return dict(proposals=proposals, excluded=exclusions, settled=a.get('is_settled') is True,
                ordinaryFocus=focus, interruptionFocus=interruption.get('observed_focus_id'),
                requestedFocus=obs.get('requestedID'), nativeVerified=obs.get('verified'),
                generation=generation, generationBinding='native_focus' if obs else 'body_records_only',
                phase=interruption.get('phase'), recovery=interruption.get('recovery'),
                dimming=interruption.get('dimming_opacity'), bracketStable=True)


def run(root, protected_path, output):
    root, protected_path, output = local(root), local(protected_path), local(output)
    require(not output.exists(), 'output_collision')
    protected = metadata_hashes(json.loads(protected_path.read_text()))
    manifest = integrity(root, protected)
    summary = json.loads(member(root, 'corpus/summary.json').read_text())
    scenarios = summary['scenarios']
    require(0 < len(scenarios) <= 16, 'scenario_limit')
    frames, items, duplicates = [], [], defaultdict(list)
    names = [s[p] for s in scenarios for p in ('control', 'before', 'visible', 'after')]
    require(len(names) == len(set(names)), 'duplicate_frame')
    require(set(names) == {p.name for p in (root/'corpus').glob('*.png')}, 'frame_membership')
    for scenario in scenarios:
        for phase in ('control', 'before', 'visible', 'after'):
            name = scenario[phase]
            require(Path(name).name == name and name.endswith('.png'), 'frame_path')
            path = member(root, 'corpus/'+name)
            doc = json.loads(member(root, 'corpus/'+Path(name).with_suffix('.json').name).read_text())
            with Image.open(path) as im:
                require(im.width*im.height <= 80_000_000, 'pixel_limit')
                im.verify()
                size = im.size
            record = audit_frame(doc, size, scenario['event_id'])
            record.update(file=name, phaseInScenario=phase, scenario=scenario['name'],
                          sha256=sha(path), producerOutcome=scenario['outcome'])
            frames.append(record); duplicates[record['sha256']].append(name)
            for n, p in enumerate(record['proposals']):
                items.append(dict(id=f'{Path(name).stem}-{n}', path=str(path),
                                  sha256=record['sha256'], bounds=p['bounds']))
    # Preflight every frame before producing any diagnostic output.
    runtime = identity()
    output.mkdir(parents=True); (output/'crops').mkdir(); (output/'previews').mkdir()
    crop_records = []
    for batch in bounded_batches(items):
        for result in invoke(batch)['results']:
            raw = base64.b64decode(result['png'], validate=True)
            with Image.open(io.BytesIO(raw)) as crop:
                require(crop.size == (256, 256) and crop.format == 'PNG', 'crop_format')
                crop.verify()
            filename = result['id']+'.png'
            (output/'crops'/filename).write_bytes(raw)
            crop_records.append({'id': result['id'], 'sha256': hashlib.sha256(raw).hexdigest()})
    require(identity() == runtime, 'runtime_changed')
    require([r['id'] for r in crop_records] == [i['id'] for i in items], 'crop_membership')
    integrity(root, protected)  # Detect source changes during the audit.
    report = dict(version=1, diagnosticOnly=True, trainingAdmission=False, modelInference=False,
                  manifestSHA256=sha(root/'manifest.json'), manifestMembers=len(manifest['files']),
                  protectedMetadataSHA256=sha(protected_path), frames=frames, runtime=runtime,
                  crops=crop_records, duplicateGroups=[v for v in duplicates.values() if len(v)>1],
                  exclusions=dict(Counter(e['reason'] for f in frames for e in f['excluded'])))
    (output/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# Interruption review — diagnostic only', '',
             f'{len(frames)} frames; {len(crop_records)} production crops. No training admission or inference.', '',
             'Green: observed focused bounds. Orange: other crop candidates, including unknown focus.',
             'Covered/removed controls are excluded. Stable brackets do not prove screenshot-time alignment.', '',
             '| Frame | Settled | Native / overlay focus | Excluded |', '|---|---|---|---|']
    for f in frames:
        lines.append(f"| {f['file']} | {f['settled']} | {f['ordinaryFocus']} / {f['interruptionFocus']} | {len(f['excluded'])} |")
    for f in frames:
        if f['phaseInScenario'] not in ('visible', 'after'): continue
        dest = output/'previews'/f['file']
        preview(root/'corpus'/f['file'], dest, f['file'], f['proposals'])
        lines += ['', f"## {f['file']}", '', f"Producer outcome: {f['producerOutcome']}. Recovery: {f['recovery']}.",
                  '', f"![Diagnostic bounds](previews/{f['file']})"]
    (output/'review.md').write_text('\n'.join(lines)+'\n')
    return dict(frames=len(frames), crops=len(crop_records), exclusions=report['exclusions'],
                unsettled=sum(not f['settled'] for f in frames), duplicateGroups=len(report['duplicateGroups']))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--protected', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(run(args.root, args.protected, args.output)))
