"""Source-ordered, label-free batch-one MPS latency diagnostic, not qualification."""
import dataclasses
import statistics
import time
from PIL import Image
import roi194 as x
from eval_phase6a import filter_degenerate_predictions


def run():
    h,p,e=x.h,x.p,x.e;dest=x.OUT/'latency.json';h.require(not dest.exists(),'output_collision')
    cp,proposal=x.ready();parent=x.r.c.inputs()
    req=e.load_request(h.checked(h.ROOT,parent['manifests']['combined']),41);images={im.image_id:im for im in req.images}
    records=proposal['evaluation']['combined']['records']
    chosen=[row for row in records if row['proposals']][:8]+[row for row in records if not row['proposals']][:8]
    h.require(len(chosen)==16,'sample_support')
    import torch
    from ultralytics import YOLO
    start=time.monotonic();base=YOLO(str(h.checked(h.ROOT,parent['checkpoints']['022'],256*1024**2)));model=YOLO(str(cp))
    load_seconds=time.monotonic()-start;cid=e.load_names().index('pageControl');settings=x.r.c.SETTINGS;rows=[]
    def predict(net,source,im):
        prediction=net.predict(source=source,imgsz=640,conf=settings['confidence'],iou=settings['iou'],
            max_det=settings['maxDetections'],augment=settings['augment'],agnostic_nms=settings['agnosticNMS'],
            save=False,stream=False,verbose=False,device='mps')
        h.require(len(prediction)==1,'prediction_count');b=prediction[0].boxes
        det=[dict(classID=int(c),score=float(s),xyxyPixels=list(map(float,box))) for c,s,box in zip(b.cls.tolist(),b.conf.tolist(),b.xyxy.tolist())]
        det,_=filter_degenerate_predictions(im,41,det)
        return e.make_result(im,41,detections=det)
    for cycle in ('cold_pass','warm_pass'):
        for selected in chosen:
            im=images[selected['imageID']];torch.mps.synchronize();begin=time.monotonic()
            original=predict(base,str(im.image_path),im);torch.mps.synchronize();base_end=time.monotonic()
            items={};crop_seconds=0;inference_seconds=0
            for index,d in x.r.proposals(original,cid):
                a=time.monotonic();roi=x.r.window(im.width,im.height,d['xyxyPixels'])
                with Image.open(im.image_path) as opened:crop=opened.convert('RGB').crop(roi)
                crop_seconds+=time.monotonic()-a
                crop_im=dataclasses.replace(im,width=crop.width,height=crop.height)
                a=time.monotonic();result=predict(model,crop,crop_im);torch.mps.synchronize();inference_seconds+=time.monotonic()-a
                items[index]=dict(window=roi,status=result['status'],detections=result['detections'])
            a=time.monotonic();x.r.refine(original,items,cid);merge_seconds=time.monotonic()-a
            rows.append(dict(cycle=cycle,imageID=im.image_id,proposals=len(items),baseSeconds=base_end-begin,
                cropSeconds=crop_seconds,secondPassSeconds=inference_seconds,mergeSeconds=merge_seconds,totalSeconds=time.monotonic()-begin))
    warm=[r for r in rows if r['cycle']=='warm_pass']
    groups={}
    for label,has_proposals in [('proposal',True),('no_proposal',False)]:
        selected=[row for row in warm if bool(row['proposals'])==has_proposals]
        groups[label]=dict(count=len(selected),medianTotalSeconds=statistics.median(row['totalSeconds'] for row in selected) if selected else None,
            medianAddedSeconds=statistics.median(row['totalSeconds']-row['baseSeconds'] for row in selected) if selected else None)
    h.write(dest,dict(source=h.ref(__file__),checkpoint=h.ref(cp),base=parent['checkpoints']['022'],modelLoadSeconds=load_seconds,
        rows=rows,warmByProposalPresence=groups,warmMedianSeconds={k:statistics.median(r[k] for r in warm) for k in ('baseSeconds','cropSeconds','secondPassSeconds','mergeSeconds','totalSeconds')},
        scope='16label-free source-ordered cases balanced8/8, not population-weighted; cold_pass includes first-use startup, not each frame cold; MPS batch-one, not CoreML qualification',productionEligible=False),sealed=True)
    print('Latency sample complete',flush=True)


if __name__=='__main__':run()
