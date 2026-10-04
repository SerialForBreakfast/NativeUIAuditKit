"""CHANGE80: approved change-only adaptation through the existing training dispatcher."""
import argparse
import os
import time
from collections import Counter
from pathlib import Path
import numpy as np
import focus_direct_transition as d
from prepare_transition_inputs import references

VERSION='focus-change-adaptation-v1'
ARM='transition-change-adaptation'
CONFIG=dict(model=ARM,epochs=600,batch=44,lr=.0001,seed=42,threads=2,backend='cpu',
    optimizer='adam',selection='fixed-last',augmentation='none',maxOutputBytes=2*1024**3)


def pins():
    return dict(base=d.pins(),adapter=d.h.ref(Path(__file__)))


def prepare(output):
    out=d.h.fresh(output);start=time.monotonic()
    root=d.h.ROOT/'reports/work/NATIVE-ADMISSION-77/admitted'
    corpus=d.h.read(root/'corpus.json');admission=d.h.read(root/'admission.json')
    d.h.require(corpus==d.collect(corpus['sources']),'change_source_changed')
    rows=d.admitted(corpus,admission)
    d.h.require(Counter(r['split'] for r in rows)=={'train':44,'development':5},'change_membership')
    x=np.stack([d.encode(*(d.pixels(ref) for ref in r['images'])) for r in rows])
    out.mkdir(parents=True);np.save(out/'x.npy',x,allow_pickle=False)
    doc=dict(version=VERSION,configuration=CONFIG,pins=pins(),corpus=d.h.ref(root/'corpus.json'),
        admission=d.h.ref(root/'admission.json'),sourceReferences=references(corpus),
        rowIDs=[r['id'] for r in rows],x=d.h.ref(out/'x.npy'),
        initializer=d.h.ref(d.h.ROOT/'NativeUITrainer/focus_ring_runs/temporal68-dtm013/last.pt'),
        control=d.h.ref(d.h.ROOT/'reports/work/BATCH-79-B/native-ready/control.json'),
        ranker=d.h.ref(d.h.ROOT/'NativeUITrainer/focus_ring_runs/native79-dtm017/result.json'))
    doc['protocolSHA256']=d.h.digest(doc);d.h.write(out/'protocol.json',doc)
    d.h.write(out/'approval.json',dict(version='change-adaptation-approval-v1',approved=True,
        protocolSHA256=doc['protocolSHA256'],runName='change80-dtm018',arm=ARM,
        decisionReference='Maintainer explicitly authorizes training; CHANGE80 one600epoch change-head-only DTM013adaptation on approved44/5,2GiB,no capture or promotion.'))
    d.h.write(out/'preparation.json',dict(elapsedSeconds=time.monotonic()-start,encodedPairs=len(rows),
        tensorBytes=x.nbytes,modelLoaded=False,trainingLaunched=False),sealed=True)
    print(doc['protocolSHA256'])


def load_protocol(path,arm,run_name,approval_path=None):
    path=d.h.local(path);doc=d.h.read(path)
    d.h.require(doc.get('version')==VERSION and doc.get('configuration')==CONFIG and arm==ARM,'change_configuration')
    d.h.require(doc['protocolSHA256']==d.h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}) and doc['pins']==pins(),'change_protocol_pins')
    corpus=d.h.read(d.h.checked(d.h.ROOT,doc['corpus']))
    d.h.require(corpus['corpusSHA256']==d.h.digest({k:v for k,v in corpus.items() if k!='corpusSHA256'}),'change_corpus_digest')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,doc['admission'])))
    d.h.require(Counter(r['split'] for r in rows)=={'train':44,'development':5} and
        doc['rowIDs']==[r['id'] for r in rows] and doc['sourceReferences']==references(corpus),'change_membership')
    for ref in doc['sourceReferences']:d.h.checked(d.h.ROOT,ref)
    x=np.load(d.h.checked(d.h.ROOT,doc['x']),allow_pickle=False)
    d.h.require(x.dtype==np.float32 and x.shape==(49,6,64,96) and np.isfinite(x).all() and
        ((x>=0)&(x<=1)).all(),'change_tensor')
    control=d.h.read(d.h.checked(d.h.ROOT,doc['control']))
    d.h.require(control['corpusSHA256']==corpus['corpusSHA256'] and control['models']['DTM013']==doc['initializer'],'change_control_binding')
    d.h.checked(d.h.ROOT,doc['initializer'])
    scores=[v for v in control['results'] if v['model']=='DTM013' and v['condition']=='baseline']
    ranker=d.h.read(d.h.checked(d.h.ROOT,doc['ranker']))
    d.h.checked(d.h.ROOT,ranker['model'])
    d.h.require(len(scores)==len(ranker['results'])==len(rows) and
        {r['id'] for r in scores}=={r['id'] for r in rows}=={r['id'] for r in ranker['results']},'change_control_membership')
    approval=None
    if approval_path:
        approval=d.h.ref(d.h.local(approval_path));a=d.h.read(d.h.checked(d.h.ROOT,approval))
        d.h.require(a.get('version')=='change-adaptation-approval-v1' and a.get('approved') is True and
            a.get('protocolSHA256')==doc['protocolSHA256'] and a.get('runName')==run_name and
            a.get('arm')==arm and a.get('decisionReference'),'change_approval')
    out=d.old.fresh_run(run_name)
    report=dict(formatVersion='focus-change-preflight-v1',protocolVersion=VERSION,configuration=CONFIG,
        launchEligible=approval is not None,blockers=[] if approval else ['missing_approval'],
        protocolSHA256=doc['protocolSHA256'],protocolFile=d.h.ref(path),approval=approval,
        output=str(out.relative_to(d.h.ROOT)),releaseEligible=False)
    return report,(doc,rows,x,scores,ranker['results'])


def run(report,experiment_id):
    start=time.monotonic();fresh,payload=load_protocol(d.h.checked(d.h.ROOT,report['protocolFile']),ARM,
        Path(report['output']).name,d.h.checked(d.h.ROOT,report['approval']))
    d.h.require(fresh==report and fresh['launchEligible'],'change_preflight_changed')
    doc,rows,x,control,ranker=payload
    native_prefix=d.h.read(d.h.checked(d.h.ROOT,doc['corpus']))['sources']['nativeTable']['sha256']+':'
    torch=d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(d.h.checked(d.h.ROOT,doc['initializer']),map_location='cpu',weights_only=True)
    d.h.require(state['version']==d.VERSION and state['configuration']==d.TEMPORAL_CONFIG,'change_initializer_configuration')
    net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    tx=torch.from_numpy(x);difference=(tx[:,3:]-tx[:,:3]).abs()
    with torch.inference_mode():before=net.change(difference).sigmoid().flatten().numpy()
    expected={v['id']:v['prediction']['changeProbability'] for v in control}
    d.h.require(all(abs(float(p)-expected[r['id']])<=1e-6 for r,p in zip(rows,before)),'change_initializer_parity')
    ids=[i for i,r in enumerate(rows) if r['split']=='train'];labels=torch.tensor([float(rows[i]['changed']) for i in ids])
    out=d.old.fresh_run(Path(report['output']).name);out.mkdir(parents=True)
    d.h.write(out/'execution.json',dict(status='started',experimentID=experiment_id,pid=os.getpid(),protocol=report['protocolFile']))
    fit_start=time.monotonic();net,history=d.fit_change_head(net,tx[ids],labels,CONFIG);fit_seconds=time.monotonic()-fit_start
    d.h.require(all(torch.equal(value,net.state_dict()[name]) for name,value in state['state'].items() if not name.startswith('change.')),'change_geometry_parity')
    torch.save(dict(version=d.VERSION,configuration=d.TEMPORAL_CONFIG,adaptation=CONFIG,state=net.state_dict()),out/'last.pt')
    with torch.inference_mode():after=net.change(difference).sigmoid().flatten().numpy()
    replay=d.model(d.TEMPORAL_CONFIG);replay.load_state_dict(torch.load(out/'last.pt',map_location='cpu',weights_only=True)['state']);replay.eval()
    with torch.inference_mode():again=replay.change(difference).sigmoid().flatten().numpy()
    d.h.require(np.array_equal(after,again),'change_checkpoint_replay')
    boxes={v['id']:v for v in ranker};results=[]
    for row,a,b in zip(rows,before,after):
        confidence=max(float(b),1-float(b));known=confidence>=d.CONFIG['confidence']
        results.append(dict(id=row['id'],split=row['split'],nativeTable=row['id'].startswith(native_prefix),
            expectedChange=row['changed'],before=float(a),after=float(b),beforeCorrect=bool((a>=.5)==row['changed']),
            afterCorrect=bool((b>=.5)==row['changed']),abstained=not known,
            joint=bool(known and (b>=.5)==row['changed'] and boxes[row['id']]['bothBoxesCorrect'])))
    summary={}
    for group in ('originalTrain','nativeTrain','exposedSettings'):
        values=[r for r in results if ('exposedSettings' if r['split']=='development' else 'nativeTrain' if r['nativeTable'] else 'originalTrain')==group]
        summary[group]=dict(pairs=len(values),beforeCorrect=sum(r['beforeCorrect'] for r in values),
            afterCorrect=sum(r['afterCorrect'] for r in values),abstentions=sum(r['abstained'] for r in values),joint=sum(r['joint'] for r in values))
    result=dict(version=VERSION,protocol=report['protocolFile'],model=d.h.ref(out/'last.pt'),
        results=results,summary=summary,history=history,fitSeconds=fit_seconds,elapsedSeconds=time.monotonic()-start,
        geometryWeightsUnchanged=True,checkpointReplay=True,releaseEligible=False)
    d.h.write(out/'result.json',result,sealed=True)
    d.h.require(sum(p.stat().st_size for p in out.iterdir())<CONFIG['maxOutputBytes'],'change_output_budget')
    d.h.write(out/'completion.json',dict(status='completed',exitCode=0,pid=os.getpid(),result=d.h.ref(out/'result.json')),sealed=True)
    print(summary);return 0


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',required=True);p.add_argument('--approve',action='store_true')
    args=p.parse_args()
    if not args.approve:p.error('explicit experiment authorization required')
    prepare(args.prepare)
