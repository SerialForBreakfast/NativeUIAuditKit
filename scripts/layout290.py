"""Compare alternating approved layouts with the retained fixed-layout control."""
import argparse
from pathlib import Path
import time
import numpy as np
import representation287 as model

base = model.base
torch = base.torch
OUT = base.ROOT / 'reports/work/TRANSITION-290/DTM082'


def replace_rows(original, labels, replacement, values, count):
    result = original.copy()
    seen = set()
    start = len(original)-2*count
    base.require(start >= 0, 'native_row_count')
    base.require(len(replacement['rows']) == len(values), 'replacement_count')
    for row, value in zip(replacement['rows'], values):
        i = row['trainingIndex']
        base.require(type(i) is int and start <= i < start+count and i not in seen, 'replacement_index')
        base.require(row['role'] == 'train' and labels[i] == labels[i+count] == row['changed'], 'replacement_role')
        seen.add(i)
        result[i] = value
        result[i+count] = base.reporting.reverse(value[None])[0]
    return result


def run():
    base.require(not OUT.exists(), 'output_collision')
    torch.set_num_threads(2)
    manifest, _, replacement, rx, _, _, _, initializer, pins = base.prepare()
    original = np.load(base.PACKAGE/'training.npy', allow_pickle=False)
    labels = np.load(base.PACKAGE/'labels.npy', allow_pickle=False)
    membership = base.read(base.PACKAGE/'membership.json')
    shifted = replace_rows(original, labels, replacement, rx, len(membership['selected']))
    prior = base.ROOT/'reports/work/TRANSITION-287/DTM081'
    registration = base.read(prior/'registration.json')
    old = base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights = np.load(base.checked(old['weights']), allow_pickle=False)
    for name, value in [('training', shifted), ('labels', labels), ('weights', weights)]:
        base.require(base.sha(value.tobytes()) == registration[name+'SHA256'], name+'_identity')
    base.require(base.ref(initializer) == registration['initializer'], 'initializer_identity')
    base.checked(registration['runner']); base.checked(registration['residualImplementation'])
    result = base.read(prior/'result.json')
    control = model.load_candidate(base.checked(result['model']))
    net = model.extend(base.load_model(initializer))
    config = registration['configuration']
    base.require(config['epochs'] == 120 and config['seed'] == 42, 'fixed_configuration')
    changed = np.array([not np.array_equal(a,b) for a,b in zip(original,shifted)])
    OUT.mkdir(parents=True)
    base.write(OUT/'registration.json', dict(version='layout290-v1',
        hypothesis='Alternating approved original and shifted layouts reduces dependence on a fixed layout.',
        configuration=config, initializer=base.ref(initializer), pins=pins,
        representation=model.REPRESENTATION, runner=base.ref(Path(__file__)),
        trainer=base.ref(Path(base.trainer.__file__)), control=base.ref(prior/'result.json'),
        controlEvaluation=base.ref(prior/'evaluation.json'), originalSHA256=base.sha(original.tobytes()),
        shiftedSHA256=base.sha(shifted.tobytes()), labelsSHA256=base.sha(labels.tobytes()),
        weightsSHA256=base.sha(weights.tobytes()), rows=len(labels), changedRows=int(changed.sum()),
        epochSchedule=['shifted' if epoch%2 == 0 else 'original' for epoch in range(120)],
        updates=120*((len(labels)+config['batch']-1)//config['batch']),
        controlReuse='Same initialization, representation, labels, weights, order, epochs, and updates. Only layout schedule changes.',
        outputCapBytes=256*1024**2, wallTimeLimit=None, dataRolesChanged=False,
        selection='fixed-last', acceptance='No individual regressions against DTM067, DTM078, or DTM081.',
        productionEligible=False))
    print('Registered alternating layouts:', int(changed.sum()), 'changed rows.', flush=True)
    started = time.monotonic()
    def progress(row):
        base.write(OUT/f"epoch-{row['epoch']:04d}.json", row)
        print(row, flush=True)
    net, history = base.trainer.fit(net, torch.from_numpy(shifted), torch.from_numpy(labels), config,
        progress, torch.from_numpy(weights), alternate_inputs=torch.from_numpy(original))
    torch.save(dict(state=net.state_dict(), representation=model.REPRESENTATION,
                    registration=base.ref(OUT/'registration.json')), OUT/'last.pt')
    restored = model.load_candidate(OUT/'last.pt')
    fit = base.metrics(restored, shifted, labels)
    base.require(fit == base.metrics(net, shifted, labels), 'checkpoint_parity')
    base.write(OUT/'result.json', dict(fit=fit, originalFit=base.metrics(restored,original,labels),
        history=history, model=base.ref(OUT/'last.pt'), checkpointParity=True,
        seconds=time.monotonic()-started, productionEligible=False))
    refs = {'DTM067':base.load_model(initializer), 'DTM081':control,
            'DTM078':base.load_model(base.checked(base.read(base.ROOT/'reports/work/CONFLICT-281/DTM078/result.json')['model']))}
    evaluation = base.evaluate_full(restored, refs, manifest)
    base.write(OUT/'evaluation.json', evaluation)
    size = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(size < 256*1024**2, 'output_budget')
    base.write(OUT/'completion.json', dict(seconds=time.monotonic()-started, outputBytes=size,
        regressionPassed=evaluation['regressionPassed'], productionEligible=False))
    print('Complete:', evaluation['regressionPassed'], flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args(); run()
