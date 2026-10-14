"""Bound tiny-case scores without training or selecting another candidate."""
from pathlib import Path
import numpy as np
import constrained323 as c

b=c.b;t=c.t;m=c.m;n=c.n


def upper_scores(scores,labels,features,query_scores,query_features):
    z=m.design(scores,labels);base=z@np.array([1.,1.,0.]);_,floor,keep=m.protected(z)
    b.require(features.ndim==2 and features.shape[0]==len(scores) and np.isfinite(features).all(),'bound_features')
    b.require(query_scores.ndim==2 and query_scores.shape[1]==2 and np.isfinite(query_scores).all(),'bound_queries')
    b.require(query_features.shape==(len(query_scores),features.shape[1]) and np.isfinite(query_features).all(),'bound_query_features')
    signed=features*(2*labels-1)[:,None];result=[]
    for s,phi in zip(query_scores,query_features):
        solved=m.solve(-phi,-signed[keep],base[keep]-floor,[(-1,1)]*features.shape[1])
        b.require(solved.success,'bound_solver')
        result.append(float(s.sum()-solved.fun))
    return result


def run():
    # This diagnostic runs only after the fixed candidate completes evaluation.
    completion=b.read(c.OUT/'completion.json');b.checked(completion['model']);b.checked(completion['report'])
    reg,d=m.inputs();net=n.load(b.checked(completion['model']));t.set_num_threads(2)
    scores=np.concatenate((d['original'],d['authored']));labels=np.r_[d['labels'],d['authoredLabels']]
    old=b.read(n.f.a.OUT/'report.json');rows=[v for v in old['tinyLogits'] if v['condition'] in ('forward','reverse')]
    query=np.asarray([[v['whole'],v['correction']] for v in rows],np.float32)
    def features(values):
        with t.inference_mode():
            layer=net.change.fusion
            hidden=layer.layers[:2]((t.from_numpy(values)-layer.center)/layer.scale).numpy()
        return np.column_stack((hidden,np.ones(len(values))))
    train_features=features(scores)
    b.require(b.sha(train_features.tobytes())==b.read(c.OUT/'run/registration.json')['featureSHA256'],'bound_feature_hash')
    maxima=upper_scores(scores,labels,train_features,query,features(query))
    result=dict(source=b.ref(Path(__file__)),candidate=b.ref(c.OUT/'run/last.pt'),
        developmentReport=b.ref(n.f.a.OUT/'report.json'),training=b.ref(n.f.OUT/'registration.json'),
        threshold=m.H,coefficientBounds=[-1,1],rolesChanged=False,
        rows=[dict(index=row['index'],condition=row['condition'],baselineLogit=float(s.sum()),
                   maximumFeasibleLogit=maximum,canReachChange=maximum>=m.H)
              for row,s,maximum in zip(rows,query,maxima)],
        limitation='Development-only upper bounds, optimized separately per case. No single model or general architecture claim.',
        use='Diagnosis after evaluation only. No coefficients saved, new checkpoint, threshold choice, or second fit.')
    b.write(c.OUT/'reachability.json',result);print(result)


if __name__=='__main__':run()
