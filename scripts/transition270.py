"""Compare fixed initialization and update budgets on admitted native examples."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
for key, folder in [('TMPDIR', '.build/direct53-tmp'), ('TORCH_HOME', '.build/direct53-torch')]:
    os.environ[key] = str(ROOT / folder)

import numpy as np
import torch
import artifact_storage as storage
import native_adapt152 as trainer
import transition249_worker as worker
import transition245 as reporting
from diagnose_reflow115 import decisions

OUT = ROOT / 'reports/work/TRANSITION-270'
PACKAGE = ROOT / 'reports/work/TRANSITION-249/artifacts/package'
CONFIG = dict(epochs=3120, lr=.0001, batch=16, seed=42, threads=2,
              inputSize=[192, 128], selection='fixed-last')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(values):
    return hashlib.sha256(values).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=worker.digest(path))


def checked(record):
    logical = ROOT / record['path']
    require(not Path(record['path']).is_absolute() and '..' not in logical.parts, 'reference_path')
    path = storage.resolve_input(logical)
    require(worker.digest(path) == record['sha256'], 'reference_hash')
    return path


def qualifies(original, adapted):
    return (adapted['summary']['correct'] == 64 and adapted['meanBCE'] < .1
            and (adapted['summary']['correct'] > original['summary']['correct']
                 or (adapted['summary']['correct'] == original['summary']['correct']
                     and adapted['meanBCE'] < original['meanBCE'])))


def metrics(net, x, y):
    with torch.inference_mode():
        logits = torch.cat([net.change(net.change_inputs(torch.from_numpy(v))).flatten()
                            for v in np.array_split(x, max(1, (len(x) + 7) // 8))])
        p = logits.sigmoid().numpy()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, torch.from_numpy(y))
    return dict(summary=trainer.w.summary(p, y), forcedCorrect=int(((p >= .5) == y).sum()),
                meanBCE=float(loss), rawLogitRange=[float(logits.min()), float(logits.max())],
                logitMagnitudeAbove20=int((logits.abs() > 20).sum()), probabilities=p.tolist())


def load_model(path):
    net = worker.make_model(torch, paired_context=True)
    net.load_state_dict(torch.load(path, map_location='cpu', weights_only=True)['state'])
    return net.eval()


def prepare():
    manifest = worker.read_package(PACKAGE)
    prior = read(ROOT / 'reports/work/TRANSITION-266/preflight.json')
    for key in ('package', 'replacements', 'admission'):
        checked(prior[key])
    replacement = read(checked(prior['replacements']))
    admission = read(checked(prior['admission']))
    require(admission['approved'] and admission['role'] == 'development-training'
            and admission['protectedEndpointOverlap'] is False, 'admission')
    checked(admission['intake'])
    rx = np.load(checked(replacement['tensor']), allow_pickle=False)
    checked(replacement['campaign']); checked(replacement['intake'])
    seen = set()
    for row, value in zip(replacement['rows'], rx):
        require(row['role'] == 'train' and sha(value.tobytes()) == row['tensorSHA256'], 'row_tensor')
        for r in row['images'] + row['metadata']:
            if r['sha256'] not in seen:
                checked(r); seen.add(r['sha256'])
    ids = prior['balancedReplacementIndices']
    require(len(ids) == len(set(ids)) == 32 and len(rx) == len(replacement['rows']), 'membership')
    selected = [replacement['rows'][i] for i in ids]
    require([r['sourceRowID'] for r in selected] == prior['balancedSourceRows'], 'source_membership')
    x = np.concatenate((rx[ids], reporting.reverse(rx[ids])))
    y0 = np.array([r['changed'] for r in selected], np.float32)
    y = np.concatenate((y0, y0))
    old = read(ROOT / 'reports/work/TRANSITION-266/DTM073/registration.json')
    require(sha(x.tobytes()) == old['trainingSHA256'] and sha(y.tobytes()) == old['labelsSHA256'], 'balanced_identity')
    require(np.bincount(y.astype(int)).tolist() == [32, 32], 'balanced_labels')
    original = checked(old['initializer'])
    diag = read(ROOT / 'reports/work/TRANSITION-266/initialization-diagnosis.json')
    adapted = checked(diag['results']['DTM067']['model'])
    initial = load_model(original)
    sanity = np.load(PACKAGE / 'sanity.npy', allow_pickle=False)
    require(np.allclose(worker.score(initial, sanity), np.load(PACKAGE / 'sanity_scores.npy'), atol=1e-4, rtol=0), 'baseline_parity')
    pins = dict(package=ref(PACKAGE / 'manifest.json'), prior=ref(ROOT / 'reports/work/TRANSITION-266/preflight.json'),
                initializerOriginal=ref(original), initializerAdapted=ref(adapted),
                trainer=ref(Path(trainer.__file__)), runner=ref(Path(__file__)),
                trainingSHA256=sha(x.tobytes()), labelsSHA256=sha(y.tobytes()),
                configuration=CONFIG, updates=3120 * 4, outputCapBytes=64 * 1024**2,
                wallTimeLimit=None, torchVersion=torch.__version__, numpyVersion=np.__version__,
                device='cpu', thresholds=[.15, .85], verifiedSourceFiles=len(seen), productionEligible=False)
    return manifest, prior, replacement, rx, x, y, original, adapted, pins


def fit_one(name, initializer, x, y, configuration, pins, weights=None):
    target = OUT / name
    target.mkdir()
    write(target / 'registration.json', dict(pins=pins, initializer=ref(initializer), configuration=configuration,
          rows=len(x), trainingSHA256=sha(x.tobytes()), labelsSHA256=sha(y.tobytes()),
          weightsSHA256=None if weights is None else sha(weights.tobytes()), selection='fixed-last'))
    net = load_model(initializer)
    before = metrics(net, x, y)
    write(target / 'initial.json', before)
    def progress(row):
        if row['epoch'] == 1 or row['epoch'] % 100 == 0 or row['epoch'] == configuration['epochs']:
            write(target / f"epoch-{row['epoch']:04}.json", row)
            print(name, row, flush=True)
    net, history = trainer.fit(net, torch.from_numpy(x), torch.from_numpy(y), configuration,
                              progress, weights=None if weights is None else torch.from_numpy(weights))
    torch.save(dict(state=net.state_dict(), registration=ref(target / 'registration.json')), target / 'last.pt')
    restored = load_model(target / 'last.pt')
    result = metrics(restored, x, y)
    require(result == metrics(net, x, y), 'checkpoint_parity')
    result.update(history=history, model=ref(target / 'last.pt'), geometryFrozen=True,
                  checkpointParity=True, updates=configuration['epochs'] * ((len(x)+15)//16), productionEligible=False)
    write(target / 'result.json', result)
    print(name, result['summary'], 'BCE', result['meanBCE'], flush=True)
    return restored, result


def evaluate_full(net, references, manifest):
    membership = read(PACKAGE / 'membership.json')
    rows = membership['rows']
    report = {}
    for name in manifest['evaluation']:
        x = np.load(PACKAGE / name, allow_pickle=False)
        y = (np.array([r['changed'] for r in rows]) if 'native' in name else
             np.array(membership['replayLabels']) if 'replay' in name else np.zeros(len(x)))
        p = worker.score(net, x)
        item = dict(summary=trainer.w.summary(p, y), probabilities=p.tolist(), lostCorrect={})
        for key, reference in references.items():
            rp = worker.score(reference, x)
            item['lostCorrect'][key] = int(((decisions(rp) == y) & (decisions(p) != y)).sum())
        if name == 'native.npy':
            item['byRoleAndCondition'] = reporting.summaries(p, rows)
        report[name] = item
    from transition250 import interpolate
    strengths = []
    for name in ('left8', 'center8', 'global8'):
        x = np.load(PACKAGE / (name+'.npy'), allow_pickle=False)
        for strength in (0., .25, .5, 1.):
            v = interpolate(x, strength)
            for order, value in [('forward', v), ('reverse', reporting.reverse(v))]:
                p = worker.score(net, value); y = np.zeros(len(value))
                lost = {k:int(((decisions(worker.score(r, value)) == y) & (decisions(p) != y)).sum())
                        for k,r in references.items()}
                strengths.append(dict(condition=name, strength=strength, order=order,
                                      summary=trainer.w.summary(p,y), lostCorrect=lost))
    return dict(conditions=report, strengths=strengths,
                regressionPassed=all(not any(v['lostCorrect'].values()) for v in list(report.values())+strengths),
                productionEligible=False)


def run():
    torch.set_num_threads(2)
    for key in ('TMPDIR', 'TORCH_HOME'):
        Path(os.environ[key]).mkdir(parents=True, exist_ok=True)
    manifest, prior, replacement, rx, x, y, original, adapted, pins = prepare()
    write(OUT / 'preflight.json', pins)
    print('Preflight passed; exact 64 balanced rows; 12,480 updates per fit.', flush=True)
    _, first = fit_one('DTM075', original, x, y, CONFIG, pins)
    _, second = fit_one('DTM076', adapted, x, y, CONFIG, pins)
    eligible = qualifies(first, second)
    write(OUT / 'selection.json', dict(conditionalFullRun=eligible, selectionUses='training fit only',
          originalCorrect=first['summary']['correct'], adaptedCorrect=second['summary']['correct'],
          originalBCE=first['meanBCE'], adaptedBCE=second['meanBCE']))
    if eligible:
        full = np.load(PACKAGE / 'training.npy', allow_pickle=False)
        labels = np.load(PACKAGE / 'labels.npy', allow_pickle=False)
        membership = read(PACKAGE / 'membership.json')
        native_count = (len(full) - len(membership['replayLabels'])) // 2
        for row,value in zip(replacement['rows'], rx):
            i = row['trainingIndex']
            require(labels[i] == row['changed'] and labels[i+native_count] == row['changed'], 'replacement_label')
            full[i] = value; full[i+native_count] = reporting.reverse(value[None])[0]
        require(sha(full.tobytes()) == prior['fullTrainingSHA256'], 'full_training_identity')
        reg = read(ROOT / 'reports/work/TRANSITION-266/DTM074/registration.json')
        weights = np.load(checked(reg['weights']), allow_pickle=False)
        require(sha(labels.tobytes()) == reg['labelsSHA256'], 'full_label_identity')
        net, _ = fit_one('DTM077', adapted, full, labels, dict(CONFIG, epochs=120), pins, weights)
        refs = dict(DTM067=load_model(adapted), DTM074=load_model(checked(
            read(ROOT / 'reports/work/TRANSITION-266/DTM074/result.json')['model'])))
        result = evaluate_full(net, refs, manifest)
        write(OUT / 'DTM077/evaluation.json', result)
    total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    require(total < 64 * 1024**2, 'output_cap')
    write(OUT / 'completion.json', dict(runs=3 if eligible else 2, outputBytes=total,
          conditionalFullRun=eligible, productionEligible=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    run()
