"""Test retained detail features and fit one constrained residual readout."""
import argparse
import gc
from pathlib import Path
import time
import numpy as np
import constrained323 as prior
import conflict320

d=prior.diagnostic;m=prior.m;b=prior.b;t=prior.t;r=prior.r
a=m.f.a
OUT=b.ROOT/'reports/work/FOCUS-324'
VERSION='features324-v1'


def retained(base, images):
    b.require(images.ndim==4 and images.shape[1] in (6,18) and images.shape[2:]==(128,192),'feature_images')
    whole=images[:,:6]
    details=images[:,6:] if images.shape[1]==18 else r.encoded_details(whole,2)
    context=base.whole[:10](r.s.c.model.change_inputs(None,whole))
    detail=t.stack([base.detail(r.s.c.model.change_inputs(None,details[:,6*j:6*(j+1)])) for j in range(2)]).mean(0)
    features=t.cat((context,detail),1)
    scores=t.cat((base.whole[10](context),base.correction(features)),1)
    return features,scores


def normalization(features):
    b.require(features.ndim==2 and features.shape[1]==64 and len(features)>0 and np.isfinite(features).all(),'feature_values')
    return features.mean(0),np.maximum(features.std(0),.001)


class FeatureChange(t.nn.Module):
    def __init__(self,base,center,scale):
        super().__init__();self.base=base
        center=np.asarray(center);scale=np.asarray(scale)
        b.require(center.shape==scale.shape==(64,) and np.isfinite(center).all() and np.isfinite(scale).all() and (scale>=.001).all(),'feature_normalization')
        self.register_buffer('center',t.as_tensor(center,dtype=t.float32))
        self.register_buffer('scale',t.as_tensor(scale,dtype=t.float32))
        self.readout=t.nn.Linear(64,1)
        t.nn.init.zeros_(self.readout.weight);t.nn.init.zeros_(self.readout.bias)

    @property
    def whole(self):return self.base.whole

    def forward(self,images):
        if images.ndim==2:
            b.require(images.shape[1]==66 and t.isfinite(images).all(),'feature_cache')
            features,scores=images[:,:64],images[:,64:]
        else:features,scores=retained(self.base,images)
        return scores.sum(1,keepdim=True)+self.readout((features-self.center)/self.scale)


def make(net,center,scale):
    net.change=FeatureChange(net.change,center,scale);return net


def load(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION,'feature_checkpoint')
    state=saved['state']
    net=r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2)
    net=make(net,state['change.center'].numpy(),state['change.scale'].numpy())
    net.load_state_dict(state);return net.eval()


def extract(net,values,details):
    features=[];scores=[]
    with t.inference_mode():
        for start in range(0,len(values),8):
            images=t.from_numpy(np.concatenate((values[start:start+8],details[start:start+8]),1))
            f,s=retained(net.change,images);features.append(f.numpy());scores.append(s.numpy())
    return np.concatenate(features),np.concatenate(scores)


def summary(logits,labels,indices):
    ids=np.asarray(indices,dtype=int)
    b.require(len(ids)>0,'empty_feature_group')
    p=1/(1+np.exp(-np.clip(logits[ids],-80,80)))
    return b.trainer.w.summary(p,labels[ids])


def audit():
    t.set_num_threads(2);started=time.monotonic();reg,cached=m.inputs()
    b.require(not (OUT/'registration.json').exists(),'output_collision');OUT.mkdir(exist_ok=True)
    corpus=b.read(b.checked(reg['corpus']));review=b.read(b.checked(reg['review']))
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==reg['corpus']['sha256'],'review_required')
    b.write(OUT/'registration.json',dict(parent=b.ref(m.f.OUT/'registration.json'),runner=b.ref(Path(__file__)),
        solver=b.ref(Path(d.__file__)),model=reg['model'],rolesChanged=False,evaluationUsed=False,
        featureDefinition='32 context features and 32 mean-pooled detail features. Original image windows remain unchanged.',
        coefficientBounds=[-1,1],minimumScale=.001,targetMargin=m.H+.25,thresholds=[.15,.85],
        candidateRule='One combined-feature correction only if weighted hinge improves by more than 0.0001.',
        outputCapBytes=256*1024**2,memoryBudgetBytes=8*1024**3,threads=2))
    manifest,membership,full,labels,weights,extra,controls,_,schedule=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    for name,value in [('training',values),('labels',labels),('weights',weights)]:
        b.require(b.sha(value.tobytes())==reg['originalHashes'][name+'SHA256'],'original_'+name)
    rows=r.s.schedule_rows(membership,schedule,labels);groups=conflict320.groups(rows,labels)
    details,_=r.prepare(values,rows,2)
    b.require(b.sha(details.tobytes())==b.read(r.OUT/'regions-2/views.json')['sha256'],'detail_hash')
    net=r.load_candidate(b.checked(reg['model']));features,scores=extract(net,values,details)
    b.require(np.max(np.abs(scores-cached['original']))<2e-5,'original_score_parity')
    del values,details;gc.collect()
    values=np.load(b.checked(corpus['tensor']),allow_pickle=False);details,_=r.prepare(values,corpus['rows'],2)
    af,asc=extract(net,values,details)
    b.require(np.max(np.abs(asc-cached['authored']))<2e-5,'authored_score_parity')
    del values,details;gc.collect()
    features=np.concatenate((features,af));scores=np.concatenate((scores,asc))
    labels=np.r_[cached['labels'],cached['authoredLabels']]
    center,scale=normalization(features);normalized=(features-center)/scale
    counts=np.bincount(cached['auxiliaryIndices'],weights=cached['weights'],minlength=len(af))
    b.require((counts>0).all(),'unscheduled_authored')
    weights=np.r_[cached['weights'],.25*counts]/len(cached['original'])
    np.savez(OUT/'features.npz',features=features,scores=scores,labels=labels,weights=weights,center=center,scale=scale)
    fits={}
    for name,cols in [('detail',normalized[:,32:]),('context_detail',normalized)]:
        fits[name]=d.fixed_feature_bound(scores,labels,weights,np.column_stack((cols,np.ones(len(cols)))))
    fit=fits['context_detail'];logits=scores.sum(1)+np.column_stack((normalized,np.ones(len(normalized))))@fit['diagnosticCoefficients']
    for condition in sorted({row['condition'] for row in corpus['rows']}):
        groups['authored:'+condition]=[1820+i for i,row in enumerate(corpus['rows']) if row['condition']==condition]
    size_path=r.s.OUT/'size-audit.json';size_rows=b.read(size_path)['rows']
    b.require(len(size_rows)==len(rows),'size_schedule')
    for i,(row,measured) in enumerate(zip(rows,size_rows)):
        if row is not None:b.require(measured['images']==row['images'],'size_source_identity')
        sizes=[e['minimumEncodedSize'] for e in measured.get('endpoints',[]) if e['status']=='measured']
        size='unknown' if len(sizes)!=2 else ('below4' if min(sizes)<4 else '4to8' if min(sizes)<8 else '8to16' if min(sizes)<16 else '16plus')
        groups.setdefault('encoded-body-size:'+size,[]).append(i)
    for layout in sorted({row['layout'] for row in corpus['rows']}):
        groups['authored-layout:'+layout]=[1820+i for i,row in enumerate(corpus['rows']) if row['layout']==layout]
    grouped={key:dict(before=summary(scores.sum(1),labels,ids),after=summary(logits,labels,ids)) for key,ids in groups.items()}
    b.write(OUT/'audit.json',dict(registration=b.ref(OUT/'registration.json'),cache=b.ref(OUT/'features.npz'),
        fits=fits,groups=grouped,supportsCorrection=fit['minimumHinge']<fit['baselineHinge']-1e-4,
        featureDimensions=64,trainingRows=1820,authoredRows=240,evaluationUsed=False,
        sizeEvidence=b.ref(size_path),
        effectStrength='Not independently varied in this training corpus. No strength-separation claim.',
        seconds=time.monotonic()-started))
    print('Feature audit',fits,flush=True)


def run():
    started=time.monotonic();t.set_num_threads(2);reg,cached=m.inputs();audit=b.read(OUT/'audit.json')
    registration=b.read(b.checked(audit['registration']))
    for key in ('runner','solver','model'):b.checked(registration[key])
    b.require(audit['supportsCorrection'],'correction_not_supported')
    data=np.load(b.checked(audit['cache']),allow_pickle=False)
    out=OUT/'run';b.require(not out.exists(),'output_collision');out.mkdir()
    net=make(r.load_candidate(b.checked(reg['model'])),data['center'],data['scale'])
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.readout.')}
    coefficients=np.array(audit['fits']['context_detail']['diagnosticCoefficients'])
    b.require(coefficients.shape==(65,) and np.isfinite(coefficients).all() and (np.abs(coefficients)<=1+1e-8).all(),'feature_coefficients')
    b.write(out/'registration.json',dict(parent=b.ref(m.f.OUT/'registration.json'),audit=b.ref(OUT/'audit.json'),
        runner=b.ref(Path(__file__)),trainer=b.ref(Path(d.__file__)),trainableParameters=65,
        selection='Use the single training-only constrained solution. No evaluation selection.',rolesChanged=False))
    with t.no_grad():
        net.change.readout.weight.copy_(t.as_tensor(coefficients[:-1],dtype=t.float32)[None])
        net.change.readout.bias.copy_(t.as_tensor(coefficients[-1:],dtype=t.float32))
    b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    inputs=t.from_numpy(np.concatenate((data['features'],data['scores']),1))
    with t.inference_mode():logits=net.change(inputs).flatten().numpy()
    constraints=prior.check_margins(data['scores'],data['labels'],logits)
    t.save(dict(state=net.state_dict(),representation=VERSION),out/'last.pt');restored=load(out/'last.pt')
    sanity=np.load(b.checked(reg['parityImages']),allow_pickle=False)
    imagep=b.worker.score(restored,sanity)
    with t.inference_mode():cachep=restored.change(inputs[:8]).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(imagep-cachep))<1e-6,'cache_image_parity')
    b.require(np.array_equal(imagep,b.worker.score(net,sanity)),'checkpoint_parity')
    hinge=float(data['weights']@np.maximum(0,m.H+.25-(2*data['labels']-1)*logits))
    b.require(abs(hinge-audit['fits']['context_detail']['minimumHinge'])<2e-5,'objective_parity')
    b.write(out/'fit.json',dict(constraints=constraints,frozenTensors=len(frozen),actualHinge=hinge,
        cacheImageMaximumError=float(np.max(np.abs(imagep-cachep))),checkpointParity=True,
        authored=summary(logits,data['labels'],list(range(1820,2060))),original=summary(logits,data['labels'],list(range(1820))),
        seconds=time.monotonic()-started))
    membership=b.read(b.checked(reg['membership']));native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,v):
        if key=='native.npy':return np.concatenate((v,nd),1)
        if key=='reverse_native.npy':return np.concatenate((v,r.reverse_details(nd)),1)
        return v
    initializer=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(initializer)},b.read(b.checked(reg['manifest'])),input_transform=transform)
    b.write(out/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=load)
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),report=b.ref(OUT/'report.json'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<256*1024**2,'output_budget')
    print('Complete',time.monotonic()-started,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['audit','run']);args=parser.parse_args()
    audit() if args.mode=='audit' else run()
