"""Report matched detail-filter results without another inference run."""
from collections import Counter
import numpy as np
import filters327 as f


def main():
    b=f.b;out=f.OUT;reg=b.read(out/'inputs.json')
    b.checked(reg['control']);b.checked(reg['cache'])
    rows=b.read(b.checked(reg['corpus']))['rows']['independent']
    labels=np.array([v['changed'] for v in rows],np.float32)
    old=b.read(f.e.OUT/'independent/run/training.json')
    new=b.read(out/'run/training.json')
    scores={'initial':np.array(new['initialProbabilities'][240:]),
            'fixed_filters':np.array(old['probabilities'][240:]),
            'learned_filters':np.array(new['probabilities'][240:])}
    cells={}
    for name,prob in scores.items():
        b.require(prob.shape==labels.shape,'score_membership')
        result={}
        for size in (3,6):
            for width in (1,3):
                for contrast in (.25,.75):
                    for condition in ('movement','artwork-only','identical'):
                        ids=[i for i,v in enumerate(rows) if (v['sizePixels'],v['widthPixels'],v['contrast'],v['condition'])==(size,width,contrast,condition)]
                        result[str((size,width,contrast,condition))]=b.trainer.w.summary(prob[ids],labels[ids])
        cells[name]=dict(summary=b.trainer.w.summary(prob,labels),cells=result)
    comparison=b.read(out/'report.json');native={}
    membership=b.read(b.PACKAGE/'membership.json')['rows']
    reference=b.read(f.e.OUT/'independent/run/evaluation.json')
    candidate=b.read(out/'run/evaluation.json')
    for role in sorted({v['role'] for v in membership}):
        ids=[i for i,v in enumerate(membership) if v['role']==role]
        y=np.array([membership[i]['changed'] for i in ids])
        native[role]=dict(rows=len(ids),groups=len({membership[i]['group'] for i in ids}))
        for name,doc in [('control',reference),('candidate',candidate)]:
            prob=np.array(doc['conditions']['native.npy']['probabilities'])
            native[role][name]=b.trainer.w.summary(prob[ids],y)
    changes=comparison['comparisons']['FOCUS326-independent']['cases']
    losses=Counter(v['group'] for v in changes if v.get('lostCorrect') and v['input']=='native.npy')
    gains=Counter(v['group'] for v in changes if v.get('gainedCorrect') and v['input']=='native.npy')
    b.write(out/'comparison.json',dict(inputs=b.ref(out/'inputs.json'),training=cells,nativeRoles=native,
        nativeLostGroups=dict(losses),nativeGainedGroups=dict(gains),comparisons=comparison['comparisons'],
        limitation='Retained development checks and training cells. No independent deployment accuracy.',productionEligible=False))
    print('Authored training:',{k:v['summary'] for k,v in cells.items()})
    print('Native group losses:',dict(losses),'gains:',dict(gains))
    print('Retained control:',comparison['comparisons']['FOCUS326-independent']['summary'])


if __name__=='__main__':main()
