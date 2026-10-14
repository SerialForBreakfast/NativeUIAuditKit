"""Register a bounded template batch. Approve each immutable job separately."""
import argparse
from pathlib import Path
import subprocess
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from experiment_templates import pin
from template_analysis397 import SUITES


def build(folder):
    folder.mkdir(parents=True,exist_ok=True);jobs=[]
    def saved(name,value):
        path=folder/name
        if path.exists():q.require(q.load(path)==value,'immutable_preparation_changed')
        else:q.save(path,value)
        return pin(path)
    def output(job,name):
        result=q.load(q.QUEUE/'jobs'/job/'attempts/1/result.json')
        q.require(result['status']=='complete','producer_not_complete:'+job)
        record=next(r for r in result['outputs'] if r['path']==name)
        path=q.QUEUE/'jobs'/job/'attempts/1/out'/name
        q.require(q.digest(path)==record['sha256'],'producer_output_changed')
        return pin(path)
    def add(suffix,template,question,decision,inputs,parameters=None,dependencies=None):
        doc=dict(version='hcf-template-description-v1',id='hcf397-'+suffix,owner='research-host-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=dependencies or [])
        saved(suffix+'.json',doc);templates.register(doc);jobs.append(doc['id']);return doc['id']
    catalog=output('hcf371r4-40-catalog','admission.json')
    retained=output('hcf371-00-retained','admission.json')
    rules=output('hcf371r4-60-rules','comparison.json')
    proposal=add('01-proposals','T18','Can the fixed crop classifier select focus from retained outline proposals?',
        'Separate proposal-limited misses from selection errors. Preserve the failed HCF389 attempt.',
        dict(catalog=catalog,retained=retained,rules=rules,
             model=output('hcf375c-70-crop-train','final.pt'),
             tool=pin(q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool')))
    dep=dict(job=proposal,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/proposal/'spec.json')),outputs=['proposal-selection.json'])
    for suffix,source,label in [('02-rules','hcf371r4-60-rules','independent outline rules'),
                                ('03-detector','hcf388-detector-evaluate','full-screen detector'),
                                ('04-known-box-upper-bound','hcf375c-80-crop-evaluate','known-box classifier upper bound')]:
        add(suffix,'T15','Which cases change when proposal-based selection replaces '+label+'?',
            'Report gains and lost successes by profile. Do not treat known boxes as deployable proposals.',
            dict(baseline=output(source,'comparison.json'),candidate=dict(job=proposal,output='proposal-selection.json')),
            dict(comparison=label+' versus fixed outline proposals plus crop classification'),[dep])
    for suite in SUITES:
        cfg=saved(suite+'-qualification.json',dict(version='template-qualification-v1',suite=suite,
             tests=[pin(q.MODULES/(name+'.py')) for name in SUITES[suite]]))
        add('hardening-'+suite,'T16','Do '+suite+' checks pass through the background execution flow?',
            'Require positive and negative software checks to pass. A failure blocks only affected descendants.',
            dict(qualification=cfg),dict(suite=suite))
    add('preparation-cost','T17','Does shared image preparation save time across 3 compatible consumers?',
        'Compare identical geometry and decoded metadata across 3 alternating-order repetitions. Report measured time, not predicted savings.',
        dict(catalog=catalog),dict(repetitions=3,maxFrames=24))
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=q.ROOT,text=True).strip()
    add('consumer-identity','T19','Can TTR identify the exact compiled model and parent-frame crop contract?',
        'Produce pinned identities and coordinate semantics. Actual TTR inference remains a separate requirement.',
        dict(export=output('hcf396-10-compress','export.json'),membership=pin(q.ROOT/'reports/work/TEMPLATE395/runtime-membership.json')),
        dict(sourceRevision=revision))
    saved('batch.json',dict(jobs=jobs,modelAccepted=False,trainingStarted=False,
        nextRequirements=['Pinned outer-ring-v2 executable or candidate outputs on matching cases.',
                          'Accepted observer API and actual TTR receipt.',
                          'Qualified no-focus labels and untouched audit groups.']))
    return jobs


def successors(folder):
    jobs=[]
    def register(doc):
        path=folder/(doc['id']+'.json')
        if path.exists():q.require(q.load(path)==doc,'successor_description_changed')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id'])
    for name in ('hardening-contracts','hardening-queue-recovery','preparation-cost'):
        doc=q.load(folder/(name+'.json'));doc['id']+='-v2'
        if 'qualification' in doc['inputs']:
            cfg=dict(version='template-qualification-v1',suite=doc['parameters']['suite'],
                tests=[pin(q.MODULES/(name+'.py')) for name in SUITES[doc['parameters']['suite']]])
            path=folder/(doc['id']+'-qualification.json')
            if path.exists():q.require(q.load(path)==cfg,'successor_tests_changed')
            else:q.save(path,cfg)
            doc['inputs']['qualification']=pin(path)
        register(doc)
    base=q.load(folder/'01-proposals.json')
    selection=q.QUEUE/'jobs/hcf397-01-proposals/attempts/1/out/proposal-selection.json'
    result=q.load(selection.parent.parent/'result.json')
    q.require(result['status']=='complete','proposal_success_required')
    register(dict(version='hcf-template-description-v1',id='hcf397-proposal-failure-audit',owner='research-host-NUIAK',template='T20',
        question='Are retained focus misses caused by missing proposals or rejected matching proposals?',
        decision='Prioritize proposal coverage when boxes are absent. Review crop geometry and scores when matching boxes exist.',
        inputs={**{k:base['inputs'][k] for k in ('catalog','retained','rules')},'selection':pin(selection)},parameters={},dependencies=[]))
    return jobs


def boundary(folder):
    base=q.load(folder/'01-proposals.json');jobs=[]
    for suffix,scale in [('five-percent',1.05),('ten-percent',1.10)]:
        ident='hcf397-boundary-'+suffix
        doc=dict(base,id=ident,template='T21',parameters=dict(scale=scale),
            question='Does '+suffix+' candidate expansion recover rejected matching outlines?',
            decision='Use unchanged images, model, and thresholds. Report gains and losses before considering training or deployment.')
        path=folder/(ident+'.json');q.save(path,doc);templates.register(doc);jobs.append(ident)
        dependency=dict(job=ident,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/ident/'spec.json')),outputs=['proposal-selection.json'])
        for source,label in [('hcf397-01-proposals','original-proposals'),('hcf388-detector-evaluate','detector')]:
            name='proposal-selection.json' if source=='hcf397-01-proposals' else 'comparison.json'
            reference=pin(q.QUEUE/'jobs'/source/'attempts/1/out'/name)
            report=dict(version='hcf-template-description-v1',id=ident+'-vs-'+label,owner='research-host-NUIAK',template='T15',
                question='Does '+suffix+' expansion preserve '+label+' successes?',decision='Report case-linked gains and losses by profile. Reject replacement when previous successes are lost.',
                inputs=dict(baseline=reference,candidate=dict(job=ident,output='proposal-selection.json')),
                parameters=dict(comparison=label+' versus expanded proposals'),dependencies=[dependency])
            q.save(folder/(report['id']+'.json'),report);templates.register(report);jobs.append(report['id'])
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--successors',action='store_true');mode.add_argument('--boundary',action='store_true');args=parser.parse_args()
    for ident in (boundary if args.boundary else successors if args.successors else build)(q.ROOT/'reports/work/HCF397'):
        if args.approve:
            approval.approve(q.QUEUE,ident,'agent:research-host-NUIAK',
                'Maintainer approves HCF template comparisons and process qualification. No training, capture, or Standard changes.')
        print(ident,flush=True)
