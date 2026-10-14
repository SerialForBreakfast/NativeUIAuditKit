"""Measure repeat variation without changing production gates or original views."""
import math
from pathlib import Path

import research_queue as q

OUT = None


def references():
    deps = q.load(OUT / 'dependencies.json')
    for dep in deps:
        for item in dep['outputs']:
            path = q.ROOT / item['path']
            q.require(q.digest(path) == item['sha256'], 'seed_dependency_changed')
    return deps


def training():
    import position355 as p
    import duration358 as duration
    config = q.load(OUT / 'seed.json')
    seed = config['seed']
    q.require(seed in (43, 44), 'seed_not_predefined')
    dep, = references()
    baseline = q.load(q.ROOT / dep['outputs'][0]['path'])
    q.require(baseline['seed'] == 42, 'seed_control_not_verified')
    previous = p.a.b.trainer.fit

    def fit(net, x, y, settings, progress, **kwargs):
        settings.update(seed=seed, epochs=30)
        return previous(net, x, y, settings, progress, **kwargs)

    p.OUT = OUT
    duration.OUT = OUT
    p.a.b.trainer.fit = fit
    try:
        duration.training()
    finally:
        p.a.b.trainer.fit = previous
    result = q.load(OUT / 'fit.json')
    history = [dict(epoch=index + 1, trainLoss=row['loss']) for index, row in enumerate(result['history'])]
    q.save(OUT / 'history.json', history)
    q.save(OUT / 'training-report.json', dict(epochs=len(history), seed=seed, modelAccepted=False))
    q.save(OUT / 'model.json', dict(path=str(OUT / 'last.pt'), sha256=q.digest(OUT / 'last.pt'), seed=seed))


def retained_control():
    """Reuse the verified seed-42 replay instead of training it again."""
    dep, = references()
    receipt = q.load(q.ROOT / dep['result']['path'])
    q.require(receipt.get('replay', {}).get('matched') is True, 'control_replay_not_matched')
    weights, = [item for item in dep['outputs'] if item['path'].endswith('/last.pt')]
    q.save(OUT / 'model.json', dict(path=str(q.ROOT / weights['path']), sha256=weights['sha256'], seed=42))
    q.save(OUT / 'sources.json', dep['outputs'])


def evaluate():
    import numpy as np
    import additive341 as a
    config = q.load(OUT / 'seed-evaluation.json')
    manifest = q.load(q.ROOT / config['manifest']['path'])
    q.require(q.digest(q.ROOT / config['manifest']['path']) == config['manifest']['sha256'], 'seed_manifest_changed')
    dep, = references()
    model_ref, = dep['outputs']
    model = q.load(q.ROOT / model_ref['path'])
    path = Path(model['path'])
    q.require(q.digest(path) == model['sha256'], 'seed_model_changed')
    a.t.set_num_threads(2)
    network = a.e.load_candidate(path)
    values, baseline = [], []
    for chunk in manifest['chunks']:
        source = q.ROOT / chunk['path']
        q.require(q.digest(source) == chunk['sha256'], 'seed_chunk_changed')
        with np.load(source, allow_pickle=False) as data:
            tensor = a.t.from_numpy(data['tensor'])
            with a.t.inference_mode():
                for offset in range(0, len(tensor), 8):
                    values.extend(a.t.sigmoid(network.change(tensor[offset:offset + 8])).flatten().tolist())
            baseline.extend(data['probabilities'].tolist())
    q.require(len(values) == len(manifest['rows']) == len(baseline), 'seed_membership_count')
    rows = [dict(**row, probability=value, baselineProbability=old)
            for row, value, old in zip(manifest['rows'], values, baseline)]
    q.save(OUT / 'predictions.json', dict(rows=rows, seed=model['seed'], model=model,
        modelAccepted=False, limitation='Mixed retained roles are reported separately. This is not an independent final audit.'))


def decision(value):
    q.require(math.isfinite(value) and 0 <= value <= 1, 'seed_probability')
    return 1 if value >= 0.85 else 0 if value <= 0.15 else None


def compare(documents):
    q.require({d['seed'] for d in documents} == {42, 43, 44} and len(documents) == 3, 'seed_set_incomplete')
    indexed = {}
    for doc in documents:
        rows = {row['id']: row for row in doc['rows']}
        q.require(len(rows) == len(doc['rows']) and rows, 'seed_duplicate_case')
        indexed[doc['seed']] = rows
    first = indexed[42]
    cases = []
    for seed, rows in indexed.items():
        q.require(rows.keys() == first.keys(), 'seed_membership_mismatch')
        for ident in first:
            q.require(all(rows[ident][key] == first[ident][key] for key in
                          ('changed', 'group', 'role', 'images', 'baselineProbability')), 'seed_case_changed')
    for ident, row in first.items():
        correct = {str(seed): decision(rows[ident]['probability']) == row['changed'] for seed, rows in indexed.items()}
        cases.append(dict(id=ident, group=row['group'], role=row['role'], baselineCorrect=decision(row['baselineProbability']) == row['changed'],
                          correct=correct, stableSuccess=all(correct.values()), varied=len(set(correct.values())) > 1))
    slices = []
    for role in sorted({row['role'] for row in cases}):
        selected = [row for row in cases if row['role'] == role]
        slices.append(dict(role=role, frames=len(selected), groups=len({row['group'] for row in selected}),
            stableSuccesses=sum(row['stableSuccess'] for row in selected), variedCases=sum(row['varied'] for row in selected),
            losses={str(seed): sum(row['baselineCorrect'] and not row['correct'][str(seed)] for row in selected) for seed in indexed}))
    return dict(rows=cases, slices=slices, modelAccepted=False, productionGateChanged=False,
        nextAction='Review varied cases and their margins before proposing any retention-rule change.',
        limitation='Three seeds describe this recipe only. Related frames are not independent trials.')


def report():
    deps = references()
    documents = [q.load(q.ROOT / dep['outputs'][0]['path']) for dep in deps]
    q.save(OUT / 'comparison.json', compare(documents))
    q.save(OUT / 'sources.json', [item for dep in deps for item in dep['outputs']])
