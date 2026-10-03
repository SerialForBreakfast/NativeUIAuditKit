"""Stride-aligned control for the position comparison; same frozen inputs and model."""
import argparse
import hashlib
import os
import sys
import time
import human_annotation_review as h
from focus_priorities46 import square_content, measure, summarize
from reference_benchmark45 import prepare_environment
from train_fullscreen_focus import source_image, runtime_identity


def aligned(content, scales, controls, delta, side=640):
    import numpy as np
    room=side-content.shape[0];center=room//2;y=center+delta
    h.require(delta%32==0 and 0<=y<=room,'aligned_offset')
    canvas=np.full((side,side,3),114,dtype=np.uint8);canvas[y:y+content.shape[0]]=content
    sx,sy=scales
    return canvas,[dict(c,bounds=[c['bounds'][0]*sx,c['bounds'][1]*sy+y,c['bounds'][2]*sx,c['bounds'][3]*sy]) for c in controls],y


def run(base,output):
    base=h.local(base);output=h.fresh(output);output.mkdir(parents=True)
    protocol=h.read(base/'protocol.json');h.require(protocol['runtime']==runtime_identity(),'runtime_changed')
    h.write(output/'protocol.json',dict(parent=h.ref(base/'protocol.json'),implementation=h.ref(h.ROOT/'scripts/focus_alignment46.py'),
        checkpoint=protocol['models']['one'],offsetDeltas=[-128,128],inferences=60,maxOutputBytes=128*1024**2))
    prepare_environment();os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',TMPDIR=str(h.ROOT/'.build/debug-output/focus-launch/tmp'))
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
    sys.addaudithook(offline)
    from ultralytics import YOLO
    from PIL import Image
    import numpy as np
    started=time.monotonic();model=YOLO(str(h.checked(h.ROOT,protocol['models']['one'])));rows=[]
    for f in protocol['frames']:
        p,size,pixel=source_image(f['image']);h.require(pixel==f['pixelSHA256'],'changed_input')
        with Image.open(p) as image:rgb=np.array(image.convert('RGB'))
        content,scales=square_content(rgb)
        for delta in (-128,128):
            image,controls,y=aligned(content,scales,f['controls'],delta);tick=time.monotonic()
            result=model.predict(source=np.ascontiguousarray(image[:,:,::-1]),imgsz=640,conf=.001,
                                 iou=.7,device='mps',rect=True,save=False,verbose=False)[0]
            preds=[dict(box=b,score=s) for b,s in zip(result.boxes.xyxy.cpu().tolist(),result.boxes.conf.cpu().tolist())]
            row=dict(id=f['id'],family=f['family'],focusSlot=f['focusSlot'],arm=f'one-aligned{delta}',
                offset=y,contentSHA256=hashlib.sha256(content.tobytes()).hexdigest(),controls=controls,
                predictions=preds,measure=measure(f,controls,preds),seconds=time.monotonic()-tick)
            h.write(output/f'{len(rows):03d}.json',row);rows.append(row)
            h.require(sum(p.stat().st_size for p in base.parent.rglob('*') if p.is_file())<=128*1024**2,'tranche_output_limit')
        print(f'{len(rows)}/60',flush=True)
    h.require(len(rows)==60,'control_membership')
    h.write(output/'summary.json',dict(**h.FLAGS,groups=summarize(rows),pid=os.getpid(),seconds=time.monotonic()-started,inferences=60))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.base,a.output)
