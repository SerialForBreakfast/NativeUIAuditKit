"""Fixed retained-data diagnostics; no fitting, capture or admission."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import subprocess
import time

import human_annotation_review as h
import real_model_scorecard as s
from model_priority_preflight import yolo_box

OUT = h.ROOT/'reports/work/LOCAL-DIAGNOSTICS-38'
PROPOSALS = h.ROOT/'reports/work/PROPOSAL-RECOVERY-37/comparison/result.json'
MODEL = h.ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'


def decision(boxes, probabilities, controls):
    h.require(len(boxes)==len(probabilities) and bool(boxes), 'invalid_scores')
    h.require(all(isinstance(p,(float,int)) and 0<=p<=1 for p in probabilities), 'invalid_probability')
    target=[c['bounds'] for c in controls if c['state']=='focused']
    h.require(len(target)==1, 'nonunique_target')
    matches=[i for i,b in enumerate(boxes) if s.iou(b,target[0])>=.5]
    peak=max(probabilities); winners=[i for i,p in enumerate(probabilities) if p==peak]
    winner=winners[0]
    outcome=('target_missing' if not matches else
             'below_threshold' if peak<.8500000238418579 else
             'tied' if len(winners)>1 else
             'correct' if winner in matches else 'distractor_wins')
    return dict(outcome=outcome,winner=winner,probability=peak,
                targetBest=max((probabilities[i] for i in matches),default=None))


def focus(replay):
    out=OUT/'focus-v3';tool=h.ROOT/'.build/debug/FocusRingTool'
    source=h.sealed(PROPOSALS,'proposal-recovery-result-v1')
    frames=s.load_frames(s.INVENTORY);by_sha={f['sha256']:f for f in frames}
    tree=[h.ref(p) for p in sorted(MODEL.rglob('*')) if p.is_file()]
    protocol=dict(source=h.ref(PROPOSALS),tool=h.ref(tool),model=tree,script=h.ref(Path(__file__)),
                  inventory=h.ref(s.INVENTORY),threshold=.8500000238418579)
    if not replay:
        h.fresh(out);out.mkdir(parents=True);h.write(out/'protocol.json',protocol)
    else:
        old=h.read(out/'protocol.json')
        h.require(old==protocol,'changed_protocol')
    started=time.monotonic();rows=[]
    for index,row in enumerate(source['frames']):
        frame=by_sha[row['image']['sha256']];boxes=row['arms']['allGeometry']
        image=h.checked(h.ROOT,row['image']);width,height=h.image(h.ROOT,row['image'])
        chunk_size=min(32,80_000_000//(width*height));scores=[]
        for chunk,offset in enumerate(range(0,len(boxes),chunk_size)):
            path=out/f'{index:03d}-{chunk}.json'
            if not replay:
                request=dict(version=1,root=str(h.ROOT),mode='infer',model=str(MODEL),allowOutOfFrameBounds=True,items=[
                    dict(id=str(i),path=str(image),sha256=frame['sha256'],bounds=b)
                    for i,b in enumerate(boxes[offset:offset+chunk_size],offset)])
                proc=subprocess.run([str(tool)],input=json.dumps(request),text=True,capture_output=True,
                    timeout=max(1,600-(time.monotonic()-started)))
                path.write_text(proc.stdout);path.with_suffix('.stderr').write_text(proc.stderr)
                h.require(proc.returncode==0,'focus_probe_failed')
            reply=h.read(path);expected=list(range(offset,min(offset+chunk_size,len(boxes))))
            h.require([int(r['id']) for r in reply['results']]==expected,'changed_crop_membership')
            scores.extend(r['probability'] for r in reply['results'])
        rows.append(dict(image=frame['sha256'],screen=frame['screen'],complete=frame['complete'],
                         **decision(boxes,scores,frame['controls'])))
    h.require(tree==[h.ref(p) for p in sorted(MODEL.rglob('*')) if p.is_file()],'changed_model')
    result=dict(rows=rows,allTargetOutcomes=dict(Counter(r['outcome'] for r in rows)),
        completeOutcomes=dict(Counter(r['outcome'] for r in rows if r['complete'])))
    if replay:h.require(result==h.read(out/'result.json'),'replay_mismatch')
    else:
        h.write(out/'result.json',result)
        h.write(out/'timing.json',dict(seconds=time.monotonic()-started,pid=os.getpid()))
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))


def ios_members():
    base=h.ROOT/'reports/work/IOS-R013-EVAL'
    pre=h.read(base/'preflight.json',64*1024*1024)
    dataset=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r7'
    members=[]
    for family in ('GalleryPage','OnboardingPage'):
        chosen=sorted([m for m in pre['members'] if m['family']==family and m['split']=='test'],key=lambda m:m['imageID'])[:20]
        h.require(len(chosen)==20,'missing_family')
        for m in chosen:
            image=h.local(dataset/m['imageID']);label=h.local(dataset/m['imageID'].replace('/images/','/labels/').replace('.png','.txt'))
            h.require(h.sha(image)==m['imageSHA256'] and h.sha(label)==m['labelSHA256'],'changed_source')
            members.append(dict(**m,image=h.ref(image),label=h.ref(label)))
    return members


def ios_metrics(members, rows):
    from eval_ios_r6_baseline import compute_ap_at_iou
    cid=h.taxonomy().index('pageControl');gt=defaultdict(dict);pred=defaultdict(list)
    counts=Counter();sizes=[]
    h.require([r['imageID'] for r in rows]==[m['imageID'] for m in members],'incomplete_predictions')
    for m,row in zip(members,rows):
        truth=[b for c,b in (yolo_box(l,m['width'],m['height']) for l in
                h.checked(h.ROOT,m['label']).read_text().splitlines() if l.strip()) if c==cid]
        gt[cid][m['imageID']]=[(x,y,x+w,y+v) for x,y,w,v in truth]
        ds=row['detections'];operating=[d for d in ds if d['score']>=.25]
        def box(d):
            x,y,X,Y=d['xyxyPixels'];return [x,y,X-x,Y-y]
        for d in ds:
            if d['classID']==cid:pred[cid].append((m['imageID'],d['score'],tuple(d['xyxyPixels'])))
        typed=[box(d) for d in operating if d['classID']==cid]
        counts['support']+=len(truth);counts['typedPredictions']+=len(typed)
        for threshold in (.5,.75):
            counts[f'geometry{threshold}']+=len(s.matching(truth,[box(d) for d in operating],threshold))
            counts[f'typed{threshold}']+=len(s.matching(truth,typed,threshold))
        sizes.extend(min(b[2:])*row['imgsz']/max(m['width'],m['height']) for b in truth)
    pred[cid].sort(key=lambda p:-p[1]);counts['unmatchedTypedAt50']=counts['typedPredictions']-counts['typed0.5']
    return dict(counts,ap50=compute_ap_at_iou(gt,pred,cid,.5),ap75=compute_ap_at_iou(gt,pred,cid,.75),
                minInputShortSide=min(sizes),meanInputShortSide=sum(sizes)/len(sizes))


def ios(replay):
    out=OUT/'ios';members=ios_members()
    checkpoint=h.ROOT/'NativeUITrainer/yolo_runs/phase6a_r013/weights/best.pt'
    from importlib.metadata import version
    protocol=dict(members=members,checkpoint=h.ref(checkpoint),sizes=[640,960,1280],
        versions={n:version(n) for n in ('torch','ultralytics','Pillow')},script=h.ref(Path(__file__)))
    if replay:
        old=h.read(out/'protocol.json')
        h.require({k:v for k,v in old.items() if k!='script'}=={k:v for k,v in protocol.items() if k!='script'},'changed_protocol')
    else:
        h.fresh(out);out.mkdir(parents=True);h.write(out/'protocol.json',protocol)
        import eval_phase6a as ev
        import torch
        from ultralytics import YOLO
        h.require(torch.backends.mps.is_available(),'mps_unavailable')
        model=YOLO(str(checkpoint));h.require(list(model.names.values())==h.taxonomy(),'changed_taxonomy')
    started=time.monotonic();summary={}
    for size in protocol['sizes']:
        path=out/f'predictions-{size}.json'
        if not replay:
            rows=[];arm_start=time.monotonic()
            for m in members:
                h.require(time.monotonic()-started<300,'inference_budget_exceeded')
                result=model.predict(source=str(h.checked(h.ROOT,m['image'])),imgsz=size,conf=.001,iou=.7,
                    max_det=300,augment=False,agnostic_nms=False,save=False,verbose=False,device='mps')[0]
                ds=[dict(classID=int(c),score=float(p),xyxyPixels=list(map(float,b)))
                    for c,p,b in zip(result.boxes.cls.tolist(),result.boxes.conf.tolist(),result.boxes.xyxy.tolist())]
                rows.append(dict(imageID=m['imageID'],imgsz=size,detections=ds))
            h.write(path,rows);h.write(out/f'timing-{size}.json',dict(seconds=time.monotonic()-arm_start,pid=os.getpid()))
        summary[str(size)]=ios_metrics(members,h.read(path))
        print(size,summary[str(size)],flush=True)
    h.require(protocol['checkpoint']==h.ref(checkpoint),'changed_weights')
    if replay:h.require(summary==h.read(out/'result.json'),'replay_mismatch')
    else:h.write(out/'result.json',summary)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['focus','ios']);parser.add_argument('--replay',action='store_true')
    args=parser.parse_args();globals()[args.mode](args.replay)
