"""Fixed-checkpoint confidence/localization diagnosis; never selects a threshold."""
import os
import sys
import time
from collections import defaultdict
import human_annotation_review as h
from train_fullscreen_focus import source_image,runtime_identity
from fullscreen_readthrough import score_boxes


def main():
    os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false')
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
    sys.addaudithook(offline)
    from ultralytics import YOLO
    base=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
    out=base/'confidence-diagnosis';h.require(not out.exists(),'output_exists');out.mkdir()
    contract=h.read(base/'run-long.json');h.require(runtime_identity()==contract['runtime'],'runtime_changed')
    verified={f['id']:f for f in h.read(base/'run-long/validated.json')['frames']}
    frames=[f for f in contract['frames'] if f['split']=='evaluation']
    h.require(len(frames)==500,'membership_changed')
    paths={f['id']:source_image(f['image'],verified[f['id']])[0] for f in frames}
    pins=[h.ref(base/'run-long.json'),h.ref(h.ROOT/'scripts/diagnose_fullscreen41.py')]
    h.write(out/'configuration.json',dict(sources=pins,frames=500,inferences=1000,
        candidateConfidence=.001,declaredConfidence=.25,nmsIoU=.7,matchIoU=.5,
        authorization='In-scope FSF002 failure diagnosis; same fixed checkpoints and evaluation membership.'))
    started=time.monotonic();reports={}
    for name,relative in [('one','evaluation'),('ten','run-long')]:
        prior=h.read(base/relative/'terminal-evaluation.json')
        checkpoint=h.checked(h.ROOT,prior['checkpoint']);model=YOLO(str(checkpoint))
        declared=dict(tp=0,fp=0,fn=0);groups=defaultdict(list)
        with (out/(name+'-progress.jsonl')).open('x') as progress:
            import json
            for f in frames:
                prediction=model.predict(source=str(paths[f['id']]),imgsz=640,conf=.001,iou=.7,
                    device='mps',verbose=False,save=False)[0]
                boxes=prediction.boxes.xyxy.cpu().tolist();scores=prediction.boxes.conf.cpu().tolist()
                annotation=h.read(h.checked(h.ROOT,f['annotation']));controls=[];targets=[]
                for c in annotation['controls']:
                    x,y,w,height=c['bounds'];target=[x,y,x+w,y+height]
                    confidence=max((s for b,s in zip(boxes,scores) if score_boxes([b],[target])['tp']),default=0.)
                    controls.append(dict(id=c['id'],state=c['state'],confidence=confidence))
                    if c['state']=='focused':targets.append(target);groups[c['id']].append(confidence)
                counted=score_boxes([b for b,s in zip(boxes,scores) if s>=.25],targets)
                for k,v in counted.items():declared[k]+=v
                row=dict(id=f['id'],controls=controls,boxes=boxes,scores=scores,declared=counted)
                progress.write(json.dumps(row)+'\n');progress.flush()
                h.require(sum(p.stat().st_size for p in out.iterdir())<=128*1024**2,'output_limit')
        h.require(declared==prior['totals'],'declared_score_replay_changed')
        import statistics
        reports[name]=dict(checkpoint=prior['checkpoint'],declared=declared,groups={k:dict(
            count=len(v),localizedAt001=sum(x>=.001 for x in v),above025=sum(x>=.25 for x in v),
            medianConfidence=statistics.median(v),minConfidence=min(v),maxConfidence=max(v)) for k,v in groups.items()})
    h.write(out/'summary.json',dict(pid=os.getpid(),seconds=time.monotonic()-started,reports=reports,
        interpretation='Post-result diagnosis, not threshold selection or independent evaluation.'))
    print(reports)


if __name__=='__main__':main()
