"""RESET604 T1.2: Build and freeze the TVBench v1 Development Manifest from reviewed REALAPP554 frames.

Combines all unique human-reviewed frames (`status == 'accepted'`) across:
- `reports/work/REALAPP554/review/` (`labels-v2/`)
- `reports/work/REALAPP554/review-dev/` (`labels/`)
Preserves complete=False for focus-only frames (`PhotoGuessingGame`, `Swiftfin`), normalizes unflagged accepted draft
boxes to `visibility: 'visible'` (per `REALAPP554` recheck convention), and validates every label with `real_app_benchmark543`.
"""
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from PIL import Image

import real_app_benchmark543 as r543
import research_queue as q
from template_inputs398 import pin

RA = q.ROOT / 'reports/work/REALAPP554'
DEFAULT_OUT = q.ROOT / 'dataset/real_apps/tvbench-v1'


def normalize_label(raw_label, image_sha):
    """Preserve reviewer flags, original provenance/visibility, unresolved objects, and completeness rules."""
    q.require(raw_label.get('imageSHA256') == image_sha, 'tvbench_dev_label_sha')
    review = raw_label.get('review') or {}
    q.require(review.get('status') == 'accepted' and review.get('blinded') is True and review.get('reviewer'),
              'tvbench_dev_unaccepted_label')
    objs = []
    unresolved_count = 0
    flagged_counts = {}
    unflagged_unknown_promoted = 0
    has_unresolved_defect = False

    for o in raw_label.get('objects', []):
        flag = o.get('flag')
        orig_vis = o.get('visibility', 'unknown')
        orig_cls = o.get('class')
        orig_prov = o.get('provenance', 'sdk-draft')
        if flag is not None:
            flagged_counts[flag] = flagged_counts.get(flag, 0) + 1
        if flag in ('wrong-box', 'wrong-class'):
            has_unresolved_defect = True
            unresolved_count += 1
            cls_val = None
            vis = orig_vis
        elif flag == 'not-control':
            unresolved_count += 1
            cls_val = None
            vis = orig_vis
        else:
            cls_val = orig_cls
            if orig_vis == 'unknown' and orig_cls is not None and flag is None:
                # Documented validate-and-flag convention (real_app_pilot554.py):
                # frame acceptance promotes unflagged unknown-visibility drafts to visible.
                vis = 'visible'
                unflagged_unknown_promoted += 1
            else:
                vis = orig_vis
                if cls_val is None or vis == 'unknown':
                    unresolved_count += 1
        objs.append({
            'id': o['id'],
            'class': cls_val,
            'box': o['box'],
            'visibility': vis,
            'provenance': orig_prov,
            'sourceClass': orig_cls,
            'sourceVisibility': orig_vis,
            'sourceFlag': flag,
        })

    complete = bool(raw_label.get('complete', False)) and not has_unresolved_defect
    review_doc = dict(
        review,
        confirmationRule='frame_acceptance_confirms_unflagged_drafts_to_visible',
        unflaggedUnknownPromotedCount=unflagged_unknown_promoted,
        flaggedCounts=flagged_counts,
        unresolvedCount=unresolved_count,
    )
    return dict(raw_label, complete=complete, objects=objs, review=review_doc)


def build_dev_manifest(out_dir=DEFAULT_OUT, version_tag='v2'):
    out_dir = Path(out_dir)
    labels_dir = out_dir / f'dev-labels-{version_tag}'
    labels_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        (RA / 'review/cases.json', RA / 'review/labels-v2'),
        (RA / 'review-dev/cases.json', RA / 'review-dev/labels'),
    ]
    apps = {}
    cases = []
    seen_shas = set()
    classes = None

    for cases_path, src_labels in sources:
        doc = q.load(cases_path)
        if classes is None:
            classes = list(doc['classes'])
        for c in doc['cases']:
            lbl_src = src_labels / f"{c['id']}.json"
            if not lbl_src.is_file():
                continue
            raw_lbl = q.load(lbl_src)
            if (raw_lbl.get('review') or {}).get('status') != 'accepted':
                continue
            sha = c['sha256']
            q.require(sha not in seen_shas, f'tvbench_dev_duplicate_image:{c["id"]}')
            seen_shas.add(sha)

            img_path = Path(c['image'])
            q.require(img_path.is_file() and q.digest(img_path) == sha, f'tvbench_dev_image_missing:{c["id"]}')
            with Image.open(img_path) as im:
                q.require(im.size == (c['width'], c['height']), f'tvbench_dev_size:{c["id"]}')
                px_sha = hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()

            norm_lbl = normalize_label(raw_lbl, sha)
            norm_path = labels_dir / f"{c['id']}.json"
            q.save(norm_path, norm_lbl, replace=True)

            case_entry = dict(
                id=c['id'],
                app=c['app'],
                flow=c['flow'],
                group=c['flow'],
                status='captured',
                width=c['width'],
                height=c['height'],
                image=pin(img_path),
                pixelSHA256=px_sha,
                labels=pin(norm_path),
                reviewSummary=dict(
                    complete=norm_lbl['complete'],
                    unresolvedCount=norm_lbl['review']['unresolvedCount'],
                    unflaggedUnknownPromotedCount=norm_lbl['review']['unflaggedUnknownPromotedCount'],
                    flaggedCounts=norm_lbl['review']['flaggedCounts'],
                ),
            )
            r543.validate_labels(norm_lbl, case_entry, classes)
            cases.append(case_entry)
            if c['app'] not in apps:
                apps[c['app']] = dict(id=c['app'], kind='independent-app', trainingExposure='excluded', sealed=False)

    manifest = dict(
        version='tvbench-v2',
        split='development',
        sealed=False,
        trainingEligible=False,
        classes=classes,
        baseline=dict(confidence=0.25, matchingIoU=0.5),
        apps=list(apps.values()),
        cases=cases,
        reviewPolicy='frame_acceptance_confirms_unflagged_drafts_to_visible; unresolved flags force complete=False',
        limitation='Development benchmark (42 human-reviewed screens across 3 apps / 11 flows: 23 control-complete, 42 focus-reviewed). Never sealed test.',
    )
    out_path = out_dir / f'dev-manifest-{version_tag}.json'
    q.save(out_path, manifest, replace=True)
    return dict(
        manifest=str(out_path),
        sha256=q.digest(out_path),
        cases=len(cases),
        apps={a['id']: sum(1 for c in cases if c['app'] == a['id']) for a in manifest['apps']},
    )


def freeze_ax_development(pack, out_dir, layout_ids=None):
    """Snapshot human-accepted AX development references. Review drafts never enter the snapshot."""
    import framework_projection604 as fp
    import real_app_review554 as reviewer

    pack, out_dir = Path(pack).resolve(), Path(out_dir).resolve()
    q.require(out_dir.is_relative_to(q.ROOT) and not out_dir.exists(), 'new_project_output_required')
    doc = q.load(pack / 'cases.json')
    classes = fp.tvos_classes()
    q.require(doc.get('version') == 'tvbench-ax-review-v1' and doc.get('labelMode') == 'contract'
              and doc.get('classes') == classes, 'ax_contract_pack_required')
    # Only apps cleared for benchmark review; designated training apps (NewsTV, TVCatalog, Photo Guessing Game) stay out.
    # Joe added the 3 media apps on 2026-11-25 ("Yes, add them"), after their B405-298 label and layout reviews.
    allowed = {'com.apple.HeadBoard', 'com.apple.TVSettings', 'org.jellyfin.swiftfin', 'com.thatcube.Plozz', 'org.nuiak.rc561.strimr'}
    cases, labels, images, ids = [], {}, set(), set()
    for c in doc['cases']:
        key = c['id']
        q.require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', key) and key not in ids and c['app'] in allowed, 'ax_case_or_app')
        ids.add(key)
        saved = pack / 'labels' / (key + '.json')
        if not saved.is_file():
            continue
        raw = q.load(saved)
        if raw['review']['status'] != 'accepted':
            continue
        reviewer.check(raw, c, classes, doc['focusStates'])
        image = Path(c['image'])
        q.require(q.digest(image) == c['sha256'], 'ax_review_image_changed')
        with Image.open(image) as im:
            q.require(im.size == (c['width'], c['height']), 'ax_review_dimensions')
            pixels = hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
        q.require(pixels not in images, 'ax_duplicate_reviewed_pixels')
        images.add(pixels)
        label = normalize_label(raw, c['sha256'])
        for target, original in zip(label['objects'], raw['objects'], strict=True):
            if 'roleSource' in original:
                target['roleSource'] = original['roleSource']
        # A rejected box supplies no geometry. A rejected role can still localize the control.
        label['objects'] = [o for o in label['objects'] if o['sourceFlag'] not in ('not-control', 'wrong-box')]
        case = dict(id=key, app=c['app'], flow=c['flow'], group=c['flow'], status='captured',
                    width=c['width'], height=c['height'], image=pin(image), pixelSHA256=pixels)
        if layout_ids and key in layout_ids:
            layout = layout_ids[key]
            q.require(isinstance(layout, str) and layout.strip(), 'ax_layout_id')
            case['independentLayoutId'] = layout
        focus = label['focus']
        legacy = dict(label, focus=dict(focus, state='no_focus')) if focus['state'] == 'known_no_focus' else label
        r543.validate_labels(legacy, case, classes)
        labels[key] = label
        cases.append(case)
    q.require(cases, 'ax_no_accepted_human_reviews')
    q.require(not layout_ids or set(layout_ids) <= ids, 'ax_unknown_layout_case')
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out_dir.parent) as temp:
        staged = Path(temp) / 'snapshot'
        (staged / 'labels').mkdir(parents=True)
        for case in cases:
            name = Path('labels') / (case['id'] + '.json')
            q.save(staged / name, labels[case['id']])
            case['labels'] = dict(path=str((out_dir / name).relative_to(q.ROOT)), sha256=q.digest(staged / name))
        manifest = dict(version='tvbench-v2', split='development', sealed=False, trainingEligible=False,
                        classes=classes, cases=cases, sourcePack=pin(pack/'cases.json'),
                        apps=[dict(id=a, sealed=False) for a in sorted({c['app'] for c in cases})],
                        pending=len(ids)-len(cases), baseline=dict(confidence=0.25, matchingIoU=0.5))
        q.save(staged / 'manifest.json', manifest)
        staged.rename(out_dir)
    return out_dir / 'manifest.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--ax-review', type=Path, help='Freeze accepted contract AX labels as a development snapshot in a new --out directory')
    parser.add_argument('--layout-ids', type=Path, help='Optional reviewed case-to-independent-layout mapping for the AX snapshot')
    args = parser.parse_args()
    if args.ax_review:
        print(freeze_ax_development(args.ax_review, args.out, q.load(args.layout_ids) if args.layout_ids else None))
        return
    print(json.dumps(build_dev_manifest(args.out), indent=2))


if __name__ == '__main__':
    main()
