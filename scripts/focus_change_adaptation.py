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
NATIVE_CONFIG=dict(CONFIG,batch=68)
CONTEXT_CONFIG=dict(NATIVE_CONFIG,inputRepresentation='paired-context-difference-v1')
RESOLUTION_CONFIG=dict(CONTEXT_CONFIG,inputSize=[192,128])
CONTEXT_CONFIGS=(CONTEXT_CONFIG,RESOLUTION_CONFIG)
NATIVE_CONFIGS=(NATIVE_CONFIG,*CONTEXT_CONFIGS)


def score_change(net,x,configuration):
    width,height=configuration.get('inputSize',[96,64])
    d.h.require(tuple(x.shape[1:])==(6,height,width),'change_score_shape')
    return net.change(net.change_inputs(x)).sigmoid().flatten()


def initialize(state,config):
    """Preserve old function; newly available appearance channels start at zero."""
    torch=d.torch_runtime()
    model_config=d.PAIRED_TEMPORAL_CONFIG if config in CONTEXT_CONFIGS else state['configuration']
    net=d.model(model_config);weights=dict(state['state'])
    if config in CONTEXT_CONFIGS:
        source=weights['change.0.weight']
        d.h.require(tuple(source.shape)==(8,3,3,3),'change_context_initializer_shape')
        expanded=torch.zeros((8,9,3,3),dtype=source.dtype,device=source.device)
        expanded[:,:3]=source;weights['change.0.weight']=expanded
    net.load_state_dict(weights,strict=True)
    return net.eval(),model_config


def control_scores(control,doc,corpus):
    if doc['configuration'] in NATIVE_CONFIGS:
        d.h.require(control.get('version')=='native88-frozen-diagnostic-v1' and
            control.get('seal')==d.h.digest({k:v for k,v in control.items() if k!='seal'}) and
            control['corpus']==doc['corpus'] and control['changeModel']==doc['initializer'],
            'change_control_binding')
        return [dict(id=r['id'],prediction=dict(changeProbability=r['probability'])) for r in control['results']]
    d.h.require(control['corpusSHA256']==corpus['corpusSHA256'] and
        control['models']['DTM013']==doc['initializer'],'change_control_binding')
    return [v for v in control['results'] if v['model']=='DTM013' and v['condition']=='baseline']


def pins():
    return dict(base=d.pins(),adapter=d.h.ref(Path(__file__)),resolutionEncoder=d.h.ref(d.h.ROOT/'scripts/diagnose_signal95.py'))


def prepare(output,native_actions=False,paired_context=False,higher_resolution=False):
    out=d.h.fresh(output);start=time.monotonic()
    paired_context=paired_context or higher_resolution
    native_actions=native_actions or paired_context
    root=d.h.ROOT/('reports/work/NATIVE-87/admitted' if native_actions else 'reports/work/NATIVE-ADMISSION-77/admitted')
    config=RESOLUTION_CONFIG if higher_resolution else CONTEXT_CONFIG if paired_context else NATIVE_CONFIG if native_actions else CONFIG
    corpus=d.h.read(root/'corpus.json');admission=d.h.read(root/'admission.json')
    d.h.require(corpus==d.collect(corpus['sources']),'change_source_changed')
    rows=d.admitted(corpus,admission)
    d.h.require(Counter(r['split'] for r in rows)=={'train':config['batch'],'development':5},'change_membership')
    if higher_resolution:
        from diagnose_signal95 import encoded
        x=np.stack([encoded(*(d.pixels(ref) for ref in r['images']),size=(192,128))[0] for r in rows])
    else:x=np.stack([d.encode(*(d.pixels(ref) for ref in r['images'])) for r in rows])
    out.mkdir(parents=True);np.save(out/'x.npy',x,allow_pickle=False)
    doc=dict(version=VERSION,configuration=config,pins=pins(),corpus=d.h.ref(root/'corpus.json'),
        admission=d.h.ref(root/'admission.json'),sourceReferences=references(corpus),
        rowIDs=[r['id'] for r in rows],x=d.h.ref(out/'x.npy'),
        initializer=d.h.ref(d.h.ROOT/('NativeUITrainer/focus_ring_runs/change80-dtm018/last.pt' if native_actions else 'NativeUITrainer/focus_ring_runs/temporal68-dtm013/last.pt')),
        control=d.h.ref(d.h.ROOT/('reports/work/NATIVE-88/diagnostic-r2/diagnostic.json' if native_actions else 'reports/work/BATCH-79-B/native-ready/control.json')),
        ranker=d.h.ref(d.h.ROOT/('NativeUITrainer/focus_ring_runs/native87-dtm020/result.json' if native_actions else 'NativeUITrainer/focus_ring_runs/native79-dtm017/result.json')))
    if higher_resolution:
        previous=d.h.read(d.h.ROOT/'reports/work/CONTEXT-93/ready/protocol.json')
        d.h.require(previous['protocolSHA256']==d.h.digest({k:v for k,v in previous.items() if k!='protocolSHA256'}) and
            previous['corpus']==doc['corpus'] and previous['admission']==doc['admission'] and
            previous['rowIDs']==doc['rowIDs'],'resolution_base_binding')
        doc['baseInputs']=previous['x'];d.h.checked(d.h.ROOT,doc['baseInputs'])
    doc['protocolSHA256']=d.h.digest(doc);d.h.write(out/'protocol.json',doc)
    d.h.write(out/'approval.json',dict(version='change-adaptation-approval-v1',approved=True,
        protocolSHA256=doc['protocolSHA256'],runName='resolution96-dtm023' if higher_resolution else 'context93-dtm022' if paired_context else 'change92-dtm021' if native_actions else 'change80-dtm018',arm=ARM,
        decisionReference=('Standing approved local experiment RESOLUTION96: one192x128change-only paired-context comparison,600epochs,approved68/5,frozen96geometry/ranker,2GiB,no-wall-time override,no capture/export/promotion.' if higher_resolution else
            'Standing approved local experiment tranche CONTEXT93: one600epoch paired-context9channel change-head comparison from DTM018 on approved68/5,zero new channels,2GiB,no-wall-time override,no capture/export/promotion.' if paired_context else
            'Standing approved local experiment tranche CHANGE92: one600epoch existing change-head adaptation from DTM018 on approved68/5,2GiB,no-wall-time override,no capture/export/promotion.' if native_actions else
            'Maintainer explicitly authorizes training; CHANGE80 one600epoch change-head-only DTM013adaptation on approved44/5,2GiB,no capture or promotion.')))
    d.h.write(out/'preparation.json',dict(elapsedSeconds=time.monotonic()-start,encodedPairs=len(rows),
        tensorBytes=x.nbytes,modelLoaded=False,trainingLaunched=False),sealed=True)
    print(doc['protocolSHA256'])


def evaluate_self_pairs(protocol_path,result_path,output):
    """Diagnostic identity invariant; constructed examples are never admitted."""
    h=d.h;out=h.fresh(output);p=h.read(h.local(protocol_path));result=h.read(h.local(result_path))
    h.require(result.get('seal')==h.digest({k:v for k,v in result.items() if k!='seal'}) and
        result['protocol']==h.ref(h.local(protocol_path)),'self_pair_result_binding')
    h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}) and
        p['configuration']==RESOLUTION_CONFIG,'self_pair_protocol')
    corpus=h.read(h.checked(h.ROOT,p['corpus']));rows=d.admitted(corpus,h.read(h.checked(h.ROOT,p['admission'])))
    high=np.load(h.checked(h.ROOT,p['x'],64*1024**2),allow_pickle=False)
    low=np.load(h.checked(h.ROOT,p['baseInputs']),allow_pickle=False)
    h.require(p['rowIDs']==[r['id'] for r in rows] and high.shape==(len(rows),6,128,192) and
        low.shape==(len(rows),6,64,96) and len(rows)<=256,'self_pair_membership')
    unique={}
    for i,row in enumerate(rows):
        for j,ref in enumerate(row['images']):
            h.checked(h.ROOT,ref)
            value=(row['split'],low[i,3*j:3*j+3],high[i,3*j:3*j+3])
            if ref['sha256'] in unique:
                old=unique[ref['sha256']]
                h.require(old[0]==value[0] and np.array_equal(old[1],value[1]) and
                    np.array_equal(old[2],value[2]),'self_pair_duplicate_conflict')
            else:unique[ref['sha256']]=value
    torch=d.torch_runtime();torch.set_num_threads(2);predictions=[];summary={}
    for name,model_ref,index,config in [('initializer',p['initializer'],1,CONFIG),('candidate',result['model'],2,RESOLUTION_CONFIG)]:
        state=torch.load(h.checked(h.ROOT,model_ref),map_location='cpu',weights_only=True)
        h.require(state['adaptation']==config,'self_pair_model_configuration')
        net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
        items=list(unique.items());scores=[]
        for start in range(0,len(items),8):
            batch=np.stack([np.concatenate((v[index],v[index])) for _,v in items[start:start+8]])
            with torch.inference_mode():scores.extend(score_change(net,torch.from_numpy(batch),config).tolist())
        for (sha,value),score in zip(items,scores):
            predictions.append(dict(model=name,imageSHA256=sha,split=value[0],probability=score,
                rawFalseChange=score>=.5,confidentFalseChange=score>=.85,abstained=max(score,1-score)<.85))
        summary[name]={}
        for split in ('train','development'):
            values=[v for v in predictions if v['model']==name and v['split']==split]
            summary[name][split]=dict(frames=len(values),rawFalseChanges=sum(v['rawFalseChange'] for v in values),
                confidentFalseChanges=sum(v['confidentFalseChange'] for v in values),abstentions=sum(v['abstained'] for v in values))
    report=dict(version='change-self-pair-diagnostic-v1',**h.FLAGS,protocol=h.ref(h.local(protocol_path)),
        candidate=h.ref(h.local(result_path)),implementation=h.ref(Path(__file__)),results=predictions,summary=summary,
        constructed=True,trainingLaunched=False,limitation='Same-frame invariant, not genuine navigation or new data admission.')
    out.mkdir(parents=True);h.write(out/'diagnostic.json',report,sealed=True);return report


def load_protocol(path,arm,run_name,approval_path=None):
    path=d.h.local(path);doc=d.h.read(path)
    d.h.require(doc.get('version')==VERSION and doc.get('configuration') in (CONFIG,*NATIVE_CONFIGS) and arm==ARM,'change_configuration')
    config=doc['configuration'];count=config['batch']
    d.h.require(doc['protocolSHA256']==d.h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}) and doc['pins']==pins(),'change_protocol_pins')
    corpus=d.h.read(d.h.checked(d.h.ROOT,doc['corpus']))
    d.h.require(corpus['corpusSHA256']==d.h.digest({k:v for k,v in corpus.items() if k!='corpusSHA256'}),'change_corpus_digest')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,doc['admission'])))
    d.h.require(Counter(r['split'] for r in rows)=={'train':count,'development':5} and
        doc['rowIDs']==[r['id'] for r in rows] and doc['sourceReferences']==references(corpus),'change_membership')
    for ref in doc['sourceReferences']:d.h.checked(d.h.ROOT,ref)
    width,height=config.get('inputSize',[96,64])
    x=np.load(d.h.checked(d.h.ROOT,doc['x'],64*1024**2),allow_pickle=False)
    d.h.require(x.dtype==np.float32 and x.shape==(count+5,6,height,width) and np.isfinite(x).all() and
        ((x>=0)&(x<=1)).all(),'change_tensor')
    if config==RESOLUTION_CONFIG:
        base=np.load(d.h.checked(d.h.ROOT,doc['baseInputs']),allow_pickle=False)
        d.h.require(base.dtype==np.float32 and base.shape==(count+5,6,64,96) and
            np.isfinite(base).all() and ((base>=0)&(base<=1)).all(),'resolution_base_tensor')
    control=d.h.read(d.h.checked(d.h.ROOT,doc['control']))
    d.h.checked(d.h.ROOT,doc['initializer'])
    scores=control_scores(control,doc,corpus)
    ranker=d.h.read(d.h.checked(d.h.ROOT,doc['ranker']))
    d.h.checked(d.h.ROOT,ranker['model'])
    if config in NATIVE_CONFIGS:
        d.h.require(control['rankModel']==ranker['model'],'change_ranker_binding')
    d.h.require(len(scores)==len(ranker['results'])==len(rows) and
        {r['id'] for r in scores}=={r['id'] for r in rows}=={r['id'] for r in ranker['results']},'change_control_membership')
    approval=None
    if approval_path:
        approval=d.h.ref(d.h.local(approval_path));a=d.h.read(d.h.checked(d.h.ROOT,approval))
        d.h.require(a.get('version')=='change-adaptation-approval-v1' and a.get('approved') is True and
            a.get('protocolSHA256')==doc['protocolSHA256'] and a.get('runName')==run_name and
            a.get('arm')==arm and a.get('decisionReference'),'change_approval')
    out=d.old.fresh_run(run_name)
    report=dict(formatVersion='focus-change-preflight-v1',protocolVersion=VERSION,configuration=config,
        launchEligible=approval is not None,blockers=[] if approval else ['missing_approval'],
        protocolSHA256=doc['protocolSHA256'],protocolFile=d.h.ref(path),approval=approval,
        output=str(out.relative_to(d.h.ROOT)),releaseEligible=False)
    return report,(doc,rows,x,scores,ranker['results'])


def run(report,experiment_id):
    start=time.monotonic();fresh,payload=load_protocol(d.h.checked(d.h.ROOT,report['protocolFile']),ARM,
        Path(report['output']).name,d.h.checked(d.h.ROOT,report['approval']))
    d.h.require(fresh==report and fresh['launchEligible'],'change_preflight_changed')
    doc,rows,x,control,ranker=payload
    config=doc['configuration']
    sources=d.h.read(d.h.checked(d.h.ROOT,doc['corpus']))['sources']
    native_prefix=sources['nativeActions' if config in NATIVE_CONFIGS else 'nativeTable']['sha256']+':'
    torch=d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(d.h.checked(d.h.ROOT,doc['initializer']),map_location='cpu',weights_only=True)
    d.h.require(state['version']==d.VERSION and state['configuration']==d.TEMPORAL_CONFIG,'change_initializer_configuration')
    if config in NATIVE_CONFIGS:d.h.require(state.get('adaptation')==CONFIG,'change_initializer_adaptation')
    net,model_config=initialize(state,config)
    tx=torch.from_numpy(x)
    with torch.inference_mode():
        if config==RESOLUTION_CONFIG:
            original,_=initialize(state,NATIVE_CONFIG)
            d.h.require(torch.allclose(score_change(net,tx,config),score_change(original,tx,config),atol=1e-6,rtol=0),'resolution_initializer_parity')
            base=torch.from_numpy(np.load(d.h.checked(d.h.ROOT,doc['baseInputs']),allow_pickle=False))
            before=score_change(net,base,CONTEXT_CONFIG).numpy()
        else:before=score_change(net,tx,config).numpy()
    expected={v['id']:v['prediction']['changeProbability'] for v in control}
    d.h.require(all(abs(float(p)-expected[r['id']])<=1e-6 for r,p in zip(rows,before)),'change_initializer_parity')
    ids=[i for i,r in enumerate(rows) if r['split']=='train'];labels=torch.tensor([float(rows[i]['changed']) for i in ids])
    out=d.old.fresh_run(Path(report['output']).name);out.mkdir(parents=True)
    d.h.write(out/'execution.json',dict(status='started',experimentID=experiment_id,pid=os.getpid(),protocol=report['protocolFile']))
    fit_start=time.monotonic();net,history=d.fit_change_head(net,tx[ids],labels,config);fit_seconds=time.monotonic()-fit_start
    d.h.require(all(torch.equal(value,net.state_dict()[name]) for name,value in state['state'].items() if not name.startswith('change.')),'change_geometry_parity')
    torch.save(dict(version=d.VERSION,configuration=model_config,adaptation=config,state=net.state_dict()),out/'last.pt')
    with torch.inference_mode():after=score_change(net,tx,config).numpy()
    replay=d.model(model_config);replay.load_state_dict(torch.load(out/'last.pt',map_location='cpu',weights_only=True)['state']);replay.eval()
    with torch.inference_mode():again=score_change(replay,tx,config).numpy()
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
    d.h.require(sum(p.stat().st_size for p in out.iterdir())<config['maxOutputBytes'],'change_output_budget')
    d.h.write(out/'completion.json',dict(status='completed',exitCode=0,pid=os.getpid(),result=d.h.ref(out/'result.json')),sealed=True)
    print(summary);return 0


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',required=True);p.add_argument('--approve',action='store_true')
    p.add_argument('--native-actions',action='store_true',help='Prepare the separately scoped CHANGE92 admitted68/5 comparison')
    p.add_argument('--paired-context',action='store_true',help='Prepare the CONTEXT93 paired appearance architecture comparison')
    p.add_argument('--higher-resolution',action='store_true',help='Prepare the RESOLUTION96 change-only192x128 comparison')
    args=p.parse_args()
    if not args.approve:p.error('explicit experiment authorization required')
    prepare(args.prepare,args.native_actions,args.paired_context,args.higher_resolution)
