"""Preserve original views and add measured boundary evidence."""
import argparse
import copy
from pathlib import Path
import time
import numpy as np
from PIL import Image
import edge329 as e
import regions331 as proposals

b=e.b; r=e.r; t=e.t
OUT=b.ROOT/'reports/work/FOCUS-341'


def added_windows(values):
    old=r.windows(values)
    energy=proposals.boundary_energy(values)
    result=[]
    yy,xx=t.meshgrid(t.arange(97),t.arange(161),indexing='ij')
    for i,boxes in enumerate(old):
        score=t.nn.functional.avg_pool2d(energy[i:i+1],32,stride=1)[0,0].clone()
        for x,y in boxes:
            score[(xx<x+32)&(xx+32>x)&(yy<y+32)&(yy+32>y)]=-1
        peak=int(score.flatten().argmax())
        result.append((peak%161,peak//161) if float(score.flatten()[peak])>0 else None)
    return result


def added_details(values,rows):
    output=np.zeros((len(values),6,128,192),np.float32)
    for start in range(0,len(values),8):
        part=t.from_numpy(np.array(values[start:start+8]))
        for k,box in enumerate(added_windows(part)):
            if box is None:continue
            i=start+k;x,y=box
            if rows[i] is not None:
                images=[r.s.image(v['path'],v['sha256']) for v in rows[i]['images']]
                b.require(np.array_equal(r.s.encoded(*images,(192,128))[0],values[i]),'source_encoding')
                output[i]=r.s.crop_pair(images,[x,y,x+32,y+32],preserve_padding=True)
            else:
                output[i,:,:,32:160]=t.nn.functional.interpolate(part[k:k+1,:,y:y+32,x:x+32],
                    size=(128,128),mode='bilinear',align_corners=False)[0].numpy()
    return output


class AddedChange(t.nn.Module):
    def __init__(self,old):
        super().__init__();self.whole=old;self.detail=copy.deepcopy(old.detail)
        self.correction=t.nn.Linear(32,1)
        t.nn.init.zeros_(self.correction.weight);t.nn.init.zeros_(self.correction.bias)

    def forward(self,images):
        b.require(images.shape[1] in (6,24),'added_channels')
        if images.shape[1]==6:
            old=t.cat((images,r.encoded_details(images,2)),1)
            added=t.from_numpy(added_details(images.detach().cpu().numpy(),[None]*len(images))).to(images)
        else:old=images[:,:18];added=images[:,18:]
        inputs=t.cat((r.s.c.model.change_inputs(None,added),e.gradient_channels(added)),1)
        return self.whole(old)+self.correction(self.detail(inputs))


def model():
    net=e.load_candidate(e.OUT/'run/last.pt');net.change=AddedChange(net.change)
    return net


def load(path):
    state=t.load(path,map_location='cpu',weights_only=True)
    b.require(state['representation']=='additive341-v1','checkpoint_version')
    net=model();net.load_state_dict(state['state']);return net.eval()


def magnitude(first,second):
    return float(np.abs(first.astype(np.int16)-second.astype(np.int16)).sum(dtype=np.float64))


def match_content(first,alternative,target):
    """Fit pixel magnitude without using model predictions."""
    b.require(first.shape==alternative.shape and target>0,'match_inputs')
    maximum=magnitude(first,alternative)
    if maximum<target*.9:return None
    low,high=0.,1.;best=None
    for _ in range(20):
        alpha=(low+high)/2
        image=np.rint(first.astype(np.float32)*(1-alpha)+alternative.astype(np.float32)*alpha).astype(np.uint8)
        measured=magnitude(first,image);error=abs(measured-target)/max(measured,target)
        if best is None or error<best[0]:best=(error,image,alpha,measured)
        if measured<target:low=alpha
        else:high=alpha
    return best if best[0]<=.1 else None


def generate():
    started=time.monotonic();dest=OUT/'negatives';b.require(not dest.exists(),'output_collision');dest.mkdir()
    source=b.read(b.ROOT/'reports/work/FOCUS-326/corpus.json')
    rows=source['rows']['independent'];lookup={v['id']:v for v in rows};records=[];gaps=[]
    protected={v['group'] for v in b.read(b.PACKAGE/'membership.json')['rows'] if v['role']!='train'}
    for row in rows:
        if row['condition']!='movement' or row['reverse']:continue
        b.require(row['role']=='train' and row['group'] not in protected,'role')
        first,moved=[np.asarray(r.s.image(v['path'],v['sha256'])) for v in row['images']]
        target=magnitude(first,moved)
        art=lookup[row['id'].replace('-movement-','-artwork-only-')]
        alternative=np.asarray(r.s.image(art['images'][1]['path'],art['images'][1]['sha256']))
        result=match_content(first,alternative,target);method='retained-artwork'
        allowed=np.zeros(first.shape[:2],bool)
        for x,y,w,h in row['endpoints'][0]['bodyBounds']:allowed[y:y+h,x:x+w]=True
        if result is None:
            # A content panel changes outside both retained control patches.
            method='background-panel';allowed[:]=False;allowed[390:690,640:1280]=True
            alternative=first.copy()
            artwork=r.s.image(art['images'][1]['path'],art['images'][1]['sha256'])
            x,y,w,h=row['endpoints'][0]['bodyBounds'][1]
            panel=artwork.crop((x,y,x+w,y+h)).resize((640,300),Image.Resampling.LANCZOS)
            alternative[390:690,640:1280]=np.asarray(panel)
            result=match_content(first,alternative,target)
        if result is None:gaps.append(row['id']);continue
        error,image,alpha,actual=result
        b.require(not np.any(image[~allowed]!=first[~allowed]),'changed_effect_or_geometry')
        path=dest/(row['id']+'.png');Image.fromarray(image).save(path)
        pin=b.ref(path)
        with Image.open(path) as decoded:b.require(np.array_equal(np.asarray(decoded),image),'png_roundtrip')
        records.append(dict(row,id=row['id']+'-matched-content',changed=0,condition='matched-content',
            images=[row['images'][0],pin],endpoints=[row['endpoints'][0]]*2,
            matchedMovementID=row['id'],method=method,alpha=alpha,targetMagnitude=target,
            actualMagnitude=actual,relativeError=error,labelAuthority='Authored content edit with unchanged focus and effect pixels.'))
        b.require(time.monotonic()-started<800,'generation_timeout')
    b.write(OUT/'negatives.json',dict(version='matched-content341-v1',rows=records,gaps=gaps,
        source=b.ref(b.ROOT/'reports/work/FOCUS-326/corpus.json'),seconds=time.monotonic()-started,
        nativeQualified=False,rolesChanged=False))
    print('Matched negatives',len(records),'gaps',len(gaps),flush=True)


def audit():
    t.set_num_threads(2);started=time.monotonic();records=[]
    rows=b.read(b.PACKAGE/'membership.json')['rows'];values=np.load(b.PACKAGE/'native.npy',mmap_mode='r')
    for i,row in enumerate(rows):
        if row['role']!='train':continue
        scenes,error=e.audit.scenes_for(row)
        if error:records.append(dict(index=i,status=error));continue
        paired,_,error=e.audit.bodies(row,scenes)
        if error:records.append(dict(index=i,status=error));continue
        part=t.from_numpy(np.array(values[i:i+1]));old=r.windows(part)[0];extra=added_windows(part)[0]
        images=[r.s.image(v['path'],v['sha256']) for v in row['images']]
        delta=np.abs(np.asarray(images[0],dtype=np.float32)-np.asarray(images[1],dtype=np.float32)).mean(2)
        inner,band=e.audit.masks(delta.shape,paired);mask=np.zeros(delta.shape,bool)
        for x,y in old:
            x0,y0,x1,y1=e.audit.source_window([x,y,x+32,y+32],images[0].size)
            e.audit.fill(mask,[x0,y0,x1-x0,y1-y0])
        before=e.audit.measure(delta,inner,band,mask)
        if extra:
            x,y=extra;x0,y0,x1,y1=e.audit.source_window([x,y,x+32,y+32],images[0].size)
            e.audit.fill(mask,[x0,y0,x1-x0,y1-y0])
        after=e.audit.measure(delta,inner,band,mask)
        records.append(dict(index=i,group=row['group'],status='measured',original=before,added=after,extra=extra))
    b.write(OUT/'audit.json',dict(rows=records,seconds=time.monotonic()-started,
        extraDetailPixelsPercent=50,extraTotalInputPixelsPercent=100/3,
        control=b.ref(e.OUT/'run/last.pt'),candidateJustified=any(v['status']=='measured' and
            v['added']['proposalBoundaryCoverage'] is not None and
            v['added']['proposalBoundaryCoverage']>v['original']['proposalBoundaryCoverage']+.02 for v in records)))
    print('Boundary audit',len(records),flush=True)


def train():
    import gc
    import report291
    started=time.monotonic();t.set_num_threads(2)
    b.require(b.read(OUT/'audit.json')['candidateJustified'],'no_coverage_gain')
    b.require(not (OUT/'run').exists(),'output_collision');(OUT/'run').mkdir()
    settings=b.read(OUT/'config.json');arms=settings['arms']
    balance=settings.get('balance342',False);preservation=settings.get('preservationWeight',0.)
    b.require(type(balance) is bool and preservation in (0.,1.) and (balance or not preservation),'balance_scope')
    b.require(len(arms)==1 and arms[0] in ('added-detail','added-detail-and-content'),'bounded_arm')
    reg=b.read(e.OUT/'inputs.json');reg['trainer']=b.ref(Path(b.trainer.__file__))
    config=dict(reg['configuration'],addedBoundary341=True)
    b.write(OUT/'registration.json',dict(control=b.ref(e.OUT/'run/last.pt'),
        runner=b.ref(Path(__file__)),trainer=reg['trainer'],membership=b.ref(b.PACKAGE/'membership.json'),
        audit=b.ref(OUT/'audit.json'),negatives=b.ref(OUT/'negatives.json'),configuration=config,
        selection='fixed-last',rolesChanged=False,thresholds=[.15,.85],
        arms=arms,balance342=balance,preservationWeight=preservation,secondsPerArm=1800,bytesPerArm=2*1024**3))
    e.f.OUT=OUT
    values,details,labels,weights,aux,ad,ay,indices=e.f.prepare(reg)
    membership=b.read(b.PACKAGE/'membership.json')
    source=r.s.c.prepare()[-1]
    rows=r.s.schedule_rows(membership,source,labels)
    extra=added_details(values,rows)
    original_hash=e.f.digest(details)
    details=np.concatenate((details,extra),1);del extra;gc.collect()
    b.require(e.f.digest(details[:,:12])==original_hash,'original_crops_changed')
    authored=b.read(OUT/'preparation.json')['rows']
    ad=np.concatenate((ad,added_details(aux,authored)),1)
    negatives=b.read(OUT/'negatives.json')['rows']
    b.require(len(negatives)>0,'no_negatives')
    nx=np.stack([r.s.encoded(*[r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in negatives])
    nd,_=r.prepare(nx,negatives,2);nd=np.concatenate((nd,added_details(nx,negatives)),1)
    # Keep the existing auxiliary schedule. Replace half its negative updates in the second arm.
    mixed=np.concatenate((aux,nx));mixed_details=np.concatenate((ad,nd));mixed_indices=indices.copy()
    positions=np.flatnonzero(labels==0)[::2]
    mixed_indices[positions]=len(aux)+np.arange(len(positions))%len(nx)
    if balance:
        import balance342
        decision=b.read(OUT/'balance-audit.json')
        b.require(decision['balancedJustified'] and (not preservation or decision['preservationJustified']),'balance_evidence')
        mixed_indices=balance342.schedule(labels,authored,indices,len(nx),config['epochs'])
        b.require(np.array_equal(np.concatenate((ay,np.zeros(len(nx))))[mixed_indices],
                                np.tile(labels,(config['epochs'],1))),'rotating_labels')
        b.write(OUT/'schedule.json',dict(indices=mixed_indices.tolist(),sha256=e.f.digest(mixed_indices),
            epochs=config['epochs'],rolesChanged=False))
    b.write(OUT/'views.json',dict(originalCropsSHA256=original_hash,originalPreserved=True,
        addedViewsSHA256=e.f.digest(details[:,12:]),auxiliarySHA256=e.f.digest(ad),
        matchedNegatives=len(nx),replacedAuxiliaryUpdates=len(positions),trainingViews=len(values)))
    for arm in arms:
        folder=OUT/'run'/arm;folder.mkdir();begin=time.monotonic();net=model()
        avalues,adt,ids=(aux,ad,indices) if arm=='added-detail' else (mixed,mixed_details,mixed_indices)
        extra_args={}
        if preservation:
            def reference(x,d):
                outputs=[]
                with t.inference_mode():
                    for start in range(0,len(x),8):
                        values=t.from_numpy(np.concatenate((x[start:start+8],d[start:start+8,:12]),1))
                        outputs.append(net.change.whole(values).flatten().detach())
                return t.cat(outputs)
            original_reference=reference(values,details)
            # New negatives have no preservation target. Zero logits remain outside the confidence mask.
            auxiliary_reference=t.cat((reference(aux,ad),t.zeros(len(nx))))
            extra_args=dict(preservation_logits=original_reference,auxiliary_preservation_logits=auxiliary_reference,
                            preservation_weight=preservation)
        def progress(row):
            b.write(folder/f"epoch-{row['epoch']:04d}.json",row)
            print(arm,row,flush=True)
            import research_queue as q
            q.save(OUT.parent/'progress.json',dict(step='Train '+arm,completed=row['epoch'],total=30,
                unit='epochs',updatedAt=time.time()),replace=True)
            b.require(time.monotonic()-begin<1800,'training_timeout')
        net,history=b.trainer.fit(net,t.from_numpy(values),t.from_numpy(labels),config,progress,
            t.from_numpy(weights),detail_inputs=t.from_numpy(details),auxiliary_inputs=t.from_numpy(avalues),
            auxiliary_detail=t.from_numpy(adt),auxiliary_indices=t.from_numpy(ids),auxiliary_weight=.25,**extra_args)
        t.save(dict(state=net.state_dict(),representation='additive341-v1'),folder/'last.pt')
        restored=load(folder/'last.pt');sanity=np.concatenate((values[:8],details[:8]),1)
        b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'reload_parity')
        b.write(folder/'fit.json',dict(history=history,seconds=time.monotonic()-begin,originalFrozen=True,checkpointParity=True))
        del net,restored;gc.collect()
    del values,details,aux,ad,mixed,mixed_details,nx,nd;gc.collect()
    native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    original,_=r.prepare(native,membership['rows'],2)
    native_detail=np.concatenate((original,added_details(native,membership['rows'])),1)
    for arm in arms:
        folder=OUT/'run'/arm;net=load(folder/'last.pt')
        def transform(key,x):
            if key=='native.npy':return np.concatenate((x,native_detail),1)
            if key=='reverse_native.npy':return np.concatenate((x,r.reverse_details(native_detail)),1)
            return x
        result=b.evaluate_full(net,{},b.read(b.PACKAGE/'manifest.json'),input_transform=transform)
        b.write(folder/'evaluation.json',result)
        summary,cases=report291.summarize_comparison(b.read(e.OUT/'run/evaluation.json'),result,membership)
        tiny,trows,_=r.s.tiny_rows();td,_=r.prepare(tiny,trows,2)
        tx=np.concatenate((tiny,td,added_details(tiny,trows)),1)
        probs=b.worker.score(net,tx)
        b.write(folder/'comparison.json',dict(summary=summary,cases=cases,tinyProbabilities=probs.tolist(),
            tinySummary=b.trainer.w.summary(probs,np.array([v['changed'] for v in trows])),productionEligible=False))
        print(arm,summary,flush=True)
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,productionEligible=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['generate','audit','train'])
    globals()[parser.parse_args().mode]()
