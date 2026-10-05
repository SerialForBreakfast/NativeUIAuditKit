"""Independent bounded CPU replay; never import the returned worker implementation."""
import gzip
import json
import time
import numpy as np
import worker_eval161 as v
from replay_spatial163 import region
from diagnose_reflow115 import decisions
h=v.h
BASE=h.ROOT/'reports/work/WORKER-ENVELOPE-166/artifacts/return01'
COUNT=286*768
FRACTIONS=(.125,.25,.5)
TRANSFORMS=((.6,.2),(.8,.1),(1.,.12),(1.,-.12))


def spec(i):
    h.require(type(i) is int and 0<=i<COUNT,'index_range')
    c,k=divmod(i,768);cell,k=divmod(k,12);size,t=divmod(k,4);gy,gx=divmod(cell,8)
    return c,gy,gx,size,t


def bounds(rect,gy,gx,size):
    h.require(gy in range(8) and gx in range(8) and size in range(3),'grid_range')
    x0,y0,x1,y1=rect;w,ht=x1-x0,y1-y0
    h.require(w>0 and ht>0,'empty_rect')
    ew,eh=max(1,int(w*FRACTIONS[size])),max(1,int(ht*FRACTIONS[size]))
    a=int((gx+.5)*w/8)-ew//2;b=int((gy+.5)*ht/8)-eh//2
    return [x0+max(0,a),y0+max(0,b),x0+min(w,a+ew),y0+min(ht,b+eh)]


def transform(torch,pair,rect,i):
    _,gy,gx,size,t=spec(i);a,b,c,d=bounds(rect,gy,gx,size)
    out=pair.clone();gain,offset=TRANSFORMS[t]
    out[3:,b:d,a:c]=torch.round((pair[3:,b:d,a:c]*gain+offset).clamp(0,1)*255)/255
    return out


def sample_indices():
    # Every source case and every spatial/size/photometric cell, independent of scores.
    return sorted({c*768+(c*37)%768 for c in range(286)}|
                  {(cell%286)*768+cell for cell in range(768)})


def checked_scores(chunks):
    vectors=[[] for _ in range(3)];mi=0;start=0
    for q in chunks:
        h.require(mi<3 and q['model']==mi and q['start']==start,'chunk_order')
        p=np.asarray(q['probabilities'],np.float32)
        h.require(p.ndim==1 and len(p)==min(1024,COUNT-start) and
                  np.isfinite(p).all() and ((p>=0)&(p<=1)).all(),'chunk_values')
        vectors[mi].extend(p.tolist());start+=len(p)
        if start==COUNT:mi+=1;start=0
    h.require(mi==3 and start==0,'incomplete_scores')
    return np.asarray(vectors,np.float32)


def run():
    started=time.monotonic();output=BASE/'evaluation.json';h.require(not output.exists(),'output_collision')
    root=BASE/'extracted';work=root/'reports/work/ENVELOPE166/attempt01'
    for ref in h.read(root/'inventory.json',1024**2):v.w.t.verified(root/ref['path'],ref)
    pins=h.read(work/'pins.json',2*1024**2);state=h.read(work/'cursor.json',2*1024**2)
    h.require(state['state']=='completed' and state['model']==3 and state['next']==0 and
              state['pinsSHA256']==h.sha(work/'pins.json'),'terminal_pins')
    cfg=pins['config'];h.require(cfg['count']==COUNT and cfg['grid']==8 and cfg['batch']==32 and
        cfg['fractions']==list(FRACTIONS) and cfg['transforms']==[list(x) for x in TRANSFORMS] and
        cfg['thresholds']==[.15,.85] and cfg['trainingUpdates']==0,'configuration')
    h.require(pins['request']['sha256']==h.sha(h.ROOT/'reports/coordination/worker166-request.json'),'request_pin')
    for name,ref in pins['sources'].items():h.require(h.sha(h.ROOT/'scripts'/name)==ref['sha256'],'source_pin')
    def local_ref(ref):
        p=v.w.t.path_under(root,ref['file']);v.w.t.verified(p,ref);return p
    vectors=checked_scores(h.read(local_ref(entry['file'])) for entry in state['chunks'])
    torch=v.n.d.torch_runtime();torch.set_num_threads(2)
    export=v.w.BASE.parent/'export01/payload';maskroot=v.BASE.parent/'export01/payload'
    for directory in (export,maskroot):
        for ref in v.w.t.document(directory/'manifest.json')['files']:v.w.t.verified(directory/ref['path'],ref)
    data=torch.load(export/'training.pt',weights_only=True,map_location='cpu')
    mask=torch.load(maskroot/'masks.pt',weights_only=True,map_location='cpu')['contentMask']
    _,_,groups=v.derived(torch,data['images'],data['labels'],mask)
    images=torch.cat([data['images'],groups['identity']]);h.require(v.digest(images)==pins['imagesSHA256'],'input_pin')
    endpoints={}
    for row,m in zip(data['images'],mask):
        for offset in (0,3):endpoints.setdefault(v.digest(row[offset:offset+3]),m[offset:offset+3])
    masks=list(mask[:,3:])+list(endpoints.values());rects=[]
    for m in masks:
        full=region(m.numpy(),'full');ys,xs=np.nonzero(full[0])
        rects.append([int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1])
    h.require(rects==pins['rects'] and len(pins['cases'])==286,'mask_case_binding')
    indices=sample_indices();chosen=set(indices);tensors={};seen=set();metadata=local_ref(pins['metadata'])
    with gzip.open(metadata,'rt') as stream:
        count=0
        for line in stream:
            h.require(count<COUNT and len(line)<10000,'metadata_bound')
            row=json.loads(line);c,gy,gx,size,t=spec(count)
            h.require([row[k] for k in ('index','case','gy','gx','size','transform')]==[count,c,gy,gx,size,t]
                and row['box']==bounds(rects[c],gy,gx,size),'metadata_identity')
            seen.add(row['tensorSHA256'])
            if count in chosen:
                value=transform(torch,images[c],rects[c],count)
                h.require(v.digest(value)==row['tensorSHA256'],'sample_tensor_hash');tensors[count]=value
            count+=1
        h.require(count==COUNT and len(seen)==pins['uniqueVariantTensors'],'metadata_count')
    sample=torch.stack([tensors[i] for i in indices]);report={}
    peer=h.read(work/'report/aggregates.json',4*1024**2)
    labels=np.asarray([r['label'] for r in pins['cases']]);h.require(np.array_equal(labels[:108],data['labels'].numpy()) and (labels[108:]==0).all(),'labels')
    for mi,runid in enumerate(('DTM050','DTM051','DTM052')):
        checkpoint=v.BASE/'extracted'/runid/'last.pt';h.require(h.sha(checkpoint)==pins['checkpoints'][runid]['sha256'],'checkpoint_pin')
        net=v.checked(torch,v.n.make_model(torch,paired_context=True),torch.load(checkpoint,weights_only=True,map_location='cpu'),runid)
        baseline=v.n.score(net,images);p=v.n.score(net,sample)
        expected=np.asarray(state['baselines'][runid],np.float32);gpu=vectors[mi,indices]
        h.require(expected.shape==(286,) and np.isfinite(expected).all() and ((expected>=0)&(expected<=1)).all(),'baseline_values')
        h.require(np.array_equal(decisions(baseline),decisions(expected)) and np.array_equal(decisions(p),decisions(gpu)),'categorical_replay')
        delta=float(np.max(np.abs(p-gpu)));h.require(delta<=1e-4,'numerical_replay')
        cats=decisions(vectors[mi]);bc=np.repeat(decisions(expected),768)
        totals=dict(unchanged=int((cats==0).sum()),changed=int((cats==1).sum()),abstentions=int((cats==-1).sum()),
            confidentFlips=int(((cats!=-1)&(bc!=-1)&(cats!=bc)).sum()),baselineLabelAgreement=int((cats==np.repeat(labels,768)).sum()))
        h.require(totals==peer['totals'][mi],'aggregate_mismatch')
        report[runid]=dict(totals=totals,maximumProbabilityDifference=delta,sampleScores=len(indices),baselineScores=286)
        print(runid,report[runid],flush=True)
    h.write(output,dict(results=report,allScoresAccountedFor=3*COUNT,sampleIndices=indices,source=h.ref(__file__),
        inventory=h.ref(root/'inventory.json'),seconds=time.monotonic()-started,productionEligible=False,
        limitation='Sampled independent inference replay; all score totals verified. Related-source counterfactual diagnostics, not native accuracy or new labels.'),sealed=True)


if __name__=='__main__':run()
