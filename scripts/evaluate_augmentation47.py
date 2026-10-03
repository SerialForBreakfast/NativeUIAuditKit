"""Fixed post-training robustness and real-screen comparisons; no threshold selection."""
import argparse
import hashlib
import os
import sys
import time
import human_annotation_review as h
from train_fullscreen_focus import source_image,runtime_identity
from reference_benchmark45 import prepare_environment
from focus_priorities46 import square_content,place,measure,summarize
from focus_alignment46 import aligned
import real_fullscreen42 as real

BASE=h.ROOT/'reports/work/FOCUS-AUGMENTATION-47'
VARIANTS=('rect640','rect1280','top','center','bottom','aligned-128','aligned128')


def expected_controls(frame,variant):
    h.require(variant in VARIANTS,'unknown_variant')
    if variant.startswith('rect'):return frame['controls'],None
    w,v=frame['size'];height=round(v*640/w);room=640-height
    y={'top':0,'center':room//2,'bottom':room,'aligned-128':room//2-128,'aligned128':room//2+128}[variant]
    h.require(0<=y<=room,'invalid_padding')
    return [dict(c,bounds=[c['bounds'][0]*640/w,c['bounds'][1]*(height/v)+y,
                           c['bounds'][2]*640/w,c['bounds'][3]*(height/v)]) for c in frame['controls']],y


def protocol():
    panel=h.ROOT/'reports/work/FOCUS-PRIORITIES-46/run/protocol.json'
    physical=h.ROOT/'reports/work/REAL-TRANSFER-42/focus/protocol.json'
    p=h.read(panel);r=h.read(physical)
    h.require(p['runtime']==r['runtime']==runtime_identity(),'runtime_changed')
    models={}
    for name in ('translation','translation-scale'):
        fit=h.read(BASE/'runs'/name/'training-complete.json')
        h.require(fit['epochs']==1 and fit['selection']=='fixed-last-epoch','incomplete_fit')
        h.checked(h.ROOT,fit['checkpoint']);models[name]=fit['checkpoint']
    return dict(version='augmentation47-comparison-v1',panel=h.ref(panel),real=h.ref(physical),
        frames=p['frames'],realFrames=r['frames'],models=models,runtime=runtime_identity(),
        variants=list(VARIANTS),maxInferences=512,confidence=.25,candidateConfidence=.001,nms=.7,
        metricSources=[h.ref(h.ROOT/'scripts'/s) for s in ('focus_priorities46.py','real_fullscreen42.py','real_model_scorecard.py')])


def run(replay=False):
    output=BASE/'comparison';p=protocol()
    if replay:h.require(h.read(output/'protocol.json')==p,'changed_protocol')
    else:
        h.fresh(output);output.mkdir(parents=True);h.write(output/'protocol.json',p)
        prepare_environment();os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',TMPDIR=str(h.ROOT/'.build/debug-output/focus-launch/tmp'))
        def offline(event,args):
            if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
        sys.addaudithook(offline)
        from ultralytics import YOLO
        from PIL import Image
        import numpy as np
        start=time.monotonic();count=0
        for name,checkpoint in p['models'].items():
            model=YOLO(str(h.checked(h.ROOT,checkpoint)));folder=output/name;folder.mkdir()
            h.require(model.names=={0:'focusedControl'},'model_taxonomy')
            def predict(image,resolution):
                nonlocal count
                result=model.predict(source=np.ascontiguousarray(image[:,:,::-1]),imgsz=resolution,
                    conf=.001,iou=.7,device='mps',rect=True,save=False,verbose=False)[0]
                count+=1
                h.require(count<=512,'inference_budget')
                return [dict(box=b,score=s) for b,s in zip(result.boxes.xyxy.cpu().tolist(),result.boxes.conf.cpu().tolist())]
            for i,f in enumerate(p['frames']):
                path,size,pixel=source_image(f['image']);h.require(pixel==f['pixelSHA256'],'changed_pixels')
                with Image.open(path) as image:rgb=np.array(image.convert('RGB'))
                content,scales=square_content(rgb)
                for variant in VARIANTS:
                    if variant.startswith('rect'):image=rgb;controls=f['controls'];offset=None;resolution=int(variant[4:])
                    elif variant.startswith('aligned'):
                        image,controls,offset=aligned(content,scales,f['controls'],int(variant[7:]));resolution=640
                    else:image,controls,offset=place(content,scales,f['controls'],variant);resolution=640
                    tick=time.monotonic();preds=predict(image,resolution)
                    row=dict(id=f['id'],family=f['family'],focusSlot=f['focusSlot'],arm=name+'-'+variant,
                        offset=offset,controls=controls,predictions=preds,seconds=time.monotonic()-tick,
                        contentSHA256=hashlib.sha256(content.tobytes()).hexdigest() if offset is not None else None,
                        measure=measure(f,controls,preds))
                    h.write(folder/f'panel-{i:03d}-{variant}.json',row)
                print(f'{name}: panel {i+1}/30',flush=True)
            for i,f in enumerate(p['realFrames']):
                path=h.checked(h.ROOT,f['image'])
                with Image.open(path) as image:rgb=np.array(image.convert('RGB'))
                tick=time.monotonic();preds=predict(rgb,640)
                h.write(folder/f'real-{i:03d}.json',dict(image=f['image'],predictions=preds,seconds=time.monotonic()-tick))
            h.require(sum(x.stat().st_size for x in BASE.rglob('*') if x.is_file())<=2*1024**3,'tranche_output_budget')
        h.require(count==512,'inference_count');h.write(output/'execution.json',dict(pid=os.getpid(),seconds=time.monotonic()-start,inferences=count))
    summaries={}
    for name in p['models']:
        folder=output/name;panel=[];real_rows=[];predictions=[]
        for i,f in enumerate(p['frames']):
            for variant in VARIANTS:
                r=h.read(folder/f'panel-{i:03d}-{variant}.json')
                expected,offset=expected_controls(f,variant)
                # Permit only floating-point operation-order noise in coordinates.
                h.require(r['offset']==offset and len(r['controls'])==len(expected),'panel_geometry')
                for a,b in zip(r['controls'],expected):
                    h.require(a['id']==b['id'] and a['state']==b['state'] and
                        all(abs(x-y)<1e-8 for x,y in zip(a['bounds'],b['bounds'])),'panel_geometry')
                h.require(r['id']==f['id'] and r['measure']==measure(f,r['controls'],r['predictions']),'panel_replay')
                panel.append(r)
        for i,f in enumerate(p['realFrames']):
            r=h.read(folder/f'real-{i:03d}.json');h.require(r['image']==f['image'],'real_image_binding')
            real_rows.append(real.frame_metrics(f,r['predictions'],h.read(real.OLD/f'{i:03d}.json')))
            predictions.append(r['predictions'])
        summaries[name]=dict(panel=summarize(panel),real=real.summarize(p['realFrames'],predictions,real_rows),realRows=real_rows)
    report=dict(**h.FLAGS,protocol=h.ref(output/'protocol.json'),arms=summaries)
    if replay:h.require(h.read(output/'summary.json')==report,'summary_replay')
    else:h.write(output/'summary.json',report)
    print({k:v['real']['focusedRecall'] for k,v in summaries.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--replay',action='store_true');a=p.parse_args();run(a.replay)
