"""Reconstruct retained loss weights without loading images or training."""
from collections import defaultdict
import numpy as np
import condition291 as c

base = c.base


def totals(rows, weights):
    base.require(len(rows) == len(weights) and np.isfinite(weights).all() and (weights > 0).all(), 'weights')
    buckets = defaultdict(lambda: dict(entries=0, weight=0.0))
    for row, weight in zip(rows, weights):
        key = (row['group'], row['changed'], row['condition'])
        buckets[key]['entries'] += 1
        buckets[key]['weight'] += float(weight)
    total = float(weights.astype(np.float64).sum())
    return [dict(group=k[0], changed=k[1], condition=k[2], **v, fraction=v['weight']/total)
            for k, v in sorted(buckets.items())]


def run():
    out = base.ROOT/'reports/work/FOCUS-307/exposure.json'
    base.require(out.parent.is_dir() and not out.exists(), 'output_collision_or_missing_parent')
    package = base.read(base.PACKAGE/'manifest.json')
    for name in ('membership.json', 'labels.npy'):
        base.require(base.worker.digest(base.PACKAGE/name) == package['files'][name]['sha256'], 'input_hash')
    membership = base.read(base.PACKAGE/'membership.json')
    registration = base.read(base.ROOT/'reports/work/TRANSITION-291/registration.json')
    parent = base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights = np.load(base.checked(parent['weights']), allow_pickle=False)
    labels = np.load(base.PACKAGE/'labels.npy', allow_pickle=False)
    added = registration['addedRows']
    controls = c.select_controls(membership, added)
    base.require(controls.tolist() == registration['controlIndices'], 'controls')
    output_labels, output_weights, _ = c.balanced_weights(weights, labels, membership, added, controls)
    base.require(base.sha(output_weights.tobytes()) == registration['weightsSHA256'], 'schedule_weights')
    base.require(base.sha(output_labels.tobytes()) == registration['labelsSHA256'], 'schedule_labels')
    replay = [dict(group='legacy-replay-unresolved', changed=int(y), condition='legacy_replay')
              for y in membership['replayLabels']]
    native = [dict(group=membership['rows'][i]['group'], changed=membership['rows'][i]['changed'],
                   condition='+'.join(sorted(membership['rows'][i]['conditions']))) for i in membership['selected']]
    original = replay+native+native
    results = {}
    for model, positive, negative in [('DTM083', False, False), ('DTM084', True, True),
                                       ('DTM085', True, False), ('DTM086', False, True)]:
        extra = [dict(group=r['group'], changed=r['changed'], condition=r['condition'])
                 if (positive if r['changed'] else negative) else original[int(i)]
                 for r, i in zip(added, controls)]
        rows = original+extra+extra
        base.require([r['changed'] for r in rows] == output_labels.tolist(), 'row_labels')
        results[model] = totals(rows, output_weights)
    base.write(out, dict(version='exposure307-v1', runner=base.ref(base.ROOT/'scripts/exposure307.py'),
        registration=base.ref(base.ROOT/'reports/work/TRANSITION-291/registration.json'),
        membership=base.ref(base.PACKAGE/'membership.json'), weights=parent['weights'], models=results,
        entries=len(output_weights), weightSum=float(output_weights.astype(np.float64).sum()),
        interpretation='Relative loss weights, not measured gradients or independent trials.',
        limitations=['Reverse pairs repeat group exposure.', 'Legacy replay ancestry remains unresolved here.'],
        training=False, rolesChanged=False))


if __name__ == '__main__': run()
