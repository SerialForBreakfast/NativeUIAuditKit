"""Matched HCF rules, crop models, and detectors. Audit data remains locked."""
import base64
import os
from pathlib import Path
import time
import numpy as np
from PIL import Image
import research_queue as q
import hcf_study371 as study
from hcf_spatial_audit import body_bounds
from score_hcf_pilot import iou

OUT = None


def box(value):
    return dict(zip(('x','y','width','height'), value))


def outline_rule(image):
    """Find bright closed strokes without labels, proposals, or profile metadata."""
    import cv2
    rgb = np.asarray(image.convert('RGB'))
    mask = ((rgb.min(axis=2) >= 220) & ((rgb.max(axis=2)-rgb.min(axis=2)) <= 30)).astype(np.uint8)*255
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    if hierarchy is not None:
        for index, contour in enumerate(contours):
            child = int(hierarchy[0,index,2])
            if child < 0: continue
            x,y,w,h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if min(w,h) < 40 or max(w,h) > max(image.size)*.8 or not .3 <= w/h <= 4: continue
            if area/(w*h) < .65: continue
            hole = abs(cv2.contourArea(contours[child]))
            # A large enclosed hole distinguishes a stroke from filled white content.
            if not .55 <= hole/max(area,1) <= .99: continue
            fill = np.count_nonzero(mask[y:y+h,x:x+w])/(w*h)
            if fill > .45: continue
            candidate = [float(x),float(y),float(w),float(h)]
            if any(iou(box(candidate),box(other)) > .8 for other in candidates): continue
            candidates.append(candidate)
    return dict(decision='select' if len(candidates)==1 else 'abstain',
                box=candidates[0] if len(candidates)==1 else None, candidates=candidates,
                reason='unique_bright_closed_stroke' if len(candidates)==1 else 'no_unique_outline')


def summarize(rows, predictions):
    q.require(rows and len(rows)==len(predictions), 'comparison_membership')
    results = []
    for row,pred in zip(rows,predictions):
        q.require(row['id'] == pred['id'], 'prediction_order')
        overlap = None if pred['box'] is None else iou(box(pred['box']),box(row['boxes'][row['focus']]))
        result = 'miss' if overlap is None else 'correct' if overlap >= .5 else 'wrong'
        results.append(dict(id=row['id'], outcome=result, iou=overlap, profile=row['profile'],
            role=row['role'], family=row['family'], group=row['group'], prediction=pred, sha256=row['sha256']))
    def counts(items):
        total = len(items); correct=sum(r['outcome']=='correct' for r in items); wrong=sum(r['outcome']=='wrong' for r in items)
        return dict(frames=total, correct=correct, wrong=wrong, misses=total-correct-wrong,
            coverage=(correct+wrong)/total if total else None, recall=correct/total if total else None,
            precision=correct/(correct+wrong) if correct+wrong else None)
    slices = {}
    for row in results:
        key = row['role']+'/'+row['profile']+'/'+row['family']
        slices.setdefault(key,[]).append(row)
    return dict(rows=results, counts=counts(results), slices={key:counts(value) for key,value in slices.items()},
        groups=len({r['group'] for r in rows}), families=len({r['family'] for r in rows}), modelAccepted=False,
        noFocusSupport=0, falseSelectionOnNoFocus=None,
        limitation='Native image-card family only. No-focus and physical-device accuracy remain unavailable.')


def retained():
    cfg = q.load(OUT/'config.json'); rows=[]
    for source in cfg['captures']:
        path=q.ROOT/source['path']; q.require(q.digest(path)==source['sha256'], 'retained_capture_changed')
        doc=q.load(path); q.require(doc['complete'] and doc['cleanup'], 'retained_capture_incomplete')
        for frame in doc['frames']:
            if frame['repeat'] != 0: continue
            import hcf_capture362 as h
            h.verified_profile(frame['profileReceipt']['receipt'],frame['profile'])
            image=path.parent/frame['path']; q.require(q.digest(image)==frame['sha256'], 'retained_image_changed')
            with Image.open(image) as im: width,height=im.size
            rows.append(dict(id=path.parents[4].name+'-'+frame['id'], path=str(image),sha256=frame['sha256'],
                boxes=body_bounds(frame),focus=frame['focus'],profile=frame['profile'],role='retained',
                family='inspected-native-cards',group=doc['group'],width=width,height=height))
    q.save(OUT/'admission.json',dict(rows=rows, cases=[],trainingAdmitted=False))


def corpus():
    study.OUT=OUT
    docs=study.dependency('admission.json')
    cfg=q.load(OUT/'config.json')
    rows=[r for doc in docs for r in doc['rows'] if r['role'] in cfg['roles']]
    q.require(rows and 'audit' not in cfg['roles'], 'comparison_audit_locked')
    q.require(len({r['id'] for r in rows})==len(rows), 'comparison_duplicate')
    for row in rows:
        if cfg.get('sourceProjectRoot'):
            original=Path(cfg['sourceProjectRoot'])
            q.require(original.is_absolute(), 'comparison_original_root')
            image=Path(row['path'])
            if image.is_relative_to(original):
                row['path']=str(q.local_path(q.ROOT,str(image.relative_to(original))))
        q.require(q.digest(Path(row['path']))==row['sha256'], 'comparison_image_changed')
    return rows,cfg


def rules():
    rows,cfg=corpus(); predictions=[]
    for index,row in enumerate(rows):
        start=time.monotonic()
        with Image.open(row['path']) as image: result=outline_rule(image)
        predictions.append(dict(id=row['id'],**result,seconds=time.monotonic()-start))
        study.progress('Score fixed full-frame HCF outline rules',index+1,len(rows))
    result=summarize(rows,predictions); result['method']='bright-closed-stroke-v1'
    result['ruleSourceSHA256']=q.digest(Path(__file__))
    result['scope']='Independent research rule, not a claim about the TTR runtime rule.'
    q.save(OUT/'comparison.json',result)


def candidate_crop():
    rows,cfg=corpus()
    import focus_runtime
    import torch
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    model=q.ROOT/cfg['baseline']['path']
    if cfg.get('candidate'):
        refs=[r for d in q.load(OUT/'dependencies.json') for r in d['outputs'] if r['path'].endswith('/model.json')]
        q.require(len(refs)==1,'candidate_model_missing')
        artifact=q.load(q.ROOT/refs[0]['path']); model=Path(artifact['path'])
        q.require(q.digest(model)==artifact['sha256'],'candidate_model_changed')
    else: q.require(q.digest(model)==cfg['baseline']['sha256'],'baseline_changed')
    torch.set_num_threads(2)
    network=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
    network.load_state_dict(torch.load(model,map_location='cpu',weights_only=True)['state_dict'],strict=True)
    predictions=[]
    crop_folder=OUT/'crops';crop_folder.mkdir()
    for index,row in enumerate(rows):
        # Oracle boxes isolate classification. They do not establish proposal recall.
        items=[dict(id=row['id']+'-'+key,path=row['path'],sha256=row['sha256'],bounds=value) for key,value in row['boxes'].items()]
        image_root=Path(cfg['storage']['root']) if Path(row['path']).is_relative_to(cfg['storage']['root']) else q.ROOT
        reply=focus_runtime.invoke(items,image_root=image_root)
        samples=[]
        for item,result in zip(items,reply['results']):
            path=crop_folder/(item['id']+'.png')
            with path.open('xb') as stream:stream.write(base64.b64decode(result['png'],validate=True))
            samples.append(dict(path=path))
        arrays=[]
        for sample in samples:
            with Image.open(sample['path']) as image:
                q.require(image.size==(256,256),'comparison_crop_size')
                arrays.append(np.array(image.convert('RGB'),copy=True))
        with torch.no_grad():
            tensor=torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255
            scores=torch.sigmoid(network(tensor)).reshape(-1).tolist()
        selected=[i for i,score in enumerate(scores) if score >= .85]
        prediction=dict(id=row['id'],box=items[selected[0]]['bounds'] if len(selected)==1 else None,
            scores=scores,decision='select' if len(selected)==1 else 'abstain')
        predictions.append(prediction)
        # These deterministic crops are reproducible. Keep their hashes in results and remove only this job's copies.
        prediction['cropHashes']=[q.digest(sample['path']) for sample in samples]
        for sample in samples:sample['path'].unlink()
        study.progress('Score crop classifier with observed control proposals',index+1,len(rows))
    result=summarize(rows,predictions);result.update(method='crop-candidate' if cfg.get('candidate') else 'crop-baseline',
        modelSHA256=q.digest(model),proposalMode='oracle',deployableAccuracy=None)
    q.save(OUT/'comparison.json',result)


def detector():
    rows,cfg=corpus()
    refs=[r for d in q.load(OUT/'dependencies.json') for r in d['outputs'] if r['path'].endswith('/model.json')]
    q.require(len(refs)==1,'detector_model_missing');artifact=q.load(q.ROOT/refs[0]['path'])
    path=Path(artifact['path']);q.require(q.digest(path)==artifact['sha256'],'detector_changed')
    os.environ.setdefault('YOLO_CONFIG_DIR',str(q.ROOT/'NativeUITrainer/.ultralytics'))
    from ultralytics import YOLO
    model=YOLO(str(path));predictions=[]
    for index,row in enumerate(rows):
        result=model.predict(row['path'],imgsz=640,conf=.25,iou=.7,device='mps',verbose=False)[0]
        boxes=result.boxes.xyxy.cpu().tolist()
        value=None
        if len(boxes)==1:
            x,y,x2,y2=boxes[0];value=[x,y,x2-x,y2-y]
        predictions.append(dict(id=row['id'],box=value,decision='select' if value else 'abstain',candidateCount=len(boxes)))
        study.progress('Score full-screen HCF detector',index+1,len(rows))
    result=summarize(rows,predictions);result.update(method='full-screen-candidate',modelSHA256=artifact['sha256'])
    q.save(OUT/'comparison.json',result)


candidate_detector = detector


def decision():
    study.OUT=OUT
    reports=study.dependency('comparison.json')
    by_method={r['method']:r for r in reports}
    q.require(set(by_method)=={'bright-closed-stroke-v1','crop-baseline','crop-candidate','full-screen-candidate'},'comparison_methods_missing')
    baseline={r['id']:r for r in by_method['crop-baseline']['rows']}
    outcomes={}
    for method,report in by_method.items():
        rows={r['id']:r for r in report['rows']};q.require(rows.keys()==baseline.keys(),'comparison_membership_mismatch')
        gains=[key for key in rows if rows[key]['outcome']=='correct' and baseline[key]['outcome']!='correct']
        losses=[key for key in rows if rows[key]['outcome']!='correct' and baseline[key]['outcome']=='correct']
        outcomes[method]=dict(counts=report['counts'],gains=gains,losses=losses,
            retainedLosses=[key for key in losses if baseline[key]['role']=='retained'])
    q.save(OUT/'decision.json',dict(comparisons=outcomes,modelAccepted=False,productionChanged=False,
        auditOpened=False,nextDecision='Review development gains and losses before freezing a final-audit candidate.',
        limitations=['Oracle crop selection is not deployable proposal performance.','No-focus controls and Office transfer need separate evidence.']))
