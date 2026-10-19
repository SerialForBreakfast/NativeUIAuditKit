"""Compile approved fixed follow-ups from completed proposal campaigns."""
import argparse
import json
from pathlib import Path

import research_queue as q
import hcf_templates395 as templates
from experiment_templates import checked, pin
from model_decision_batch434 import retain
from bounded_selection444 import rules_valid, select


def completed(queue, ident, output):
    q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'selection_job_id')
    spec = q.load(queue/'jobs'/ident/'spec.json')
    dep = dict(job=ident, specSHA256=q.text_digest(spec), outputs=[output])
    resolved = q.dependency_inputs(dict(dependencies=[dep]), queue)[0]
    return spec, dep, dict(report=resolved['outputs'][0], result=resolved['result'],
                           spec=pin(queue/'jobs'/ident/'spec.json'))


def compile_request(source, destination, queue=q.QUEUE):
    plan = q.load(source)
    q.require(set(plan) == {'version', 'id', 'sources', 'rules'} and
              plan['version'] == 'bounded-selection-request-v1' and q.ID.fullmatch(plan['id']), 'selection_request')
    q.require(set(plan['sources']) == {'baseline', 'candidate', 'contrast'}, 'selection_sources')
    rules_valid(plan['rules'])
    sources = [completed(queue, plan['sources'][key], output) for key, output in
               [('baseline','decision.json'), ('candidate','decision.json'), ('contrast','contrast.json')]]
    reports = [q.load(checked(s[2]['report'])) for s in sources]
    select(*reports, plan['rules'])  # Validate evidence before publishing any draft.
    q.require(all(s[0]['adapter']['steps'] == [step] for s, step in zip(sources,
        ['proposal_report443.run', 'proposal_report443.run', 'proposal_report443.contrast'])), 'selection_source_adapter')
    destination.mkdir(parents=True, exist_ok=True)
    specs = {}; existing = {s[1]['job']:dict(job=s[1]['job'],specSHA256=s[1]['specSHA256']) for s in sources}
    def dep(spec, outputs):return dict(job=spec['id'], specSHA256=q.text_digest(spec), outputs=outputs)
    def basic(ident, step, question, dependencies):
        return dict(version='research-spec-v2', id=ident, task=plan['id'], owner='Maximum-mini-NUIAK',
            kind='screen', authority='diagnostic', jobKind='artifact', question=question, hypothesis=question,
            controlledComparison='Use retained matched development cases, frozen scores, and unchanged Standard settings.',
            decisionRule='Preserve prior successes and no-focus abstentions. Reject new wrong selections. Do not promote.',
            nextActionByOutcome=dict(supported='Prepare independent verification within separate authority.',
                contradicted='Preserve failures and identify the missing training-only evidence.',
                inconclusive='Stop this branch and name the missing support. Do not repeat training.'),
            inputs=[pin(source), pin(q.MODULES/(step.split('.')[0]+'.py'))], selectionPlan=pin(source),
            dependencies=dependencies, evidence=dict(reads=[q.relative(source)], artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=[step],outputAttributes=[step.split('.')[0]+'.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    gate = basic(plan['id']+'-select','bounded_selection444.gate',
        'Which fixed Standard diagnostics are justified by the completed matched comparisons?', [s[1] for s in sources])
    specs[gate['id']] = gate
    def conditioned(spec, branch, summary=False):
        outputs = ['selection.json',branch+'-gate.json'] if summary else [branch+'-gate.json']
        spec['dependencies'] = [dep(gate,outputs)] + spec['dependencies']
        spec['conditions'] = [dict(job=gate['id'],output=branch+'-gate.json',outcome='supported')]
        q.validate(spec); specs[spec['id']] = spec
        return spec
    # Match completed scoring jobs by frame membership, never by list position.
    arms = []
    for report in reports[:2]:
        grouped = {}
        for row in report['rows']:grouped.setdefault(row['job'],set()).add((row['id'],row['sha256'],row['group'],row['profile']))
        q.require(1 <= len(grouped) <= 8,'selection_case_limit')
        keyed = {}
        for ident, members in grouped.items():
            key = tuple(sorted(members));q.require(key not in keyed,'selection_duplicate_membership')
            original, _, ref = completed(queue,ident,'benchmark_summary.json')
            q.require(original.get('template',{}).get('id') == 'T57','selection_scoring_template')
            raw = q.load(checked(ref['report']))
            q.require({(r['id'],r['sha256'],r['group'],r['profile']) for r in raw['rows']} == members,'selection_scoring_membership')
            keyed[key] = ref
        arms.append(keyed)
    q.require(arms[0].keys() == arms[1].keys(),'selection_matched_membership')
    branches = {'geometry':[], 'supplemental':[]}
    for index, key in enumerate(sorted(arms[0]),1):
        refs = [arm[key] for arm in arms]
        for label, ref in zip(('base','new'),refs):
            ident = f"{plan['id']}-geometry-{label}-{index:02}"
            doc = dict(version='hcf-template-description-v1',id=ident,task=plan['id'],owner='Maximum-mini-NUIAK',
                template='T61',question='Do measured proposal errors explain score losses for retained condition '+str(index)+'?',
                decision='Separate missing boxes, ambiguous matches, and score changes. Preserve development exclusions.',
                inputs=dict(report=ref['report'],receipt=ref['result']),parameters={},dependencies=[])
            branches['geometry'].append(conditioned(templates.build(doc),'geometry'))
        bundle = destination/f'supplemental-{index:02}-bundle.json'
        retain(bundle,dict(version='supplemental-proposals-v1',baseline=refs[0],supplemental=refs[1]))
        spec = basic(f"{plan['id']}-supplemental-{index:02}",'supplemental_proposals427.run',
            'Does a fixed baseline-first detector fallback recover selections without new wrong selections for condition '+str(index)+'?',[])
        spec['inputs'].append(pin(bundle));spec['stage']=[dict(to='bundle.json',**{'from':pin(bundle)})]
        spec['inputs'].append(pin(q.MODULES/'bounded_selection444.py'))
        spec['adapter']['steps'].insert(0,'bounded_selection444.verify_branch')
        spec['adapter']['outputAttributes'].append('bounded_selection444.OUT')
        spec['evidence']['reads']=[q.relative(bundle)]
        branches['supplemental'].append(conditioned(spec,'supplemental'))
    for branch, jobs in branches.items():
        # Keep the existing 10-dependency limit. Geometry groups each detector source separately.
        groups = [[s for s in jobs if '-geometry-'+arm+'-' in s['id']] for arm in ('base','new')] if branch=='geometry' else [jobs]
        for number, group in enumerate(groups,1):
            spec = basic(plan['id']+'-'+branch+'-'+str(number)+'-decision','bounded_selection444.finish',
                'What bounded next action follows from the matched '+branch+' comparisons without losing previous successes?',
                [dep(s,['benchmark_summary.json']) for s in group])
            spec['selectionBranch']=branch;conditioned(spec,branch,True)
    jobs=[]
    for ident,spec in specs.items():
        q.validate(spec);path=destination/(ident+'-spec.json');retain(path,spec)
        jobs.append(dict(job=ident,specSHA256=q.text_digest(spec),spec=pin(path)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(source),existing=list(existing.values()),
                  jobs=jobs,executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(compile_request(args.request,args.output),indent=2))
