"""TRAIN666 H2: build membership D2 = D1 + poster-grid Fixture rows + reviewed training-app real frames.

Sources (Research/Plans/H2Recipe666.md, Joe's decisions of 2026-11-25):
- D1 (`reports/work/TRAIN666/membership/d1-10class`), unchanged rows and roles.
- `composition:poster_grid` rows from the v3-d1 hold-out, now training ("Yes, train on posters").
- New poster capture batches (`--poster-batch ROOT QUALIFIED`, repeatable), ingested by `ttr_detector_ingest604.ingest_fixture_batch`
  with the capture-audit pass list, then filtered by the D1 rule.
- Reviewed, complete REALAPP554 labels of the training apps NewsTV and Photo Guessing Game (decision 2).
  Legacy classes map to the contract: `collectionItem` -> `cell`, `secondaryButton` -> `button`.
  A frame with any other or missing class is dropped whole, because an unlabelled control trains as background.
Every row of a benchmark app or of a sealed or 31-layout benchmark image is refused.
Usage: d2_membership666.py --out NEW_DIR [--poster-batch ROOT QUALIFIED_FRAMES ...]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import research_queue as q
import ttr_detector_ingest604 as ingest
from template_inputs398 import pin

D1 = q.ROOT / 'reports/work/TRAIN666/membership/d1-10class/membership.json'
HELD_OUT = q.ROOT / 'reports/work/RESET604/membership/v3-d1/held-out.json'
POSTER = 'composition:poster_grid'
REVIEW = q.ROOT / 'reports/work/REALAPP554'
SESSIONS = ('capture-newstv', 'capture-newstv-dev', 'capture-photo', 'capture-photo-dev')
TRAINING_APPS = ('newstv', 'photo')
LEGACY = {'collectionItem': 'cell', 'secondaryButton': 'button'}
FORBIDDEN = (q.ROOT / 'reports/work/TRAIN666/h1-scoring-31layouts/manifest-31layouts.json',
             q.ROOT / 'dataset/real_apps/tvbench-v1/sealed-manifest-v2.json')
BENCHMARK_APPS = ('swiftfin', 'plozz', 'strimr', 'tvsettings', 'headboard')


def real_frames():
    """Rows for complete, Joe-reviewed training-app frames. Return (rows, dropped)."""
    cases = {}
    for name in SESSIONS:
        for c in q.load(REVIEW/name/'session.json')['cases']:
            if c.get('status') == 'captured':
                cases[c['id']] = c
    rows, dropped = [], Counter()
    for folder in ('review', 'review-dev'):
        for path in sorted((REVIEW/folder/'labels').glob('*.json')):
            label = q.load(path); case = cases.get(path.stem); app = path.stem.split('-')[0]
            if app not in TRAINING_APPS:
                continue
            if not label.get('complete') or label.get('review', {}).get('status') != 'accepted' or case is None:
                dropped['incomplete_or_unreviewed'] += 1; continue
            if any(o.get('class') not in LEGACY for o in label['objects']):
                dropped['unmapped_class'] += 1; continue
            image = Path(case['image'])
            q.require(q.digest(image) == label['imageSHA256'], 'd2_real_frame_hash:' + path.stem)
            from PIL import Image
            width, height = Image.open(image).size
            controls = [dict(id=o['id'], bounds=[round(v, 3) for v in o['box']], **{'class': LEGACY[o['class']]}) for o in label['objects']]
            rows.append(dict(id=f'realapp554-{path.stem}', group=f'realapp554-{app}-{case["group"]}', role='train', sourceRole='training-app-real',
                             trainingEligible=True, labelsComplete=True, focusState=label['focus']['state'], width=width, height=height,
                             image=pin(image), controls=controls, app=app, reviewer=label['review'].get('reviewer')))
    return rows, dropped


def build(out, poster_batches=()):
    out = Path(out); path = out/'membership.json'
    q.require(not path.exists(), f'd2_membership666_immutable_target_exists:{path}')
    base = q.load(D1); names = base['names']; rows = list(base['rows'])
    poster = [dict(r, role='train', trainingEligible=True, sourceRole='fixture-poster-holdout-released')
              for r in q.load(HELD_OUT)['rows'] if r.get('family') == POSTER]
    new_rows, new_held = [], []
    excluded = []
    for root, qualified_path in poster_batches:
        # Each chunk is ingested with its capture-audit pass list, then filtered by the D1 rule (complete labels, passed audit).
        audit_doc = q.load(qualified_path)
        for chunk in sorted(Path(root).iterdir()):
            if not (chunk/'manifest.json').is_file():
                continue
            passed = {k: set(v) for k, v in audit_doc['chunks'].get(chunk.name, {}).items()}
            got, held = ingest.ingest_fixture_batch(chunk, prefix=f'h2p_{Path(root).name}_{chunk.name}', qualified=passed)
            kept, dropped_rows = ingest._filter_rows_for_mode(got, 'd1')
            new_rows += [dict(r, sourceRole='fixture-poster-capture') for r in kept]; new_held += held; excluded += dropped_rows
    real, dropped = real_frames()
    seen, repeated = {r['image']['sha256'] for r in rows}, 0
    for r in poster + new_rows + real:
        # All targets of 1 recipe share 1 unfocused baseline image; keep it once, as v3 training rows do.
        if r['image']['sha256'] in seen:
            repeated += 1; continue
        seen.add(r['image']['sha256']); rows.append(r)
    unknown = {c['class'] for r in rows for c in r['controls']} - set(names)
    q.require(not unknown, f'd2_membership666_unknown_classes:{sorted(unknown)}')
    q.require(len({r['image']['sha256'] for r in rows}) == len(rows), 'd2_membership666_duplicate_images')
    q.require(not [r for r in rows if str(r.get('app', '')).lower() in BENCHMARK_APPS], 'd2_membership666_benchmark_app')
    doc = dict(base, rows=rows, membershipVersion='train666-d2-v1', mode='d2',
               calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               targetScope='TRAIN666 H2 D2: D1 + poster-grid Fixture rows + reviewed NewsTV and Photo Guessing Game frames.',
               limitation=base.get('limitation', '') + ' Poster-grid family released from the Fixture hold-out by Joe (2026-11-25).',
               source=dict(d1=pin(D1), heldOut=pin(HELD_OUT), posterBatches=[dict(root=str(r), audit=pin(Path(a))) for r, a in poster_batches]))
    audit = ingest.audit_membership(doc, held_out=new_held, tvbench_paths=FORBIDDEN, excluded=excluded)
    out.mkdir(parents=True, exist_ok=True); q.save(path, doc)
    audit.update(membership=pin(path), repeatedImagesSkipped=repeated,
                 added=dict(posterHoldoutReleased=sum(r['sourceRole'] == 'fixture-poster-holdout-released' for r in rows),
                            posterCapture=sum(r['sourceRole'] == 'fixture-poster-capture' for r in rows), trainingAppReal=len(real)),
                 realFramesByApp=dict(Counter(r['app'] for r in real)), realFramesDropped=dict(dropped),
                 classCounts=dict(Counter(c['class'] for r in rows for c in r['controls'])),
                 unsupportedClasses=[n for n in names if not any(c['class'] == n for r in rows for c in r['controls'])])
    q.save(out/'audit.json', audit)
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--poster-batch', nargs=2, action='append', default=[], metavar=('ROOT', 'QUALIFIED_FRAMES'),
                        help='Capture root and its comp_capture_audit604 qualified-frames.json')
    args = parser.parse_args()
    print(json.dumps(build(args.out, args.poster_batch), indent=1))


if __name__ == '__main__':
    main()
