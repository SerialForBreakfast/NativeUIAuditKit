"""Test movement emphasis with fixed appearance data and retained comparisons."""
from pathlib import Path
import time
import numpy as np
import appearance348 as m

q=m.q;t=m.t;a=m.a;OUT=None
BASE=q.ROOT/'reports/work/FOCUS-349'


def class_weights(labels,weights):
    q.require(set(np.unique(labels))=={0.,1.},'class_support')
    factors=np.array([1.,2.],np.float32)
    factors*=weights.sum()/np.sum(weights*factors[labels.astype(int)])
    return factors


def training():
    start=time.monotonic();config=q.load(OUT/'config.json');m.check_inputs(config);t.set_num_threads(2)
    m.OUT=OUT;a.e.f.OUT=OUT
    reg=q.load(a.e.OUT/'inputs.json');reg['trainer']=a.b.ref(Path(a.b.trainer.__file__))
    m.emit('Verify original views and labels',0,10)
    x,d,y,w,aux,ad,ay,indices=a.e.f.prepare(reg)
    rows=q.load(OUT/'preparation.json')['rows']
    q.require(all(r['role']=='train' for r in rows),'training_role')
    net=a.e.load_candidate(a.e.OUT/'run/last.pt')
    original=m.raw_logits(net,x,d);aux_original=m.raw_logits(net,aux,ad)
    changed=0
    for i in range(0,len(rows),8):
        v,n=m.f.source_views(rows[i:i+8],'08-gamma');changed+=n
        aux[i:i+len(v)]=v[:,:6].numpy();ad[i:i+len(v)]=v[:,6:].numpy()
        m.emit('Prepare matched gamma views',i+len(v),len(rows))
    factors=class_weights(y,w)
    q.save(OUT/'augmentation.json',dict(gamma=1.5,changedProposalPairs=changed,
        auxiliarySHA256=a.e.f.digest(aux),detailSHA256=a.e.f.digest(ad),classWeights=factors.tolist(),
        originalWeightSum=float(w.sum()),effectiveAuxiliaryWeightSum=float((w*factors[y.astype(int)]).sum()),rolesChanged=False))
    previous=q.load(q.QUEUE/'jobs/focus348-00-gamma/attempts/1/out/augmentation.json')
    q.require(previous['auxiliarySHA256']==a.e.f.digest(aux) and previous['detailSHA256']==a.e.f.digest(ad),'augmentation_changed')
    initial={k:v.clone() for k,v in net.state_dict().items()}
    settings=dict(reg['configuration'],epochs=10,seed=42,threads=2)
    def progress(row):
        q.save(OUT/f"epoch-{row['epoch']:04d}.json",row);m.emit('Train movement emphasis',row['epoch'],10)
    net,history=a.b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),settings,progress,
        weights=t.from_numpy(w),detail_inputs=t.from_numpy(d),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_indices=t.from_numpy(indices),auxiliary_weight=.25,
        preservation_logits=original,auxiliary_preservation_logits=aux_original,preservation_weight=1.,
        auxiliary_class_weights=t.from_numpy(factors))
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,initial[k])]
    q.require(changed and all(k.startswith(('change.detail.','change.correction.')) for k in changed),'changed_scope')
    t.save(dict(state=net.state_dict(),representation=a.e.VERSION,windows=2),OUT/'last.pt')
    restored=a.e.load_candidate(OUT/'last.pt');sample=np.concatenate((x[:8],d[:8]),1)
    q.require(np.array_equal(a.b.worker.score(net,sample),a.b.worker.score(restored,sample)),'reload_parity')
    q.save(OUT/'fit.json',dict(configuration=settings,history=history,classWeights=factors.tolist(),
        changedTensors=changed,seconds=time.monotonic()-start,checkpointParity=True,model=m.f.pin(OUT/'last.pt'),productionEligible=False))
    m.emit('Training complete; comparisons required',10,10)


def register(train=False):
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS349';folder.mkdir(exist_ok=True)
    oldfolder=q.ROOT/'Research/ResearchSpecs/FOCUS348'
    sources=[oldfolder/'focus348-00-gamma.json'] if train else sorted(p for p in oldfolder.glob('focus348-*.json') if '-config' not in p.name and '-00-' not in p.name)
    for source in sources:
        spec=q.load(source);config=q.load(q.ROOT/spec['stage'][0]['from']['path'])
        ident=spec['id'].replace('focus348','focus349');spec.update(id=ident,task='FOCUS349',
            hypothesis='Movement emphasis retains gamma stability gains without losing movement decisions.',
            decisionRule='Compare fixed FOCUS348 gamma and FOCUS329. Require target gains and no lost previous successes.')
        if train:
            spec['adapter']=dict(type='python-callable',steps=['movement349.training'],outputAttributes=['movement349.OUT'])
            spec['training']['experimentLogRunId']='FOCUS349'
        else:
            candidate=q.QUEUE/'jobs/focus349-00-gamma/attempts/1/out/last.pt'
            q.require(q.load(candidate.parent.parent/'result.json')['status']=='complete','incomplete_training')
            config['models']={'control':m.f.pin(q.QUEUE/'jobs/focus348-00-gamma/attempts/1/out/last.pt'),'gamma':m.f.pin(candidate)}
            config['modelNames']={'control':'FOCUS348 gamma','gamma':'FOCUS349 movement emphasis'}
        refs={v['path']:m.f.pin(q.ROOT/v['path']) for v in config['inputs']}
        refs['scripts/movement349.py']=m.f.pin(Path(__file__))
        if not train:
            for v in config['models'].values():refs[v['path']]=v
        config['inputs']=list(refs.values());spec['inputs']=config['inputs']
        cp=folder/(ident+'-config.json');q.save(cp,config);spec['stage']=[{'from':m.f.pin(cp),'to':'config.json'}]
        path=folder/(ident+'.json');q.save(path,spec);print(ident,q.submit(path),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register-training','register-evaluation'])
    register(p.parse_args().action=='register-training')
