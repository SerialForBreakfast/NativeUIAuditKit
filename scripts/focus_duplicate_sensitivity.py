"""Cached-score crop-duplicate sensitivity; official frame metrics stay unchanged."""
import argparse
from collections import defaultdict
from pathlib import Path

import focus_offline_diagnosis as o
from focus_reset_diagnostics import load
from human_focus_evaluation import metrics
from focus_representative_validation import stratum
from focus_dataset_contract import pixel_digest


def sensitivity(rows, predictions):
    # Existing evaluator validates exact prediction order, finiteness and range.
    official = metrics(rows, predictions, [])
    by_pixel = defaultdict(list)
    for row, prediction in zip(rows, predictions, strict=True):
        by_pixel[row['pixelSHA256']].append((row, prediction))
    for group in by_pixel.values():
        o.require(len({r['label'] for r, _ in group}) == 1, 'duplicate_label_conflict')
        o.require(len({p['probability'] for _, p in group}) == 1, 'duplicate_score_conflict')
    unique = [min(g, key=lambda x: x[0]['id']) for _, g in sorted(by_pixel.items())]
    return dict(official=official['full'], unique=metrics(
        [r for r, _ in unique], [p for _, p in unique], [])['full'],
        removed=[r['id'] for g in by_pixel.values() for r, _ in g
                 if r['id'] != min(x[0]['id'] for x in g)],
        frameMetrics='unchanged; crop deduplication cannot establish complete-frame selection')


def run(protocol, result, output):
    output = o.local(output); o.require(not output.exists(), 'output_collision')
    protocol, result = o.local(protocol), o.local(result)
    inputs = [o.ref(protocol), o.ref(result)]
    doc, scores = load(protocol, result)
    rows = [r for r in doc['samples'] if r['use'] == 'representative-selection']
    for row in rows:
        o.checked(row['crop'])
        o.require(pixel_digest(o.ROOT, row['crop']) == row['pixelSHA256'], 'changed_crop_pixels')
    epochs = []
    for epoch, snapshot in [(0, scores['initial'])] + [(h['epoch'], h['validation']) for h in scores['history']]:
        values = {p['id']: p for p in snapshot['predictions']}
        record = dict(epoch=epoch, overall=sensitivity(rows, [values[r['id']] for r in rows]), strata={})
        for lane in ('buttons', 'tabs', 'artwork', 'rows', 'other'):
            subset = [r for r in rows if stratum(r) == lane]
            record['strata'][lane] = sensitivity(subset, [values[r['id']] for r in subset]) if subset else {'status':'unavailable'}
        epochs.append(record)
    for ref in inputs: o.checked(ref)
    output.parent.mkdir(parents=True, exist_ok=True)
    o.write(output, dict(version='focus-duplicate-sensitivity-v1', inputs=inputs,
        threshold=.85, modelExecution=False, officialProtocolChanged=False, epochs=epochs))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('protocol', 'result', 'output'): p.add_argument('--'+name, required=True, type=Path)
    a = p.parse_args(); run(a.protocol, a.result, a.output)
