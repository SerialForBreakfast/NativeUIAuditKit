"""Resident YOLO adapter: immutable originals, in-memory labels, terminal scoring."""
import os
import json
from pathlib import Path
import sys
import time

import human_annotation_review as h


def dataset_type():
    import numpy as np
    from ultralytics.data.dataset import YOLODataset

    class ReadThroughDataset(YOLODataset):
        def __init__(self, frames, **kwargs):
            h.require(kwargs.get('cache',False) is False,'image_cache_forbidden')
            self.frames=frames
            super().__init__(img_path='contract-membership',cache=False,**{k:v for k,v in kwargs.items() if k!='cache'})
            # BaseDataset consults .npy even with cache=False. Disable that path,
            # rather than trusting that no stale adjacent cache exists on USB.
            self.npy_files=[NoCache() for _ in self.im_files]

        def get_img_files(self, _):return [f['absoluteImage'] for f in self.frames]

        def get_labels(self):
            labels=[]
            for frame in self.frames:
                values=np.asarray([list(map(float,line.split())) for line in frame['labels']],dtype=np.float32).reshape(-1,5)
                labels.append(dict(im_file=frame['absoluteImage'],shape=tuple(reversed(frame['size'])),
                    cls=values[:,:1],bboxes=values[:,1:],segments=[],normalized=True,bbox_format='xywh'))
            return labels

        def cache_images(self):raise ValueError('image_cache_forbidden')

    return ReadThroughDataset


class NoCache:
    def exists(self):return False


def trainer_type(frames):
    from ultralytics.models.yolo.detect import DetectionTrainer
    Dataset=dataset_type()
    training=[f for f in frames if f['split']=='train']
    h.require(bool(training),'missing_training_members')

    class TerminalTrainer(DetectionTrainer):
        def get_dataset(self):
            # Even the unused validation loader sees training membership only.
            return dict(train='train',val='train',nc=1,names={0:'focusedControl'},channels=3)

        def build_dataset(self,img_path,mode='train',batch=None):
            h.require(img_path=='train','evaluation_access_during_training')
            return Dataset(training,imgsz=self.args.imgsz,batch_size=batch or self.args.batch,
                augment=mode=='train',hyp=self.args,rect=False,stride=32,pad=0.,data=self.data)

        def validate(self):
            # Ultralytics invokes this on the last epoch even when val=False.
            self.best_fitness=0.
            return {},0.

        def final_eval(self):pass

        def optimizer_step(self):
            super().optimizer_step()
            self.observedOptimizerSteps=getattr(self,'observedOptimizerSteps',0)+1

    return TerminalTrainer


def score_boxes(predictions, targets, threshold=.5):
    """Confidence-ordered one-to-one matches; all boxes are pixel xyxy."""
    used=set();tp=0
    for pred in predictions:
        best=-1;overlap=threshold
        for index,target in enumerate(targets):
            if index in used:continue
            intersection=max(0,min(pred[2],target[2])-max(pred[0],target[0]))*max(0,min(pred[3],target[3])-max(pred[1],target[1]))
            union=(pred[2]-pred[0])*(pred[3]-pred[1])+(target[2]-target[0])*(target[3]-target[1])-intersection
            iou=intersection/union if union>0 else 0
            if iou>=overlap:best=index;overlap=iou
        if best>=0:used.add(best);tp+=1
    return dict(tp=tp,fp=len(predictions)-tp,fn=len(targets)-tp)


def train_terminal(doc,checked,out):
    os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',PYTHONDONTWRITEBYTECODE='1')
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled_for_local_training')
    sys.addaudithook(offline)
    from ultralytics import YOLO
    from types import SimpleNamespace
    from train_tvos_model import training_options
    from train_fullscreen_focus import augmentation_options
    started=time.monotonic()
    args=SimpleNamespace(dry_run=False,epochs=doc['epochs'],batch=doc['batch'],imgsz=doc['imgsz'],
        patience=doc['epochs']+1,workers=0,output_dir=str(out),name='model')
    kwargs=training_options(args,'contract-membership')
    kwargs.update(val=False,exist_ok=False,workers=0,plots=False,save_period=-1,cache=False,
        mosaic=0.,mixup=0.,copy_paste=0.,flipud=0.,fliplr=0.,seed=doc['seed'],
        hsv_h=0.,hsv_s=0.,hsv_v=0.,scale=0.,translate=0.,degrees=0.,shear=0.,perspective=0.,
        deterministic=True,amp=False,resume=False)
    kwargs.update(augmentation_options(doc))
    model=YOLO(str(h.checked(h.ROOT,checked['checkpoint'],128*1024*1024)))
    model.train(trainer=trainer_type(checked['frames']),**kwargs)
    trainer=model.trainer
    h.require(trainer.epoch+1==doc['epochs'],'training_incomplete')
    last=h.local(trainer.last);h.require(last.is_file(),'missing_terminal_checkpoint')
    trained=time.monotonic();h.write(out/'training-complete.json',dict(epochs=doc['epochs'],
        checkpoint=h.ref(last),seconds=trained-started,selection='fixed-last-epoch',
        augmentation=augmentation_options(doc),batchesPerEpoch=len(trainer.train_loader) if hasattr(trainer,'train_loader') else None,
        trainingFrames=sum(f['split']=='train' for f in checked['frames']),
        optimizerSteps=getattr(trainer,'observedOptimizerSteps',None),
        effectiveDatasetRect=False))
    evaluate_terminal(doc,checked,last,out)


def evaluate_terminal(doc,checked,last,out):
    """Same terminal evaluator, also callable after a completed-fit timeout."""
    from ultralytics import YOLO
    started=time.monotonic();terminal=YOLO(str(last));rows=[]
    with (out/'evaluation-progress.jsonl').open('x') as progress:
        for frame in checked['frames']:
            if frame['split']!='evaluation':continue
            result=terminal.predict(source=frame['absoluteImage'],imgsz=doc['imgsz'],conf=.25,iou=.7,
                device='mps',verbose=False,save=False)[0]
            order=result.boxes.conf.argsort(descending=True)
            boxes=result.boxes.xyxy[order].cpu().tolist()
            annotation=h.read(h.checked(h.ROOT,frame['annotation']))
            targets=[[x,y,x+w,y+v] for x,y,w,v in
                [c['bounds'] for c in annotation['controls'] if c['state']=='focused']]
            row=dict(id=frame['id'],predictedBounds=boxes,**score_boxes(boxes,targets))
            rows.append(row);progress.write(json.dumps(row)+'\n');progress.flush()
    h.write(out/'terminal-evaluation.json',dict(checkpoint=h.ref(last),confidence=.25,matchIoU=.5,
        seconds=time.monotonic()-started,frames=rows,totals={k:sum(r[k] for r in rows) for k in ('tp','fp','fn')},
        exactFrames=sum(r['fp']==0 and r['fn']==0 for r in rows),
        interpretation='Held-out synthetic configuration groups, not real-app accuracy.'))
