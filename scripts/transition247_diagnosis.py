"""Combine cached model errors and sampling support without another fit."""
from collections import Counter
import numpy as np
import transition247 as batch

t=batch.t


def support(rows):
    selected=[r for r in rows if r['role']=='train']
    groups=Counter(r['group'] for r in selected)
    return dict(rows=len(selected),groups=len(groups),largestGroups=groups.most_common(5),
                effectiveGroups=len(selected)**2/sum(n*n for n in groups.values()),
                warning='This describes row concentration, not statistical independence.',
                conditions={c:dict(Counter(str(r['changed']) for r in selected if c in r['conditions']))
                            for c in sorted({c for r in selected for c in r['conditions']})})


def errors(rows,probabilities):
    labels=np.array([r['changed'] for r in rows]);p=np.asarray(probabilities)
    t.p.review.require(p.shape==labels.shape and np.isfinite(p).all(),'score_membership')
    loss=-(labels*np.log(np.clip(p,1e-7,1-1e-7))+(1-labels)*np.log(np.clip(1-p,1e-7,1-1e-7)))
    out={}
    for condition in sorted({c for r in rows for c in r['conditions']}):
        ids=[i for i,r in enumerate(rows) if condition in r['conditions']]
        selected=[rows[i] for i in ids]
        out[condition]=dict(summary=t.n.w.summary(p[ids],labels[ids]),meanLogLoss=float(loss[ids].mean()),
            groups=len({r['group'] for r in selected}),roles=dict(Counter(r['role'] for r in selected)),
            cases=[rows[i]['id'] for i in ids if t.p.decisions(p[i:i+1])[0]!=labels[i]][:10])
    return out


def run():
    out=batch.OUT;protocol=t.sealed(out/'protocol.json');rows=protocol['rows']
    cached={}
    for model,packet in [('DTM063',245),('DTM064',245),('DTM065',246)]:
        path=t.h.ROOT/f'reports/work/TRANSITION-{packet}/artifacts/{model}/result.json'
        result=t.sealed(path)
        membership=t.sealed(path.parent.parent/'membership.json')['rows']
        t.p.review.require(membership==rows,'cached_membership_changed')
        cached[model]=dict(source=t.h.ref(path),conditions=errors(rows,result['probabilities']))
        if model=='DTM063':cached['DTM054']=dict(source=t.h.ref(path),conditions=errors(rows,result['initializerProbabilities']))
    report=dict(trainingSupport=support(rows),cachedModels=cached,
        pixelBaseline=t.h.ref(t.diagnostic.OUT/'result.json'),
        decisions=[
            'Do not repeat full adaptation with unchanged sampling.',
            'Absolute frame differences already enter the current model. Their addition is not a new hypothesis.',
            'The fixed spatial probe preserves forced distraction decisions but still confuses artwork.',
            'The frozen DTM054 probe separates more artwork examples, but loses distraction decisions.',
            'No representation wins across conditions. These probes do not prove a fundamental feature limit.',
            'Next compare group-balanced training with matched row-balanced training on one fixed representation.',
            'Use a training-only group split for selection. Do not reuse inspected reserved cases as untouched final evidence.'
        ],productionEligible=False)
    t.h.write(out/'diagnosis.json',report,sealed=True)
    print(report['trainingSupport'])


if __name__=='__main__':run()
