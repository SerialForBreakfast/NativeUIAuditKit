"""Fixed full-screen focus transfer on existing private development screenshots."""
import argparse
from collections import Counter,defaultdict
import math
import os
from pathlib import Path
import sys
import time
import human_annotation_review as h
import real_model_scorecard as s
from train_fullscreen_focus import runtime_identity
from eval_ios_r6_baseline import compute_ap_at_iou

BASE=h.ROOT/'reports/work/REAL-TRANSFER-42'
OLD=h.ROOT/'reports/work/REAL-MODEL-SCORECARD-36/production'
FIT=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/run/training-complete.json'
THRESHOLDS=(.5,.7,.9)


def xywh(d):
    x,y,X,Y=d['box']
    h.require(all(math.isfinite(v) for v in (x,y,X,Y,d['score'])) and X>x and Y>y and
        0<=d['score']<=1,'invalid_candidate')
    return [x,y,X-x,Y-y]


def frame_metrics(frame,detections,production):
    focused=[c for c in frame['controls'] if c['state']=='focused']
    h.require(len(focused)==1,'nonunique_truth')
    target=focused[0]['bounds'];operating=[d for d in detections if d['score']>=.25]
    boxes=[xywh(d) for d in operating]
    overlap=max((s.iou(b,target) for b in boxes),default=0.)
    source=s.score(frame,production)
    prior=[s.bounds(e['boundingBoxPixels']) for e in production['runtime']['result']['elements']]
    prior_overlap=max((s.iou(b,target) for b in prior),default=0.)
    outcome='incomplete'
    if frame['complete']:
        outcome=('no_focus' if not boxes else 'multiple_focus' if len(boxes)>1 else
                 'correct' if overlap>=.5 and sum(s.iou(boxes[0],c['bounds'])>=.5
                    for c in frame['controls'])==1 else 'wrong_focus')
    return dict(image=frame['sha256'],screen=frame['screen'],role=h.control_label(focused[0]),
        complete=frame['complete'],detections=len(boxes),outcome=outcome,
        productionOutcome=source['focusOutcome'],bestIoU=overlap,productionBestIoU=prior_overlap,
        localized={str(t):overlap>=t for t in THRESHOLDS},
        productionLocalized={str(t):prior_overlap>=t for t in THRESHOLDS})


def summarize(frames,predictions,rows):
    h.require(len(frames)==len(predictions)==len(rows),'missing_predictions')
    gt={0:{}};pred={0:[]};groups=defaultdict(lambda:dict(frames=0,localized=0,productionLocalized=0))
    unreviewed=0;known_unfocused=0
    for f,ds,row in zip(frames,predictions,rows):
        for d in ds:
            if d['score']<.25:continue
            matches=[c for c in f['controls'] if s.iou(xywh(d),c['bounds'])>=.5]
            if not matches and not f['complete']:unreviewed+=1
            if matches and all(c['state']=='unfocused' for c in matches):known_unfocused+=1
        for name in ('screen:'+f['screen'],'role:'+row['role']):
            group=groups[name];group['frames']+=1;group['localized']+=row['localized']['0.5']
            group['productionLocalized']+=row['productionLocalized']['0.5']
        if not f['complete']:continue
        targets=[c['bounds'] for c in f['controls'] if c['state']=='focused']
        gt[0][f['sha256']]=[(x,y,x+w,y+v) for x,y,w,v in targets]
        pred[0].extend((f['sha256'],d['score'],tuple(d['box'])) for d in ds)
    pred[0].sort(key=lambda r:-r[1])
    return dict(frames=len(rows),completeFrames=len(gt[0]),
        focusedRecall={str(t):sum(r['localized'][str(t)] for r in rows) for t in THRESHOLDS},
        productionFocusedRecall={str(t):sum(r['productionLocalized'][str(t)] for r in rows) for t in THRESHOLDS},
        completeOutcomes=dict(Counter(r['outcome'] for r in rows if r['complete'])),
        productionCompleteOutcomes=dict(Counter(r['productionOutcome'] for r in rows if r['complete'])),
        completeAP={str(t):compute_ap_at_iou(gt,pred,0,t) if gt[0] else None for t in THRESHOLDS},
        groups=dict(groups),partialUnreviewedPredictions=unreviewed,
        detectionsOnKnownUnfocusedControls=known_unfocused)


def run(replay=False,report_output=None):
    out=BASE/'focus';frames=s.load_frames(s.INVENTORY)
    h.require(len(frames)==46 and sum(f['complete'] for f in frames)==7,'changed_inventory')
    h.require(h.read(OLD/'inputs.json')['frames']==frames,'production_inventory_changed')
    checkpoint=h.read(FIT)['checkpoint'];weights=h.checked(h.ROOT,checkpoint)
    protocol=dict(frames=frames,inventory=h.ref(s.INVENTORY),checkpoint=checkpoint,
        runtime=runtime_identity(),source=h.ref(Path(__file__)),metric=h.ref(Path(s.__file__)),
        candidateConfidence=.001,confidence=.25,nmsIoU=.7,imgsz=640,device='mps',
        purpose='Existing real development evidence; no training admission.')
    if replay:
        frozen=h.read(out/'protocol.json')
        h.require({k:v for k,v in frozen.items() if k!='source'}==
            {k:v for k,v in protocol.items() if k!='source'},'changed_protocol')
        prior_report=h.read(out/'result.json')
        h.checked(h.ROOT,prior_report['protocol'])
        for ref in prior_report['sources']:h.checked(h.ROOT,ref)
    else:
        h.fresh(out);out.mkdir(parents=True);h.write(out/'protocol.json',protocol)
        os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false')
        def offline(event,args):
            if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
        sys.addaudithook(offline)
        from ultralytics import YOLO
        start=time.monotonic();model=YOLO(str(weights))
        h.require(model.names=={0:'focusedControl'},'wrong_model_taxonomy')
        for i,f in enumerate(frames):
            tick=time.monotonic()
            result=model.predict(source=str(h.checked(h.ROOT,f['image'])),imgsz=640,conf=.001,iou=.7,
                device='mps',verbose=False,save=False)[0]
            detections=[dict(box=b,score=p) for b,p in zip(result.boxes.xyxy.cpu().tolist(),result.boxes.conf.cpu().tolist())]
            h.write(out/f'{i:03d}.json',dict(image=f['sha256'],detections=detections,seconds=time.monotonic()-tick))
            h.require(sum(p.stat().st_size for p in out.iterdir())<=128*1024**2,'output_limit')
        h.write(out/'execution.json',dict(pid=os.getpid(),seconds=time.monotonic()-start,images=46))
    rows=[];predictions=[];sources=[]
    for i,f in enumerate(frames):
        path=out/f'{i:03d}.json';d=h.read(path)
        h.require(d['image']==f['sha256'],'changed_prediction_image')
        prior=OLD/f'{i:03d}.json';sources.extend([h.ref(path),h.ref(prior)])
        for candidate in d['detections']:xywh(candidate)
        rows.append(frame_metrics(f,d['detections'],h.read(prior)));predictions.append(d['detections'])
    result=dict(protocol=h.ref(out/'protocol.json'),sources=sources,rows=rows,
        summary=summarize(frames,predictions,rows),
        interpretation='Diagnostic real screenshots; AP uses seven complete screens only. Operating thresholds differ by model.')
    if report_output:
        h.require(replay,'new_analysis_requires_retained_predictions')
        target=h.local(report_output)
        result['analysisSource']=h.ref(Path(__file__))
        h.write(target,result)
    elif replay:h.require(h.read(out/'result.json')==result,'replay_mismatch')
    else:h.write(out/'result.json',result)
    print(result['summary'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');p.add_argument('--report-output')
    args=p.parse_args();run(args.replay,args.report_output)
