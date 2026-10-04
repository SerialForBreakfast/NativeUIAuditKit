"""Frozen before/after nuisance stress; no new labels or admission."""
import argparse
import hashlib
from pathlib import Path
import time
import numpy as np
import content127 as c
a=c.a;h=c.h;q=c.q


def intensity(x,mask,gain,offset,endpoint):
    h.require(endpoint in (0,1),'endpoint')
    changed=c.intervene(x,mask,gain,offset)
    changed[:,3*(1-endpoint):3*(1-endpoint)+3]=x[:,3*(1-endpoint):3*(1-endpoint)+3]
    return changed


def shift(x,mask,dx,both):
    h.require(type(dx)is int and abs(dx)==2 and mask.shape==x.shape and mask.dtype==bool,'shift_contract')
    out=x.copy()
    for index in range(len(x)):
        for endpoint in ((0,1) if both else (1,)):
            ch=slice(3*endpoint,3*endpoint+3);m=mask[index,3*endpoint]
            ys,xs=np.where(m);h.require(len(xs)>0,'empty_content')
            left,right=int(xs.min()),int(xs.max())+1;top,bottom=int(ys.min()),int(ys.max())+1
            h.require(m[top:bottom,left:right].all() and right-left>abs(dx),'content_rectangle')
            out[index,ch,top:bottom,left:right]=0
            if dx>0:out[index,ch,top:bottom,left+dx:right]=x[index,ch,top:bottom,left:right-dx]
            else:out[index,ch,top:bottom,left:right+dx]=x[index,ch,top:bottom,left-dx:right]
    return out


def run(output):
    out=h.fresh(output);start=time.monotonic();x,y,mask,net,ref,groups,parent=c.setup()
    torch=a.r.d.torch_runtime()
    candidate_path=h.ROOT/'NativeUITrainer/focus_ring_runs/content127-dtm031/result.json'
    candidate=h.read(candidate_path)
    h.require(candidate['seal']==h.digest({k:v for k,v in candidate.items() if k!='seal'}),'candidate_seal')
    old_state={k:v.clone() for k,v in net.state_dict().items()}
    new_state=torch.load(h.checked(h.ROOT,candidate['model']),weights_only=True,map_location='cpu')['state']
    configs=[(name+'_'+str(ep),dict(kind='intensity',gain=g,offset=b,endpoint=ep))
        for name,(g,b) in q.TRANSFORMS.items() for ep in (0,1)]
    configs += [('shift_'+str(dx)+'_'+str(both),dict(kind='shift',dx=dx,both=both))
        for dx in (-2,2) for both in (True,False)]
    results={};reference={};input_sha=hashlib.sha256(x.tobytes()).hexdigest()
    with torch.no_grad():
        for name,state,expected in [('DTM030',old_state,ref),('DTM031',new_state,np.asarray(candidate['reports']['original']['probabilities'],dtype=np.float32))]:
            net.load_state_dict(state);p=a.score(net,torch.from_numpy(x)).numpy()
            h.require(np.array_equal(p,expected),'baseline_replay');reference[name]=p
        for label,config in configs:
            v=intensity(x,mask,config['gain'],config['offset'],config['endpoint']) if config['kind']=='intensity' else shift(x,mask,config['dx'],config['both'])
            h.require(np.array_equal(x[~mask],v[~mask]),'padding_changed')
            record=dict(configuration=config,tensorSHA256=hashlib.sha256(v.tobytes()).hexdigest(),models={})
            for name,state in [('DTM030',old_state),('DTM031',new_state)]:
                net.load_state_dict(state);p=a.score(net,torch.from_numpy(v)).numpy()
                record['models'][name]=dict(summary=q.summarize(p,y,groups,reference[name]),probabilities=p.tolist())
            results[label]=record
    h.require(hashlib.sha256(x.tobytes()).hexdigest()==input_sha,'input_changed')
    unique_identities=len({hashlib.sha256(v[:3].tobytes()).hexdigest() for v in x[207:]})
    doc=dict(version=1,source=h.ref(__file__),setupSource=h.ref(c.__file__),modelReferences=dict(DTM030=parent['model'],DTM031=candidate['model']),
        sourceProtocol=h.ref(a.READY/'protocol.json'),tensorSHA256=input_sha,maskSHA256=hashlib.sha256(mask.tobytes()).hexdigest(),
        originalPairs=207,identityPairs=226,distinctEncodedIdentityFrames=unique_identities,groups=groups,conditions=results,
        elapsedSeconds=time.monotonic()-start,training=False,admission=False,independentEvaluation=False,
        limitation='Encoded nuisance interventions; shifted content can clip. Label agreement is not independently reviewed transformed truth.')
    out.mkdir(parents=True);h.write(out/'report.json',doc,sealed=True)
    print({label:{name:dict(original=sum(row['summary'][g]['correct'] for g in ('oldTrain','admittedSettings','region')),
        identity=row['summary']['identical']['correct']) for name,row in r['models'].items()} for label,r in results.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
