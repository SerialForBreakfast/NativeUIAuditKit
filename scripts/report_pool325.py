"""Report the matched pooling runs without selecting another fit."""
from pathlib import Path
import numpy as np
import pool325 as p


def main():
    b=p.b;t=p.t;t.set_num_threads(2);reg=b.read(p.OUT/'inputs.json')
    old=b.read(b.checked(reg['oldCorpus']));new=b.read(b.checked(reg['corpus']));rows=old['rows']+new['rows']
    initial=p.r.load_candidate(b.checked(reg['initializer']));models={'FOCUS319':p.make(initial,0.)}
    for name in ('average','mixed'):
        done=b.read(p.OUT/name/'completion.json');models[name]=p.load(b.checked(done['model']))
    baseline={k:v.clone() for k,v in models['FOCUS319'].state_dict().items()};results={}
    for name,net in models.items():
        data=np.load(b.checked(reg['cache']['mixed' if name=='mixed' else 'average']),allow_pickle=False)
        with t.inference_mode():
            pred=net.change(t.from_numpy(data['auxiliary'])).sigmoid().flatten().numpy()
            original=net.change(t.from_numpy(data['original'])).sigmoid().flatten().numpy()
        groups={}
        for key,ids in [('old',list(range(240))),('small',list(range(240,len(rows))))]:
            groups[key]=b.trainer.w.summary(pred[ids],data['auxiliaryLabels'][ids])
        for condition in ('movement','artwork-only','identical'):
            for size in (3,6,12):
                ids=[i for i,row in enumerate(rows) if row.get('sizePixels')==size and row['condition']==condition]
                groups[f'{condition}:{size}']=b.trainer.w.summary(pred[ids],data['auxiliaryLabels'][ids])
        changed=[k for k,v in net.state_dict().items() if not t.equal(v,baseline[k])]
        b.require(all(k.startswith(('change.detail.8.','change.correction.')) for k in changed),'unexpected_parameter_change')
        results[name]=dict(original=b.trainer.w.summary(original,data['labels']),auxiliary=groups,
            changedTensors=changed,frozenTensors=len(baseline)-len(changed),probabilities=pred.tolist())
    b.write(p.OUT/'training-comparison.json',dict(source=b.ref(Path(__file__)),inputs=b.ref(p.OUT/'inputs.json'),models=results,
        trainingOnly=True,independentGroups=3,limitation='The 432 new scheduled pairs include reversals and repeated identical pairs. They are not 432 independent trials.'))
    print({k:{x:y for x,y in v.items() if x!='probabilities'} for k,v in results.items()})


if __name__=='__main__':main()
