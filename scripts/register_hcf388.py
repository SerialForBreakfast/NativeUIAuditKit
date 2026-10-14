"""Prepare or submit the finite HCF completion graph. Do not start execution."""
from pathlib import Path
import argparse
import copy
import research_queue as q
import research_approval as approval

FOLDER=q.ROOT/'Research/ResearchSpecs/HCF388'
CHANGED={'scripts/train_yolo.py','scripts/hcf_training375.py','scripts/hcf_factor_train376.py',
         'scripts/hcf_compare371.py','scripts/usb_training386.py','scripts/artifact_storage.py'}


def save(path,value):
    if path.exists():q.require(q.load(path)==value,'immutable_hcf388_changed')
    else:q.save(path,value)


def clone(old,ident):
    spec=copy.deepcopy(q.load(q.QUEUE/'jobs'/old/'spec.json'))
    spec.update(id=ident,task='HCF388')
    for ref in spec['inputs']:
        if ref['path'] in CHANGED:ref['sha256']=q.digest(q.ROOT/ref['path'])
    return spec


def config(spec,filename,**updates):
    stage=next(x for x in spec['stage'] if x['to']==filename)
    value=q.load(q.ROOT/stage['from']['path']);value.update(updates)
    path=FOLDER/(spec['id']+'-'+filename);save(path,value)
    stage['from']=dict(path=q.relative(path),sha256=q.digest(path))


def dep(spec,old,new):
    item=next(x for x in spec['dependencies'] if x['job']==old)
    item.update(job=new['id'],specSHA256=q.text_digest(new))


def reference(spec,output):
    return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=[output])


def aggregation(ident,step,deps,question):
    spec=clone('hcf375d-90-decision-v2-usb2',ident)
    spec.update(dependencies=deps,stage=[],question=question,hypothesis=question,
        controlledComparison='Read exact producer reports on unchanged inspected development and retained membership.',
        decisionRule='Missing reports fail. Report gains and losses. Do not accept a model or open final audit.')
    spec['adapter']=dict(type='python-callable',steps=['hcf_finish388.'+step],outputAttributes=['hcf_finish388.OUT'])
    spec['inputs'].append(dict(path='scripts/hcf_finish388.py',sha256=q.digest(q.ROOT/'scripts/hcf_finish388.py')))
    spec['nextActionByOutcome']=dict(supported='Qualify deployable proposals and no-focus coverage before deployment.',
                                    contradicted='Use case-linked losses to choose the next correction. Preserve the current model.')
    return spec


def build():
    FOLDER.mkdir(exist_ok=True)
    specs=[]
    train=clone('hcf375d-71-detector-train-v2-usb2','hcf388-detector-train')
    config(train,'config.json',datasetFolder='yolo-training-hcf388-fixed30',patience=0)
    config(train,'usb.json',job=train['id'])
    train['training']['experimentLogRunId']='HCF388'
    train['decisionRule']='Complete 30 epochs with early stopping disabled. Keep calibration-only best checkpoint selection. Fail at the 2 h limit.'
    train['question']=train['hypothesis']='Does the completed 30-epoch detector improve selection without losing retained successes?'
    specs.append(train)
    evaluation=clone('hcf375d-81-detector-evaluate-v2-usb2','hcf388-detector-evaluate')
    dep(evaluation,'hcf375d-71-detector-train-v2-usb2',train)
    config(evaluation,'config.json',sourceProjectRoot=str(Path.home() / 'Documents/GitHub/NativeUIAuditKit'))
    specs.append(evaluation)
    decision=clone('hcf375d-90-decision-v2-usb2','hcf388-method-decision')
    dep(decision,'hcf375d-81-detector-evaluate-v2-usb2',evaluation)
    decision['question']=decision['hypothesis']='How do rules, the crop candidate, and the completed detector compare on the same cases?'
    specs.append(decision)
    evaluations=[]
    for seed in (372,373):
        repeat=clone('hcf376-hcf-unique-train-v1-usb2-move387',f'hcf388-crop-seed{seed}-train')
        config(repeat,'config.json',profile='balanced',deduplicate=True,seed=seed)
        config(repeat,'usb.json',job=repeat['id'])
        repeat['training']['experimentLogRunId']='HCF388'
        repeat['question']=repeat['hypothesis']=f'Does balanced unique crop training preserve the 264 known-box successes with seed {seed}?'
        repeat['controlledComparison']='Change only seed against HCF375C balanced unique seed371. Preserve crops, groups, initialization, and 30 epochs.'
        repeat['decisionRule']='Complete 30 epochs. Compare against seed371 without changing the 0.85 threshold. Any lost success needs review.'
        specs.append(repeat)
        score=clone('hcf376-hcf-unique-evaluate-v1-usb2-move387',f'hcf388-crop-seed{seed}-evaluate')
        dep(score,'hcf376-hcf-unique-train-v1-usb2-move387',repeat)
        score['question']=score['hypothesis']=f'Which prior successes does crop seed {seed} preserve or lose?'
        specs.append(score);evaluations.append(score)
    baseline=q.load(q.QUEUE/'jobs/hcf375c-80-crop-evaluate/spec.json')
    review=aggregation('hcf388-seed-review','seed_review',
        [reference(baseline,'comparison.json')]+[reference(x,'comparison.json') for x in evaluations],
        'Does the balanced unique crop result repeat across 3 seeds without lost successes?')
    specs.append(review)
    specs.append(aggregation('hcf388-study-report','finish',
        [reference(decision,'decision.json'),reference(review,'seed-review.json')],
        'What does the complete HCF development study support, and what still prevents deployment?'))
    for spec in specs:save(FOLDER/(spec['id']+'.json'),spec)
    return specs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--submit',action='store_true');args=parser.parse_args()
    specs=build()
    for spec in specs:
        print(spec['id'],q.text_digest(spec),flush=True)
        if args.submit:
            q.validate(spec);q.verify_pins(spec)
            if not (q.QUEUE/'jobs'/spec['id']).exists():q.submit(FOLDER/(spec['id']+'.json'))
            approval.approve(q.QUEUE,spec['id'],'agent:hcf388',
                'Maintainer asks to finish HCF end to end through the background queue. Exact fixed comparison; no promotion.')
    if args.submit:
        for ident in ('hcf375d-81-detector-evaluate-v2-usb2','hcf375d-90-decision-v2-usb2'):
            if ident in approval.approved_map(q.QUEUE):
                approval.revoke(q.QUEUE,ident,'agent:hcf388','Explicit HCF388 successor replaces the failed producer dependency.')


if __name__=='__main__':main()
