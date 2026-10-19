"""Compile fixed detector-to-crop comparisons and a retained-success decision graph."""
from pathlib import Path
import argparse
import json
import copy

import research_queue as q
import hcf_templates395 as templates
import experiment_batch402 as batches
from experiment_templates import checked, pin
from model_decision_batch434 import retain


def completed_output(queue, ident, name):
    q.require(q.ID.fullmatch(ident),'proposal_job_identity');q.check_name(name)
    spec=q.load(queue/'jobs'/ident/'spec.json')
    resolved=q.dependency_inputs(dict(dependencies=[dict(job=ident,specSHA256=q.text_digest(spec),outputs=[name])]),queue)
    return resolved[0]['outputs'][0]


def resolved_inputs(spec,queue):
    deps={d['job']:(original,d) for original,d in zip(spec['dependencies'],q.dependency_inputs(spec,queue))}
    result={}
    for name,ref in spec['template']['inputs'].items():
        if 'path' in ref:checked(ref);result[name]=ref
        else:
            original,dep=deps[ref['job']]
            result[name]=dep['outputs'][original['outputs'].index(ref['output'])]
    return result


def author(source,destination,queue=q.QUEUE):
    """Reuse fixed proposal specifications and match candidate reference scores by input identity."""
    request=q.load(source)
    q.require(set(request)=={'version','id','question','referenceJobs','candidateScores','preservation'},'proposal_request_fields')
    q.require(request['version']=='proposal-request-v1' and q.ID.fullmatch(request['id']),'proposal_request_version')
    q.require(1<=len(request['referenceJobs'])<=32 and len(set(request['referenceJobs']))==len(request['referenceJobs']),
              'proposal_request_jobs')
    indexed={}
    for ident in request['candidateScores']:
        q.require(q.ID.fullmatch(ident),'proposal_job_identity')
        spec=q.load(queue/'jobs'/ident/'spec.json');q.require(spec['template']['id']=='T37','proposal_reference_template')
        refs=resolved_inputs(spec,queue);key=q.text_digest(refs['capture'])
        q.require(key not in indexed,'proposal_ambiguous_reference')
        indexed[key]=(refs,completed_output(queue,ident,'selection.json'))
    jobs=[]
    for index,ident in enumerate(request['referenceJobs'],1):
        q.require(q.ID.fullmatch(ident),'proposal_job_identity')
        spec=q.load(queue/'jobs'/ident/'spec.json');q.require(spec['template']['id']=='T57','proposal_reference_template')
        refs=copy.deepcopy(resolved_inputs(spec,queue))
        candidate,selection=indexed[q.text_digest(refs['capture'])]
        q.require(candidate['tool']==refs['tool'] and candidate['mapping']==refs['mapping'] and
                  candidate['proposals']==refs['ringProposals'],'proposal_reference_inputs')
        refs['candidate']=candidate['model'];refs['candidateSelection']=selection
        jobs.append(dict(version='hcf-template-description-v1',id=f"{request['id']}-score-{index:02}",
            task=request['id'],owner='Maximum-mini-NUIAK',template='T57',
            question=request['question']+' Retained proposal condition: '+ident+'.',
            decision='Measure Standard gains, prior successes lost, wrong selections, and no-focus abstentions. Do not promote.',
            controlledComparison='Only the crop candidate changes. Preserve detector outputs, frames, known-box replay, and thresholds.',
            inputs=refs,parameters={},dependencies=[]))
    destination.mkdir(parents=True,exist_ok=True)
    retain(destination/'batch.json',dict(version='experiment-batch-v1',jobs=jobs))
    plan=dict(version='proposal-campaign-v1',id=request['id'],question=request['question'],batch=pin(destination/'batch.json'),
              preservation=request['preservation'])
    retain(destination/'plan.json',plan)
    return compile_plan(destination/'plan.json',destination/'compiled',queue)


def compile_plan(source, destination, queue=q.QUEUE):
    plan=q.load(source)
    q.require(set(plan)=={'version','id','question','batch','preservation'},'proposal_campaign_fields')
    q.require(plan['version']=='proposal-campaign-v1' and q.ID.fullmatch(plan['id']),'proposal_campaign_version')
    q.require(isinstance(plan['preservation'],str) and q.ID.fullmatch(plan['preservation']),'proposal_preservation_identity')
    q.require(isinstance(plan['question'],str) and len(plan['question'])>=12,'proposal_campaign_question')
    batch=q.load(checked(plan['batch']))
    docs=batches.compile_batch(batch,queue)
    q.require(1<=len(docs)<=32 and all(d['template']=='T57' for d in docs),'proposal_campaign_templates')
    existing={}
    specs={d['id']:templates.build(d) for d in docs}
    for spec in specs.values():
        for dep in spec['dependencies']:
            if dep['job'] not in specs:existing[dep['job']]=dict(job=dep['job'],specSHA256=dep['specSHA256'])
    original=q.load(queue/'jobs'/plan['preservation']/'spec.json')
    q.require(original['adapter']['steps']==['model_decision434.decision'],'proposal_preservation_type')
    existing[original['id']]=dict(job=original['id'],specSHA256=q.text_digest(original))
    destination.mkdir(parents=True,exist_ok=True)
    def dependency(s,outputs):return dict(job=s['id'],specSHA256=q.text_digest(s),outputs=outputs)
    def make(suffix,step,deps,condition=None):
        ident=plan['id']+'-'+suffix
        q.require(ident not in specs,'proposal_report_identity_collision')
        spec=dict(version='research-spec-v2',id=ident,task=plan['id'],owner='Maximum-mini-NUIAK',kind='screen',
            authority='diagnostic',jobKind='artifact',question=plan['question'],hypothesis=plan['question'],
            controlledComparison='Use identical frames, detector proposals, crop preprocessing, and frozen thresholds for both crop models.',
            decisionRule='Require Standard detector gains without lost successes or new wrong selections. Preserve earlier consumer regressions.',
            nextActionByOutcome=dict(supported='Prepare independent verification without promotion.',
                contradicted='Diagnose lost successes and missing proposals before further training.',
                inconclusive='Record missing evidence or unchanged outcomes. Do not repeat training.'),
            inputs=[pin(source),pin(q.MODULES/'proposal_report443.py')],
            proposalPlan=pin(source),dependencies=deps,
            evidence=dict(reads=[q.relative(source)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['proposal_report443.'+step],outputAttributes=['proposal_report443.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        if condition:spec['conditions']=[dict(job=deps[0]['job'],output='gate.json',outcome=condition)]
        q.validate(spec);specs[ident]=spec;return spec
    summary=make('report','run',[dependency(s,['benchmark_summary.json']) for s in list(specs.values())]+
                 [dependency(original,['decision.json'])])
    for condition in ('supported','contradicted'):
        make(condition+'-followup','followup',[dependency(summary,['decision.json','gate.json'])],condition)
    generated=[]
    for ident,spec in specs.items():
        path=destination/(ident+'-spec.json');retain(path,spec)
        generated.append(dict(job=ident,specSHA256=q.text_digest(spec),spec=pin(path)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(source),existing=list(existing.values()),jobs=generated,
                  executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


def compile_contrast(left,right,destination,ident):
    """Reuse compiled report dependencies. Never repeat scoring for this comparison."""
    q.require(q.ID.fullmatch(ident),'proposal_contrast_id')
    manifests=[q.load(checked(ref)) for ref in (left,right)]
    reports=[]
    for manifest in manifests:
        matches=[q.load(checked(r['spec'])) for r in manifest['jobs']
                 if q.load(checked(r['spec']))['adapter']['steps']==['proposal_report443.run']]
        q.require(len(matches)==1,'proposal_contrast_report_count');reports.append(matches[0])
    destination.mkdir(parents=True,exist_ok=True)
    plan=destination/'plan.json';retain(plan,dict(version='proposal-contrast-plan-v1',left=left,right=right))
    spec=copy.deepcopy(reports[0]);spec.update(id=ident,task=ident,proposalPlan=pin(plan),inputs=[pin(plan),pin(q.MODULES/'proposal_report443.py')],
        question='Does the experimental detector recover Standard focus selections without losing selections from the retained detector?',
        hypothesis='Only changing detector proposals can explain matched full-screen selection differences.',
        dependencies=[dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['decision.json']) for s in reports],
        evidence=dict(reads=[q.relative(plan)],artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable',steps=['proposal_report443.contrast'],outputAttributes=['proposal_report443.OUT']))
    q.validate(spec);path=destination/'spec.json';retain(path,spec)
    manifest=dict(version='model-decision-compiled-v1',plan=pin(plan),
        existing=[dict(job=s['id'],specSHA256=q.text_digest(s)) for s in reports],
        jobs=[dict(job=ident,specSHA256=q.text_digest(spec),spec=pin(path))],executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest);return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--author',action='store_true')
    args=parser.parse_args()
    print(json.dumps((author if args.author else compile_plan)(args.plan,args.output),indent=2))
