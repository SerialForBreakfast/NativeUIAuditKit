"""Pinned resolution comparison using resident trainer/exporter/scorer unchanged."""
import argparse
import collections
import time
from types import SimpleNamespace
import yaml
import replay179 as r
import diagnose185 as d
h,p,e=r.h,r.p,r.e
BASE=h.ROOT/'reports/work/IOS-RESOLUTION-187/attempt04/artifacts'
CONTROL=h.ROOT/'reports/work/IOS-REPLAY-184/artifacts/experiment'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/resolution187-r024'
SIZE=1280
SETTINGS=dict(r.f.d.completed.SETTINGS,imgsz=SIZE)


def compatible(doc,control):
    h.require(doc['rows']==control['rows'] and len(doc['rows'])==432 and all(x['split']=='train' for x in doc['rows']),'membership_or_role')
    for k in ('initializer','membership','metadata','schedule'):h.require(doc[k]==control[k],'changed_'+k)
    expected=dict(control['args'],imgsz=SIZE,data=doc['args']['data'],name=RUN.name,project=str(RUN.parent))
    h.require(doc['args']==expected and expected['box']==7.5 and expected['batch']==8 and expected['epochs']==10,'changed_settings')


def bind():
    r.OUT=BASE;r.RUN=RUN


def prepare():
    h.require(not BASE.exists() and not RUN.exists(),'output_collision')
    control=p.sealed(CONTROL/'protocol.json')
    oldout=r.OUT
    try:r.OUT=CONTROL;r.inputs()
    finally:r.OUT=oldout
    for row in control['rows']:h.checked(h.ROOT,row['annotation'])
    doc=dict(control);doc.pop('seal');doc['args']=dict(control['args'],imgsz=SIZE,name=RUN.name,project=str(RUN.parent))
    old=d.exposure(control);new=d.exposure(doc)
    BASE.mkdir(parents=True);(BASE/'dataset').symlink_to(CONTROL/'dataset',target_is_directory=True)
    h.write(BASE/'input.json',h.read(CONTROL/'input.json'))
    e.load_request(BASE/'input.json',41)
    doc.update(input=h.ref(BASE/'input.json'),sources=control['sources']+[h.ref(__file__),h.ref(d.__file__),h.ref(CONTROL/'protocol.json')])
    compatible(doc,control)
    h.write(BASE/'protocol.json',doc,sealed=True)
    h.write(BASE/'exposure.json',dict(control=old,candidate=new,inputPixelRatio=new['totalInputPixelsPerEpoch']/old['totalInputPixelsPerEpoch']),sealed=True)
    print('Prepared1280;432unchanged members; no training',flush=True)


def verify():
    bind();doc=r.inputs();compatible(doc,p.sealed(CONTROL/'protocol.json'))
    for row in doc['rows']:h.checked(h.ROOT,row['annotation'])
    return doc


def enable_training_gradients(net):
    # Match resident DetectionTrainer's no-user-freeze policy. Loaded checkpoints
    # can have every parameter frozen even after Module.train().
    for name,value in net.named_parameters():
        if value.dtype.is_floating_point:value.requires_grad_('.dfl' not in name)
    h.require(any(x.requires_grad for x in net.parameters()),'no_trainable_parameters')


def loss_evidence(value):
    if isinstance(value,dict):return {k:loss_evidence(v) for k,v in value.items()}
    return value.detach().cpu().tolist()


def memory():
    doc=verify();dest=BASE/'memory.json';h.require(not dest.exists(),'output_collision')
    started=time.monotonic();out=dict(protocol=h.ref(BASE/'protocol.json'),candidateWeightsSaved=False)
    try:
        import torch
        from ultralytics import YOLO
        h.require(torch.backends.mps.is_available(),'mps_unavailable')
        exposure=p.sealed(BASE/'exposure.json')['candidate'];shape=max(exposure['batchShapes'],key=lambda x:x[0]*x[1])
        maxlabels=max(len(h.checked(h.ROOT,row['label']).read_text().splitlines()) for row in doc['rows'])
        torch.manual_seed(42);net=YOLO(str(h.checked(h.ROOT,doc['initializer'],256*1024**2))).model.to('mps').train()
        h.require(doc['args'].get('freeze') in (None,0,[]),'unexpected_freeze_policy')
        enable_training_gradients(net)
        net.args=SimpleNamespace(**doc['args']);optim=torch.optim.AdamW(net.parameters(),lr=.0001)
        boxes=torch.rand((8*maxlabels,4),device='mps');boxes[:,:2]=.2+.6*boxes[:,:2];boxes[:,2:]=.01+.1*boxes[:,2:]
        batch=dict(img=torch.rand((8,3,*shape),device='mps'),batch_idx=torch.arange(8,device='mps').repeat_interleave(maxlabels).float(),
            cls=(torch.arange(8*maxlabels,device='mps')%41).float().reshape(-1,1),bboxes=boxes)
        loss,items=net(batch);h.require(torch.isfinite(loss).all().item(),'nonfinite_probe_loss')
        loss.sum().backward();h.require(all(torch.isfinite(x.grad).all().item() for x in net.parameters() if x.grad is not None),'nonfinite_probe_gradient')
        optim.step();torch.mps.synchronize()
        out.update(passed=True,shape=[8,3,*shape],maxLabelsPerImage=maxlabels,loss=loss_evidence(items),allocatedBytes=torch.mps.current_allocated_memory(),driverBytes=torch.mps.driver_allocated_memory(),recommendedBytes=torch.mps.recommended_max_memory())
    except Exception as exc:
        out.update(passed=False,error=str(exc));raise
    finally:
        out['seconds']=time.monotonic()-started;h.write(dest,out,sealed=True)
    print('Memory preflight passed',out,flush=True)


def admission():
    verify();probe=p.sealed(BASE/'memory.json');h.require(probe['passed'] and probe['protocol']==h.ref(BASE/'protocol.json'),'memory_preflight_failed_or_changed')


def manifests():
    prior=r.f.d.inputs()
    return [('fit',r.f.OUT/'input.json'),('page',h.checked(h.ROOT,prior['evaluationManifests'][3])),('combined',h.checked(h.ROOT,prior['evaluationManifests'][0]))]


def infer():
    admission();cp=r.ready()
    for name,path in manifests():e.export_predictions(path,cp,BASE/(name+'-predictions.json'),'mps',imgsz=SIZE,discard_degenerate=True)


def report():
    admission();cp=r.ready();doc=verify();h.require(not (BASE/'evaluation.json').exists(),'output_collision');results={}
    for name,path in manifests():
        req=e.load_request(path,41);a=h.read(BASE/(name+'-predictions.json'),256*1024**2)
        e.validated_artifact(a,req,h.sha(cp),expected_settings=SETTINGS);results[name]=e.score(a,req,e.load_names())
        if name=='fit':
            cases=r.f.d.pages(req,a,e.load_names().index('pageControl'),doc['metadata'])
            for row in cases:
                row['resizedWidth']*=SIZE/640;row['resizedHeight']*=SIZE/640
            strata={s:dict(collections.Counter(row['disposition'] for row in cases if row['metadata']['placement']==s)) for s in ('leading','center','trailing')}
    reference=p.sealed(r.f.OUT/'evaluation.json');control=p.sealed(CONTROL/'evaluation.json')
    old={row['id']:row for row in control['fitCases']}
    transitions=[dict(id=row['id'],before=old[row['id']]['disposition'],after=row['disposition']) for row in cases]
    h.write(BASE/'evaluation.json',dict(results=results,strata=strata,assessment=r.assess(results,strata,reference),fitCases=cases,transitions=transitions,
        checkpoint=h.ref(cp),protocol=h.ref(BASE/'protocol.json'),control=h.ref(CONTROL/'evaluation.json'),settings=SETTINGS,
        comparisonScope='Same members; explicitly different train/inference resolution. Not equal compute or training-only effect.',productionEligible=False),sealed=True)
    print('187matched evaluation complete',flush=True)


def main(mode):
    if mode=='prepare':prepare()
    elif mode=='memory':memory()
    elif mode=='train':admission();r.train()
    else:globals()[mode]()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','memory','train','infer','report']);main(parser.parse_args().mode)
