"""Pinned Region change-only experiment orchestration using the existing trainer."""
import argparse
import os
from pathlib import Path
import time
import numpy as np
import focus_change_adaptation as c
import focus_direct_transition as d
from intake_shadow111 import read,sha,member
from prepare_collection103 import original_negatives

h=d.h
BASE=h.ROOT/'reports/work/REGION-REVIEW-112'
ROOT=h.ROOT/'reports/work/SHADOW-REGION-111/artifacts/intake/ttr-settings-region12-20261004-v2'
CONFIG=dict(c.COLLECTION_CONFIG,batch=202,originalGroupCount=202,derivedGroupCount=217,initializer='DTM025')


def source_pins():
    return {name:h.ref(h.ROOT/name) for name in ('scripts/region112_experiment.py',
        'scripts/focus_change_adaptation.py','scripts/focus_direct_transition.py','scripts/diagnose_signal95.py',
        'reports/work/REGION-REVIEW-112/visual-labels.txt','reports/work/REGION-REVIEW-112/admission.md')}


def prepare(ready):
    out=h.fresh(ready);start=time.monotonic()
    previous=h.read(h.ROOT/'reports/work/COLLECTION-104/ready/change-protocol.json')
    rows=d.admitted(h.read(h.checked(h.ROOT,previous['corpus'])),h.read(h.checked(h.ROOT,previous['admission'])))
    old_x=np.load(h.checked(h.ROOT,previous['x'],64*1024**2),allow_pickle=False)
    h.require(old_x.shape==(113,6,128,192) and len(rows)==113,'old_membership')
    survey=read(ROOT/'survey.json');index=read(BASE/'artifacts/review/index.json')
    labels=(BASE/'visual-labels.txt').read_text().splitlines()
    h.require(len(labels)==len(survey['records'])==95 and index['source_manifest_sha256']==sha(ROOT/'manifest.json'),'review_membership')
    from diagnose_signal95 import encoded
    images=[]
    for n,(r,i,label) in enumerate(zip(survey['records'],index['records'],labels),1):
        h.require(r['sequence']==i['sequence']==n and r['image_sha256']==i['image_sha256'] and
            r['native_evidence']['focusedRowLabel']==label,'visual_native_disagreement')
        path=member(ROOT,r['image']);h.require(sha(path)==r['image_sha256'],'changed_review_pixel')
        images.append(h.ref(path))
    h.require(all(a!=b for a,b in zip(labels,labels[1:])),'review_transition')
    new_x=np.stack([encoded(d.pixels(a),d.pixels(b),size=(192,128))[0] for a,b in zip(images,images[1:])])
    negatives=original_negatives(previous,rows,old_x)
    self_old=np.stack([np.concatenate([old_x[v['origins'][0]['rowIndex'],3*v['origins'][0]['endpoint']:3*v['origins'][0]['endpoint']+3]]*2)
        for v in negatives])
    # Endpoint extraction from the existing encoder, not an independent cropper.
    frame_x=[new_x[0,:3]]+[v[3:] for v in new_x]
    self_new=np.stack([np.concatenate([v,v]) for v in frame_x])
    ids=[n for n,r in enumerate(rows) if r['split']=='train'];dev=[n for n,r in enumerate(rows) if r['split']=='development']
    h.require(len(ids)==108 and len(dev)==5 and len(self_old)==122,'old_roles')
    train=np.concatenate([old_x[ids],new_x,self_old,self_new]);y=np.array([float(rows[i]['changed']) for i in ids]+[1.]*94+[0.]*217,dtype=np.float32)
    evaluation=np.concatenate([old_x,new_x,self_old,self_new])
    out.mkdir(parents=True)
    np.save(out/'train.npy',train,allow_pickle=False);np.save(out/'labels.npy',y,allow_pickle=False);np.save(out/'evaluation.npy',evaluation,allow_pickle=False)
    admission=dict(version=1,owner='Codex under October4 maintainer delegation',training=True,task='change_only',
        sourceManifest=h.ref(ROOT/'manifest.json'),visualReview=source_pins()['reports/work/REGION-REVIEW-112/visual-labels.txt'],
        images=images,changedPairs=94,derivedIdenticalNegatives=95,independenceGroup='tvos-settings-native-layout-family',
        finalEligible=False,geometryEligible=False,reviewerKind='agent_visual_review')
    h.write(out/'admission.json',admission,sealed=True)
    protocol=dict(version='region112-change-v1',configuration=CONFIG,pins=source_pins(),
        initializer=h.ref(h.ROOT/'NativeUITrainer/focus_ring_runs/collection104-dtm025/last.pt'),
        oldProtocol=h.ref(h.ROOT/'reports/work/COLLECTION-104/ready/change-protocol.json'),
        admission=h.ref(out/'admission.json'),inputs={k:h.ref(out/(k+'.npy')) for k in ('train','labels','evaluation')},
        oldLabels=[r['changed'] for r in rows],oldTrainIndices=ids,relatedSettingsIndices=dev,
        expectedSizes=dict(train=419,evaluation=424),experiment='DTM028',output='NativeUITrainer/focus_ring_runs/region112-dtm028')
    protocol['protocolSHA256']=h.digest(protocol);h.write(out/'protocol.json',protocol)
    h.write(out/'preparation.json',dict(seconds=time.monotonic()-start,train=train.shape,evaluation=evaluation.shape))
    print(protocol['protocolSHA256'])


def execute(ready):
    start=time.monotonic();p=h.read(ready/'protocol.json')
    h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}) and p['pins']==source_pins() and p['configuration']==CONFIG,'protocol_changed')
    h.require(p['protocolSHA256'] in (h.ROOT/'Research/ExperimentLog.md').read_text(),'experiment_not_logged')
    admission=h.read(h.checked(h.ROOT,p['admission']))
    h.require(admission['seal']==h.digest({k:v for k,v in admission.items() if k!='seal'}) and admission['training'] is True,'admission')
    for ref in admission['images']:h.checked(h.ROOT,ref)
    h.checked(h.ROOT,admission['sourceManifest']);h.checked(h.ROOT,p['oldProtocol'])
    x,y,e=[np.load(h.checked(h.ROOT,p['inputs'][k],256*1024**2),allow_pickle=False) for k in ('train','labels','evaluation')]
    h.require(x.shape==(419,6,128,192) and y.shape==(419,) and e.shape==(424,6,128,192),'inputs')
    torch=d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,p['initializer']),map_location='cpu',weights_only=True)
    h.require(state['configuration']==d.PAIRED_TEMPORAL_CONFIG and state['adaptation']==c.COLLECTION_CONFIG,'initializer')
    net=d.model(state['configuration']);net.load_state_dict(state['state']);net.eval();tx=torch.from_numpy(e)
    with torch.inference_mode():before=c.score_change(net,tx,CONFIG).numpy()
    h.require(p['output']=='NativeUITrainer/focus_ring_runs/region112-dtm028','run_output')
    out=d.old.fresh_run(Path(p['output']).name);out.mkdir(parents=True)
    h.write(out/'execution.json',dict(status='started',pid=os.getpid(),experimentID='DTM028',protocolSHA256=p['protocolSHA256']))
    fit=time.monotonic();net,history=d.fit_change_head(net,torch.from_numpy(x),torch.from_numpy(y),CONFIG);seconds=time.monotonic()-fit
    h.require(all(torch.equal(v,net.state_dict()[k]) for k,v in state['state'].items() if not k.startswith('change.')),'geometry_changed')
    torch.save(dict(version=d.VERSION,configuration=state['configuration'],adaptation=CONFIG,state=net.state_dict()),out/'last.pt')
    with torch.inference_mode():after=c.score_change(net,tx,CONFIG).numpy()
    replay=d.model(state['configuration']);replay.load_state_dict(torch.load(out/'last.pt',map_location='cpu',weights_only=True)['state']);replay.eval()
    with torch.inference_mode():again=c.score_change(replay,tx,CONFIG).numpy()
    h.require(np.array_equal(after,again),'checkpoint_replay')
    truth=np.array(p['oldLabels']+[True]*94+[False]*217)
    groups=dict(oldTrain=p['oldTrainIndices'],relatedSettings=p['relatedSettingsIndices'],region=list(range(113,207)),oldDerived=list(range(207,329)),regionDerived=list(range(329,424)))
    summary={}
    for name,ids in groups.items():
        a,b,t=before[ids],after[ids],truth[ids];known=lambda s:(s<=.15)|(s>=.85)
        oldgood=known(a)&((a>=.5)==t);newgood=known(b)&((b>=.5)==t)
        summary[name]=dict(count=len(ids),beforeConfidentCorrect=int(oldgood.sum()),afterConfidentCorrect=int(newgood.sum()),lostConfidentSuccesses=int((oldgood&~newgood).sum()),abstentions=int((~known(b)).sum()),rawCorrect=int(((b>=.5)==t).sum()))
    passed=summary['region']['afterConfidentCorrect']==94 and all(v['lostConfidentSuccesses']==0 for v in summary.values()) and all(summary[n]['afterConfidentCorrect']==summary[n]['count'] for n in ('oldDerived','regionDerived'))
    h.write(out/'result.json',dict(experiment='DTM028',protocolSHA256=p['protocolSHA256'],model=h.ref(out/'last.pt'),summary=summary,
        before=before.tolist(),after=after.tolist(),history=history,fitSeconds=seconds,totalSeconds=time.monotonic()-start,
        geometryUnchanged=True,checkpointReplay=True,developmentGatesPassed=passed,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_budget')
    h.write(out/'completion.json',dict(status='completed',pid=os.getpid(),exitCode=0,result=h.ref(out/'result.json')))
    print(summary)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','execute']);p.add_argument('--ready',type=Path,required=True);args=p.parse_args()
    ready=h.local(args.ready)
    prepare(ready) if args.mode=='prepare' else execute(ready)
