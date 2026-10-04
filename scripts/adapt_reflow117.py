"""Explicit exposed-Settings admission; one fixed residual fit, no promotion."""
import argparse
import hashlib
import os
import time
import numpy as np
import focus_identity_residual as r
from diagnose_reflow115 import decisions

h=r.h
READY=h.ROOT/'reports/work/REFLOW-ADAPT-117/artifacts/ready02'
CONFIG=dict(r.CONFIG,originalGroupCount=207,derivedGroupCount=226,batch=207,initializer='DTM029')


def score(net,x):
    """Preserve historical424-example batching; score the nine additions separately."""
    h.require(len(x)==433,'evaluation_membership')
    torch=r.d.torch_runtime()
    return torch.cat([r.c.score_change(net,x[:424],CONFIG),r.c.score_change(net,x[424:],CONFIG)])


def inputs():
    p=h.read(r.PARENT);h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'parent')
    old=h.read(h.checked(h.ROOT,p['oldProtocol']))
    rows=r.d.admitted(h.read(h.checked(h.ROOT,old['corpus'])),h.read(h.checked(h.ROOT,old['admission'])))
    x=np.load(h.checked(h.ROOT,p['inputs']['evaluation'],256*1024**2),allow_pickle=False)
    h.require(x.shape==(424,6,128,192) and p['relatedSettingsIndices']==[24,25,26,27,28],'membership')
    endpoints={}
    for i in p['relatedSettingsIndices']:
        h.require(rows[i]['split']=='development','previous_role')
        for ref in rows[i]['evidence']:h.checked(h.ROOT,ref)
        for j,ref in enumerate(rows[i]['images']):
            h.checked(h.ROOT,ref);endpoints.setdefault(ref['sha256'],dict(image=ref,row=i,endpoint=j))
    h.require(len(endpoints)==9,'endpoint_membership')
    extra=[np.concatenate([x[v['row'],3*v['endpoint']:3*v['endpoint']+3]]*2) for v in endpoints.values()]
    y=np.array(p['oldLabels']+[True]*94+[False]*226,dtype=np.float32)
    return p,rows,np.concatenate([x,np.stack(extra)]),y,list(endpoints.values())


def pins():
    return [h.ref(__file__),h.ref(r.__file__),h.ref(r.d.__file__),h.ref(h.ROOT/'reports/work/REFLOW-ADAPT-117/admission.md')]


def prepare():
    out=h.fresh(READY);p,rows,x,y,endpoints=inputs()
    admission=dict(version='reflow117-role-v1',decision=h.ref(h.ROOT/'reports/work/REFLOW-ADAPT-117/admission.md'),
        sourceProtocol=h.ref(r.PARENT),rows=[dict(id=rows[i]['id'],index=i,images=rows[i]['images'],
        oldRole='development',newRole='train',changed=rows[i]['changed']) for i in p['relatedSettingsIndices']],
        identityEndpoints=endpoints,independentFinalEligible=False,geometryAdmission=False)
    out.mkdir(parents=True);h.write(out/'admission.json',admission,sealed=True)
    result=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/identity114-dtm029/result.json')
    doc=dict(version='reflow117-protocol-v1',configuration=CONFIG,pins=pins(),admission=h.ref(out/'admission.json'),
        initializer=result['model'],baseline=h.ref(h.ROOT/'NativeUITrainer/focus_ring_runs/identity114-dtm029/result.json'),
        tensorSHA256=hashlib.sha256(x.tobytes()).hexdigest(),experiment='DTM030')
    doc['protocolSHA256']=h.digest(doc);h.write(out/'protocol.json',doc);print(doc['protocolSHA256'])


def execute():
    start=time.monotonic();doc=h.read(READY/'protocol.json')
    h.require(doc['protocolSHA256']==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}) and doc['pins']==pins() and doc['configuration']==CONFIG,'protocol')
    h.require(doc['protocolSHA256'] in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    out=r.d.old.fresh_run('reflow117-dtm030')
    p,rows,x,y,endpoints=inputs();h.require(hashlib.sha256(x.tobytes()).hexdigest()==doc['tensorSHA256'],'tensor_changed')
    admission=h.read(h.checked(h.ROOT,doc['admission']))
    h.require(admission['seal']==h.digest({k:v for k,v in admission.items() if k!='seal'}) and admission['identityEndpoints']==endpoints,'admission')
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,p['initializer']),weights_only=True,map_location='cpu')
    base=r.d.model(state['configuration']);base.load_state_dict(state['state']);net=r.model(base)
    initial=torch.load(h.checked(h.ROOT,doc['initializer']),weights_only=True,map_location='cpu')
    h.require(initial['version']==r.VERSION,'initializer');net.load_state_dict(initial['state']);net.eval()
    tx=torch.from_numpy(x)
    with torch.no_grad():before=score(net,tx).numpy()
    prior=h.read(h.checked(h.ROOT,doc['baseline']))
    h.require(np.array_equal(before[:424],np.array(prior['after'],dtype=np.float32)),'initial_replay')
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.')}
    out.mkdir(parents=True);h.write(out/'execution.json',dict(pid=os.getpid(),status='started',protocolSHA256=doc['protocolSHA256']))
    fit=time.monotonic();net,history=r.d.fit_change_head(net,tx,torch.from_numpy(y),CONFIG);seconds=time.monotonic()-fit
    h.require(all(torch.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    torch.save(dict(version=r.VERSION,configuration=CONFIG,state=net.state_dict(),initializer=doc['initializer']),out/'last.pt')
    with torch.no_grad():after=score(net,tx).numpy()
    replay=r.model(base);replay.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state'])
    with torch.no_grad():again=score(replay,tx).numpy()
    h.require(np.array_equal(after,again) and np.array_equal(before[207:],after[207:]),'replay_or_identity')
    groups=dict(oldTrain=p['oldTrainIndices'],admittedSettings=p['relatedSettingsIndices'],region=list(range(113,207)),identical=list(range(207,433)))
    summary={}
    for name,ids in groups.items():
        a,b,t=decisions(before[ids]),decisions(after[ids]),y[ids].astype(int)
        summary[name]=dict(count=len(ids),beforeCorrect=int((a==t).sum()),afterCorrect=int((b==t).sum()),
            lostSuccesses=int(((a==t)&(b!=t)).sum()),abstentions=int((b==-1).sum()))
    passed=all(v['afterCorrect']==v['count'] for v in summary.values())
    h.write(out/'result.json',dict(experiment='DTM030',protocol=h.ref(READY/'protocol.json'),model=h.ref(out/'last.pt'),summary=summary,
        before=before.tolist(),after=after.tolist(),history=history,fitSeconds=seconds,totalSeconds=time.monotonic()-start,
        frozenUnchanged=True,identityPreserved=True,checkpointReplay=True,trainingFitGatePassed=passed,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_budget')
    h.write(out/'completion.json',dict(status='completed',exitCode=0,result=h.ref(out/'result.json')));print(summary)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','execute']);prepare() if p.parse_args().mode=='prepare' else execute()
