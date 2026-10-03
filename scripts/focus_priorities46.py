"""Controlled resolution, padding-position and training-duration diagnostics."""
import argparse
from collections import Counter, defaultdict
import hashlib
import os
import statistics
import sys
import time
import human_annotation_review as h
from reference_benchmark45 import prepare_environment, arm_score
from diagnose_reference45 import associations
from real_fullscreen42 import xywh
from train_fullscreen_focus import runtime_identity, source_image


def choose_native(frames, annotations, per_slot=6):
    groups=defaultdict(list)
    for f in frames:
        if f['split']!='evaluation':continue
        a=annotations[f['id']]
        focused=[c for c in a['controls'] if c['state']=='focused']
        h.require(len(focused)==1,'native_single_focus')
        groups[focused[0]['id']].append(f)
    h.require(set(groups)=={'item-0','item-1','item-2'},'native_slots')
    chosen=[]
    for slot in sorted(groups):
        unique={f['image']['sha256']:f for f in groups[slot]}
        h.require(len(unique)>=per_slot,'slot_support')
        chosen.extend(unique[k] for k in sorted(unique)[:per_slot])
    return chosen


def prepare():
    base=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
    queue=h.ROOT/'reports/work/REFERENCE-IMPORT-44/review-final/audit/combined-queue.json'
    batch=h.ROOT/'reports/work/REFERENCE-IMPORT-44/review-final/native-review/batch.json'
    approval=h.ROOT/'reports/work/REFERENCE-BENCHMARK-45/human-sample-approval.json'
    q=h.read(queue);h.require(h.read(approval)['queue']==h.ref(queue),'sample_binding')
    selected=set(q['selectedFrames']);frames=[]
    for f in h.read(batch)['frames']:
        if f['id'] in selected:
            frames.append(dict(id=f['id'],image=f['image'],family=f['recipe']['appearance']['referencePack']['screen'],
                controls=[dict(id=c['sourceElementID'],bounds=c['bounds'],state=c['state']) for c in f['proposals']]))
    h.require(len(frames)==12 and len(selected)==12,'reference_membership')
    contract=base/'run.json';c=h.read(contract)
    annotations={f['id']:h.read(h.checked(h.ROOT,f['annotation'])) for f in c['frames'] if f['split']=='evaluation'}
    for f in choose_native(c['frames'],annotations):
        a=annotations[f['id']]
        h.require(a['image']==f['image'] and a['completeFocus'] is True and a['profile']=='ordinary','native_annotation')
        frames.append(dict(id=f['id'],image=f['image'],family='native26',controls=a['controls'],annotation=f['annotation']))
    pixels=set()
    for f in frames:
        _,size,pixel=source_image(f['image'])
        h.require(pixel not in pixels,'sample_duplicate');pixels.add(pixel)
        h.require(size[0]>=size[1],'landscape_required')
        f.update(size=list(size),pixelSHA256=pixel,focusSlot=next(c['id'] for c in f['controls'] if c['state']=='focused'))
    models={name:h.read(base/path/'terminal-evaluation.json')['checkpoint'] for name,path in
            [('one','evaluation'),('ten','run-long')]}
    for m in models.values():h.checked(h.ROOT,m)
    return dict(version='focus-priorities46-v1',frames=frames,models=models,runtime=runtime_identity(),
        sources=[h.ref(p) for p in (queue,batch,approval,contract)],
        implementation=h.ref(h.ROOT/'scripts/focus_priorities46.py'),
        confidence=.25,candidateConfidence=.001,nms=.7,device='mps',
        comparisons=['one-rect640','one-rect1280','one-top','one-center','one-bottom','ten-top','ten-center','ten-bottom'],
        maxInferences=240,maxOutputBytes=128*1024**2,
        authority='User assigned diagnostic experiments to prioritize failure sources; fixed-model inference only.')


def square_content(rgb, side=640):
    import cv2
    height,width=rgb.shape[:2]
    h.require(width>=height and width>0 and height>0,'landscape_required')
    resized=cv2.resize(rgb,(side,round(height*side/width)),interpolation=cv2.INTER_LINEAR)
    return resized,(side/width,resized.shape[0]/height)


def place(content, scales, controls, position, side=640):
    import numpy as np
    h.require(position in ('top','center','bottom') and content.shape[1]==side and content.shape[0]<=side,'position_shape')
    room=side-content.shape[0];y={'top':0,'center':room//2,'bottom':room}[position]
    canvas=np.full((side,side,3),114,dtype=np.uint8);canvas[y:y+content.shape[0]]=content
    sx,sy=scales
    moved=[dict(c,bounds=[c['bounds'][0]*sx,c['bounds'][1]*sy+y,c['bounds'][2]*sx,c['bounds'][3]*sy]) for c in controls]
    return canvas,moved,y


def measure(frame, controls, predictions):
    boxes=[xywh(p) for p in predictions if p['score']>=.25]
    score=arm_score(dict(frame,controls=controls),boxes,boxes)
    score.update(associations(controls,predictions))
    target=next(c['bounds'] for c in controls if c['state']=='focused')
    from real_model_scorecard import iou
    score['bestFocusScore']=max((p['score'] for p in predictions if iou(xywh(p),target)>=.5),default=0.)
    return score


def summarize(rows):
    groups=defaultdict(list)
    for r in rows:
        groups[(r['family'],r['arm'])].append(r)
        if r['family']=='native26':groups[('native26:'+r['focusSlot'],r['arm'])].append(r)
    result=[]
    for (family,arm),items in sorted(groups.items()):
        result.append(dict(family=family,arm=arm,frames=len(items),
            localized50=sum(r['measure']['localized']['0.5'] for r in items),
            containedAbove025=sum(r['measure']['focusAboveOperating'] for r in items),
            negativeOutranks=sum(r['measure']['unfocusedOutranksFocus'] for r in items),
            candidateLocalized001=sum(r['measure']['bestFocusScore']>=.001 for r in items),
            medianFocusScore=statistics.median(r['measure']['bestFocusScore'] for r in items),
            selectedKnownNegative=sum(r['measure']['selectedOnKnownUnfocused'] for r in items),
            selections=dict(Counter(r['measure']['selection'] for r in items)),
            seconds=sum(r['seconds'] for r in items)))
    return result


def run(output, replay=False):
    output=h.local(output)
    if replay:
        protocol=h.read(output/'protocol.json')
        rows=[h.read(output/f'{i:03d}.json') for i in range(protocol['maxInferences'])]
        h.require(summarize(rows)==h.read(output/'summary.json')['groups'],'summary_replay')
        print('All240retained rows reproduce the summary.');return
    h.fresh(output);output.mkdir(parents=True)
    protocol=prepare();h.write(output/'protocol.json',protocol)
    prepare_environment();os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',TMPDIR=str(h.ROOT/'.build/debug-output/focus-launch/tmp'))
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
    sys.addaudithook(offline)
    from ultralytics import YOLO
    from PIL import Image
    import numpy as np
    start=time.monotonic();rows=[]
    for name in ('one','ten'):
        model=YOLO(str(h.checked(h.ROOT,protocol['models'][name])))
        h.require(model.names=={0:'focusedControl'},'model_taxonomy')
        for f in protocol['frames']:
            p,size,pixel=source_image(f['image'])
            h.require(list(size)==f['size'] and pixel==f['pixelSHA256'],'input_changed')
            with Image.open(p) as image:rgb=np.array(image.convert('RGB'))
            content,scales=square_content(rgb);content_hash=hashlib.sha256(content.tobytes()).hexdigest()
            variants=['rect640','rect1280','top','center','bottom'] if name=='one' else ['top','center','bottom']
            for variant in variants:
                if variant.startswith('rect'):
                    image=rgb;controls=f['controls'];offset=None;resolution=int(variant[4:])
                else:image,controls,offset=place(content,scales,f['controls'],variant);resolution=640
                tick=time.monotonic()
                result=model.predict(source=np.ascontiguousarray(image[:,:,::-1]),imgsz=resolution,
                    conf=.001,iou=.7,device='mps',rect=True,save=False,verbose=False)[0]
                predictions=[dict(box=b,score=s) for b,s in zip(result.boxes.xyxy.cpu().tolist(),result.boxes.conf.cpu().tolist())]
                row=dict(id=f['id'],family=f['family'],focusSlot=f['focusSlot'],arm=name+'-'+variant,
                    inputShape=list(image.shape),offset=offset,contentSHA256=content_hash if offset is not None else None,
                    controls=controls,predictions=predictions,seconds=time.monotonic()-tick,
                    measure=measure(f,controls,predictions))
                h.write(output/f'{len(rows):03d}.json',row);rows.append(row)
                h.require(len(rows)<=240 and sum(p.stat().st_size for p in output.iterdir())<=128*1024**2,'output_budget')
            print(f'{name} {f["id"]}: {len(rows)}/240 inferences',flush=True)
    h.require(len(rows)==240,'execution_membership')
    h.write(output/'summary.json',dict(**h.FLAGS,protocol=h.ref(output/'protocol.json'),groups=summarize(rows),
        pid=os.getpid(),seconds=time.monotonic()-start,inferences=len(rows),
        caveats=['Previously exposed development and calibration evidence; no independent test claim.',
                 'Padding interventions are synthetic diagnostics, not newly rendered native states.',
                 'Resolution changes object scale and compute as well as retained detail.']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--replay',action='store_true')
    a=p.parse_args();run(a.output,a.replay)
