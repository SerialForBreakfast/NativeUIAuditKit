"""Measure decision margins and fit a frozen-branch score combination."""
import argparse
import gc
import math
from pathlib import Path
import time
import numpy as np
import authored319 as a
import conflict320 as diagnostic

b=a.b;r=a.r;t=a.t
OUT=b.ROOT/'reports/work/FOCUS-321'
VERSION='fusion321-v1'


def branch_scores(net,values,details):
    result=[]
    with t.inference_mode():
        for start in range(0,len(values),8):
            v=t.from_numpy(values[start:start+8]);d=t.from_numpy(details[start:start+8])
            whole=net.change.whole(r.s.c.model.change_inputs(None,v)).flatten()
            total=net.change(t.cat((v,d),1)).flatten()
            result.append(t.stack((whole,total-whole),1).numpy())
    return np.concatenate(result)


def margins(scores,labels):
    scores=np.asarray(scores);labels=np.asarray(labels)
    b.require(scores.shape==(len(labels),2) and len(labels)>0 and np.isfinite(scores).all()
              and np.isin(labels,[0,1]).all(),'margin_inputs')
    sign=2*labels-1;whole=scores[:,0];detail=scores[:,1];total=whole+detail
    margin=sign*total-math.log(.85/.15)
    return dict(count=len(labels),summary=b.trainer.w.summary(1/(1+np.exp(-np.clip(total,-80,80))),labels),
        marginQuantiles=np.quantile(margin,[0,.1,.5,.9,1]).tolist(),
        wholeQuantiles=np.quantile(whole,[0,.1,.5,.9,1]).tolist(),
        detailQuantiles=np.quantile(detail,[0,.1,.5,.9,1]).tolist(),
        helpfulDetail=int((sign*detail>0).sum()),
        helpfulDetailButWrongContext=int(((sign*detail>0)&(sign*whole<0)).sum()),
        helpfulDetailButBelowThreshold=int(((sign*detail>0)&(margin<0)).sum()))


class PositiveFusion(t.nn.Module):
    def __init__(self):
        super().__init__()
        self.raw=t.nn.Parameter(t.full((2,),math.log(math.expm1(1.))))
        self.bias=t.nn.Parameter(t.zeros(1))

    def forward(self,scores):
        return (scores*t.nn.functional.softplus(self.raw)).sum(1,keepdim=True)+self.bias


class FusionChange(t.nn.Module):
    def __init__(self,base):
        super().__init__();self.base=base;self.fusion=PositiveFusion()

    @property
    def whole(self):return self.base.whole

    def forward(self,images):
        if images.ndim==2:
            b.require(images.shape[1]==2,'fusion_score_shape');return self.fusion(images)
        whole=self.whole(r.s.c.model.change_inputs(None,images[:,:6])).flatten()
        total=self.base(images).flatten()
        return self.fusion(t.stack((whole,total-whole),1))


def extend(net):
    net.change=FusionChange(net.change);return net


def load_candidate(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION,'fusion_checkpoint')
    net=extend(r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2))
    net.load_state_dict(saved['state']);return net.eval()


def audit():
    b.require(not (OUT/'registration.json').exists(),'output_collision');OUT.mkdir(exist_ok=True)
    started=time.monotonic();t.set_num_threads(2)
    corpus=b.read(a.OUT/'corpus.json');review=b.read(a.OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(a.OUT/'corpus.json')['sha256'],'review_required')
    manifest,membership,full,labels,weights,extra,controls,_,reg=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    original=b.read(r.OUT/'registration.json')
    for key,value in [('training',values),('labels',labels),('weights',weights)]:
        b.require(b.sha(value.tobytes())==original[key+'SHA256'],'original_'+key)
    rows=r.s.schedule_rows(membership,reg,labels);groups=diagnostic.groups(rows,labels)
    details,_=r.prepare(values,rows,2)
    b.require(b.sha(details.tobytes())==b.read(r.OUT/'regions-2/views.json')['sha256'],'detail_hash')
    model=b.ref(a.OUT/'run/last.pt');net=r.load_candidate(b.checked(model))
    scores=branch_scores(net,values,details)
    # Keep small real-image inputs to verify the cached path after fitting.
    np.save(OUT/'parity-images.npy',np.concatenate((values[:8],details[:8]),1),allow_pickle=False)
    del values,details;gc.collect()
    authored=np.load(b.checked(corpus['tensor']),allow_pickle=False);ad,_=r.prepare(authored,corpus['rows'],2)
    auxiliary=branch_scores(net,authored,ad);ay=np.array([x['changed'] for x in corpus['rows']],np.float32)
    ids=a.schedule(labels,corpus['rows'])
    np.savez(OUT/'scores.npz',original=scores,authored=auxiliary,labels=labels,weights=weights,auxiliaryIndices=ids,authoredLabels=ay)
    bygroup={name:margins(scores[ix],labels[ix]) for name,ix in groups.items()}
    bycondition={name:margins(auxiliary[[i for i,x in enumerate(corpus['rows']) if x['condition']==name]],
                             ay[[i for i,x in enumerate(corpus['rows']) if x['condition']==name]])
                 for name in sorted({x['condition'] for x in corpus['rows']})}
    b.write(OUT/'registration.json',dict(version=VERSION,model=model,corpus=b.ref(a.OUT/'corpus.json'),review=b.ref(a.OUT/'review.json'),
        originalHashes={k:original[k] for k in ('trainingSHA256','labelsSHA256','weightsSHA256')},
        scores=b.ref(OUT/'scores.npz'),parityImages=b.ref(OUT/'parity-images.npy'),
        runner=b.ref(Path(__file__)),regions=b.ref(Path(r.__file__)),sourceDetail=b.ref(Path(r.s.__file__)),
        membership=b.ref(b.PACKAGE/'membership.json'),manifest=b.ref(b.PACKAGE/'manifest.json'),
        thresholds=[.15,.85],rolesChanged=False,configuration=dict(epochs=30,lr=.01,batch=16,seed=42,threads=2,fusionOnly=True),
        auxiliaryWeight=.25,selection='fixed-last',maximumOutputBytes=256*1024**2,memoryLimitBytes=8*1024**3))
    justified=any(x['helpfulDetailButWrongContext']>0 for x in bycondition.values())
    b.write(OUT/'margins.json',dict(registration=b.ref(OUT/'registration.json'),groups=bygroup,authored=bycondition,
        fusionJustified=justified,seconds=time.monotonic()-started,evaluationUsedForSelection=False))
    print('Training margin audit',bycondition,flush=True)


def train():
    t.set_num_threads(2);start=time.monotonic();reg=b.read(OUT/'registration.json');audit=b.read(OUT/'margins.json')
    b.checked(audit['registration']);b.require(audit['fusionJustified'],'fusion_not_justified')
    for key in ('runner','regions','sourceDetail','corpus','review','membership','manifest'):b.checked(reg[key])
    run=OUT/'run';b.require(not run.exists(),'run_collision');run.mkdir()
    data=np.load(b.checked(reg['scores']),allow_pickle=False)
    x=data['original'];y=data['labels'];weights=data['weights'];ids=data['auxiliaryIndices'];ax=data['authored'][ids]
    b.require(np.array_equal(y,data['authoredLabels'][ids]),'auxiliary_labels')
    net=extend(r.load_candidate(b.checked(reg['model'])));frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.fusion.')}
    before=net.change(t.from_numpy(x)).detach().numpy().flatten()
    b.require(np.max(np.abs(before-x.sum(1)))<1e-5,'initial_fusion_parity')
    b.write(run/'registration.json',dict(parent=b.ref(OUT/'registration.json'),margins=b.ref(OUT/'margins.json'),
        trainer=b.ref(Path(b.trainer.__file__)),trainableParameters=3,trainingRows=len(x),auxiliaryRows=len(ax),
        rolesChanged=False,thresholds=reg['thresholds'],selection='fixed-last'))
    def progress(row):b.write(run/f"epoch-{row['epoch']:04d}.json",row);print(row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),reg['configuration'],progress,t.from_numpy(weights),
        auxiliary_inputs=t.from_numpy(ax),auxiliary_weight=.25)
    b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    t.save(dict(state=net.state_dict(),representation=VERSION),run/'last.pt');restored=load_candidate(run/'last.pt')
    sanity=np.load(b.checked(reg['parityImages']),allow_pickle=False)
    imagep=b.worker.score(restored,sanity)
    with t.inference_mode():cachep=restored.change(t.from_numpy(x[:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(imagep-cachep))<=1e-6,'cache_image_parity')
    b.require(np.array_equal(imagep,b.worker.score(net,sanity)),'checkpoint_parity')
    coefficients=t.nn.functional.softplus(net.change.fusion.raw).detach().tolist()
    b.write(run/'fit.json',dict(history=history,seconds=time.monotonic()-start,coefficients=coefficients,
        bias=float(net.change.fusion.bias.detach()[0]),frozenTensors=len(frozen),
        cacheImageMaximumError=float(np.max(np.abs(imagep-cachep))),checkpointParity=True))
    manifest=b.read(b.checked(reg['manifest']));membership=b.read(b.checked(reg['membership']))
    native=np.load(b.PACKAGE/'native.npy',allow_pickle=False);nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,v):
        if key=='native.npy':return np.concatenate((v,nd),1)
        if key=='reverse_native.npy':return np.concatenate((v,r.reverse_details(nd)),1)
        return v
    initializer=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    evaluation=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(initializer)},manifest,input_transform=transform)
    b.write(run/'evaluation.json',evaluation)
    conditions={name:[i for i,v in enumerate(b.read(a.OUT/'corpus.json')['rows']) if v['condition']==name]
                for name in ('movement','artwork-only','identical')}
    with t.inference_mode():prob=net.change(t.from_numpy(data['authored'])).sigmoid().flatten().numpy()
    b.write(run/'authored.json',dict(probabilities=prob.tolist(),conditions={k:b.trainer.w.summary(prob[ix],data['authoredLabels'][ix]) for k,ix in conditions.items()}))
    import report_authored319
    report_authored319.main(OUT,loader=load_candidate)
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<reg['maximumOutputBytes'],'output_budget')
    print('Completed fusion comparison in',time.monotonic()-start,'s',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['audit','train']);args=p.parse_args()
    audit() if args.mode=='audit' else train()
