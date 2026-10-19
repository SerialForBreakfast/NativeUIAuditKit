"""Bind frozen cascade comparisons to verified future scoring receipts."""
import copy
from collections import Counter
import research_queue as q
import cached_model_cascade as cascade
from experiment_templates import checked, pin
from model_decision_batch434 import retain

OUT = None


def membership(document):
    q.require(document.get('version') == 'coverage-membership-v1', 'validation_membership_version')
    rows = document['rows']
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'validation_duplicate_membership')
    for r in rows:
        q.require(r['profile'] in ('standard', 'hcf') and all(isinstance(r[k], str) and r[k] for k in
                  ('id', 'sha256', 'case', 'group', 'condition')), 'validation_membership_fields')
    return rows


def normalize(report, expected):
    """Keep case identity, but count the original capture groups."""
    q.require(report['version'] == 'proposal-agreement-v1' and report['modelAccepted'] is False, 'validation_report')
    result = copy.deepcopy(report)
    lookup = {r['id']: r for r in expected}
    seen = set()
    for row in result['rows']:
        key = (row['id'], row['arm'], row['model'])
        q.require(key not in seen and row['id'] in lookup, 'validation_duplicate_or_unexpected')
        seen.add(key); item = lookup[row['id']]
        q.require((row['sha256'], row['profile'], row['group']) ==
                  (item['sha256'], item['profile'], item['case']), 'validation_frame_changed')
        q.require(row['arm'] in ('detector', 'detector-plus-ring') and row['model'] in ('baseline', 'candidate'), 'validation_arm')
        row.update(case=item['case'], group=item['group'], relatedToPrior=item['relatedToPrior'])
    q.require(len(seen) == len(expected)*4, 'validation_missing_rows')
    return result


def context():
    spec = q.load(OUT.parents[2]/'spec.json')
    deps = q.dependency_inputs(spec, OUT.parents[4])
    q.require(deps == q.load(OUT/'dependencies.json'), 'validation_dependencies')
    plan = q.load(checked(spec['validationPlan']))
    q.require(plan['version'] == 'cascade-validation-plan-v1', 'validation_plan')
    data = q.load(checked(plan['membership']))
    membership(data)
    return spec, deps, plan, data


def receipt():
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))


def run():
    spec, deps, plan, data = context()
    q.require(len(deps) == 2, 'validation_pair_count')
    reports = []
    for dep, source in zip(deps, spec['producerSpecs']):
        producer = q.load(checked(source))
        q.require(q.text_digest(producer) == dep['specSHA256'] and producer['id'] == dep['job'], 'validation_producer')
        reports.append(cascade.agreement.supplemental.load(dict(report=dep['outputs'][0], result=dep['result'], spec=source)))
    result = cascade.evaluate(*reports)
    q.require(result['models'] == plan['models'], 'validation_models')
    result = normalize(result, [r for r in data['rows'] if r['condition'] == spec['validationCondition']])
    q.save(OUT/'benchmark_summary.json', result)
    receipt()


def summarize(reports, data, prior, models):
    rows = membership(data)
    q.require(all(r['models'] == models for r in reports), 'validation_models')
    q.require(prior['version'] == 'proposal-agreement-decision-v1' and prior['modelAccepted'] is False and
              prior['policy'] == 'baseline-first-candidate-agreement-fallback', 'validation_prior')
    expected = sorted((r['id'], r['sha256'], r['group'], r['profile']) for r in rows)
    result = cascade.agreement.summarize(reports, expected, prior['preservation'])
    standard = [r for r in result['rows'] if r['profile'] == 'standard' and r['arm'] == 'detector' and r['model'] == 'baseline']
    result['support'] = {}
    for label, related in [('related', True), ('distinctIdentifiers', False)]:
        subset = [r for r in standard if r['relatedToPrior'] == related]
        result['support'][label] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
            gains=sum(r['gain'] for r in subset), losses=sum(r['loss'] for r in subset), newWrong=sum(r['newWrong'] for r in subset))
    previous = [r for r in prior['rows'] if r['profile']=='standard' and r['arm']=='detector' and r['model']=='baseline']
    mapping = data['priorCaseGroups']
    q.require(all(r['group'] in mapping for r in previous), 'validation_prior_group_missing')
    result['retainedPrior'] = dict(frames=len(previous), cases=len({r['group'] for r in previous}),
        originalGroups=len({mapping[r['group']] for r in previous}), outcomes=dict(Counter(r['outcome'] for r in previous)),
        gains=sum(r['gain'] for r in previous), losses=sum(r['loss'] for r in previous), newWrong=sum(r['newWrong'] for r in previous))
    result.update(policy=prior['policy'], models=models,
        limitation='Development only. Distinct group identifiers do not prove independent ancestry. Earlier standalone crop losses remain.',
        nextAction='If new regressions occur, reject expansion. Otherwise require independent native evidence before runtime qualification. Do not tune thresholds.')
    return result


def finish():
    _, deps, plan, data = context()
    result = summarize([q.load(checked(d['outputs'][0])) for d in deps[:-1]], data,
                       q.load(checked(deps[-1]['outputs'][0])), plan['models'])
    q.save(OUT/'decision.json', result)
    lines = ['# Frozen cascade validation', '', 'Outcome: '+result['outcome'], '',
             'Standard: '+str(result['slices']['standard/baseline']), '',
             'Group support: '+str(result['support']), '', result['limitation'], '', result['nextAction']]
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    receipt()


def compile_request(source, destination, queue=q.QUEUE):
    request = q.load(source)
    q.require(set(request) == {'version','id','membership','prior','pairs'} and request['version']=='cascade-validation-request-v1', 'validation_request')
    q.require(q.ID.fullmatch(request['id']) and q.ID.fullmatch(request['prior']), 'validation_id')
    data = q.load(checked(request['membership'])); rows = membership(data)
    pairs = request['pairs']
    q.require(1 <= len(pairs) <= 8 and len({p['condition'] for p in pairs})==len(pairs), 'validation_pairs')
    q.require({p['condition'] for p in pairs} == {r['condition'] for r in rows}, 'validation_conditions')
    parents = {}; bindings = []; models = None
    for pair in pairs:
        q.require(set(pair)=={'condition','primary','supplemental'}, 'validation_pair_fields')
        sources = []
        for key in ('primary','supplemental'):
            ident=pair[key];q.require(q.ID.fullmatch(ident), 'validation_producer_id')
            path=queue/'jobs'/ident/'spec.json';spec=q.load(path)
            q.require(spec['template']['id']=='T57', 'validation_template')
            pins={k:spec['template']['inputs'][k] for k in ('baseline','candidate')}
            for ref in pins.values():checked(ref)
            if models is None:models=pins
            q.require(models==pins, 'validation_model_mismatch')
            parents[ident]=spec;sources.append(pin(path))
        bindings.append(sources)
    prior=q.load(queue/'jobs'/request['prior']/'spec.json')
    q.require(prior['adapter']['steps']==['cached_model_cascade.finish'], 'validation_prior_template')
    parents[prior['id']]=prior
    destination.mkdir(parents=True,exist_ok=True)
    plan=destination/'plan.json'
    retain(plan,dict(version='cascade-validation-plan-v1',membership=request['membership'],models=models,request=pin(source)))
    def dep(s,output):return dict(job=s['id'],specSHA256=q.text_digest(s),outputs=[output])
    def make(suffix,step,deps):
        return dict(version='research-spec-v2',id=request['id']+'-'+suffix,task=request['id'],owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',jobKind='artifact',
            question='Does the frozen cascade preserve selections and abstentions on additional retained native conditions?',
            hypothesis='The fixed candidate fallback preserves retained selections beyond the original comparison.',
            controlledComparison='Keep models, scores, thresholds, and data roles fixed. Compare the cascade with retained baseline decisions.',
            decisionRule='Require no lost successes or new wrong selections. Separate original capture groups from cases. Do not promote.',
            nextActionByOutcome=dict(supported='Require independent native verification.',contradicted='Reject expansion and diagnose failures.',inconclusive='Record limited gains or support without threshold tuning.'),
            inputs=[pin(plan),request['membership'],pin(q.MODULES/'cascade_validation.py')],validationPlan=pin(plan),dependencies=deps,
            evidence=dict(reads=[q.relative(plan),request['membership']['path']],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['cascade_validation.'+step],outputAttributes=['cascade_validation.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    specs=[]
    for i,(pair,sources) in enumerate(zip(pairs,bindings),1):
        spec=make(f'compare-{i:02}','run',[dep(parents[pair[k]],'benchmark_summary.json') for k in ('primary','supplemental')])
        spec.update(producerSpecs=sources,validationCondition=pair['condition']);spec['inputs'].extend(sources)
        spec['evidence']['reads'].extend(r['path'] for r in sources);specs.append(spec)
    specs.append(make('decision','finish',[dep(s,'benchmark_summary.json') for s in specs]+[dep(prior,'decision.json')]))
    jobs=[]
    for spec in specs:
        q.validate(spec);path=destination/(spec['id']+'.json');retain(path,spec)
        jobs.append(dict(job=spec['id'],specSHA256=q.text_digest(spec),spec=pin(path)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(plan),existing=[dict(job=s['id'],specSHA256=q.text_digest(s)) for s in parents.values()],jobs=jobs,executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest
