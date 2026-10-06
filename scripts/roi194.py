"""One frozen ROI candidate, strict second-pass integration and matched scoring."""
import argparse
import collections
import csv
import importlib.metadata
import math
import os
import shutil
import time
from pathlib import Path
import yaml
import roi193 as r
from prediction_artifact import normalize_detections

h,p,e=r.h,r.p,r.e
OUT=h.ROOT/'reports/work/IOS-ROI-194/artifacts/attempt02'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/roi194-r025'


def prepare():
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    doc=p.sealed(r.OUT/'proposal.json');verification=p.sealed(r.OUT/'verification.json')
    h.require(verification['proposal']==h.ref(r.OUT/'proposal.json'),'verification_binding')
    for ref in doc['sources']+[doc['initializer']]:h.checked(h.ROOT,ref,256*1024**2)
    req=e.load_request(h.checked(h.ROOT,doc['membership']),41)
    h.require(len(req.images)==802 and doc['configurationReady'],'not_ready')
    for item in doc['evaluation'].values():e.load_request(h.checked(h.ROOT,item['manifest']),41)
    import ultralytics.engine.trainer as trainer
    args=dict(doc['args'],name=RUN.name,project=str(RUN.parent),exist_ok=False)
    h.require(args['epochs']==10 and args['batch']==8 and args['imgsz']==640 and not args['resume'],'changed_config')
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json',dict(proposal=h.ref(r.OUT/'proposal.json'),verification=h.ref(r.OUT/'verification.json'),
        sources=[h.ref(__file__),h.ref(r.__file__),h.ref(e.__file__),h.ref(h.ROOT/'scripts/eval_phase6a.py')],
        trainer=h.ref(trainer.__file__),packages={k:importlib.metadata.version(k) for k in ('torch','ultralytics','numpy','Pillow')},
        args=args,budgetBytes=2*1024**3,schedule=r.c.g.r.schedule(101,10,.25),productionEligible=False),sealed=True)


def inputs():
    doc=p.sealed(OUT/'protocol.json')
    for ref in doc['sources']+[doc['proposal'],doc['verification'],doc['trainer']]:h.checked(h.ROOT,ref,256*1024**2)
    for name,version in doc['packages'].items():h.require(importlib.metadata.version(name)==version,'dependency_changed')
    proposal=p.sealed(h.checked(h.ROOT,doc['proposal']))
    for ref in proposal['sources']+[proposal['initializer']]:h.checked(h.ROOT,ref,256*1024**2)
    e.load_request(h.checked(h.ROOT,proposal['membership']),41)
    return doc,proposal


def train():
    h.require(not RUN.exists() and not (OUT/'completion.json').exists(),'output_collision')
    doc,proposal=inputs();h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    import torch
    from ultralytics import YOLO
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    model=YOLO(str(h.checked(h.ROOT,proposal['initializer'],256*1024**2)));events=[];batch_index=[-1]
    def started(t):
        h.require(len(t.train_loader)==101 and t.args.nbs==64,'schedule')
        step=t.optimizer_step
        def counted():events.append(batch_index[0]);return step()
        t.optimizer_step=counted
    def batch(t):batch_index[0]+=1
    def budget(t):h.require(sum(x.stat().st_size for x in RUN.rglob('*') if x.is_file())<=doc['budgetBytes'],'budget')
    model.add_callback('on_train_start',started);model.add_callback('on_train_batch_start',batch);model.add_callback('on_model_save',budget)
    start=time.monotonic();h.write(OUT/'execution.json',dict(pid=os.getpid(),protocol=h.ref(OUT/'protocol.json')))
    try:
        model.train(**doc['args'])
        h.require(events==doc['schedule']['optimizerAt'],'optimizer_schedule_mismatch');budget(None)
        h.write(OUT/'completion.json',dict(exitCode=0,seconds=time.monotonic()-start,optimizerAt=events,checkpoint=h.ref(RUN/'weights/last.pt')),sealed=True)
    except Exception as exc:
        h.write(OUT/'completion.json',dict(exitCode=1,error=str(exc),seconds=time.monotonic()-start,optimizerAt=events),sealed=True);raise


def ready():
    doc,proposal=inputs();end=p.sealed(OUT/'completion.json');h.require(end['exitCode']==0,'training_failed')
    with (RUN/'results.csv').open() as stream:rows=list(csv.DictReader(stream))
    h.require([int(x['epoch']) for x in rows]==list(range(1,11)) and all(math.isfinite(float(v)) for row in rows for v in row.values()),'terminal_epochs')
    args=yaml.safe_load((RUN/'args.yaml').read_text());h.require(all(args.get(k)==v for k,v in doc['args'].items()),'settings_changed')
    return h.checked(h.ROOT,end['checkpoint'],256*1024**2),proposal


def infer():
    cp,proposal=ready();start=time.monotonic()
    for kind,plan in proposal['evaluation'].items():
        e.export_predictions(h.checked(h.ROOT,plan['manifest']),cp,OUT/(kind+'-predictions.json'),'mps',discard_degenerate=True)
    h.write(OUT/'inference.json',dict(seconds=time.monotonic()-start,checkpoint=h.ref(cp)),sealed=True)


def merge(base,records,crops,cid):
    """Sources must first pass their independent prediction-artifact validators."""
    indexed={x['imageID']:x for x in records};by_crop={x['imageID']:x for x in crops}
    h.require(len(indexed)==len(records)==len(base) and set(indexed)=={x['imageID'] for x in base},'original_membership')
    expected=[v['id'] for row in records for v in row['proposals']]
    h.require(len(expected)==len(set(expected)) and len(by_crop)==len(crops) and set(expected)==set(by_crop),'crop_membership')
    result=[]
    for row in base:
        items={};selected=dict(r.proposals(row,cid))
        for item in indexed[row['imageID']]['proposals']:
            i=item['proposalIndex'];h.require(i in selected and i not in items,'proposal_identity')
            crop=by_crop[item['id']];roi=r.window(row['width'],row['height'],selected[i]['xyxyPixels'])
            h.require(item['window']==roi and crop['width']==roi[2]-roi[0] and crop['height']==roi[3]-roi[1],'crop_geometry')
            items[i]=dict(status=crop['status'],window=roi,detections=crop['detections'])
        result.append(r.refine(row,items,cid))
    return dict(formatVersion='roi-refinement-v1',results=result,productionEligible=False)


def report():
    cp,proposal=ready();parent=r.c.inputs();names=e.load_names();cid=names.index('pageControl');scores={};counts={}
    control=p.sealed(r.c.g.CONTROL/'evaluation.json');metadata=p.sealed(r.c.g.CONTROL/'protocol.json')['metadata']
    h.require(not (OUT/'evaluation.json').exists(),'output_collision')
    for kind,plan in proposal['evaluation'].items():
        req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
        base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),req,parent['checkpoints']['022']['sha256'],expected_settings=r.c.SETTINGS)
        crop_req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        crop=e.validated_artifact(h.read(OUT/(kind+'-predictions.json'),256*1024**2),crop_req,h.sha(cp),expected_settings=r.c.SETTINGS)
        start=time.monotonic();derived=merge(base['results'],plan['records'],crop['results'],cid)
        images={im.image_id:im for im in req.images}
        for row in derived['results']:normalize_detections(row['detections'],images[row['imageID']],41)
        counts[kind]=dict(seconds=time.monotonic()-start,changedBoxes=sum(a['detections']!=b['detections'] for a,b in zip(base['results'],derived['results'])))
        h.write(OUT/(kind+'-derived.json'),dict(derived,base=parent['reused']['022'][kind],crop=h.ref(OUT/(kind+'-predictions.json')),protocol=h.ref(OUT/'protocol.json')),sealed=True)
        scores[kind]=e.score(derived,req,names)
        for a,b in zip(control['results'][kind]['perClass'],scores[kind]['perClass']):
            if a['class']!='pageControl':h.require(a==b,'non_page_metric_change')
        if kind=='fit':cases=r.c.g.r.f.d.pages(req,derived,cid,metadata)
    strata={s:dict(collections.Counter(x['disposition'] for x in cases if x['metadata']['placement']==s)) for s in ('leading','center','trailing')}
    h.write(OUT/'evaluation.json',dict(results=scores,strata=strata,fitCases=cases,transitions=r.c.transitions(control['fitCases'],cases),
        assessment=r.c.g.r.assess(scores,strata,p.sealed(r.c.g.r.f.OUT/'evaluation.json')),accounting=counts,checkpoint=h.ref(cp),
        protocol=h.ref(OUT/'protocol.json'),productionEligible=False,independentEvaluation=False),sealed=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train','infer','report']);globals()[parser.parse_args().mode]()
