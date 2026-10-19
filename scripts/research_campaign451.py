"""Compile bounded diagnosis and matched comparisons through the existing queue."""
import argparse
import copy
import json
from collections import Counter
from pathlib import Path

import research_queue as q
import hcf_templates395 as templates
from experiment_batch402 import compile_batch
from experiment_templates import checked, pin
from model_decision_batch434 import retain
from proposal_geometry_audit import audit
from proposal_campaign443 import resolved_inputs
from supplemental_proposals427 import load

OUT = None
SUCCESS = {'correct', 'correct-abstention'}
OUTCOMES = SUCCESS | {'miss', 'wrong', 'false-selection'}


def members(document):
    q.require(document.get('version') == 'coverage-membership-v1', 'campaign_membership_version')
    rows = document['rows']
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'campaign_duplicate_membership')
    for row in rows:
        q.require(row['profile'] in ('standard', 'hcf') and all(isinstance(row[k], str) and row[k]
                  for k in ('id', 'sha256', 'case', 'group', 'condition')), 'campaign_membership_fields')
    return rows


def validate_report(report, expected):
    audit(report)  # Reuse geometry and score validation without rewriting it.
    capture = q.load(checked(report['inputs']['capture']))
    q.require(capture['plan'].get('trainingEligible') is False and capture['plan']['cases'] and
              all(c['role'] == 'development' for c in capture['plan']['cases']), 'campaign_data_role')
    q.require(report.get('modelAccepted') is False, 'campaign_model_acceptance')
    q.require((report['threshold'], report['matchingIoU'], report['duplicateIoU']) == (.85, .5, .5),
              'campaign_settings')
    actual = [(r['id'], r['sha256'], r['group'], r['profile']) for r in report['rows']]
    wanted = [(r['id'], r['sha256'], r['case'], r['profile']) for r in expected]
    q.require(sorted(actual) == sorted(wanted), 'campaign_membership_changed')
    for r in report['rows']:
        q.require(type(r['noFocus']) is bool, 'campaign_focus_unknown')
        present = r['arms']['detector']['focusedProposalPresent']
        q.require(type(present) is bool or (r['noFocus'] and present is None), 'campaign_proposal_unknown')
        for arm in ('known-box', 'detector'):
            for model in ('baseline', 'candidate'):
                value = r['arms'][arm]['models'][model]
                q.require(value['outcome'] in OUTCOMES, 'campaign_outcome')
                selected = sum(s >= .85 for s in value['scores'])
                if r['noFocus']:
                    q.require(value['outcome'] == ('false-selection' if selected == 1 else 'correct-abstention'), 'campaign_no_focus_outcome')
                else:
                    q.require(value['outcome'] in {'correct','miss','wrong'} and
                              (value['outcome'] == 'miss') == (selected != 1), 'campaign_selection_outcome')


def diagnose(report, expected):
    validate_report(report, expected)
    geometry = {r['id']: r for r in audit(report)['rows']}
    groups = {r['id']: r['group'] for r in expected}
    rows = []
    for r in report['rows']:
        known = r['arms']['known-box']['models']['baseline']['outcome']
        detected = r['arms']['detector']['models']['baseline']['outcome']
        reason = 'retained-success' if detected in SUCCESS else 'selection-failure'
        if not r['noFocus'] and not r['arms']['detector']['focusedProposalPresent']:
            reason = 'missing-proposal'
        elif known in SUCCESS and detected not in SUCCESS:
            reason = 'crop-selection-failure'
        rows.append(dict(id=r['id'], sha256=r['sha256'], group=groups[r['id']], profile=r['profile'],
                         noFocus=r['noFocus'], reason=reason, known=known, detected=detected,
                         controls=geometry[r['id']]['controls']))
    return dict(version='research-diagnosis-v1', rows=rows, modelAccepted=False,
                nextRequirement='Missing boxes need eligible annotations. Crop failures need matched correction evidence.')


def compare(original, correction, expected):
    for report in (original, correction):
        validate_report(report, expected)
    fixed = set(original['inputs']) - {'candidate', 'candidateSelection'}
    q.require(set(original['inputs']) == set(correction['inputs']) and
              all(original['inputs'][k] == correction['inputs'][k] for k in fixed), 'campaign_unmatched_inputs')
    q.require(original['inputs']['baseline'] != correction['inputs']['candidate'], 'campaign_same_model')
    index = {r['id']: r for r in correction['rows']}
    groups = {r['id']: r['group'] for r in expected}
    rows = []
    for old in original['rows']:
        new = index[old['id']]
        q.require(old['noFocus'] == new['noFocus'], 'campaign_label_changed')
        for arm in ('known-box', 'detector'):
            a, b = old['arms'][arm], new['arms'][arm]
            q.require(a['candidates'] == b['candidates'] and a['models']['baseline'] == b['models']['baseline'],
                      'campaign_control_changed')
            before, after = a['models']['baseline']['outcome'], b['models']['candidate']['outcome']
            rows.append(dict(id=old['id'], sha256=old['sha256'], group=groups[old['id']], profile=old['profile'],
                noFocus=old['noFocus'], arm=arm, baseline=before, candidate=after,
                gain=before not in SUCCESS and after in SUCCESS, loss=before in SUCCESS and after not in SUCCESS,
                newWrong=after in ('wrong', 'false-selection') and before not in ('wrong', 'false-selection')))
    return dict(version='research-comparison-v1', rows=rows, modelAccepted=False,
                models={k: correction['inputs'][k] for k in ('baseline', 'candidate')})


def context():
    spec = q.load(OUT.parents[2]/'spec.json')
    deps = q.dependency_inputs(spec, OUT.parents[4])
    q.require(deps == q.load(OUT/'dependencies.json'), 'campaign_dependencies')
    plan = q.load(checked(spec['campaignPlan']))
    data = members(q.load(checked(plan['membership'])))
    return spec, plan, data, {d['job']: d for d in deps}


def read_report(ident, spec, deps):
    ref = spec['producerSpecs'][ident]
    dep = deps[ident]
    report = load(dict(report=dep['outputs'][0], result=dep['result'], spec=ref))
    q.require(report['inputs'] == resolved_inputs(q.load(checked(ref)), OUT.parents[4]), 'campaign_report_inputs')
    return report


def write(name, result):
    q.save(OUT/name, result)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))


def diagnosis():
    spec, plan, data, deps = context()
    pair = spec['pair']
    expected = [r for r in data if r['condition'] == pair['condition']]
    write('diagnosis.json', diagnose(read_report(pair['baseline'], spec, deps), expected))


def comparison():
    spec, plan, data, deps = context()
    pair = spec['pair']
    expected = [r for r in data if r['condition'] == pair['condition']]
    result = compare(read_report(pair['baseline'], spec, deps), read_report(pair['correction'], spec, deps), expected)
    diagnosis_result = q.load(checked(deps[spec['diagnosisJob']]['outputs'][0]))
    q.require({r['id'] for r in diagnosis_result['rows']} == {r['id'] for r in expected}, 'campaign_diagnosis_membership')
    result['diagnosis'] = diagnosis_result['rows']
    write('comparison.json', result)


def assess(reports, expected, retained_failures):
    rows = [r for report in reports for r in report['rows']]
    actual = [(r['id'], r['sha256'], r['group'], r['profile'], r['arm']) for r in rows]
    wanted = [(r['id'], r['sha256'], r['group'], r['profile'], a) for r in expected for a in ('known-box', 'detector')]
    q.require(sorted(actual) == sorted(wanted), 'campaign_incomplete_suite')
    q.require(reports and all(r['models'] == reports[0]['models'] for r in reports), 'campaign_models_changed')
    standard = [r for r in rows if r['profile'] == 'standard']
    deployed = [r for r in standard if r['arm'] == 'detector']
    losses = [r for r in standard if r['loss'] or r['newWrong']]
    gains = [r for r in deployed if r['gain']]
    outcome = 'contradicted' if losses or retained_failures else 'inconclusive'
    if outcome != 'contradicted' and gains and len({r['group'] for r in deployed}) >= 3 and any(r['noFocus'] for r in deployed):
        outcome = 'supported'
    slices = {}
    for profile in ('standard', 'hcf'):
        for arm in ('known-box', 'detector'):
            subset = [r for r in rows if r['profile'] == profile and r['arm'] == arm]
            slices[profile+'/'+arm] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
                gains=sum(r['gain'] for r in subset), losses=sum(r['loss'] for r in subset),
                newWrong=sum(r['newWrong'] for r in subset), noFocus=sum(r['noFocus'] for r in subset),
                outcomes=dict(Counter(r['candidate'] for r in subset)))
    return dict(version='research-campaign-decision-v1', outcome=outcome, modelAccepted=False, rows=rows, slices=slices,
        retainedFailures=retained_failures, models=reports[0]['models'],
        evidenceStates=dict(software='verified-execution', data='development-only', integration='not-assessed', model='not-promoted'),
        limitation='Original groups do not prove independent ancestry. Class errors and deployment safety remain unqualified.',
        nextAction={'contradicted':'Reject replacement. Preserve failures and identify eligible correction inputs.',
                    'inconclusive':'Stop this campaign. Record the missing gain or independent support.',
                    'supported':'Require independent verification and consumer qualification before replacement.'}[outcome])


def finish():
    spec, plan, data, deps = context()
    for failure in plan['retainedFailures']:
        checked(failure['evidence'])
    reports = [q.load(checked(deps[i]['outputs'][0])) for i in spec['comparisonJobs']]
    result = assess(reports, data, plan['retainedFailures'])
    result['diagnosis'] = [r for report in reports for r in report['diagnosis']]
    lines = ['# Research campaign decision', '', 'Outcome: '+result['outcome'], '',
             'Standard detector: '+str(result['slices']['standard/detector']), '',
             'Retained failures: '+str(len(result['retainedFailures'])), '', result['limitation'], '', result['nextAction']]
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    write('decision.json', result)


def compile_request(source, destination, queue=q.QUEUE):
    plan = q.load(source)
    q.require(set(plan) == {'version','id','question','membership','pairs','retainedFailures','budget'}, 'campaign_fields')
    q.require(plan['version'] == 'research-campaign-v1' and q.ID.fullmatch(plan['id']), 'campaign_id')
    q.require(isinstance(plan['question'], str) and 15 <= len(plan['question']) <= 1000, 'campaign_question')
    rows = members(q.load(checked(plan['membership'])))
    pairs = copy.deepcopy(plan['pairs'])
    q.require(isinstance(pairs, list) and 1 <= len(pairs) <= 8 and
              len({p['condition'] for p in pairs}) == len(pairs), 'campaign_pairs')
    q.require({p['condition'] for p in pairs} == {r['condition'] for r in rows}, 'campaign_conditions')
    q.require(isinstance(plan['retainedFailures'], list), 'campaign_retained_failures')
    for f in plan['retainedFailures']:
        q.require(set(f) == {'reason','evidence'} and isinstance(f['reason'], str) and f['reason'], 'campaign_failure')
        checked(f['evidence'])
    budget = plan['budget']
    q.require(set(budget) == {'maxJobs','maxSeconds','maxOutputBytes'} and
              all(type(v) is int and v > 0 for v in budget.values()), 'campaign_budget')
    destination.mkdir(parents=True, exist_ok=True)
    specs, parents = [], {}
    def dep(s, output):return dict(job=s['id'], specSHA256=q.text_digest(s), outputs=[output])
    def basic(ident, step, dependencies):
        return dict(version='research-spec-v2', id=ident, task=plan['id'], owner='Maximum-mini-NUIAK',
            kind='screen', authority='diagnostic', jobKind='artifact', question=plan['question'], hypothesis=plan['question'],
            controlledComparison='Freeze retained frames, boxes, baseline scores, and settings. Change only the declared crop candidate.',
            decisionRule='Reject Standard losses or new wrong selections. Preserve declared prior failures. No automatic promotion.',
            nextActionByOutcome=dict(supported='Require independent verification before replacement.',
                contradicted='Reject replacement and retain case-linked failures.',inconclusive='Name missing support. Stop this campaign.'),
            inputs=[pin(source),plan['membership'],pin(q.MODULES/'research_campaign451.py')]+[f['evidence'] for f in plan['retainedFailures']],
            campaignPlan=pin(source),dependencies=dependencies,
            evidence=dict(reads=[q.relative(source)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['research_campaign451.'+step],outputAttributes=['research_campaign451.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    models = None
    for n, pair in enumerate(pairs, 1):
        q.require(set(pair) == {'condition','baseline','correction'}, 'campaign_pair_fields')
        q.require(isinstance(pair['baseline'], str) and q.ID.fullmatch(pair['baseline']), 'campaign_parent_id')
        bp=queue/'jobs'/pair['baseline']/'spec.json';base=q.load(bp)
        q.require(base.get('template',{}).get('id') == 'T57', 'campaign_template')
        parents[base['id']]=base
        diag=basic(f"{plan['id']}-diagnose-{n:02}",'diagnosis',[dep(base,'benchmark_summary.json')])
        new_score=isinstance(pair['correction'], dict)
        if new_score:
            doc=pair['correction'];q.require(doc.get('template') == 'T57', 'campaign_template')
            correction=templates.build(compile_batch(dict(version='experiment-batch-v1',jobs=[doc]),queue)[0])
            q.require(not (queue/'jobs'/correction['id']).exists(), 'campaign_score_exists_use_id')
            pair['correction']=correction['id']
        else:
            q.require(isinstance(pair['correction'], str) and q.ID.fullmatch(pair['correction']), 'campaign_parent_id')
            correction=q.load(queue/'jobs'/pair['correction']/'spec.json')
            parents[correction['id']]=correction
        q.require(correction.get('template',{}).get('id') == 'T57', 'campaign_template')
        # Scoring inputs must be pinned or resolvable now. Output reports may arrive later.
        a=resolved_inputs(base,queue)
        b=correction['template']['inputs'] if new_score else resolved_inputs(correction,queue)
        for ref in b.values():checked(ref)
        fixed=set(a)-{'candidate','candidateSelection'}
        q.require(set(a)==set(b) and all(a[k]==b[k] for k in fixed),'campaign_unmatched_inputs')
        identities={k:b[k] for k in ('baseline','candidate')}
        if models is None:models=identities
        q.require(models==identities,'campaign_models_changed')
        diag['pair']=pair;diag['producerSpecs']={base['id']:pin(bp)};diag['inputs'].append(pin(bp))
        specs.append(diag)
        if new_score:
            correction['dependencies'].append(dep(diag,'diagnosis.json'))
            q.validate(correction); cp=destination/(correction['id']+'.json');retain(cp,correction);specs.append(correction)
        else:cp=queue/'jobs'/correction['id']/'spec.json'
        comp=basic(f"{plan['id']}-compare-{n:02}",'comparison',
            [dep(diag,'diagnosis.json'),dep(base,'benchmark_summary.json'),dep(correction,'benchmark_summary.json')])
        comp.update(pair=pair,diagnosisJob=diag['id'],producerSpecs={base['id']:pin(bp),correction['id']:pin(cp)})
        comp['inputs'].extend(comp['producerSpecs'].values());specs.append(comp)
    comparisons=[s for s in specs if s['adapter']['steps']==['research_campaign451.comparison']]
    terminal=basic(plan['id']+'-decision','finish',[dep(s,'comparison.json') for s in comparisons])
    terminal['comparisonJobs']=[s['id'] for s in comparisons];specs.append(terminal)
    q.require(len({s['id'] for s in specs})==len(specs) and not (set(parents)&{s['id'] for s in specs}), 'campaign_duplicate_job')
    q.require(len(specs)<=budget['maxJobs'] and sum(s['limits']['timeoutSeconds'] for s in specs)<=budget['maxSeconds'] and
              sum(s['limits']['maxOutputBytes'] for s in specs)<=budget['maxOutputBytes'], 'campaign_budget_exceeded')
    entries=[]
    for spec in specs:
        q.validate(spec);p=destination/(spec['id']+'.json');retain(p,spec)
        entries.append(dict(job=spec['id'],spec=pin(p),specSHA256=q.text_digest(spec)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(source),existing=[dict(job=s['id'],specSHA256=q.text_digest(s)) for s in parents.values()],
                  jobs=entries,executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(compile_request(args.request,args.output),indent=2))
