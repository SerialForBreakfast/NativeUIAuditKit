"""Test contrast-normalized details with unchanged full-frame inputs."""
import argparse
import gc
from pathlib import Path
import time
import numpy as np
import filters327 as f

b=f.b;r=f.r;t=f.t
OUT=b.ROOT/'reports/work/FOCUS-328'
VERSION='contrast328-v1'


def normalize(images):
    b.require(images.ndim==4 and images.shape[1:]==(6,128,192),'detail_shape')
    b.require(bool(t.isfinite(images).all()),'finite_detail')
    # Crops have black margins. Full-frame fallbacks keep all their pixels.
    padded=(images[:,:,:,:32]==0).all((1,2,3)) & (images[:,:,:,160:]==0).all((1,2,3))
    mask=t.ones((len(images),1,128,192),dtype=images.dtype,device=images.device)
    mask[padded,:,:,:32]=0;mask[padded,:,:,160:]=0
    count=mask.sum((2,3),keepdim=True)
    mean=(images*mask).sum((2,3),keepdim=True)/count
    scale=(((images-mean).square()*mask).sum((2,3),keepdim=True)/count).sqrt().clamp_min(.05)
    return (.5+.2*(images-mean)/scale).clamp(0,1)*mask


class ContrastChange(r.RegionChange):
    def forward(self,images):
        b.require(images.shape[1] in (6,18),'region_channels')
        whole=images[:,:6]
        details=images[:,6:] if images.shape[1]==18 else r.encoded_details(whole,2)
        context=self.whole[:10](r.s.c.model.change_inputs(None,whole))
        features=[self.detail(r.s.c.model.change_inputs(None,normalize(details[:,6*j:6*(j+1)]))) for j in range(2)]
        return self.whole[10](context)+self.correction(t.cat((context,t.stack(features).mean(0)),1))


def image_model(pin):
    net=f.image_model(pin);net.change.__class__=ContrastChange
    return net


def load_candidate(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION and saved.get('windows')==2,'checkpoint_version')
    net=r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2)
    net.change.__class__=ContrastChange;net.load_state_dict(saved['state'])
    return net.eval()


def signals(x):
    delta=x[:,3:]-x[:,:3]
    edge=(delta[:,:,:,1:]-delta[:,:,:,:-1]).abs().mean((1,2,3))
    edge+=(delta[:,:,1:,:]-delta[:,:,:-1,:]).abs().mean((1,2,3))
    return dict(brightness=delta.mean((1,2,3)),absolute=delta.abs().mean((1,2,3)),edge=edge)


def diagnose():
    t.set_num_threads(2);b.require(not (OUT/'diagnostic.json').exists(),'output_collision')
    reg=b.read(f.OUT/'inputs.json');rows=b.read(b.checked(reg['corpus']))['rows']['independent']
    # One fixed first row for every condition and factor cell. No development inputs.
    selected={}
    for row in rows:
        key=(row['sizePixels'],row['widthPixels'],row['contrast'],row['condition'])
        selected.setdefault(key,row)
    net=r.load_candidate(f.OUT/'run/last.pt');records=[]
    for key,row in selected.items():
        b.require(row['role']=='train','diagnostic_role')
        x=np.stack([r.s.encoded(*[r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0]])
        d,_=r.prepare(x,[row],2);detail=t.from_numpy(d[:,:6])
        # An affine contrast change without clipping or movement.
        perturbed=detail.clone();perturbed[:,3:,:,32:160]=.5+.5*(detail[:,3:,:,32:160]-.5)
        with t.inference_mode():
            raw=signals(detail);norm=signals(normalize(detail))
            response=[]
            for mode in ('raw','normalized'):
                values=[]
                for part in (detail,perturbed):
                    part=part if mode=='raw' else normalize(part)
                    values.append(net.change.detail(r.s.c.model.change_inputs(None,part)))
                response.append(float((values[1]-values[0]).abs().mean()))
            inputs=t.from_numpy(np.concatenate((x,d),1))
            whole=net.change.whole(r.s.c.model.change_inputs(None,inputs[:,:6])).item()
            total=net.change(inputs).item()
        records.append(dict(id=row.get('id'),group=row['group'],cell=list(key),changed=row['changed'],
            signals={name:{k:float(v.item()) for k,v in data.items()} for name,data in [('raw',raw),('normalized',norm)]},
            rawFeatureShift=response[0],normalizedFeatureShift=response[1],whole=whole,detailCorrection=total-whole))
    changed=[v for v in records if v['changed']]
    raw=float(np.mean([v['rawFeatureShift'] for v in records]));norm=float(np.mean([v['normalizedFeatureShift'] for v in records]))
    retained=all(v['signals']['normalized']['absolute']>0 for v in changed)
    justified=raw>1e-6 and norm<raw and retained
    b.write(OUT/'diagnostic.json',dict(source=b.ref(Path(__file__)),control=b.ref(f.OUT/'run/last.pt'),
        corpus=reg['corpus'],rows=records,meanRawFeatureShift=raw,meanNormalizedFeatureShift=norm,
        growthDifferencesRetained=retained,candidateJustified=justified,trainingOnly=True,
        limitation='Affine changes in selected training crops. This does not prove immunity to regional artwork changes.'))
    print('Diagnostic',raw,norm,'growth retained',retained,'candidate justified',justified,flush=True)


def register():
    b.require(not (OUT/'inputs.json').exists(),'output_collision')
    diagnostic=b.read(OUT/'diagnostic.json');b.require(diagnostic['candidateJustified'],'diagnostic_failed')
    b.checked(diagnostic['source'])
    parent=b.read(f.OUT/'inputs.json')
    reg=dict(parent,parent=b.ref(f.OUT/'inputs.json'),control=b.ref(f.OUT/'run/last.pt'),
        runner=b.ref(Path(__file__)),preparer=b.ref(Path(f.__file__)),reporter=b.ref(b.ROOT/'scripts/report_authored319.py'),
        diagnostic=b.ref(OUT/'diagnostic.json'),representation=VERSION,
        hypothesis='Per-frame detail normalization reduces contrast shortcuts while preserving spatial growth.',
        probe=None)
    b.write(OUT/'inputs.json',reg)


def run():
    started=time.monotonic();t.set_num_threads(2);reg=b.read(OUT/'inputs.json')
    for key in ('parent','corpus','review','oldCorpus','initializer','control','runner','trainer','regions','reporter','preparer','diagnostic'):b.checked(reg[key])
    out=OUT/'run';b.require(not out.exists(),'output_collision');out.mkdir()
    b.write(out/'registration.json',dict(inputs=b.ref(OUT/'inputs.json'),selection='fixed-last'))
    f.OUT=OUT
    values,details,labels,weights,aux,ad,ay,indices=f.prepare(reg)
    net=image_model(reg['initializer']);baseline={k:v.clone() for k,v in net.state_dict().items()}
    sanity=np.concatenate((values[:8],details[:8]),1)
    initial=f.score(net,aux,ad)
    def progress(row):
        row['peakBytes']=f.memory_check();b.write(out/f"epoch-{row['epoch']:04d}.json",row);print(row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(values),t.from_numpy(labels),reg['configuration'],progress,
        t.from_numpy(weights),detail_inputs=t.from_numpy(details),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_weight=.25,auxiliary_indices=t.from_numpy(indices))
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,baseline[k])]
    b.require(all(k.startswith(('change.detail.','change.correction.')) for k in changed)
              and any(k.startswith('change.detail.0.') for k in changed),'changed_scope')
    t.save(dict(state=net.state_dict(),representation=VERSION,windows=2),out/'last.pt')
    restored=load_candidate(out/'last.pt')
    b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'checkpoint_parity')
    prob=f.score(restored,aux,ad)
    b.write(out/'training.json',dict(initial=b.trainer.w.summary(initial[240:],ay[240:]),
        final=b.trainer.w.summary(prob[240:],ay[240:]),initialProbabilities=initial.tolist(),probabilities=prob.tolist()))
    b.write(out/'fit.json',dict(history=history,changedTensors=changed,seconds=time.monotonic()-started,checkpointParity=True,peakBytes=f.memory_check()))
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
    report_authored319.main(OUT,loader=load_candidate,run_folder=out)
    b.write(out/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),peakBytes=f.memory_check(),productionEligible=False))
    b.require(sum(v.stat().st_size for v in OUT.rglob('*') if v.is_file())<reg['outputCapBytes'],'output_limit')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['diagnose','register','run'])
    globals()[parser.parse_args().mode]()
