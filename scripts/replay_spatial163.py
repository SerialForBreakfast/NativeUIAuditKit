"""Resident-source replay of SPATIAL163; returned source is evidence, never executed."""
import time
import numpy as np
import worker_eval161 as v
from diagnose_reflow115 import decisions
h=v.h
BASE=h.ROOT/'reports/work/WORKER-SPATIAL-163/artifacts/return01'
ARMS=('full','left','right','top','bottom','center','middleVertical','middleHorizontal')


def region(mask,arm):
    h.require(mask.dtype==np.bool_ and mask.ndim==3 and mask.shape[0]==3,'mask_shape')
    h.require(np.array_equal(mask[0],mask[1]) and np.array_equal(mask[0],mask[2]),'mask_channels')
    ys,xs=np.nonzero(mask[0]);h.require(len(xs)>0,'empty_mask')
    x0,x1=int(xs.min()),int(xs.max())+1;y0,y1=int(ys.min()),int(ys.max())+1
    h.require(mask[:,y0:y1,x0:x1].all(),'mask_rectangle')
    w,ht=x1-x0,y1-y0;mx=x0+w//2;my=y0+ht//2
    lx,rx=x0+w//4,x0+3*w//4;ty,by=y0+ht//4,y0+3*ht//4
    boxes=dict(full=(x0,y0,x1,y1),left=(x0,y0,mx,y1),right=(mx,y0,x1,y1),
        top=(x0,y0,x1,my),bottom=(x0,my,x1,y1),center=(lx,ty,rx,by),
        middleVertical=(lx,y0,rx,y1),middleHorizontal=(x0,ty,x1,by))
    h.require(arm in boxes,'unknown_arm');a,b,c,d=boxes[arm]
    out=np.zeros_like(mask);out[:,b:d,a:c]=mask[:,b:d,a:c]
    h.require(out.any(),'empty_region');return out


def run():
    start=time.monotonic();output=BASE/'evaluation.json';h.require(not output.exists(),'output_collision')
    torch=v.n.d.torch_runtime();torch.set_num_threads(2)
    root=BASE/'extracted';manifest=v.w.t.document(root/'manifest.json')
    for ref in manifest['files']:v.w.t.verified(root/ref['file'],ref)
    # These hash-verified numerical artifacts exceed the status-YAML event cap.
    pins=h.read(root/'evidence/attempt01/manifest.json',1024**2);peer=h.read(root/'evidence/attempt01/results.json',1024**2)
    h.require(peer['request_id']=='nuiak-20261004-worker-spatial163' and peer['state']=='completed'
        and peer['training_updates']==0 and peer['scores']==5130,'peer_completion')
    c=pins['configuration'];h.require(c['arms']==list(ARMS) and c['gain']==.8 and c['offset']==.1
        and c['thresholds']==[.15,.85] and c['batch']==8,'configuration')
    for name,ref in pins['source'].items():h.require(h.sha(h.ROOT/'scripts'/name)==ref['sha256'],'source_identity')
    export=v.w.BASE.parent/'export01/payload';maskroot=v.BASE.parent/'export01/payload'
    for directory in (export,maskroot):
        for ref in v.w.t.document(directory/'manifest.json')['files']:v.w.t.verified(directory/ref['path'],ref)
    original=torch.load(export/'training.pt',weights_only=True,map_location='cpu')
    masks=torch.load(maskroot/'masks.pt',weights_only=True,map_location='cpu')['contentMask']
    x,y=original['images'],original['labels'];_,_,groups=v.derived(torch,x,y,masks)
    endpoints={}
    for row,mask in zip(x,masks):
        for offset in (0,3):endpoints.setdefault(v.digest(row[offset:offset+3]),mask[offset:offset+3])
    h.require(list(endpoints)==pins['endpointOrder'],'endpoint_order')
    controls=groups['identity'];ms=list(endpoints.values());results={}
    for runid in ('DTM050','DTM051','DTM052'):
        checkpoint=v.BASE/'extracted'/runid/'last.pt'
        h.require(h.sha(checkpoint)==pins['checkpoints'][runid]['sha256']==peer['models'][runid]['checkpoint']['sha256'],'checkpoint_identity')
        saved=torch.load(checkpoint,weights_only=True,map_location='cpu')
        net=v.checked(torch,v.n.make_model(torch,paired_context=True),saved,runid);scores={}
        for arm in ('original','identity')+ARMS:
            if arm=='original':values=x
            elif arm=='identity':values=controls
            else:
                selected=torch.from_numpy(np.stack([region(m.numpy(),arm) for m in ms]))
                values=controls.clone();values[:,3:]=torch.where(selected,torch.round((values[:,3:]*.8+.1).clamp(0,1)*255)/255,values[:,3:])
                h.require(v.digest(values)==pins['arms'][arm]['tensorSHA256'],'derived_tensor_identity')
            p=v.n.score(net,values);expected=np.asarray(peer['models'][runid]['groups'][arm]['probabilities'],dtype=np.float32)
            h.require(p.shape==expected.shape and np.isfinite(expected).all() and np.all((expected>=0)&(expected<=1)),'probability_contract')
            h.require(np.array_equal(decisions(p),decisions(expected)),'categorical_replay')
            scores[arm]=dict(summary=v.w.summary(p,y.numpy() if arm=='original' else np.zeros(len(p))),
                maximumCUDAProbabilityDifference=float(np.abs(p-expected).max()))
        results[runid]=scores;print(runid,scores['bottom'],flush=True)
    h.write(output,dict(results=results,scores=5130,seconds=time.monotonic()-start,source=h.ref(__file__),
        manifest=h.ref(root/'manifest.json'),peerResults=h.ref(root/'evidence/attempt01/results.json'),
        interpretation='Counterfactual appearance agreement, not native accuracy or training admission',productionEligible=False),sealed=True)


if __name__=='__main__':run()
