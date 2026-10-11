"""Compare one and two detail windows while freezing the original classifier."""
import argparse
import gc
from pathlib import Path
import time
import types
import numpy as np
import source310 as s

b=s.base;t=s.torch
OUT=b.ROOT/'reports/work/FOCUS-313'
VERSION='regions313-v1'


def windows(values):
    b.require(values.ndim==4 and values.shape[1:]==(6,128,192),'window_shape')
    residual=s.c.model.change_inputs(None,values)[:,9:].mean(1,keepdim=True)
    energy=t.nn.functional.avg_pool2d(residual,5,stride=1,padding=2)[:,0]
    first=s.boxes(values);result=[]
    yy,xx=t.meshgrid(t.arange(97,device=values.device),t.arange(161,device=values.device),indexing='ij')
    for i,(x,y) in enumerate(first):
        if not t.count_nonzero(residual[i]):result.append([]);continue
        # Score legal top-left positions. The second window cannot overlap the first.
        scores=t.nn.functional.avg_pool2d(energy[i:i+1,None],32,stride=1)[0,0].clone()
        overlaps=(xx<x+32)&(xx+32>x)&(yy<y+32)&(yy+32>y)
        scores[overlaps]=-1
        peak=int(scores.flatten().argmax());second=(peak%161,peak//161)
        result.append([(x,y),second] if float(scores.flatten()[peak])>0 else [(x,y)])
    return result


def encoded_details(values,count):
    output=t.zeros(len(values),6*count,128,192,dtype=values.dtype,device=values.device)
    for i,boxes in enumerate(windows(values)):
        for j in range(count):
            target=output[i,j*6:(j+1)*6]
            if not boxes:target.copy_(values[i]);continue
            x,y=boxes[min(j,len(boxes)-1)]
            target[:,:,32:160]=t.nn.functional.interpolate(values[i:i+1,:,y:y+32,x:x+32],
                size=(128,128),mode='bilinear',align_corners=False)[0]
    return output


class RegionChange(s.SourceChange):
    def __init__(self,old,count):
        super().__init__(old,True);self.count=count

    def forward(self,images):
        b.require(images.shape[1] in (6,6+6*self.count),'region_channels')
        whole=images[:,:6]
        details=images[:,6:] if images.shape[1]>6 else encoded_details(whole,self.count)
        context=self.whole[:10](s.c.model.change_inputs(None,whole))
        features=[self.detail(s.c.model.change_inputs(None,details[:,6*j:6*(j+1)])) for j in range(self.count)]
        pooled=t.stack(features).mean(0)
        return self.whole[10](context)+self.correction(t.cat((context,pooled),1))


def extend(net,count):
    b.require(type(count) is int and count in (1,2),'window_count')
    net.change=RegionChange(net.change,count)
    net.change_inputs=types.MethodType(s.previous.identity_inputs,net)
    return net


def load_candidate(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION,'checkpoint_version')
    net=extend(s.c.model.extend(b.worker.make_model(t,paired_context=True)),saved['windows'])
    net.load_state_dict(saved['state']);return net.eval()


def prepare(values,rows,count):
    output=np.empty((len(values),6*count,128,192),np.float32);audit=[]
    for start in range(0,len(values),8):
        part=t.from_numpy(np.array(values[start:start+8]));selected=windows(part)
        output[start:start+len(part)]=encoded_details(part,count).numpy()
        for k,boxes in enumerate(selected):
            i=start+k;row=rows[i];delta=np.abs(values[i,:3]-values[i,3:]).mean(0)
            mask=np.zeros((128,192),bool)
            for x,y in boxes[:count]:mask[y:y+32,x:x+32]=True
            if row is not None:
                images=[s.image(r['path'],r['sha256']) for r in row['images']]
                b.require(images[0].size==images[1].size,'frame_size')
                b.require(np.array_equal(s.encoded(*images,(192,128))[0],values[i]),'source_encoding_parity')
                for j in range(count):
                    if not boxes:continue
                    x,y=boxes[min(j,len(boxes)-1)]
                    output[i,6*j:6*(j+1)]=s.crop_pair(images,[x,y,x+32,y+32],preserve_padding=True)
            audit.append(dict(index=i,windows=boxes[:count],sourceAvailable=row is not None,
                images=None if row is None else row['images'],
                energyFraction=None if not delta.sum() else float(delta[mask].sum()/delta.sum())))
    return output,audit


def reverse_details(values):
    return np.concatenate([b.reporting.reverse(values[:,j:j+6]) for j in range(0,values.shape[1],6)],1)


def run(out):
    b.require(not out.exists(),'output_collision');t.set_num_threads(2);started=time.monotonic()
    manifest,membership,full,labels,weights,extra,controls,_,reg=s.c.prepare()
    added=s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    parent=b.ROOT/'reports/work/TRANSITION-292/DTM085'
    b.require(b.sha(values.tobytes())==b.read(parent/'registration.json')['trainingSHA256'],'schedule_identity')
    initializer=b.checked(b.read(parent/'result.json')['model']);rows=s.schedule_rows(membership,reg,labels)
    config=dict(reg['configuration'],epochs=30,detailOnly=True)
    out.mkdir(parents=True)
    b.write(out/'registration.json',dict(version=VERSION,runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),
        sourceHelper=b.ref(Path(s.__file__)),cropper=b.ref(b.ROOT/'scripts/detail307.py'),initializer=b.ref(initializer),
        configuration=config,trainingSHA256=b.sha(values.tobytes()),labelsSHA256=b.sha(labels.tobytes()),
        weightsSHA256=b.sha(weights.tobytes()),membership=b.ref(b.PACKAGE/'membership.json'),
        hypothesis='Two detail regions recover distant changes without adapting the original classifier.',
        thresholds=[.15,.85],selection='fixed-last',rolesChanged=False,outputCapBytes=128*1024**2,
        memoryLimitBytes=8*1024**3,wallTimeLimit=None,torchVersion=str(t.__version__),
        acceptance='Improve tiny decisions without losing previous correct decisions.',
        emptyRegion='Repeat the first detail when no positive second region exists; identical pairs use full frames.'))
    refs={'DTM085':s.c.model.load_candidate(initializer)};completed={}
    native=np.load(b.PACKAGE/'native.npy',allow_pickle=False);tiny,trows,tpin=s.tiny_rows()
    for count in (1,2):
        folder=out/f'regions-{count}';folder.mkdir();begin=time.monotonic()
        detail,audit=prepare(values,rows,count)
        b.write(folder/'views.json',dict(sha256=b.sha(detail.tobytes()),rows=audit))
        t.manual_seed(42);net=extend(s.c.model.load_candidate(initializer),count)
        frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith(('change.detail.','change.correction.'))}
        sanity=np.concatenate((values[:8],detail[:8]),1)
        delta=float(np.abs(b.worker.score(net,sanity)-b.worker.score(refs['DTM085'],values[:8])).max())
        b.require(delta<=1e-6,'initial_parity')
        b.write(folder/'registration.json',dict(parent=b.ref(out/'registration.json'),windows=count,
            parameters=sum(p.numel() for p in net.parameters()),maximumInitialError=delta,views=b.ref(folder/'views.json')))
        def progress(row):b.write(folder/f"epoch-{row['epoch']:04d}.json",row);print(count,row,flush=True)
        net,history=b.trainer.fit(net,t.from_numpy(values),t.from_numpy(labels),config,progress,
            t.from_numpy(weights),detail_inputs=t.from_numpy(detail))
        b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_branch_changed')
        t.save(dict(state=net.state_dict(),representation=VERSION,windows=count),folder/'last.pt')
        restored=load_candidate(folder/'last.pt')
        b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'reload_parity')
        b.write(folder/'fit.json',dict(history=history,frozenWeightsVerified=True,checkpointParity=True,seconds=time.monotonic()-begin))
        del detail,audit,net;gc.collect()
        native_detail,_=prepare(native,membership['rows'],count)
        def transform(key,x):
            if key=='native.npy':return np.concatenate((x,native_detail),1)
            if key=='reverse_native.npy':return np.concatenate((x,reverse_details(native_detail)),1)
            return x
        evaluation=b.evaluate_full(restored,refs,manifest,input_transform=transform)
        b.write(folder/'evaluation.json',evaluation)
        td,ta=prepare(tiny,trows,count);p=b.worker.score(restored,np.concatenate((tiny,td),1));small=[]
        for condition in sorted({r['condition'] for r in trows}):
            ids=[i for i,r in enumerate(trows) if r['condition']==condition]
            small.append(dict(condition=condition,summary=b.trainer.w.summary(p[ids],np.array([trows[i]['changed'] for i in ids])),probabilities=p[ids].tolist()))
        b.write(folder/'tiny.json',dict(input=tpin,results=small,windows=ta,independentFinalAudit=False))
        completed[str(count)]=dict(model=b.ref(folder/'last.pt'),tiny=small,regressionPassed=evaluation['regressionPassed'],seconds=time.monotonic()-begin)
        del native_detail,td,restored;gc.collect()
    size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());b.require(size<128*1024**2,'output_budget')
    b.write(out/'completion.json',dict(runs=completed,outputBytes=size,seconds=time.monotonic()-started,productionEligible=False,rolesChanged=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',required=True,action='store_true')
    parser.parse_args();run(OUT)
