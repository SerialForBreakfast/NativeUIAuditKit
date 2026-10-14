"""Bound development scores after the fixed feature candidate completes."""
from pathlib import Path
import numpy as np
import features324 as f
import reachability323 as reach


def run():
    b=f.b;t=f.t;t.set_num_threads(2)
    done=b.read(f.OUT/'completion.json');b.checked(done['report'])
    net=f.load(b.checked(done['model']));audit=b.read(f.OUT/'audit.json')
    data=np.load(b.checked(audit['cache']),allow_pickle=False)
    tiny,rows,pin=f.r.s.tiny_rows();details,_=f.r.prepare(tiny,rows,2)
    images=t.from_numpy(np.concatenate((tiny,details),1))
    with t.inference_mode():
        features,scores=f.retained(net.change.base,images)
        logits=net.change(images).flatten().numpy()
    query=(features.numpy()-data['center'])/data['scale']
    train=(data['features']-data['center'])/data['scale']
    ids=[i for i,row in enumerate(rows) if row['condition'] in ('forward','reverse')]
    maxima=reach.upper_scores(data['scores'],data['labels'],np.column_stack((train,np.ones(len(train)))),
        scores.numpy()[ids],np.column_stack((query[ids],np.ones(len(ids)))))
    result=[]
    positives=train[data['labels']==1];negatives=train[data['labels']==0]
    for i,maximum in zip(ids,maxima):
        result.append(dict(index=i,condition=rows[i]['condition'],currentLogit=float(logits[i]),
            maximumFeasibleLogit=maximum,canReachChange=maximum>=f.m.H,
            nearestPositiveDistance=float(np.linalg.norm(positives-query[i],axis=1).min()),
            nearestNegativeDistance=float(np.linalg.norm(negatives-query[i],axis=1).min())))
    b.write(f.OUT/'feature-diagnosis.json',dict(source=b.ref(Path(__file__)),solver=b.ref(Path(reach.__file__)),
        candidate=done['model'],cache=audit['cache'],input=pin,threshold=f.m.H,rows=result,
        interpretation='Each upper bound uses different coefficients. It does not show that one model can fix all cases.',
        use='Post-evaluation diagnosis only. No weights saved, threshold changes, second fit, or data-role changes.',
        distanceMeaning='Euclidean distance in training-standardized features. Not a calibrated confidence or proof of label ambiguity.'))
    print(result,flush=True)


if __name__=='__main__':run()
