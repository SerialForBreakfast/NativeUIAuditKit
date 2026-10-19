"""Test a baseline-first model cascade using verified cached proposal reports."""
import copy
import research_queue as q
import proposal_agreement445 as agreement
from experiment_templates import checked, pin
from model_decision_batch434 import retain

OUT = None


def evaluate(primary, secondary):
    result = agreement.evaluate(primary, secondary)
    sources = {r['id']: r for r in primary['rows']}
    proposals = {r['id']: r for r in secondary['rows']}
    for row in result['rows']:
        if row['model'] != 'baseline':
            continue  # Keep the candidate comparison separate from the cascade.
        source = sources[row['id']]['arms'][row['arm']]
        target = proposals[row['id']]['arms'][row['arm']]
        single = sum(s >= .85 for s in source['models']['baseline']['scores']) == 1
        allowed, reason = agreement.agreement(source, target, 'candidate')
        allowed = allowed and not single and row['profile'] == 'standard'
        outcome = target['models']['candidate']['outcome'] if allowed else row['reference']
        row.update(outcome=outcome, usedSupplemental=allowed,
            reason=reason if allowed else 'retain-baseline',
            gain=row['reference'] not in agreement.SUCCESS and outcome in agreement.SUCCESS,
            loss=row['reference'] in agreement.SUCCESS and outcome not in agreement.SUCCESS,
            newWrong=row['reference'] not in agreement.WRONG and outcome in agreement.WRONG,
            lostUnrestrictedGain=row['unrestricted'] in agreement.SUCCESS and outcome not in agreement.SUCCESS,
            preventedNewWrong=row['unrestricted'] in agreement.WRONG and row['reference'] not in agreement.WRONG and outcome not in agreement.WRONG)
    result['policy'] = 'baseline-first-candidate-agreement-fallback'
    result['limitation'] = 'Post-hoc development only. Candidate-only rows are not the cascade. No production change.'
    return result


def context():
    agreement.OUT = OUT
    return agreement.context()


def gate():
    _, deps, _ = context()
    source = q.load(checked(deps[0]['outputs'][0]))
    q.require(source['version'] == 'proposal-agreement-decision-v1' and source['modelAccepted'] is False, 'cascade_source')
    baseline = source['slices']['standard/baseline']
    candidate = source['slices']['standard/candidate']
    supported = baseline['newWrong'] > 0 and candidate['gain'] > 0 and candidate['newWrong'] == 0 and candidate['loss'] == 0
    q.save(OUT/'gate.json', dict(version='research-condition-v1', outcome='supported' if supported else 'contradicted',
        reason='Test a candidate fallback only after measured agreement differences.', evidence=[deps[0]['result']]))
    q.save(OUT/'preservation.json', source['preservation'])
    agreement.receipt()


def run():
    spec, _, _ = context()
    ref = next(s['from'] for s in spec['stage'] if s['to'] == 'bundle.json')
    source = checked(ref)
    q.require(q.digest(source) == q.digest(OUT/'bundle.json'), 'cascade_stage')
    bundle = q.load(source)
    q.require(set(bundle) == {'version', 'baseline', 'supplemental'} and bundle['version'] == 'supplemental-proposals-v1', 'cascade_bundle')
    q.save(OUT/'benchmark_summary.json', evaluate(agreement.supplemental.load(bundle['baseline']), agreement.supplemental.load(bundle['supplemental'])))
    agreement.receipt()


def finish():
    _, deps, plan = context()
    result = agreement.summarize([q.load(checked(d['outputs'][0])) for d in deps[1:]],
        plan['membership'], q.load(checked(deps[0]['outputs'][1])))
    result['policy'] = 'baseline-first-candidate-agreement-fallback'
    result['nextAction'] = 'Require independent groups if supported. Otherwise stop this cascade branch without threshold tuning.'
    q.save(OUT/'decision.json', result)
    (OUT/'report.md').write_text('# Baseline-first candidate fallback\n\nOutcome: '+result['outcome']+'\n\n'+str(result['slices'])+'\n\n'+result['nextAction']+'\n')
    agreement.receipt()


def compile_request(source, destination, queue=q.QUEUE):
    """Reuse the qualified agreement graph compiler; change only the policy adapter."""
    request = q.load(source)
    q.require(set(request) == {'version', 'id', 'decision', 'bundles', 'review'} and request['version'] == 'cached-cascade-request-v1', 'cascade_request')
    parent = q.load(queue/'jobs'/request['review']/'spec.json')
    q.require(parent['adapter']['steps'] == ['proposal_agreement445.finish'], 'cascade_review')
    destination.mkdir(parents=True, exist_ok=True)
    base = {k: v for k, v in request.items() if k != 'review'}
    base['version'] = 'proposal-agreement-request-v1'
    retain(destination/'base-request.json', base)
    draft = agreement.compile_request(destination/'base-request.json', destination/'draft', queue)
    specs = [q.load(checked(r['spec'])) for r in draft['jobs']]
    final = {}
    jobs = []
    for original in specs:
        spec = copy.deepcopy(original)
        step = spec['adapter']['steps'][0].split('.')[-1]
        spec['adapter'] = dict(type='python-callable', steps=['cached_model_cascade.'+step], outputAttributes=['cached_model_cascade.OUT'])
        spec['inputs'].append(pin(q.MODULES/'cached_model_cascade.py'))
        spec['question'] = 'Can the Standard-only classifier recover abstentions without changing retained baseline selections?'
        spec['hypothesis'] = 'The candidate rejects decorative false selections while the baseline preserves its previous selections.'
        spec['controlledComparison'] = 'Keep scores, boxes, groups, and thresholds fixed. Use candidate agreement only after baseline abstention.'
        if step == 'gate':
            spec['dependencies'] = [dict(job=parent['id'], specSHA256=q.text_digest(parent), outputs=['decision.json'])]
        else:
            for dep in spec['dependencies']:
                dep['specSHA256'] = q.text_digest(final[dep['job']])
        q.validate(spec)
        final[spec['id']] = spec
        path = destination/(spec['id']+'.json');retain(path, spec)
        jobs.append(dict(job=spec['id'], specSHA256=q.text_digest(spec), spec=pin(path)))
    manifest = dict(version='model-decision-compiled-v1', plan=draft['plan'], jobs=jobs,
        existing=[dict(job=parent['id'], specSHA256=q.text_digest(parent))], executionStarted=False, modelAccepted=False)
    retain(destination/'compiled.json', manifest)
    return manifest
