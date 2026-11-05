"""Score fixed role detectors with existing prediction and COCO implementations."""
import research_queue as q
from template_adapters395 import resolve_inputs,document
from template_inputs398 import checked
OUT=None


def matched_cases(frames,predictions):
    from perception_benchmark import _iou
    rows=[]
    for frame in frames:
        detections=[d for d in predictions[checked(frame['image'])] if d['score']>=.5]
        available=set(range(len(detections)))
        for truth in frame['truth']:
            options=[i for i in available if detections[i]['cls']==truth['cls'] and _iou(detections[i]['box'],truth['box'])>=.5]
            selected=max(options,key=lambda i:_iou(detections[i]['box'],truth['box'])) if options else None
            if selected is not None:available.remove(selected)
            rows.append(dict(id=frame['id']+'|'+truth['id'],group=frame['group'],dataset=frame['dataset'],
                className=truth['cls'],correct=selected is not None))
    return rows


def assess(left,right):
    q.require(left['manifest']==right['manifest'] and left['settings']==right['settings'],'role_unmatched_inputs')
    a={r['id']:r for r in left['cases']};b={r['id']:r for r in right['cases']}
    q.require(a.keys()==b.keys(),'role_membership_changed')
    q.require(all({k:v for k,v in a[i].items() if k!='correct'}=={k:v for k,v in b[i].items() if k!='correct'} for i in a),'role_references_changed')
    gains=[i for i in a if not a[i]['correct'] and b[i]['correct']]
    lost=[i for i in a if a[i]['correct'] and not b[i]['correct']]
    metrics=[r.get('metrics',{}) for r in (left,right)]
    q.require(metrics[0].keys()==metrics[1].keys(),'role_metric_scope_changed')
    deltas={name:metrics[1][name]['AP50']-metrics[0][name]['AP50'] for name in metrics[0]}
    regressions=[]
    for name in metrics[0]:
        a_roles=metrics[0][name]['perRoleAP50'];b_roles=metrics[1][name]['perRoleAP50']
        q.require(a_roles.keys()==b_roles.keys(),'role_support_changed')
        regressions += [name+'|'+role for role in a_roles if b_roles[role]-a_roles[role]<-.02]
    mean_delta=sum(deltas.values())/len(deltas) if deltas else None
    outcome='contradicted' if lost or regressions else 'supported' if gains and mean_delta is not None and mean_delta>=.01 else 'inconclusive'
    return dict(version='role-comparison567-v1',outcome=outcome,meanAP50Delta=mean_delta,perDatasetAP50Delta=deltas,roleRegressions=regressions,
        gains=gains,lostPriorSuccesses=lost,metricsStatus='provisional',modelAccepted=False,
        limitation='Development and generated-screen evidence. Detection gains do not establish focus selection or real-app accuracy.',
        nextAction='Reject replacement after any loss. Otherwise qualify focus, runtime parity, and fresh independent flows.')


def score():
    import roles559_evaluate as evaluator
    r=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT);manifest=document(r['manifest'])
    q.require(manifest['version']=='role-evaluation567-v1','role_manifest')
    frames=manifest['frames'];q.require(frames and len({f['id'] for f in frames})==len(frames),'role_duplicate_frames')
    membership=document(manifest['trainingMembership'])
    excluded={row['image']['sha256'] for row in membership['rows']}
    q.require(not excluded & {f['image']['sha256'] for f in frames},'role_training_overlap')
    for frame in frames:
        q.require(len({t['id'] for t in frame['truth']})==len(frame['truth']),'role_duplicate_truth')
        checked(frame['image'])
        for ref in frame['references']:checked(ref)
    evaluator.SQUARE=True
    images=list(dict.fromkeys(checked(f['image']) for f in frames))
    predictions=evaluator.rule_b(evaluator.predict(checked(r['model']),images,.001))
    sets={}
    for dataset in sorted({f['dataset'] for f in frames}):
        members=[f for f in frames if f['dataset']==dataset]
        paths=[checked(f['image']) for f in members]
        truth={checked(f['image']):[dict(cls=t['cls'],box=t['box']) for t in f['truth']] for f in members}
        if all(f['complete'] for f in members):sets[dataset]=evaluator.coco(paths,truth,{p:predictions[p] for p in paths})
    q.save(OUT/'benchmark_summary.json',dict(version='role-evaluation567-v1',model=r['model'],manifest=r['manifest'],
        settings=dict(square640=True,ruleB=True,nmsIoU=.45,apConfidence=.001,caseConfidence=.5,iou=.5),
        cases=matched_cases(frames,predictions),metrics=sets,metricsStatus='provisional',modelAccepted=False,
        limitation='Generated-screen development only. No independent real-app accuracy or focus selection claim.'))
    receipt()


def compare():
    r=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    q.save(OUT/'benchmark_summary.json',assess(document(r['baseline']),document(r['candidate'])));receipt()


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
