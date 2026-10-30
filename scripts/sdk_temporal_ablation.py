"""Reuse verified paired predictions and score only the duplicated-after intervention."""
from collections import Counter
from pathlib import Path
import research_queue as q
from experiment_templates import pin, checked
from sdk_temporal508 import rows
from sdk_campaign508 import pair
from temporal_pairs414 import decision, outcome

OUT = None


def prepare(request):
    q.require(set(request) == {'version', 'id', 'sourceSpec', 'sourceResult', 'sourceSummary'}, 'ablation_fields')
    q.require(request['version'] == 'sdk-temporal-ablation-v1' and q.ID.fullmatch(request['id']), 'ablation_identity')
    spec = q.load(checked(request['sourceSpec']))
    q.require(spec['adapter']['steps'] == ['sdk_temporal508.run'], 'ablation_source_adapter')
    source = q.load(checked(spec['inputs'][0]))
    result_path = checked(request['sourceResult'])
    result = q.load(result_path)
    summary_path = checked(request['sourceSummary'])
    q.require(result['status'] == 'complete' and result['specSHA256'] == q.text_digest(spec), 'ablation_source_completion')
    q.require(summary_path == result_path.parent/'out/benchmark_summary.json', 'ablation_summary_location')
    q.require(any(x['path'] == 'benchmark_summary.json' and x['sha256'] == request['sourceSummary']['sha256']
                  for x in result['outputs']) and q.outputs_intact(result_path.parent, result), 'ablation_source_outputs')
    data = rows(source)
    pairs = [pair(ref) for ref in source['pairs']]
    q.require(all(p['temporalEligible'] and p['observed'] != 'unknown' for p in pairs), 'ablation_unknown_identity')
    q.require(all(r['changed'] == int(p['observed'] in ('move', 'arrival', 'departure'))
                  for r, p in zip(data, pairs)), 'ablation_label_semantics')
    report = q.load(summary_path)
    q.require(report['version'] == 'sdk-temporal-comparison-v1' and report['models'] == source['models'], 'ablation_model_identity')
    q.require(set(report['results']) == set(source['models']), 'ablation_model_membership')
    for name in source['models']:
        old = report['results'][name]
        q.require(len(old) == len(data), 'ablation_membership')
        for expected, actual in zip(data, old):
            q.require(all(actual[k] == v for k, v in expected.items()), 'ablation_row_identity')
            q.require(actual['outcome'] == outcome(decision(actual['probability']), expected['changed']), 'ablation_old_outcome')
    return spec, source, data, report


def compare(data, report, scores):
    q.require(set(scores) == set(report['results']), 'ablation_score_models')
    results = {}
    for name, values in scores.items():
        q.require(len(values) == len(data), 'ablation_score_count')
        entries = []
        for row, old, value in zip(data, report['results'][name], values):
            new = outcome(decision(value), row['changed'])
            entries.append(dict(**row, pairedProbability=old['probability'], repeatedAfterProbability=value,
                pairedOutcome=old['outcome'], repeatedAfterOutcome=new,
                lostWithRemoval=old['outcome'] == 'correct' and new != 'correct',
                recoveredWithRemoval=old['outcome'] != 'correct' and new == 'correct'))
        results[name] = entries
    return dict(version='sdk-temporal-ablation-result-v1', results=results,
        counts={name:dict(Counter(r['repeatedAfterOutcome'] for r in rr)) for name, rr in results.items()},
        lostWithRemoval={name:sum(r['lostWithRemoval'] for r in rr) for name, rr in results.items()},
        recoveredWithRemoval={name:sum(r['recoveredWithRemoval'] for r in rr) for name, rr in results.items()},
        groups=sorted({r['group'] for r in data}), trainingEligible=False, modelAccepted=False,
        limitation='Review-only intervention. Repeated after frames are not a single-image model. Related pairs do not establish independent accuracy or background robustness.')


def build(path):
    request = q.load(path)
    spec, source, data, report = prepare(request)
    refs = [pin(path), *[request[k] for k in ('sourceSpec', 'sourceResult', 'sourceSummary')],
            *spec['inputs'], *[im for row in data for im in row['images']], pin(Path(__file__).resolve())]
    refs = list({r['path']:r for r in refs}.values())
    return dict(version='research-spec-v2', id=request['id'], task='TEMPORAL544', owner='Maximum-mini-NUIAK',
        kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs,
        adapter=dict(type='python-callable', steps=['sdk_temporal_ablation.run'], outputAttributes=['sdk_temporal_ablation.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[r['path'] for r in refs[:-1]]),
        question='Do correct native focus-change decisions need the before frame?',
        hypothesis='Removing before-frame information loses observed movement decisions while preserving unchanged-focus decisions.',
        controlledComparison='Reuse completed ordered-pair predictions. Score duplicated after frames with identical weights and fixed 0.15/0.85 thresholds.',
        decisionRule='Report lost and recovered cases per model. Do not infer destination accuracy or promote models.',
        nextActionByOutcome=dict(supported='Add independent content-only and departure groups before training.',
            contradicted='Diagnose scene shortcuts before preparing a training correction.',
            inconclusive='Keep original predictions and report missing condition coverage.'))


def run():
    import additive341 as a
    import report_additive341 as scoring
    spec = q.load(OUT.parents[2]/'spec.json')
    request = q.load(checked(spec['inputs'][0]))
    _, source, data, report = prepare(request)
    intervention = [dict(row, images=[row['images'][1], row['images'][1]]) for row in data]
    a.t.set_num_threads(2)
    scores = {}
    for name, ref in source['models'].items():
        model = a.e.load_candidate(checked(ref)); model.eval()
        with a.t.inference_mode():
            scores[name] = scoring.score_rows(model, intervention, False).tolist()
    result = compare(data, report, scores)
    result.update(models=source['models'], sourceSummary=request['sourceSummary'])
    q.save(OUT/'benchmark_summary.json', result)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    q.save(args.output, build(args.request))
