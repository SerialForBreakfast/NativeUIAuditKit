"""Report matched decisions and check whether the added correction helps."""
import argparse
from collections import defaultdict
from pathlib import Path
import time
import numpy as np
import context309 as run
import report291
from report_spatial297 import counts, decision

base = run.base


def metrics(probabilities, labels):
    base.require(np.isin(labels, [0, 1]).all(), 'invalid_label')
    return counts([int(v) for v in labels], [decision(float(v)) for v in probabilities])


def main(out):
    base.require((out/'completion.json').exists(), 'training_incomplete')
    base.require(not (out/'comparison.json').exists(), 'output_collision')
    registration = base.read(out/'registration.json')
    base.checked(registration['runner']); base.checked(registration['trainer'])
    base.require(registration['version'] == run.VERSION, 'report_version')
    membership = base.read(base.checked(registration['membership']))
    evaluations = {name: base.read(out/name/'evaluation.json') for name in ('whole-control', 'context-detail')}
    evaluations['DTM085'] = base.read(base.ROOT/'reports/work/TRANSITION-292/DTM085/evaluation.json')
    evaluations['DTM083'] = base.read(base.ROOT/'reports/work/TRANSITION-291/DTM083/evaluation.json')
    older = {'DTM078': base.ROOT/'reports/work/CONFLICT-281/DTM078/evaluation.json',
             'DTM081': base.ROOT/'reports/work/TRANSITION-287/DTM081/evaluation.json'}
    evaluations.update({name: base.read(path) for name, path in older.items()})
    contrasts = {}
    for name in ('DTM078', 'DTM081', 'DTM083', 'DTM085', 'whole-control'):
        summaries, cases = report291.summarize_comparison(evaluations[name], evaluations['context-detail'], membership)
        grouped = defaultdict(lambda: dict(gains=0, losses=0))
        for row in cases:
            key = (row['input'], row['group'], row['role'])
            grouped[key]['gains'] += row['gainedCorrect']
            grouped[key]['losses'] += row['lostCorrect']
        contrasts[name] = dict(summaries=summaries, cases=cases,
            groups=[dict(input=k[0], group=k[1], role=k[2], **v) for k, v in grouped.items()])
    candidate = run.load_candidate(base.checked(base.read(out/'context-detail/fit.json')['model']))
    run.torch.set_num_threads(2)
    tiny, tiny_rows, tiny_ref = run.tiny_inputs()
    base.require(tiny_ref == registration['tiny'], 'tiny_identity')
    sources = {name: np.load(base.PACKAGE/name, mmap_mode='r', allow_pickle=False)
               for name in ('native.npy', 'left8.npy', 'center8.npy', 'global8.npy')}
    sources['tiny'] = tiny
    corrected = {}; corrections = {}
    for name, values in sources.items():
        parts = []
        hook = candidate.change.correction.register_forward_hook(
            lambda module, inputs, output: parts.append(output.detach().cpu().numpy().reshape(-1)))
        try: corrected[name] = base.worker.score(candidate, values)
        finally: hook.remove()
        corrections[name] = np.concatenate(parts)
    # This ablation keeps trained whole-frame weights. It removes only the added correction.
    with run.torch.no_grad():
        candidate.change.correction.weight.zero_(); candidate.change.correction.bias.zero_()
    ablations = {}
    for name, values in sources.items():
        labels = ([r['changed'] for r in membership['rows']] if name == 'native.npy' else
                  [r['changed'] for r in tiny_rows] if name == 'tiny' else [0]*len(values))
        probabilities = base.worker.score(candidate, values)
        ablations[name] = dict(withCorrection=metrics(corrected[name], labels),
            withoutCorrection=metrics(probabilities, labels),
            meanAbsoluteScoreChange=float(np.abs(corrected[name]-probabilities).mean()),
            maximumAbsoluteScoreChange=float(np.abs(corrected[name]-probabilities).max()),
            correctionLogits=dict(minimum=float(corrections[name].min()), maximum=float(corrections[name].max()),
                                  mean=float(corrections[name].mean())))
        if name == 'tiny':
            ablations[name]['cases'] = [dict(id=row['id'], condition=row['condition'],
                correctionLogit=float(corrections[name][i]), withCorrection=float(corrected[name][i]),
                withoutCorrection=float(probabilities[i])) for i, row in enumerate(tiny_rows)]
    sanity = np.load(base.PACKAGE/'sanity.npy', allow_pickle=False)[:8]
    timings = {}
    for name in ('DTM085', 'whole-control', 'context-detail'):
        path = base.checked(registration['initializer']) if name == 'DTM085' else base.checked(base.read(out/name/'fit.json')['model'])
        net = run.c.model.load_candidate(path) if name == 'DTM085' else run.load_candidate(path)
        begin = time.perf_counter(); base.worker.score(net, sanity); cold = time.perf_counter()-begin
        samples = []
        for _ in range(5):
            begin = time.perf_counter(); base.worker.score(net, sanity); samples.append(time.perf_counter()-begin)
        timings[name] = dict(batch=len(sanity), firstBatchSeconds=cold, warmBatchSeconds=samples,
            warmMedianSecondsPerPair=float(np.median(samples)/len(sanity)), checkpointBytes=path.stat().st_size,
            parameters=sum(p.numel() for p in net.parameters()))
    base.write(out/'comparison.json', dict(version='context309-report-v1',
        inputs=[base.ref(out/'registration.json'), base.ref(out/'completion.json'), tiny_ref,
                base.ref(out/'whole-control/evaluation.json'), base.ref(out/'context-detail/evaluation.json'),
                base.ref(base.ROOT/'reports/work/TRANSITION-292/DTM085/evaluation.json'),
                base.ref(base.ROOT/'reports/work/TRANSITION-291/DTM083/evaluation.json'),
                *[base.ref(path) for path in older.values()]],
        runner=base.ref(Path(__file__)), contrasts=contrasts, correctionAblation=ablations, timings=timings,
        productionEligible=False, finalAudit=False,
        limits=['The ablation is diagnostic, not a selected model.',
                'Timing uses resident CPU execution, not Core ML or isolated hardware.',
                'Repeated and reversed pairs are not independent trials.',
                'The tiny set contains only 4 original development pairs.']))
    print('Case comparisons, correction ablation, and CPU timing complete.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', required=True, action='store_true')
    parser.add_argument('--output', type=Path, default=run.OUT)
    args = parser.parse_args()
    base.require(args.output.resolve().is_relative_to(base.ROOT), 'output_boundary')
    main(args.output)
