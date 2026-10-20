"""Compile detector fits and full-screen comparisons without another execution engine."""
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
from proposal_campaign443 import resolved_inputs
from research_campaign451 import members, validate_report, SUCCESS
from supplemental_proposals427 import load

OUT = None


def compare(left, right, expected):
    """Change detector boxes only. Keep the crop model and all reference inputs fixed."""
    for report in (left, right):
        validate_report(report, expected)
    q.require(set(left['inputs']) == set(right['inputs']) and all(
        left['inputs'][k] == right['inputs'][k] for k in left['inputs'] if k != 'scorecard'),
        'detector_campaign_crop_or_input_changed')
    cards = [q.load(checked(r['inputs']['scorecard'])) for r in (left, right)]
    q.require(cards[0]['settings'] == cards[1]['settings'] and cards[0]['inputs'] == cards[1]['inputs']
              and cards[0]['frames'] == cards[1]['frames'], 'detector_campaign_unmatched_scorecards')
    q.require(cards[0]['identity']['detector']['nmsIoU'] == cards[1]['identity']['detector']['nmsIoU'],
              'detector_campaign_nms_changed')
    indexed = {r['id']: r for r in right['rows']}
    groups = {r['id']: r['group'] for r in expected}
    result = []
    for old in left['rows']:
        new = indexed[old['id']]
        q.require(old['noFocus'] == new['noFocus'] and old['arms']['known-box'] == new['arms']['known-box'],
                  'detector_campaign_control_changed')
        a, b = [r['arms']['detector']['models']['candidate']['outcome'] for r in (old, new)]
        result.append(dict(id=old['id'], group=groups[old['id']], sha256=old['sha256'], profile=old['profile'],
            noFocus=old['noFocus'], baseline=a, candidate=b, gain=a not in SUCCESS and b in SUCCESS,
            loss=a in SUCCESS and b not in SUCCESS,
            newWrong=b in ('wrong','false-selection') and a not in ('wrong','false-selection'),
            proposalBefore=old['arms']['detector']['focusedProposalPresent'],
            proposalAfter=new['arms']['detector']['focusedProposalPresent']))
    return result


def assess(rows, retained):
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'detector_campaign_duplicate_cases')
    standard = [r for r in rows if r['profile'] == 'standard']
    q.require(standard, 'detector_campaign_standard_missing')
    bad = any(r['loss'] or r['newWrong'] for r in standard)
    support = len({r['group'] for r in standard}) >= 3 and any(r['noFocus'] for r in standard)
    outcome = 'contradicted' if bad or retained else 'supported' if support and any(r['gain'] for r in standard) else 'inconclusive'
    return dict(version='detector-campaign-decision-v1', outcome=outcome, modelAccepted=False, rows=rows,
        retainedFailures=retained, profiles={p:dict(
            baseline=dict(Counter(r['baseline'] for r in rows if r['profile']==p)),
            candidate=dict(Counter(r['candidate'] for r in rows if r['profile']==p)),
            gains=[r['id'] for r in rows if r['profile']==p and r['gain']],
            losses=[r['id'] for r in rows if r['profile']==p and r['loss']],
            newWrong=[r['id'] for r in rows if r['profile']==p and r['newWrong']],
            groups=len({r['group'] for r in rows if r['profile']==p})) for p in ('standard','hcf')},
        limitation='Inspected development cases. Group counts do not establish deployment safety. HCF stays separate.',
        nextAction='Reject replacement and inspect case-linked failures.' if outcome=='contradicted' else
                   'Require independent consumer verification.' if outcome=='supported' else
                   'Record missing gains or coverage before further training.')


def finish():
    spec=q.load(OUT.parents[2]/'spec.json');queue=OUT.parents[4]
    plan=q.load(checked(spec['campaignPlan']))
    membership=members(q.load(checked(plan['membership'])))
    deps={d['job']:d for d in q.dependency_inputs(spec,queue)}
    rows=[]; timings=[]
    for pair in spec['pairs']:
        reports=[]
        for ident in (pair['baseline'],pair['candidate']):
            dep=deps[ident];sp=spec['producerSpecs'][ident]
            report=load(dict(report=dep['outputs'][0],result=dep['result'],spec=sp))
            q.require(report['inputs']==resolved_inputs(q.load(checked(sp)),queue),'detector_campaign_report_inputs')
            reports.append(report)
        rows.extend(compare(*reports,[r for r in membership if r['condition']==pair['condition']]))
    for failure in plan['retainedFailures']: checked(failure['evidence'])
    result=assess(rows,plan['retainedFailures'])
    # Preserve durations separately. These do not measure authoring or avoidable idle time.
    for ident,dep in deps.items():
        receipt=q.load(checked(dep['result']))
        timings.append(dict(job=ident,wallSeconds=receipt.get('wallSeconds'),result=dep['result']))
    result['executionEvidence']=timings
    q.save(OUT/'decision.json',result)
    (OUT/'report.md').write_text('# Detector campaign decision\n\nOutcome: '+result['outcome']+
        '\n\nStandard: '+json.dumps(result['profiles']['standard'])+'\n\n'+result['limitation']+'\n\n'+result['nextAction']+'\n')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('decision.json','report.md')]))


def compile_request(source, destination, queue=q.QUEUE):
    plan=q.load(source)
    q.require(set(plan)=={'version','id','question','membership','training','pairs','retainedFailures','budget'},'detector_campaign_fields')
    q.require(plan['version']=='detector-campaign-v1' and q.ID.fullmatch(plan['id']),'detector_campaign_version')
    q.require(isinstance(plan['question'],str) and 15<=len(plan['question'])<=1000,'detector_campaign_question')
    rows=members(q.load(checked(plan['membership'])))
    pairs=plan['pairs'];q.require(1<=len(pairs)<=8 and len({p['condition'] for p in pairs})==len(pairs),'detector_campaign_pairs')
    q.require({p['condition'] for p in pairs}=={r['condition'] for r in rows},'detector_campaign_conditions')
    for failure in plan['retainedFailures']:
        q.require(set(failure)=={'reason','evidence'} and failure['reason'],'detector_campaign_failure');checked(failure['evidence'])
    authored=[];parents={};resolved=[]
    train=plan['training']
    if train is not None:
        q.require(isinstance(train,dict) and train.get('template')=='T89','detector_campaign_training')
        data=q.load(checked(train['inputs']['membership']))
        q.require(data.get('trainingAdmitted') is True and data['version']=='detector-training-membership-v2','detector_campaign_admission')
        q.require(data['rows'] and all(r['role']=='train' and r['trainingEligible'] is True and r['labelsComplete'] is True for r in data['rows']), 'detector_campaign_training_roles')
        q.require(not {r['group'] for r in data['rows']} & {r['group'] for r in rows},'detector_campaign_group_leak')
        q.require(not {r['image']['sha256'] for r in data['rows']} & {r['sha256'] for r in rows},'detector_campaign_pixel_leak')
        q.require(train['training']['epochs']==30 and train['training']['resume']=='restart','detector_campaign_training_budget')
        authored.append(copy.deepcopy(train))
    for index,pair in enumerate(pairs,1):
        q.require(set(pair)=={'condition','baseline','candidate'},'detector_campaign_pair_fields')
        base=q.load(queue/'jobs'/pair['baseline']/'spec.json');q.require(base['template']['id']=='T57','detector_campaign_template')
        parents[base['id']]=base
        if train is None:
            candidate=q.load(queue/'jobs'/pair['candidate']/'spec.json');q.require(candidate['template']['id']=='T57','detector_campaign_template')
            parents[candidate['id']]=candidate
            a,b=resolved_inputs(base,queue),resolved_inputs(candidate,queue)
            q.require(set(a)==set(b) and all(a[k]==b[k] for k in a if k!='scorecard'),'detector_campaign_unmatched_inputs')
            ident=candidate['id']
        else:
            q.require(pair['candidate'] is None,'detector_campaign_candidate_binding')
            refs=copy.deepcopy(resolved_inputs(base,queue));card=q.load(checked(refs['scorecard']))
            infer=plan['id']+f'-detect-{index:02}';ident=plan['id']+f'-focus-{index:02}'
            common=dict(version='hcf-template-description-v1',owner='Maximum-mini-NUIAK',task=plan['id'],question=plan['question'],decision='Preserve Standard and all retained successes. No promotion.')
            authored.append(dict(common,id=infer,template='T56',inputs=dict(labels=card['inputs'],model=dict(job=train['id'],output='final.pt'),baseline=refs['scorecard']),parameters=card['settings']))
            refs['scorecard']=dict(job=infer,output='scorecard.json')
            authored.append(dict(common,id=ident,template='T57',inputs=refs,parameters={}))
        resolved.append(dict(pair,candidate=ident))
    built=[templates.build(d) for d in compile_batch(dict(version='experiment-batch-v1',jobs=authored),queue)] if authored else []
    rebound={}
    for spec in built:
        if spec.get('template',{}).get('id')=='T89':
            spec['limits']['timeoutSeconds']=7200
        for dependency in spec.get('dependencies',[]):
            if dependency['job'] in rebound:
                dependency['specSHA256']=q.text_digest(rebound[dependency['job']])
        rebound[spec['id']]=spec
    specs={s['id']:s for s in built};all_specs={**parents,**specs}
    ids=sorted({p[k] for p in resolved for k in ('baseline','candidate')})
    terminal=dict(version='research-spec-v2',id=plan['id']+'-decision',task=plan['id'],owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',jobKind='artifact',
        question=plan['question'],hypothesis=plan['question'],controlledComparison='Change only detector weights. Keep crop models, frames, thresholds, and known-box checks fixed.',
        decisionRule='Reject Standard losses and new wrong selections. Preserve declared regressions. Never promote.',
        nextActionByOutcome=dict(supported='Require independent consumer verification before replacement.',
            contradicted='Reject replacement and retain case-linked failures.',inconclusive='Name missing evidence before further fitting.'),
        campaignPlan=pin(source),pairs=resolved,inputs=[pin(source),plan['membership'],pin(Path(__file__))]+[f['evidence'] for f in plan['retainedFailures']],
        dependencies=[dict(job=i,specSHA256=q.text_digest(all_specs[i]),outputs=['benchmark_summary.json']) for i in ids],
        evidence=dict(reads=[q.relative(source)],artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable',steps=['detector_campaign457.finish'],outputAttributes=['detector_campaign457.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    budget=plan['budget'];q.require(set(budget)=={'maxJobs','maxSeconds','maxOutputBytes'} and all(type(v)is int and v>0 for v in budget.values()),'detector_campaign_budget')
    total=built+[terminal]
    q.require(len(total)<=budget['maxJobs'] and sum(s['limits']['timeoutSeconds'] for s in total)<=budget['maxSeconds'] and sum(s['limits']['maxOutputBytes'] for s in total)<=budget['maxOutputBytes'],'detector_campaign_budget_exceeded')
    destination.mkdir(parents=True,exist_ok=True)
    for s in built:retain(destination/(s['id']+'.json'),s)
    terminal['producerSpecs']={i:pin(destination/(i+'.json') if i in specs else queue/'jobs'/i/'spec.json') for i in ids}
    terminal['inputs']+=list(terminal['producerSpecs'].values())
    entries=[]
    for s in total:
        q.validate(s);path=destination/(s['id']+'.json');retain(path,s);entries.append(dict(job=s['id'],spec=pin(path),specSHA256=q.text_digest(s)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(source),existing=[dict(job=i,specSHA256=q.text_digest(s)) for i,s in parents.items()],jobs=entries,executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('request',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(compile_request(args.request,args.output),indent=2))
