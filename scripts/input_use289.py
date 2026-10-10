"""Measure added-input use without training or changing labels."""
import argparse
from collections import defaultdict
from pathlib import Path
import time
import types
import numpy as np
import representation287 as model

base = model.base
OUT = base.ROOT / 'reports/work/TRANSITION-289'


def without_residual(self, images):
    inputs = model.change_inputs(self, images)
    inputs[:, 9:] = 0
    return inputs


def compare(normal, suppressed, labels):
    normal, suppressed, labels = map(np.asarray, (normal, suppressed, labels))
    base.require(normal.ndim == 1 and normal.shape == suppressed.shape == labels.shape, 'score_shape')
    base.require(np.isfinite(normal).all() and np.isfinite(suppressed).all(), 'score_finite')
    base.require(((normal >= 0) & (normal <= 1)).all()
                 and ((suppressed >= 0) & (suppressed <= 1)).all(), 'score_range')
    base.require(np.isin(labels, [0, 1]).all(), 'labels')
    a, b = base.decisions(normal), base.decisions(suppressed)
    shift = np.abs(normal - suppressed)
    return dict(count=len(labels), normal=base.trainer.w.summary(normal, labels),
                suppressed=base.trainer.w.summary(suppressed, labels),
                decisionChanges=int((a != b).sum()),
                lostCorrect=int(((a == labels) & (b != labels)).sum()),
                gainedCorrect=int(((a != labels) & (b == labels)).sum()),
                meanAbsoluteScoreChange=float(shift.mean()) if len(shift) else None,
                maximumAbsoluteScoreChange=float(shift.max()) if len(shift) else None)


def score_pair(net, suppressed_net, inputs, expected):
    normal = base.worker.score(net, inputs)
    expected = np.asarray(expected)
    base.require(normal.shape == expected.shape and np.isfinite(expected).all(), 'cache_shape')
    base.require(np.max(np.abs(normal-expected)) <= 1e-6, 'cache_parity')
    return normal, base.worker.score(suppressed_net, inputs)


def run():
    base.require(not OUT.exists(), 'output_collision')
    base.torch.set_num_threads(2)
    manifest = base.worker.read_package(base.PACKAGE)
    membership = base.read(base.PACKAGE/'membership.json')
    prior = base.ROOT/'reports/work/TRANSITION-287/DTM081'
    result = base.read(prior/'result.json')
    evaluation = base.read(prior/'evaluation.json')
    checkpoint = base.checked(result['model'])
    registration = base.read(prior/'registration.json')
    base.require(registration['representation'] == model.REPRESENTATION, 'representation_identity')
    base.checked(registration['runner'])
    base.checked(registration['residualImplementation'])
    base.checked(registration['pins']['package'])
    net = model.load_candidate(checkpoint)
    suppressed_net = model.load_candidate(checkpoint)
    suppressed_net.change_inputs = types.MethodType(without_residual, suppressed_net)
    pins = [base.ref(prior/name) for name in ('result.json','evaluation.json','registration.json')]
    pins += [base.ref(base.PACKAGE/'manifest.json'), base.ref(base.PACKAGE/'membership.json'),
             base.ref(Path(__file__)), base.ref(Path(base.worker.__file__))]
    audit_path = base.ROOT/'reports/work/SIGNAL-286/result.json'
    audit = base.read(audit_path)
    pins.append(base.ref(audit_path))
    # Replacements have different pixels. Do not attach their measurements to old frames.
    regions = {r['originalID']: r for r in audit['rows'] if r['id'] == r['originalID']}
    cached = {}
    for name, directory in [('DTM078','CONFLICT-281'), ('DTM080','SIGNAL-286')]:
        path = base.ROOT/f'reports/work/{directory}/{name}/evaluation.json'
        cached[name] = base.read(path)
        pins.append(base.ref(path))
    OUT.mkdir()
    base.write(OUT/'registration.json', dict(version='input-use289-v1', inputs=pins,
        model=result['model'], threads=2, outputCapBytes=64*1024**2,
        intervention='Set only appended residual inputs to zero after normal preprocessing.',
        training=False, dataRolesChanged=False, productionEligible=False))
    started = time.monotonic()
    reports, cases = {}, []
    for name in manifest['evaluation']:
        inputs = np.load(base.PACKAGE/name, mmap_mode='r', allow_pickle=False)
        rows = membership['rows'] if 'native' in name else None
        labels = np.array([r['changed'] for r in rows]) if rows else (
            np.asarray(membership['replayLabels']) if 'replay' in name else np.zeros(len(inputs)))
        normal, suppressed = score_pair(net, suppressed_net, inputs,
                                        evaluation['conditions'][name]['probabilities'])
        reports[name] = compare(normal, suppressed, labels)
        reports[name]['normalProbabilities'] = normal.tolist()
        reports[name]['suppressedProbabilities'] = suppressed.tolist()
        for index, (a, b, label) in enumerate(zip(normal, suppressed, labels)):
            row = rows[index] if rows else {}
            item = dict(condition=name, index=index, id=row.get('id', f'{name}:{index}'),
                group=row.get('group'), role=row.get('role', 'development-diagnostic'),
                changed=int(label), probability=float(a), suppressedProbability=float(b),
                decision=int(base.decisions(np.array([a]))[0]),
                suppressedDecision=int(base.decisions(np.array([b]))[0]),
                absoluteScoreChange=float(abs(a-b)), conditions=row.get('conditions', []),
                references={key: value['conditions'][name]['probabilities'][index]
                            for key, value in cached.items()})
            region = regions.get(item['id'])
            if region:
                item['observedRegionAudit'] = {k: region[k] for k in
                    ('focusRegionFraction','focusRegionAreaFraction','insideMean255',
                     'outsideMean255','minimumFocusedWidth')}
                item['regionEvidence'] = 'Cached matched-frame diagnostic; not a model input.'
            else:
                item['observedRegionAudit'] = None
                item['regionEvidence'] = 'Unavailable or replaced pixels; no inferred match.'
            cases.append(item)
        print(name, reports[name]['decisionChanges'], 'changed decisions', flush=True)
    groups = defaultdict(list)
    for row in cases:
        if 'native' in row['condition']:
            groups[(row['condition'],row['role'],row['group'])].append(row)
    grouped = [dict(condition=k[0],role=k[1],group=k[2],**compare(
        [r['probability'] for r in rows], [r['suppressedProbability'] for r in rows],
        [r['changed'] for r in rows])) for k,rows in sorted(groups.items())]
    base.write(OUT/'result.json', dict(version='input-use289-v1', conditions=reports, groups=grouped,
        cases=cases, seconds=time.monotonic()-started,
        limitations=['Suppressed inputs can be outside the training distribution.',
                    'Intervention scores do not establish deployment accuracy.',
                    'Related and reversed frames are not independent trials.',
                    'This test measures one added input group, not all model causes.'],
        productionEligible=False))
    total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(total < 64*1024**2, 'output_budget')
    base.write(OUT/'completion.json',dict(cases=len(cases),conditions=len(reports),
        seconds=time.monotonic()-started,outputBytes=total,training=False,productionEligible=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args()
    run()
