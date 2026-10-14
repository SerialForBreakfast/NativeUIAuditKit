"""Train detail filters on retained images and compare the retained control."""
import argparse
import gc
import hashlib
import resource
import time
from pathlib import Path
import numpy as np
import effect326 as e

b=e.b;r=e.r;t=e.t;p=e.p
OUT=b.ROOT/'reports/work/FOCUS-327'


def digest(values):
    return hashlib.sha256(memoryview(np.ascontiguousarray(values))).hexdigest()


def memory_check():
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    b.require(peak<8*1024**3,'memory_limit')
    return peak


def image_model(pin):
    net=p.load(b.checked(pin))
    net.change.__class__=r.RegionChange
    return net


def register():
    b.require(not (OUT/'inputs.json').exists(),'output_collision')
    parent=b.read(e.OUT/'inputs.json')
    for key in ('corpus','review','oldCorpus','initializer','pooling','parity'):b.checked(parent[key])
    config=dict(parent['configuration'],cachedDetailOnly=False)
    b.write(OUT/'inputs.json',dict(parent=b.ref(e.OUT/'inputs.json'),
        **{key:parent[key] for key in ('corpus','review','oldCorpus','initializer','parity')},
        control=b.ref(e.OUT/'independent/run/last.pt'),cache=parent['cache']['independent'],
        runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),regions=b.ref(Path(r.__file__)),
        reporter=b.ref(b.ROOT/'scripts/report_authored319.py'),configuration=config,
        hypothesis='Learning detail filters improves the same task that fixed filters cannot fit.',
        selection='fixed-last',thresholds=[.15,.85],auxiliaryWeight=.25,rolesChanged=False,
        probe=dict(rows=32,epochs=30,selection='First 16 changed and 16 unchanged new training rows.'),
        outputCapBytes=2*1024**3,memoryLimitBytes=8*1024**3,wallTimeLimit=None,
        acceptance='Improve native decisions without lost previous successes or increased false changes.',
        torchVersion=str(t.__version__)))


def prepare(reg):
    start=time.monotonic()
    cache=np.load(b.checked(reg['cache']),allow_pickle=False)
    manifest,membership,full,labels,weights,extra,controls,_,source=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)))
    del full,extra,added;gc.collect()
    original=b.read(r.OUT/'registration.json')
    for key,value in [('training',values),('labels',labels),('weights',weights)]:
        b.require(digest(value)==original[key+'SHA256'],'original_'+key)
    b.require(np.array_equal(labels,cache['labels']) and np.array_equal(weights,cache['weights']),'retained_schedule')
    details,audit=r.prepare(values,r.s.schedule_rows(membership,source,labels),2)
    b.require(digest(details)==b.read(r.OUT/'regions-2/views.json')['sha256'],'original_details')
    rows=b.read(b.checked(reg['oldCorpus']))['rows']+b.read(b.checked(reg['corpus']))['rows']['independent']
    protected={v['group'] for v in membership['rows'] if v['role']!='train'}
    b.require(all(v['role']=='train' and v['group'] not in protected for v in rows),'protected_group')
    review=b.read(b.checked(reg['review']));validation=b.read(b.checked(review['validation']))
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==reg['corpus']['sha256']
              and validation['passed'] and validation['corpus']==reg['corpus'],'retained_review')
    aux=np.empty((len(rows),6,128,192),np.float32)
    ad=np.empty((len(rows),12,128,192),np.float32)
    net=p.load(b.checked(reg['initializer']));maximum=0.
    for startrow in range(0,len(rows),8):
        subset=rows[startrow:startrow+8]
        x=np.stack([r.s.encoded(*[r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in subset])
        d,_=r.prepare(x,subset,2)
        aux[startrow:startrow+len(x)]=x;ad[startrow:startrow+len(x)]=d
        features,_=p.cache(net,x,d)
        maximum=max(maximum,float(np.abs(features[0.]-cache['auxiliary'][startrow:startrow+len(x)]).max()))
    ay=np.array([v['changed'] for v in rows],np.float32);indices=e.a.schedule(labels,rows)
    b.require(np.array_equal(indices,cache['indices']) and np.array_equal(ay[indices],labels),'auxiliary_labels')
    features,_=p.cache(net,values,details)
    maximum=max(maximum,float(np.abs(features[0.]-cache['original']).max()))
    b.require(maximum<1e-6,'retained_feature_parity')
    b.write(OUT/'preparation.json',dict(originalSHA256=digest(values),detailSHA256=digest(details),
        auxiliarySHA256=digest(aux),auxiliaryDetailSHA256=digest(ad),indicesSHA256=digest(indices),
        rows=rows,maximumFeatureError=maximum,originalViews=len(labels),auxiliaryRows=len(rows),
        seconds=time.monotonic()-start,peakBytes=memory_check(),rolesChanged=False))
    print('Prepared retained images',time.monotonic()-start,flush=True)
    return values,details,labels,weights,aux,ad,ay,indices


def score(net,x,details):
    parts=[]
    for i in range(0,len(x),8):
        parts.append(b.worker.score(net,np.concatenate((x[i:i+8],details[i:i+8]),1)))
    return np.concatenate(parts)


def probe(reg,aux,ad,ay):
    ids=np.concatenate([np.flatnonzero(ay[240:]==label)[:16]+240 for label in (0,1)])
    b.require(len(ids)==32,'probe_support')
    x=t.from_numpy(aux[ids]);details=t.from_numpy(ad[ids]);y=t.from_numpy(ay[ids])
    net=image_model(reg['initializer']);net.train()
    for name,param in net.named_parameters():param.requires_grad_(name.startswith(('change.detail.','change.correction.')))
    logits=net.change(t.cat((x,details),1)).flatten()
    loss=t.nn.functional.binary_cross_entropy_with_logits(logits,y);loss.backward()
    gradients={name:float(param.grad.norm()) for name,param in net.named_parameters() if name.startswith('change.detail.')}
    b.require(all(np.isfinite(v) and v>0 for v in gradients.values()),'probe_gradients')
    before=float(loss.detach());net=image_model(reg['initializer'])
    net,history=b.trainer.fit(net,x,y,dict(reg['configuration'],epochs=30),detail_inputs=details)
    with t.inference_mode():after=float(t.nn.functional.binary_cross_entropy_with_logits(net.change(t.cat((x,details),1)).flatten(),y))
    result=dict(indices=ids.tolist(),gradients=gradients,beforeLoss=before,afterLoss=after,history=history,
                passed=bool(np.isfinite(after) and after<before),trainingOnly=True,weightsDiscarded=True)
    b.write(OUT/'probe.json',result);b.require(result['passed'],'probe_fit')
    print('Training-only probe',before,after,flush=True)


def run():
    started=time.monotonic();t.set_num_threads(2);reg=b.read(OUT/'inputs.json')
    for key in ('parent','corpus','review','oldCorpus','initializer','control','runner','trainer','regions','reporter'):b.checked(reg[key])
    out=OUT/'run';b.require(not out.exists(),'output_collision');out.mkdir()
    b.write(out/'registration.json',dict(inputs=b.ref(OUT/'inputs.json'),selection='fixed-last'))
    values,details,labels,weights,aux,ad,ay,indices=prepare(reg)
    probe(reg,aux,ad,ay)
    net=image_model(reg['initializer']);baseline={k:v.clone() for k,v in net.state_dict().items()}
    sanity=np.concatenate((values[:8],details[:8]),1)
    b.require(np.max(np.abs(b.worker.score(net,sanity)-b.worker.score(p.load(b.checked(reg['initializer'])),sanity)))<1e-6,'initial_image_parity')
    initial=score(net,aux,ad)
    def progress(row):
        row['peakBytes']=memory_check();b.write(out/f"epoch-{row['epoch']:04d}.json",row);print(row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(values),t.from_numpy(labels),reg['configuration'],progress,
        t.from_numpy(weights),detail_inputs=t.from_numpy(details),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_weight=.25,auxiliary_indices=t.from_numpy(indices))
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,baseline[k])]
    b.require(all(k.startswith(('change.detail.','change.correction.')) for k in changed)
              and any(k.startswith('change.detail.0.') for k in changed),'changed_scope')
    t.save(dict(state=net.state_dict(),representation=r.VERSION,windows=2),out/'last.pt')
    restored=r.load_candidate(out/'last.pt')
    b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'checkpoint_parity')
    prob=score(restored,aux,ad)
    b.write(out/'training.json',dict(initial=b.trainer.w.summary(initial[240:],ay[240:]),
        final=b.trainer.w.summary(prob[240:],ay[240:]),initialProbabilities=initial.tolist(),probabilities=prob.tolist()))
    b.write(out/'fit.json',dict(history=history,changedTensors=changed,seconds=time.monotonic()-started,checkpointParity=True,peakBytes=memory_check()))
    del values,details,aux,ad,net;gc.collect()
    membership=b.read(b.PACKAGE/'membership.json');native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,nd),1)
        if key=='reverse_native.npy':return np.concatenate((x,r.reverse_details(nd)),1)
        return x
    init=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(init)},b.read(b.PACKAGE/'manifest.json'),input_transform=transform)
    b.write(out/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=r.load_candidate,run_folder=out)
    b.write(out/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),peakBytes=memory_check(),productionEligible=False))
    b.require(sum(v.stat().st_size for v in OUT.rglob('*') if v.is_file())<reg['outputCapBytes'],'output_limit')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['register','run']);args=parser.parse_args()
    globals()[args.mode]()
