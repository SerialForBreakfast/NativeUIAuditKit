"""Frozen residual attribution, training-support and order-consistency audit."""
import argparse
from pathlib import Path
import time
import numpy as np
import focus_identity_residual as r

h=r.h


def decisions(p):
    p=np.asarray(p)
    h.require(np.isfinite(p).all() and ((p>=0)&(p<=1)).all(),'probability')
    return np.where(p<=.15,0,np.where(p>=.85,1,-1))


def nearest(v,features,indices,count=5):
    """Cosine support only; distances do not establish labels or independence."""
    v=np.asarray(v);features=np.asarray(features)
    h.require(v.ndim==1 and features.ndim==2 and features.shape[1]==len(v) and
              np.isfinite(v).all() and np.isfinite(features).all(),'features')
    scores=[];vn=float(np.linalg.norm(v))
    for i in indices:
        norm=float(np.linalg.norm(features[i]))
        if vn>1e-12 and norm>1e-12:scores.append((int(i),float(features[i]@v/(norm*vn))))
    return [dict(index=i,cosine=s) for i,s in sorted(scores,key=lambda p:(-p[1],p[0]))[:count]]


def contribution_grid(features,weights):
    h.require(features.shape[-1]==weights.shape[-1]==576,'grid_shape')
    return (features*weights).reshape(-1,24,4,6).sum(axis=1)


def run(output):
    start=time.monotonic();out=h.fresh(output)
    parent=h.read(r.PARENT)
    h.require(parent['protocolSHA256']==h.digest({k:v for k,v in parent.items() if k!='protocolSHA256'}),'protocol')
    result_path=h.ROOT/'NativeUITrainer/focus_ring_runs/identity114-dtm029/result.json'
    result=h.read(result_path)
    h.require(result['seal']==h.digest({k:v for k,v in result.items() if k!='seal'}),'result')
    p=h.read(h.checked(h.ROOT,parent['oldProtocol']))
    rows=r.d.admitted(h.read(h.checked(h.ROOT,p['corpus'])),h.read(h.checked(h.ROOT,p['admission'])))
    x=np.load(h.checked(h.ROOT,parent['inputs']['evaluation'],256*1024**2),allow_pickle=False)
    h.require(x.shape==(424,6,128,192) and len(rows)==113,'membership')
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,parent['initializer']),weights_only=True,map_location='cpu')
    base=r.d.model(state['configuration']);base.load_state_dict(state['state']);base.eval()
    candidate=torch.load(h.checked(h.ROOT,result['model']),weights_only=True,map_location='cpu')
    h.require(candidate['version']==r.VERSION and candidate['configuration']==r.CONFIG,'model_version')
    net=r.model(base);net.load_state_dict(candidate['state']);net.eval();tx=torch.from_numpy(x)
    with torch.no_grad():
        z=net.change_inputs(tx);prob=net.change(z).sigmoid().flatten().numpy()
        rev=net.change(net.change_inputs(torch.cat([tx[:,3:],tx[:,:3]],1))).sigmoid().flatten().numpy()
    h.require(np.array_equal(prob,np.asarray(result['after'],dtype=np.float32)),'replay')
    f=z[:,1:].numpy();w=net.change.linear.weight.detach().numpy()[0]
    grids=contribution_grid(f,w);correction=f@w
    h.require(np.allclose(grids.sum((1,2)),correction,atol=1e-4,rtol=1e-5),'contribution_sum')
    negatives=[i for i in parent['oldTrainIndices'] if not rows[i]['changed']]
    positives=[i for i in parent['oldTrainIndices'] if rows[i]['changed']]+list(range(113,207))
    difference=np.abs(x[:,3:]-x[:,:3]).mean((1,2,3))
    negative_records=[dict(index=i,id=rows[i]['id'],sourceGroup=rows[i]['group'],role=rows[i]['split'],
        images=rows[i]['images'],meanPixelDifference=float(difference[i]),baseLogit=float(z[i,0]),
        correction=float(correction[i]),probability=float(prob[i])) for i in negatives]
    h.require(len(negatives)+len(positives)==202,'original_accounting')
    # Source inspection is separate from numerical features; verify exact reviewed bytes.
    for ref in rows[25]['images']:h.checked(h.ROOT,ref)
    focus_cases={}
    for i in [25,26,28,161,162]:
        focus_cases[str(i)]=dict(meanPixelDifference=float(difference[i]),baseLogit=float(z[i,0]),
            correction=float(correction[i]),probability=float(prob[i]),grid=grids[i].tolist(),
            featureNorm=float(np.linalg.norm(f[i])),
            closestTrainingNegative=nearest(f[i],f,[j for j in negatives if j!=i]),
            closestTrainingPositive=nearest(f[i],f,[j for j in positives if j!=i]))
    groups=dict(oldTrain=parent['oldTrainIndices'],relatedSettings=parent['relatedSettingsIndices'],
                region=list(range(113,207)),identical=list(range(207,424)))
    order={name:dict(count=len(ids),categoricalDisagreements=int((decisions(prob[ids])!=decisions(rev[ids])).sum()),
        maximumProbabilityDifference=float(np.abs(prob[ids]-rev[ids]).max())) for name,ids in groups.items()}
    doc=dict(version='reflow115-audit-v1',inputs=parent['inputs']['evaluation'],sourceProtocol=h.ref(r.PARENT),
        candidate=result['model'],implementation=h.ref(__file__),parentResult=h.ref(result_path),
        negativeCount=len(negatives),positiveCount=len(positives),trainingNegatives=negative_records,
        cases=focus_cases,orderConsistency=order,
        reversedProbabilities=rev.tolist(),allCorrections=correction.tolist(),
        failedPairImages=rows[25]['images'],
        visualReview='Same VoiceOver row remains focused; On becomes Off, help row disappears and lower rows reflow. Legacy retained capture, not a new Settings operation.',
        limitation='Coarse pooled feature contributions and cosine support are not causal or independent-quality evidence.',
        elapsedSeconds=time.monotonic()-start,training=False,dataRolesChanged=False)
    out.mkdir(parents=True);h.write(out/'report.json',doc,sealed=True)
    print({k:doc[k] for k in ('negativeCount','positiveCount','orderConsistency','elapsedSeconds')})
    print('failed_pair',focus_cases['25'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
