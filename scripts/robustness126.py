"""Frozen input-sensitivity and residual attribution, not independent evaluation."""
import argparse
import hashlib
import time
from pathlib import Path
import numpy as np
import adapt_reflow117 as a
from diagnose_reflow115 import decisions
h=a.h
TRANSFORMS={'dim':(.8,0.),'contrast':(.8,.1),'bright':(.8,.2)}


def transform(x,gain,offset):
    h.require(np.isfinite(x).all() and x.min()>=0 and x.max()<=1 and
              0<gain<=1 and 0<=offset<=1-gain+1e-7,'transform_range')
    return x*np.float32(gain)+np.float32(offset)


def summarize(p,y,groups,reference):
    d=decisions(p); rd=decisions(reference); result={}
    for name,ids in groups.items():
        labels=y[ids].astype(int)
        result[name]=dict(count=len(ids),correct=int((d[ids]==labels).sum()),
            abstentions=int((d[ids]==-1).sum()),
            confidentWrong=int(((d[ids]!=labels)&(d[ids]!=-1)).sum()),
            decisionChanges=int((d[ids]!=rd[ids]).sum()),
            lostCorrect=int(((rd[ids]==labels)&(d[ids]!=labels)).sum()),
            failureIndices=[i for i in ids if d[i]!=int(y[i])])
    return result


def run(output):
    start=time.monotonic(); out=h.fresh(output)
    parent,rows,x,y,_=a.inputs(); original=hashlib.sha256(x.tobytes()).hexdigest()
    result_path=h.ROOT/'NativeUITrainer/focus_ring_runs/reflow117-dtm030/result.json'
    result=h.read(result_path)
    h.require(result['seal']==h.digest({k:v for k,v in result.items() if k!='seal'}),'seal')
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    base_state=torch.load(h.checked(h.ROOT,parent['initializer']),weights_only=True,map_location='cpu')
    base=a.r.d.model(base_state['configuration']);base.load_state_dict(base_state['state']);base.eval()
    state=torch.load(h.checked(h.ROOT,result['model']),weights_only=True,map_location='cpu')
    net=a.r.model(base);net.load_state_dict(state['state']);net.eval()
    groups=dict(oldTrain=parent['oldTrainIndices'],admittedSettings=parent['relatedSettingsIndices'],
                region=list(range(113,207)),identical=list(range(207,433)))
    h.require(sorted(i for ids in groups.values() for i in ids)==list(range(433)),'group_accounting')
    with torch.no_grad():
        ref=a.score(net,torch.from_numpy(x)).numpy()
        h.require(np.array_equal(ref,np.array(result['after'],dtype=np.float32)),'baseline_replay')
        z=net.change_inputs(torch.from_numpy(x))
        correction=net.change.linear(z[:,1:]).flatten()
        h.require(torch.equal(correction[207:],torch.zeros_like(correction[207:])),'identity_residual')
        base_prob=z[:,0].sigmoid().numpy()
        interventions={}
        for name,(gain,offset) in TRANSFORMS.items():
            v=transform(x,gain,offset);features=net.change_inputs(torch.from_numpy(v))
            bp=features[:,0].sigmoid().numpy();cp=net.change(features).sigmoid().flatten().numpy()
            interventions[name]=dict(gain=gain,offset=offset,tensorSHA256=hashlib.sha256(v.tobytes()).hexdigest(),
                base=summarize(bp,y,groups,base_prob),candidate=summarize(cp,y,groups,ref),
                baseProbabilities=bp.tolist(),candidateProbabilities=cp.tolist())
        sweep={}
        for alpha in (0.,.25,.5,.75,1.):
            p=(z[:,0]+alpha*correction).sigmoid().numpy()
            sweep[str(alpha)]=dict(summary=summarize(p,y,groups,ref),probabilities=p.tolist())
    h.require(hashlib.sha256(x.tobytes()).hexdigest()==original,'input_mutated')
    logits=(z[:,0]+correction).numpy();signed=(2*y-1)*logits
    doc=dict(version='robustness126-v1',implementation=h.ref(__file__),sourceResult=h.ref(result_path),
        sourceProtocol=h.ref(a.READY/'protocol.json'),model=result['model'],baseModel=parent['initializer'],
        tensorSHA256=original,groups=groups,baseline=summarize(ref,y,groups,ref),
        interventions=interventions,residualMultipliers=sweep,baseLogits=z[:,0].tolist(),
        correctionLogits=correction.tolist(),signedMargins=signed.tolist(),
        saturatedLogits=int((np.abs(logits)>20).sum()),identityResidualExactlyZero=True,
        training=False,independentEvaluation=False,paddingTransformed=True,
        elapsedSeconds=time.monotonic()-start)
    out.mkdir(parents=True);h.write(out/'report.json',doc,sealed=True)
    print({name:{g:(v['correct'],v['count']) for g,v in row['candidate'].items()} for name,row in interventions.items()})
    print('residual', {alpha:{g:v['correct'] for g,v in row['summary'].items()} for alpha,row in sweep.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
