"""RESET604 T2.1: Offline reconciliation audit of captured `appearance.composition` v5 Fixture chunks.

Evaluates every captured chunk (including bisect `_a`/`_b` chunks) in place with
`fixture_composition_qual604.qualify_recipes(capture=False, batch_dir=...)` against the
pre-capture expectations of its generated recipe. Writes per-chunk reports and
`qualified-frames.json`, which `ttr_detector_ingest604.build_v3` uses as the admission gate.
No Simulator, TTR, or network access.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import fixture_composition_qual604 as fcq
import research_queue as q

FRAME_KIND = {'focused': 'foc', 'baseline_no_focus': 'unf'}


def audit(capture_root, recipes_dir, out_dir, pixel_tolerance_px=8.0, min_iou=0.90):
    capture_root, recipes_dir, out_dir = (Path(p).resolve() for p in (capture_root, recipes_dir, out_dir))
    index = q.load(recipes_dir / 'index.json')
    family_of = {r['recipe']: r['family'] for r in index['rows']}
    chunks, totals = {}, Counter()
    per_family = {}
    reasons = Counter()
    for chunk in sorted(p for p in capture_root.iterdir() if p.is_dir() and (p / 'manifest.json').is_file()):
        manifest = q.load(chunk / 'manifest.json')
        names = sorted({(e.get('metadata') or {}).get('recipeFile') for e in manifest} - {None})
        q.require(all((recipes_dir / n).is_file() for n in names), f'comp_audit_missing_recipe:{chunk.name}')
        report = fcq.qualify_recipes({n: recipes_dir / n for n in names}, out_dir / chunk.name,
                                     pixel_tolerance_px, min_iou, capture=False, batch_dir=chunk)
        passed = {}
        for row in report['rows']:
            fam = family_of.get(row['recipe'], 'unknown')
            stats = per_family.setdefault(fam, Counter())
            stats['frames'] += 1
            totals['frames'] += 1
            if row.get('passed'):
                stats['passed'] += 1
                totals['passed'] += 1
                passed.setdefault(row['id'], []).append(FRAME_KIND[row['frame']])
            else:
                for key in ('missingControls', 'extraControls', 'wrongRoles', 'geometryErrors', 'focusErrors'):
                    if row.get(key):
                        reasons[key] += 1
                if row.get('reason'):
                    reasons[row['reason']] += 1
        chunks[chunk.name] = {k: sorted(v) for k, v in passed.items()}
    doc = dict(
        version='comp-capture-audit604-v1',
        captureRoot=str(capture_root.relative_to(q.ROOT)) if capture_root.is_relative_to(q.ROOT) else str(capture_root),
        recipesIndexSha256=q.digest(recipes_dir / 'index.json'),
        pixelTolerancePx=pixel_tolerance_px, minIoU=min_iou,
        frames=totals['frames'], passedFrames=totals['passed'],
        passRate=round(totals['passed'] / max(1, totals['frames']), 4),
        failureReasons=dict(reasons),
        perFamily={k: dict(v) for k, v in sorted(per_family.items())},
        chunks=chunks,
    )
    q.save(out_dir / 'qualified-frames.json', doc, replace=True)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-root', type=Path, default=q.ROOT / 'dataset/tvos_captures/reset604/comp-v1')
    parser.add_argument('--recipes-dir', type=Path, default=q.ROOT / 'reports/work/RESET604/recipes-comp-v1')
    parser.add_argument('--out', type=Path, default=q.ROOT / 'reports/work/RESET604/comp-capture-v1-qual')
    args = parser.parse_args()
    doc = audit(args.capture_root, args.recipes_dir, args.out)
    print(json.dumps({k: v for k, v in doc.items() if k != 'chunks'}, indent=2))


if __name__ == '__main__':
    main()
