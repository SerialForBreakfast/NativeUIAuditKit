"""Check whether fixed nonlinear features allow a protected training improvement."""
from pathlib import Path
import numpy as np
from scipy import sparse
import nonlinear322 as n

m=n.m;b=n.b;t=n.t


def fixed_feature_bound(scores,labels,weights,features):
    z=m.design(scores,labels);baseline=z@np.array([1.,1.,0.]);_,floor,keep=m.protected(z)
    b.require(features.ndim==2 and len(features)==len(labels) and np.isfinite(features).all(),'feature_inputs')
    b.require(weights.shape==labels.shape and np.isfinite(weights).all() and (weights>0).all(),'feature_weights')
    signed=features*(2*labels-1)[:,None];rows=len(labels);width=features.shape[1]
    A=sparse.vstack([sparse.hstack([-signed,-sparse.eye(rows)]),
        sparse.hstack([-signed[keep],sparse.csr_matrix((int(keep.sum()),rows))])]).tocsr()
    q=m.solve(np.r_[np.zeros(width),weights],A,np.r_[baseline-(m.H+.25),baseline[keep]-floor],
        [(-1.,1.)]*width+[(0,None)]*rows)
    b.require(q.success,'feature_bound_failure')
    return dict(baselineHinge=float(weights@np.maximum(0,m.H+.25-baseline)),minimumHinge=float(q.fun),
                coefficientBound=1.,minimumProtectedSlack=float((baseline[keep]+signed[keep]@q.x[:width]-floor).min()) if keep.any() else None,
                diagnosticCoefficients=q.x[:width].tolist(),isTrainedModel=False,evaluationUsed=False)


def run():
    reg,d=m.inputs();saved=b.read(m.OUT/'nonlinear/registration.json');b.checked(saved['runner'])
    b.checked(saved['trainer']);t.set_num_threads(2);t.manual_seed(42)
    net=n.make(n.r.load_candidate(b.checked(reg['model'])),saved['center'],saved['scale'])
    scores=np.concatenate((d['original'],d['authored']));labels=np.r_[d['labels'],d['authoredLabels']]
    counts=np.bincount(d['auxiliaryIndices'],weights=d['weights'],minlength=len(d['authored']))
    b.require((counts>0).all(),'unscheduled_authored')
    weights=np.r_[d['weights'],.25*counts]/len(d['original'])
    with t.inference_mode():
        layer=net.change.fusion
        features=layer.layers[:2]((t.from_numpy(scores)-layer.center)/layer.scale).numpy()
    features=np.column_stack((features,np.ones(len(scores))))
    result=fixed_feature_bound(scores,labels,weights,features)
    unique,ids=np.unique(scores,axis=0,return_inverse=True)
    result.update(exactConflictingScoreGroups=sum(len(np.unique(labels[ids==i]))>1 for i in range(len(unique))),
        original=b.ref(m.OUT/'separation.json'),candidateRegistration=b.ref(m.OUT/'nonlinear/registration.json'),
        source=b.ref(Path(__file__)),featureSHA256=b.sha(features.tobytes()),
        interpretation='Training-only feasibility check. No checkpoint, evaluation selection, or second fit.')
    b.write(m.OUT/'guard-diagnosis.json',result);print(result)


if __name__=='__main__':run()
