"""Compare matched detector resolutions and retain an independent model baseline."""
import research_queue as q
from experiment_templates import checked
from detector_case_match411 import load_bundle,evaluate,summarize
from detector_training_batch478 import assessment

OUT=None


def compare(baseline,candidate,labels,matched=True):
    a,b=[q.load(checked(x)) for x in (baseline,candidate)]
    data=q.load(checked(labels))
    q.require(data['role']=='development' and data['trainingEligible'] is False,'resolution515_role')
    q.require(a['inputs']==b['inputs']==labels and a['frames']==b['frames'],'resolution515_membership')
    settings=[dict(x['settings']) for x in (a,b)];sizes=[s.pop('imageSize') for s in settings]
    q.require(all(s in (640,960,1280) for s in sizes) and settings[0]==settings[1],'resolution515_settings')
    ids=[dict(x['identity']['detector']) for x in (a,b)]
    for identity,size in zip(ids,sizes):
        q.require(identity.pop('imageSize')==size and identity.get('engine')=='pytorch','resolution515_engine')
    if matched:q.require(ids[0]==ids[1] and sizes[0]!=sizes[1],'resolution515_matched_weights')
    bundle=dict(version='detector-case-inputs-v1',role='development',platform=data['platform'],format='real-model-scorecard-v1',
                confidence=settings[0]['confidence'],labelReview=data['labelReview'],baseline=baseline,candidate=candidate,labels=labels)
    images,predictions,meta=load_bundle(bundle)
    params=('geometry',None,{},'class-aware')
    rows,extra=evaluate(images,predictions,params,settings[0]['confidence'])
    result=summarize(rows,extra,params,meta)
    result['comparison']='matched-resolution' if matched else 'retained-model-preservation'
    result['modelAccepted']=False
    result['limitation']='Development observations. Unmatched predictions are not verified false positives. No focus or deployment qualification.'
    return result


def run():
    spec=q.load(OUT.parents[2]/'spec.json');plan=q.load(checked(spec['plan']))
    q.require(plan['version']=='detector-resolution-plan-v1','resolution515_plan')
    deps=q.dependency_inputs(spec,OUT.parents[4])
    if spec['operation']=='compare':
        row=plan['pairs'][spec['index']]
        q.require(len(deps)==1 and deps[0]['job']==row['candidate'],'resolution515_dependency')
        candidate=deps[0]['outputs'][0]
        result=dict(version='detector-resolution-comparison-v1',matched=compare(row['baseline'],candidate,row['labels']),
                    preservation=compare(row['preservation'],candidate,row['labels'],False),modelAccepted=False)
    else:
        reports=[q.load(checked(d['outputs'][0])) for d in deps]
        q.require(len(reports)==len(plan['pairs']) and reports,'resolution515_complete_graph')
        matched=assessment([r['matched'] for r in reports]);preservation=assessment([r['preservation'] for r in reports])
        result=dict(version='detector-resolution-decision-v1',matched=matched,preservation=preservation,modelAccepted=False,
                    outcome='contradicted' if 'contradicted' in (matched['outcome'],preservation['outcome']) else
                    'supported' if matched['outcome']=='supported' else 'inconclusive',
                    nextAction='Reject losses against either baseline. If supported, qualify independent coverage and runtime. Do not promote.')
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))


def make_spec(ident,plan,deps,index=None):
    from experiment_templates import pin
    from pathlib import Path
    return dict(version='research-spec-v2',id=ident,task='STREAM515',owner='Maximum-mini-NUIAK',authority='diagnostic',kind='screen',jobKind='artifact',
        question='Does higher detector resolution recover localization without losing retained detections?',
        hypothesis='Higher resolution preserves detail lost at the lower detector input size.',
        controlledComparison='Keep weights, labels, confidence, NMS, and data roles fixed. Compare retained-model preservation separately.',
        decisionRule='Reject losses against either baseline. Do not infer verified false positives from unmatched predictions.',
        nextActionByOutcome=dict(supported='Qualify independent coverage and runtime.',contradicted='Preserve models and diagnose losses.',inconclusive='Stop without evidence of benefit.'),
        inputs=[pin(plan),pin(Path(__file__))],plan=pin(plan),operation='compare' if index is not None else 'finish',index=index,
        dependencies=deps,adapter=dict(type='python-callable',steps=['detector_resolution515.run'],outputAttributes=['detector_resolution515.OUT']),
        evidence=dict(reads=[q.relative(plan)],artifactReceipt='artifact-receipt.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
