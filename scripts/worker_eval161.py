"""Independent ROBUST153 tensor reconstruction and resident-source CPU evaluation."""
import hashlib
import json
import time
import numpy as np
import native_adapt152 as n
import worker_candidate151 as w
from diagnose_reflow115 import decisions
h=n.h
BASE=h.ROOT/'reports/work/WORKER-ROBUST-153/artifacts/return01'


def digest(tensor):return hashlib.sha256(tensor.contiguous().numpy().tobytes()).hexdigest()


def derived(torch,x,y,mask):
    h.require(x.shape==mask.shape and mask.dtype==torch.bool and x.shape==(108,6,128,192) and y.shape==(108,), 'original_membership')
    endpoints={}
    for i in range(len(x)):
        for side in (0,1):
            im=x[i,side*3:side*3+3];m=mask[i,side*3:side*3+3];key=digest(im)
            if key in endpoints:h.require(torch.equal(endpoints[key][1],m),'endpoint_mask_conflict')
            else:endpoints[key]=(im,m)
    h.require(len(endpoints)==178,'endpoint_count')
    controls=torch.stack([torch.cat([im,im]) for im,_ in endpoints.values()])
    masks=torch.stack([m for _,m in endpoints.values()])
    def transform(gain,offset):
        out=controls.clone();out[:,3:]=torch.where(masks,torch.round((out[:,3:]*gain+offset).clamp(0,1)*255)/255,out[:,3:])
        h.require(torch.equal(out[:,:3],controls[:,:3]) and torch.equal(out[:,3:][~masks],controls[:,3:][~masks]),'padding_or_before_changed')
        return out
    groups=dict(original=x,reverse=torch.cat([x[:,3:],x[:,:3]],1),identity=controls)
    for i,(gain,offset) in enumerate(((.6,.2),(.8,.1),(1.,.12))):groups['nuisance'+str(i)]=transform(gain,offset)
    train=torch.cat(list(groups.values()));labels=torch.cat([y,y,torch.zeros(712)])
    groups['withheld_related_diagnostic']=transform(.9,.04)
    return train,labels,groups


def checked(torch,net,saved,run):
    c=saved['pins']['configuration'];cursor=saved['cursor'];control=run=='DTM052'
    expected=dict(run_id=run,seed=43 if run=='DTM051' else 42,kind='control' if control else 'augmented',
        rows=286 if control else 928,optimizer_updates=69600,batch=8,optimizer='Adam',lr=.001,
        loss='BCEWithLogitsLoss unweighted mean',device='cuda:0',dtype='float32',amp=False,tf32=False,compile=False,
        selection='fixed-last',thresholds=[.15,.85],deterministic=True,pool_adapter='fixed8x8-equivalent-v1',maximum_seconds=28800)
    h.require(saved['version']=='robust153-checkpoint-v1' and c==expected and cursor['steps']==69600 and
        cursor['epoch']==(1933 if control else 600) and cursor['next_batch']==(12 if control else 0),'checkpoint_completion_config')
    refs=net.state_dict();state=saved['model'];h.require(set(refs)==set(state),'state_keys')
    for k,v in state.items():h.require(isinstance(v,torch.Tensor) and v.shape==refs[k].shape and v.dtype==refs[k].dtype and torch.isfinite(v).all(),'state_tensor')
    net.load_state_dict(state);return net.eval()


def run():
    started=time.monotonic();torch=n.d.torch_runtime();torch.set_num_threads(2)
    root=BASE/'extracted';manifest=w.t.document(root/'manifest.json')
    for ref in manifest['files']:w.t.verified(root/ref['file'],ref)
    for name in ('focus_spatial_transition.py','focus_temporal_transition.py'):
        h.require((root/'sources'/name).read_bytes()==(h.ROOT/'scripts'/name).read_bytes(),'source_architecture')
    export=w.BASE.parent/'export01/payload';original_manifest=w.t.document(export/'manifest.json')
    for ref in original_manifest['files']:w.t.verified(export/ref['path'],ref)
    original=torch.load(export/'training.pt',weights_only=True,map_location='cpu');ox=original['images'];oy=original['labels']
    maskroot=BASE.parent/'export01/payload';mm=w.t.document(maskroot/'manifest.json')
    for ref in mm['files']:w.t.verified(maskroot/ref['path'],ref)
    mask=torch.load(maskroot/'masks.pt',weights_only=True,map_location='cpu')['contentMask']
    h.require(digest(mask)==mm['maskBytesSHA256'] and h.sha(export/'training.pt')==mm['trainingTensorSHA256'],'mask_binding')
    train,labels,groups=derived(torch,ox,oy,mask)
    x,y,localmask,localgroups,px,peer_rows,ids,ny,_,_=n.inputs()
    results={}
    for runid in ('DTM050','DTM051','DTM052'):
        saved=torch.load(root/runid/'last.pt',weights_only=True,map_location='cpu');pins=saved['pins']
        net=checked(torch,n.make_model(torch,paired_context=True),saved,runid)
        selected=torch.cat([ox,groups['identity']]) if runid=='DTM052' else train
        sy=torch.cat([oy,torch.zeros(178)]) if runid=='DTM052' else labels
        h.require(digest(selected)==pins['training_images_sha256'] and digest(sy)==pins['training_labels_sha256'] and
            pins['mask_sha256']==digest(mask) and pins['original_pins']['data']['sha256']==h.sha(export/'training.pt') and
            pins['request']['sha256']==h.sha(h.ROOT/'reports/coordination/worker153-request.json') and
            pins['prepared_manifest']['sha256']==h.sha(root/'prepared/manifest.json'),'checkpoint_data_pins')
        metrics=w.t.document(root/runid/'metrics.json');replay={}
        for name,values in groups.items():
            p=n.score(net,values);truth=oy.numpy() if name in ('original','reverse') else np.zeros(len(values))
            gpu=np.asarray(metrics['groups'][name]['probabilities'],np.float32)
            h.require(gpu.shape==p.shape and np.array_equal(decisions(p),decisions(gpu)),'cpu_cuda_decisions')
            replay[name]=dict(summary=w.summary(p,truth),maximumCUDAProbabilityDifference=float(np.abs(p-gpu).max()))
        lp=n.score(net,torch.from_numpy(x));npred=n.score(net,torch.from_numpy(px))
        reverse=n.score(net,torch.from_numpy(np.concatenate([x[:,3:],x[:,:3]],axis=1)))
        stress={}
        for mode in ('global8','left8','center8'):
            p=n.score(net,torch.from_numpy(n.nuisance.localized(x[207:],localmask[207:],mode)))
            stress[mode]=dict(summary=w.summary(p,np.zeros(len(p))),probabilities=p.tolist())
        h.require(np.array_equal(npred,n.score(net,torch.from_numpy(px))),'local_repeatability')
        results[runid]=dict(checkpoint=h.ref(root/runid/'last.pt'),workerReplay=replay,
            groups={k:w.summary(lp[v],y[v]) for k,v in localgroups.items()},
            reversal={k:w.summary(reverse[v],y[v]) for k,v in localgroups.items()},
            native=w.summary(npred[ids],ny),nativeCases=[dict(r,probability=float(p),scored=i in ids) for i,(r,p) in enumerate(zip(peer_rows,npred))],
            probabilities=lp.tolist(),stress=stress,localRepeatability=True)
        print(runid,results[runid]['groups'],results[runid]['native'],flush=True)
    h.write(BASE/'evaluation.json',dict(version='worker-eval161-v1',results=results,source=h.ref(__file__),
        mask=h.ref(maskroot/'manifest.json'),data=h.ref(export/'training.pt'),seconds=time.monotonic()-started,
        independentEvaluation=False,productionEligible=False,backend='resident source CPU float32 batch8',
        limitation='Retained development evidence, not independent release qualification. Geometry branch remains untrained.'),sealed=True)


if __name__=='__main__':run()
