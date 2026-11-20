"""RESET604 T1.1/T1.2: Blinded review-pack builder for TVBench v1 sealed and dev-extra apps.

Keeps sealed test integrity strict:
- Never displays sealed images or outputs per-frame predictions.
- Deduplicates OFFICE603 recording frames by 48 x 27 grayscale signature only.
- Separates app families cleanly (Swiftfin stays dev; Strimr, Plozz, TVCatalog, Office stay sealed).
- Outputs `real_app_review554` compatible blinded empty drafts (no model predictions).

Usage:
  tvbench_sealed_prep604.py [--diff-threshold 2.0] [--out dataset/real_apps/tvbench-v1]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image

import real_app_review554 as rev554
import research_queue as q

VERSION = 'tvbench-sealed-prep-v1'
DEFAULT_DEV_MANIFEST = q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest.json'
DEFAULT_OFFICE_DIR = q.ROOT / 'reports/work/OFFICE603/ttr-recording-fa34bcf7-9e58-4b04-8672-9f8a47a5875f'
DEFAULT_RC561_HOLDOUT = q.ROOT / 'reports/work/RC561/holdout/manifest.json'
DEFAULT_SEALED_CAPTURES = q.ROOT / 'dataset/real_apps/tvbench-v1/sealed-captures/manifest.json'
DEFAULT_SWIFTFIN_EXTRA_DIR = q.ROOT / 'dataset/real_apps/realapp554/capture-swiftfin-2'
DEFAULT_OUT = q.ROOT / 'dataset/real_apps/tvbench-v1'

RC561_APPS = {
    'rc561-swiftfin-screen-01': 'org.jellyfin.swiftfin',
    'rc561-strimr-screen-01': 'org.nuiak.rc561.strimr',
    'rc561-plozz-screen-01': 'com.thatcube.Plozz',
    'rc561-tvcatalog-screen-01': 'com.example.apple-samplecode.TVCatalog',
    'rc561-tvcatalog-buttons': 'com.example.apple-samplecode.TVCatalog',
    'rc561-tvcatalog-description': 'com.example.apple-samplecode.TVCatalog',
    'rc561-tvcatalog-search': 'com.example.apple-samplecode.TVCatalog',
    'rc561-tvcatalog-sidebar': 'com.example.apple-samplecode.TVCatalog',
}


def grayscale_signature(image_path, size=(48, 27)):
    """Return flattened 48 x 27 grayscale intensities and (width, height) without viewing pixels."""
    with Image.open(image_path) as img:
        w, h = img.size
        thumb = img.convert('L').resize(size, Image.Resampling.BILINEAR)
        pixels = thumb.get_flattened_data() if hasattr(thumb, 'get_flattened_data') else thumb.getdata()
        return list(pixels), (w, h)


def mean_abs_diff(sig_a, sig_b):
    """Mean absolute pixel intensity difference between two equal-length signatures."""
    return sum(abs(a - b) for a, b in zip(sig_a, sig_b)) / len(sig_a)


def dedupe_image_records(records, diff_threshold=2.0, sig_size=(48, 27)):
    """Cluster chronologically ordered records by blinded 48 x 27 grayscale mean-abs-diff."""
    groups = []
    for rec in records:
        sig, dims = grayscale_signature(rec['abs_path'], size=sig_size)
        matched = None
        for grp in groups:
            if mean_abs_diff(sig, grp['rep_sig']) <= diff_threshold:
                matched = grp
                break
        if matched is None:
            groups.append(dict(rep=dict(rec, dims=dims), rep_sig=sig, duplicates=[]))
        else:
            matched['duplicates'].append(rec['id'])
    return [dict(g['rep'], duplicates=g['duplicates']) for g in groups]


def _sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def _load_press_index(office_dir):
    """Load `pilot-press-index.tsv` keyed by Frame ID (checking inside office_dir and its parent)."""
    for candidate in (Path(office_dir) / 'pilot-press-index.tsv', Path(office_dir).parent / 'pilot-press-index.tsv'):
        if candidate.is_file():
            with candidate.open(newline='') as f:
                return {
                    row['Frame ID']: row
                    for row in csv.DictReader(f, delimiter='\t')
                    if row.get('Frame ID')
                }, True
    return {}, False


def _office_ordered_records(office_dir):
    """Join OFFICE603 images to `capture-events.jsonl` and `pilot-press-index.tsv`, quarantining unsettled/unjoined frames."""
    office_dir = Path(office_dir)
    img_dir = office_dir / 'images'
    seq_by_sha = {}
    for meta_path in sorted(office_dir.glob('capture-metadata-*.json')):
        meta = q.load(meta_path)
        sha = meta.get('sha256')
        seq = meta.get('sequenceNumber')
        if sha and sha not in seq_by_sha:
            seq_by_sha[sha] = int(seq) if seq is not None else 10**9

    events_path = office_dir / 'capture-events.jsonl'
    events_by_sha = {}
    if events_path.is_file():
        for line in events_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev.get('payload_sha256'):
                events_by_sha[ev['payload_sha256']] = ev

    press_by_event, has_press_index = _load_press_index(office_dir)

    clean_tuples = []
    quarantined = []
    seen_sha = set()
    for p in sorted(img_dir.glob('*.png')):
        sha = _sha256(p)
        if sha in seen_sha:
            continue
        seen_sha.add(sha)
        rel_img = str(p.relative_to(q.ROOT)) if p.is_relative_to(q.ROOT) else str(p)
        if not events_path.is_file():
            quarantined.append(dict(image=rel_img, sha256=sha, reason='missing_capture_events_log'))
            continue
        ev = events_by_sha.get(sha)
        if ev is None:
            quarantined.append(dict(image=rel_img, sha256=sha, reason='missing_capture_event'))
            continue
        role = ev.get('role')
        if role not in ('postInputSettled', 'standalone'):
            quarantined.append(dict(
                image=rel_img, sha256=sha, eventId=ev.get('event_id'),
                captureRole=role, reason=f'unsettled_role:{role}',
            ))
            continue
        press = press_by_event.get(ev.get('event_id'))
        if role == 'postInputSettled' and has_press_index and press is None:
            quarantined.append(dict(
                image=rel_img, sha256=sha, eventId=ev.get('event_id'),
                captureRole=role, reason='missing_press_index',
            ))
            continue
        seq = ev.get('capture_sequence')
        if seq is None:
            seq = seq_by_sha.get(sha, 10**9)
        clean_tuples.append((int(seq), p.name, sha, p, ev, press))

    clean_tuples.sort(key=lambda t: (t[0], t[1]))
    records = []
    for i, (seq, _, sha, p, ev, press) in enumerate(clean_tuples):
        rel_img = str(p.relative_to(q.ROOT)) if p.is_relative_to(q.ROOT) else str(p)
        records.append(dict(
            id=f'office603-{i:03d}',
            app='office.kanopy',
            flow='recording-fa34bcf7',
            abs_path=p,
            rel_image=rel_img,
            sha256=sha,
            sequence=seq,
            captureRole=ev.get('role'),
            eventId=ev.get('event_id'),
            caseId=ev.get('case_id'),
            command=(press or {}).get('Command') or ('standalone' if ev.get('role') == 'standalone' else None),
            exposure='previously-inspected-development',
        ))
    return records, quarantined


def _blank_draft(sha256_hex):
    return dict(
        imageSHA256=sha256_hex,
        complete=False,
        objects=[],
        focus=dict(state='unknown', box=None),
        review=dict(blinded=True, reviewer='', status='pending'),
    )


def _write_review_pack(pack_dir, records, note):
    """Write `cases.json` + empty blinded `drafts/` compatible with `real_app_review554.py`."""
    pack_dir = Path(pack_dir)
    drafts_dir = pack_dir / 'drafts'
    labels_dir = pack_dir / 'labels'
    drafts_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for rec in records:
        w, h = rec['dims']
        cases.append(dict(
            id=rec['id'],
            app=rec['app'],
            flow=rec['flow'],
            image=rec['rel_image'],
            sha256=rec['sha256'],
            width=w,
            height=h,
            plannedFocus=None,
            expectedScreen=None,
            duplicates=rec.get('duplicates', []),
            exposure=rec.get('exposure', 'unknown'),
            captureRole=rec.get('captureRole'),
            command=rec.get('command'),
        ))
        q.save(drafts_dir / f"{rec['id']}.json", _blank_draft(rec['sha256']), replace=True)

    q.save(
        pack_dir / 'cases.json',
        dict(
            version='realapp554-review-v1',
            classes=rev554.CLASSES,
            cases=cases,
            note=note,
        ),
        replace=True,
    )
    return cases


def build_packs(
    out_dir=DEFAULT_OUT,
    dev_manifest_path=DEFAULT_DEV_MANIFEST,
    office_dir=DEFAULT_OFFICE_DIR,
    rc561_holdout_path=DEFAULT_RC561_HOLDOUT,
    sealed_captures_path=DEFAULT_SEALED_CAPTURES,
    swiftfin_extra_dir=DEFAULT_SWIFTFIN_EXTRA_DIR,
    diff_threshold=2.0,
    version_tag='v2',
):
    out_dir = Path(out_dir)
    dev_manifest = q.load(dev_manifest_path) if Path(dev_manifest_path).exists() else dict(cases=[], apps=[])
    dev_shas = {c['image']['sha256'] for c in dev_manifest.get('cases', []) if 'image' in c}
    dev_apps = {a['id'] for a in dev_manifest.get('apps', [])}

    # 1. Join OFFICE603 recording frames to capture-events & press-index; quarantine unverified frames
    if Path(office_dir).exists():
        raw_office, quarantined_office = _office_ordered_records(office_dir)
    else:
        raw_office, quarantined_office = [], []
    raw_office = [r for r in raw_office if r['sha256'] not in dev_shas]
    deduped_office = dedupe_image_records(raw_office, diff_threshold=diff_threshold)

    # 2. Separate RC561 apps: keep dev app (Swiftfin) out of sealed set; tag previously-inspected exposure
    sealed_records = list(deduped_office)
    dev_extra_records = []
    if Path(rc561_holdout_path).exists():
        rc561 = q.load(rc561_holdout_path)
        for c in rc561.get('cases', []):
            cid = c['case_id']
            app_id = RC561_APPS.get(cid, 'rc561.unknown')
            abs_img = q.ROOT / c['image']
            sha = _sha256(abs_img)
            q.require(sha == c['sha256'], 'rc561_sha_mismatch:' + cid)
            if sha in dev_shas:
                continue
            with Image.open(abs_img) as img:
                dims = img.size
            rec = dict(
                id=cid,
                app=app_id,
                flow='rc561-holdout',
                abs_path=abs_img,
                rel_image=c['image'],
                sha256=sha,
                dims=dims,
                duplicates=[],
                exposure='previously-inspected-development',
            )
            if app_id in dev_apps:
                dev_extra_records.append(rec)
            else:
                sealed_records.append(rec)

    # 2b. Add fresh uninspected blinded system/app sealed captures (tvbench_sealed_capture604.py)
    if Path(sealed_captures_path).exists():
        seen_sealed_shas = {r['sha256'] for r in sealed_records} | dev_shas
        sc_doc = q.load(sealed_captures_path)
        for c in sc_doc.get('cases', []):
            abs_img = q.ROOT / c['image']
            if not abs_img.is_file():
                continue
            sha = _sha256(abs_img)
            q.require(sha == c['sha256'], 'sealed_capture_sha_mismatch:' + c['id'])
            if sha in seen_sealed_shas or c['app'] in dev_apps:
                continue
            seen_sealed_shas.add(sha)
            with Image.open(abs_img) as img:
                dims = img.size
            sealed_records.append(dict(
                id=c['id'],
                app=c['app'],
                flow=c.get('flow', 'sealed-capture'),
                abs_path=abs_img,
                rel_image=c['image'],
                sha256=sha,
                dims=dims,
                duplicates=[],
                exposure='uninspected-candidate',
            ))

    # 3. Remaining unreviewed capture-swiftfin-2 screens belong strictly to dev_extra
    if Path(swiftfin_extra_dir).exists():
        seen_dev_extra = {r['sha256'] for r in dev_extra_records} | dev_shas
        for p in sorted(Path(swiftfin_extra_dir).glob('*.png')):
            sha = _sha256(p)
            if sha in seen_dev_extra:
                continue
            seen_dev_extra.add(sha)
            with Image.open(p) as img:
                dims = img.size
            dev_extra_records.append(dict(
                id=f'dev-swiftfin2-{p.stem}',
                app='org.jellyfin.swiftfin',
                flow='capture-swiftfin-2',
                abs_path=p,
                rel_image=str(p.relative_to(q.ROOT)) if p.is_relative_to(q.ROOT) else str(p),
                sha256=sha,
                dims=dims,
                duplicates=[],
                exposure='previously-inspected-development',
            ))

    suffix = f'-{version_tag}' if version_tag else ''
    sealed_dir_name = f'review-sealed{suffix}'
    dev_extra_dir_name = f'review-dev-extra{suffix}'
    plan_name = f'sealed-plan{suffix}.json'

    # Write blinded review packs (compatible directly with real_app_review554.py serve)
    _write_review_pack(
        out_dir / sealed_dir_name,
        sealed_records,
        'TVBench v1 sealed + quarantined-separated review pack (blinded empty or SDK-only drafts; no heuristic OCR or model predictions).',
    )
    _write_review_pack(
        out_dir / dev_extra_dir_name,
        dev_extra_records,
        'TVBench v1 additional dev-app (Swiftfin) review pack.',
    )

    by_app_sealed = {}
    by_exposure = {}
    for r in sealed_records:
        by_app_sealed[r['app']] = by_app_sealed.get(r['app'], 0) + 1
        exp = r.get('exposure', 'unknown')
        by_exposure[exp] = by_exposure.get(exp, 0) + 1

    fresh_uninspected = by_exposure.get('uninspected-candidate', 0)
    plan = dict(
        version='tvbench-sealed-prep-v2',
        diffThreshold=diff_threshold,
        devReviewedCount=len(dev_manifest.get('cases', [])),
        devExtraQueuedCount=len(dev_extra_records),
        officeCleanRawCount=len(raw_office),
        officeDedupedCount=len(deduped_office),
        officeQuarantinedCount=len(quarantined_office),
        quarantined=quarantined_office,
        sealedQueuedTotal=len(sealed_records),
        freshSealedUninspectedCount=fresh_uninspected,
        previouslyInspectedQueuedCount=by_exposure.get('previously-inspected-development', 0),
        sealedTargetCount=100,
        sealedRemainingGap=max(0, 100 - fresh_uninspected),
        sealedByApp=by_app_sealed,
        sealedByExposure=by_exposure,
        reviewCommands=dict(
            sealed=f'PYTHONPATH=scripts python3 scripts/real_app_review554.py serve --dir dataset/real_apps/tvbench-v1/{sealed_dir_name} --port 8770',
            devExtra=f'PYTHONPATH=scripts python3 scripts/real_app_review554.py serve --dir dataset/real_apps/tvbench-v1/{dev_extra_dir_name} --port 8771',
        ),
    )
    q.save(out_dir / plan_name, plan, replace=True)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diff-threshold', type=float, default=2.0)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--version-tag', default='v2')
    args = parser.parse_args()
    plan = build_packs(out_dir=args.out, diff_threshold=args.diff_threshold, version_tag=args.version_tag)
    print(json.dumps(plan, indent=2))


if __name__ == '__main__':
    main()
