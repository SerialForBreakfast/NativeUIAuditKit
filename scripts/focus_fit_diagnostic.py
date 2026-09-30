"""Small balanced training-fit diagnostic using an immutable, previously encoded cache."""
import argparse
from collections import Counter
import json
import math

import focus_human_static_experiment as static
import focus_paired_experiment as paired
from focus_dataset_contract import ROOT, digest, local

a=static.a
require=static.require
VERSION='focus-fit-diagnostic-v1'
CONFIG=dict(epochs=1000,batch=48,lr=.01,model='mobilenet_v3_small_frozen',seed=42,
            maxSeconds=300,augmentation='none',inputSize=256,initialization='fresh-linear-head',
            testDuringTraining=False,selection='diagnostic-training-fit-only')


def select(base):
    native=[r for r in base['samples'] if r['use']=='train-candidate']
    human=[r for r in base['samples'] if r['use']=='human-static-auxiliary']
    groups=paired.pairs(native,base['sampling']['weights'])
    # Appearance mapping comes from the exact admitted baseline, not class guesses.
    assembly=static.sealed(base['inputs']['assembly'],'assemblySHA256')
    mapping=assembly['trainingAppearance']
    selected=[];seen=set()
    for lane in ('buttons','tabs','artwork','rows'):
        count=0
        for pair in sorted(groups,key=lambda p:digest(p['ids'])):
            rows=[native[i] for i in pair['indices']]
            if any(mapping[r['id']]['stratum']!=lane for r in rows):continue
            pixels=[r['crop']['pixelSHA256'] for r in rows]
            if len(set(pixels))!=2 or seen.intersection(pixels):continue
            selected+=rows;seen.update(pixels);count+=1
            if count==4:break
        require(count==4,'insufficient_unique_training_pairs')
    frames=sorted({r['frameID'] for r in human});require(len(frames)==8,'changed_human_frames')
    for frame in frames:
        for label in (1,0):
            candidates=sorted((r for r in human if r['frameID']==frame and r['label']==label
                               and r['pixelSHA256'] not in seen),key=lambda r:r['id'])
            require(bool(candidates),'missing_human_label')
            row=candidates[0];require('pairID' not in row,'fabricated_pair')
            selected.append(row);seen.add(row['pixelSHA256'])
    validate_subset(selected,base['samples'])
    return selected


def validate_subset(rows,all_rows):
    require(len(rows)==48 and len({r['id'] for r in rows})==48
            and Counter(r['label'] for r in rows)=={0:24,1:24},'unbalanced_or_duplicate_fit_subset')
    originals={r['id']:r for r in all_rows}
    for r in rows:
        require(r==originals.get(r['id']) and r['split']=='train'
                and r['use'] in ('train-candidate','human-static-auxiliary'),'not_admitted_training')
    pixels=[r.get('pixelSHA256',r['crop'].get('pixelSHA256')) for r in rows]
    require(None not in pixels and len(set(pixels))==48,'duplicate_training_pixels')
    forbidden={r.get('pixelSHA256',r['crop'].get('pixelSHA256')) for r in all_rows if r['split']=='validation'}
    require(not set(pixels)&forbidden,'development_overlap')


def assemble(spec):
    require(spec['version']=='focus-fit-input-v1','wrong_fit_input')
    base=static.sealed(spec['base'],'protocolSHA256')
    require(base['version']==static.VERSION,'wrong_feature_base')
    preflight=static.read_ref(spec['preflight']);receipt=static.read_ref(spec['receipt'])
    require(preflight['protocolSHA256']==base['protocolSHA256'] and receipt['representation']==base['representation']
            and receipt['backboneUnchanged'] is True,'wrong_cache_provenance')
    a.checked(spec['cache']);a.checked(base['representation']['weights'])
    for ref in static.read_ref(base['inputs']['inventoryInputs']):a.checked(ref)
    rows=select(base);static.check_pixels(base['samples'])
    validation=[r for r in base['samples'] if r['split']=='validation']
    runtime=static.rep.retention.runtime_identity()
    runtime['code'] += [a.reference(ROOT/'scripts'/n) for n in ('focus_fit_diagnostic.py',
        'focus_paired_experiment.py','focus_pretrained_experiment.py','focus_representative_experiment.py',
        'focus_representative_validation.py','human_focus_evaluation.py','human_focus_roles.py')]
    doc=dict(version=VERSION,inputs=spec,samples=rows+validation,runtime=runtime,
        configuration=CONFIG,selection=base['selection'],representation=base['representation'],warmCheckpoint=None,
        counts=dict(training=48,development=315,retention=18),
        fitDiagnostic=dict(trainingIDs=[r['id'] for r in rows],maxUpdates=1000,
                           consecutivePasses=5,positiveFloor=.85,negativeCeiling=.15,maxTrainingBCE=.05),
        releaseEligible=False,unmetQualificationBlockers=['diagnostic memorization is not model qualification'])
    doc['protocolSHA256']=digest(doc);return doc


def load_protocol(path,arm,run_name,approval_path=None):
    path=local(path);doc=static.sealed(a.reference(path),'protocolSHA256')
    require(doc['version']==VERSION and doc==assemble(doc['inputs']),'changed_fit_protocol')
    require(arm=='fit-diagnostic' and run_name=='fdr019-balanced-fit','wrong_fit_run')
    out=ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists(),'output_collision')
    blockers=[];approval_ref=None
    if approval_path is None:blockers.append('missing_fit_approval')
    else:
        approval_ref=a.reference(local(approval_path));approval=static.read_ref(approval_ref)
        require(approval==dict(version='focus-fit-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
            authority='Maintainer approved small balanced learning diagnostic, 2026-09-30',
            arm=arm,runName=run_name,scope='one-diagnostic-no-export-no-promotion'),'stale_fit_approval')
    rows=[{**r,'path':a.checked({k:r['crop'][k] for k in ('path','sha256')})} for r in doc['samples']]
    return dict(formatVersion=static.rep.FORMAT,protocolVersion=VERSION,launchEligible=not blockers,
        configurationValid=True,executionAuthorized=False,blockers=blockers,releaseEligible=False,
        **{k:doc[k] for k in ('configuration','selection','representation','warmCheckpoint','runtime',
                            'counts','fitDiagnostic','protocolSHA256','unmetQualificationBlockers')},
        cachedInputs=doc['inputs'],protocolFile=a.reference(path),approval=approval_ref,arm=arm),rows


def prepare_features(report,train,validation,device,output):
    import torch
    spec=report['cachedInputs'];base=static.read_ref(spec['base'])
    all_train=[r for r in base['samples'] if r['split']=='train']
    all_validation=[r for r in base['samples'] if r['split']=='validation']
    cache=torch.load(a.checked(spec['cache']),map_location='cpu',weights_only=True)
    receipt=static.read_ref(spec['receipt'])
    paired.validate_tensors(cache,receipt,all_train,all_validation)
    require([r['id'] for r in validation]==[r['id'] for r in all_validation],'changed_fit_validation_order')
    lookup={r['id']:i for i,r in enumerate(all_train)}
    indices=torch.tensor([lookup[r['id']] for r in train])
    x,y=cache['train'];dataset=torch.utils.data.TensorDataset(x[indices],y[indices])
    torch.manual_seed(42);head=torch.nn.Linear(576,1).to(device)
    with (output/'fit-feature-receipt.json').open('x') as f:
        json.dump(dict(source=spec,selectedIndices=indices.tolist(),originalReceipt=receipt,
                       encoderLoaded=False,headParameters=577,
                       initialHeadSHA256=paired.base.state_digest(head)),f,indent=2)
    return head,dataset,torch.utils.data.TensorDataset(*cache['validation'])


def fit_metrics(predictions,rows,loss):
    require(len(predictions)==len(rows) and [p['id'] for p in predictions]==[r['id'] for r in rows]
            and len({r['id'] for r in rows})==len(rows),'fit_prediction_membership')
    require(math.isfinite(loss) and loss>=0,'invalid_fit_loss')
    confident=correct=0;groups={}
    for p,r in zip(predictions,rows):
        q=p['probability']
        require(type(q) in (int,float) and math.isfinite(q) and 0<=q<=1 and p['label']==r['label']
                and r['split']=='train','invalid_fit_prediction')
        hit=q>=.85 if r['label'] else q<=.15
        confident+=hit;correct+=int(q>=.5)==r['label']
        key='human' if r['use']=='human-static-auxiliary' else 'native-fixture'
        group=groups.setdefault(key,dict(n=0,confidentCorrect=0,classificationCorrect=0))
        group['n']+=1;group['confidentCorrect']+=hit;group['classificationCorrect']+=int(q>=.5)==r['label']
    return dict(n=len(rows),confidentCorrect=confident,classificationCorrect=correct,groups=groups,
                fitPass=confident==len(rows) and loss<=.05)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=local,required=True);args=p.parse_args()
    require(not args.output.exists(),'output_collision')
    prior=ROOT/'NativeUITrainer/focus_ring_runs/fdr017-static-baseline'
    spec=dict(version='focus-fit-input-v1',base=a.reference(ROOT/'reports/work/HUMAN-STATIC-ADMISSION/frozen-ready/protocol.json'),
        cache=a.reference(prior/'features.pt'),receipt=a.reference(prior/'pretrained-features.json'),
        preflight=a.reference(prior/'preflight.json'))
    doc=assemble(spec);args.output.mkdir(parents=True)
    approval=dict(version='focus-fit-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
        authority='Maintainer approved small balanced learning diagnostic, 2026-09-30',
        arm='fit-diagnostic',runName='fdr019-balanced-fit',scope='one-diagnostic-no-export-no-promotion')
    for name,value in [('protocol.json',doc),('approval.json',approval)]:
        with (args.output/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False)
    print(json.dumps(dict(protocolSHA256=doc['protocolSHA256'],counts=doc['counts'])))


if __name__=='__main__':main()
