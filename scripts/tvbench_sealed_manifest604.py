"""RESET604 T1.2/T1.3: Split human-validated review labels cleanly by exposure.

Strictly separates independent sealed qualification from previously-inspected regressions:
- `uninspected-candidate` accepted labels -> `sealed-manifest-<tag>.json` (`split="sealed-test"`, `sealed=True`).
- `previously-inspected-development` accepted labels (e.g. OFFICE603 Kanopy) ->
  `dev-regression-manifest-<tag>.json` (`split="development-regression"`, `sealed=False`),
  used strictly as anti-regression checks (e.g. catching static synopsis text mislabeled as buttons),
  never for independent sealed qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

import real_app_benchmark543 as r543
import research_queue as q
import tvbench_dev_manifest604 as dm
from template_inputs398 import pin

DEFAULT_OUT = q.ROOT / 'dataset/real_apps/tvbench-v1'


def _build_split_manifest(
    records,
    classes,
    labels_out,
    split_name,
    sealed,
    target_frames,
    limitation,
):
    labels_out.mkdir(parents=True, exist_ok=True)
    apps = {}
    cases = []
    seen_shas = set()
    complete_count = 0
    focused_count = 0
    no_focus_count = 0

    for c, raw_lbl in records:
        sha = c['sha256']
        q.require(sha not in seen_shas, f"tvbench_duplicate_image:{c['id']}")
        seen_shas.add(sha)

        img_path = Path(c['image'])
        if not img_path.is_absolute():
            img_path = q.ROOT / img_path
        q.require(img_path.is_file() and q.digest(img_path) == sha, f"tvbench_image_missing:{c['id']}")
        with Image.open(img_path) as im:
            q.require(im.size == (c['width'], c['height']), f"tvbench_size:{c['id']}")
            px_sha = hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()

        norm_lbl = dm.normalize_label(raw_lbl, sha)
        norm_path = labels_out / f"{c['id']}.json"
        q.save(norm_path, norm_lbl, replace=True)

        case_entry = dict(
            id=c['id'],
            app=c['app'],
            flow=c['flow'],
            group=c['flow'],
            exposure=c.get('exposure', 'unknown'),
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
        if norm_lbl['complete']:
            complete_count += 1
        if norm_lbl['focus']['state'] == 'focused':
            focused_count += 1
        elif norm_lbl['focus']['state'] == 'no_focus':
            no_focus_count += 1
        if c['app'] not in apps:
            apps[c['app']] = dict(id=c['app'], kind='independent-app', trainingExposure='excluded', sealed=sealed)

    target_reached = bool(target_frames and len(cases) >= target_frames)
    checkpoint_status = (
        'complete'
        if target_reached
        else ('partial-human-validated' if cases else 'awaiting-uninspected-sdk-validated-frames')
    )
    return dict(
        version='tvbench-v2',
        split=split_name,
        sealed=sealed,
        checkpointStatus=checkpoint_status,
        trainingEligible=False,
        classes=classes,
        baseline=dict(confidence=0.25, matchingIoU=0.5),
        apps=list(apps.values()),
        cases=cases,
        summary=dict(
            acceptedFrames=len(cases),
            completeControlFrames=complete_count,
            focusedFrames=focused_count,
            noFocusFrames=no_focus_count,
            targetFrames=target_frames,
            remainingToTarget=max(0, (target_frames or 0) - len(cases)),
        ),
        limitation=limitation,
        reviewPolicy='frame_acceptance_confirms_unflagged_drafts_to_visible; unresolved flags force complete=False',
    )


def build_sealed_manifest(
    review_dir=DEFAULT_OUT / 'review-sealed-v2',
    out_dir=DEFAULT_OUT,
    version_tag='v2',
):
    review_dir = Path(review_dir)
    out_dir = Path(out_dir)
    cases_doc = q.load(review_dir / 'cases.json')
    classes = list(cases_doc['classes'])
    src_labels_dir = review_dir / 'labels'

    sealed_records = []
    regression_records = []

    for c in cases_doc['cases']:
        lbl_path = src_labels_dir / f"{c['id']}.json"
        if not lbl_path.is_file():
            continue
        raw_lbl = q.load(lbl_path)
        if (raw_lbl.get('review') or {}).get('status') != 'accepted':
            continue
        exposure = c.get('exposure', 'unknown')
        if exposure == 'uninspected-candidate':
            sealed_records.append((c, raw_lbl))
        else:
            regression_records.append((c, raw_lbl))

    sealed_manifest = _build_split_manifest(
        sealed_records,
        classes,
        out_dir / f'sealed-labels-{version_tag}',
        split_name='sealed-test',
        sealed=True,
        target_frames=100,
        limitation='Independent sealed qualification split (uninspected-candidate frames only).',
    )
    sealed_path = out_dir / f'sealed-manifest-{version_tag}.json'
    q.save(sealed_path, sealed_manifest, replace=True)

    reg_manifest = _build_split_manifest(
        regression_records,
        classes,
        out_dir / f'dev-regression-labels-{version_tag}',
        split_name='development-regression',
        sealed=False,
        target_frames=len(regression_records),
        limitation='Previously-inspected-development HDMI frames (no embedded SDK observations). Regression checks only; never independent qualification.',
    )
    reg_path = out_dir / f'dev-regression-manifest-{version_tag}.json'
    q.save(reg_path, reg_manifest, replace=True)

    return dict(
        sealedManifest=str(sealed_path),
        sealedSHA256=q.digest(sealed_path),
        sealedStatus=sealed_manifest['checkpointStatus'],
        sealedSummary=sealed_manifest['summary'],
        regressionManifest=str(reg_path),
        regressionSHA256=q.digest(reg_path),
        regressionSummary=reg_manifest['summary'],
        regressionApps={a['id']: sum(1 for c in reg_manifest['cases'] if c['app'] == a['id']) for a in reg_manifest['apps']},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-dir', type=Path, default=DEFAULT_OUT / 'review-sealed-v2')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--version-tag', default='v2')
    args = parser.parse_args()
    print(json.dumps(build_sealed_manifest(args.review_dir, args.out, args.version_tag), indent=2))


if __name__ == '__main__':
    main()
