"""Score retained native controls and fixed proposals. Keep no-focus cases explicit."""
import base64
import io
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs
from coverage_reports402 import rectangle

OUT=None


def outcome(scores,boxes,truth):
    from hcf_compare371 import iou
    import math
    q.require(len(scores)==len(boxes) and all(math.isfinite(s) and 0<=s<=1 for s in scores),'native_score_invalid')
    selected=[i for i,s in enumerate(scores) if s>=.85]
    if len(selected)!=1:
        return 'correct-abstention' if truth is None else 'miss'
    if truth is None:return 'false-selection'
    return 'correct' if iou(rectangle(boxes[selected[0]]),rectangle(truth))>=.5 else 'wrong'


def run():
    import numpy as np
    from PIL import Image
    import torch
    import focus_runtime
    import native343
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];refs=resolve_inputs(cfg,OUT)
    artifact=document(refs['capture']);raw=document(refs['proposals']);mapping=document(refs['mapping'])
    geometry=document(refs['geometry'])
    source=Path(artifact['path'])
    q.require(source.resolve()==source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'),'native_source_scope')
    q.require(q.digest(source)==artifact['sha256'],'native_source_changed')
    capture=q.load(source);q.require(capture['complete'] and capture['cleanup'],'native_capture_incomplete')
    frames=capture['frames'];q.require([f['id'] for f in frames]==[r['id'] for r in raw]==[r['id'] for r in geometry['rows']], 'native_membership')
    model=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
    model.load_state_dict(torch.load(checked(refs['model']),map_location='cpu',weights_only=True)['state_dict'],strict=True)
    torch.set_num_threads(2);focus_runtime.TOOL=checked(refs['tool'])
    results=[]
    for frame,proposal in zip(frames,raw):
        native343.signature(frame['before'],frame['before'],frame['focus'])
        native343.signature(frame['after'],frame['before'],frame['focus'])
        scene=frame['before']['scene'];w,h=scene['scene_width'],scene['scene_height']
        q.require([w,h]==[3840,2160],'native_mapping_size')
        path=q.local_path(source.parent,frame['path']);q.require(q.digest(path)==frame['sha256']==proposal['sha256'],'native_pixels_changed')
        controls=[e for e in scene['elements'] if e['element_id'] in scene['focus_observation']['plannedFocusIDs']]
        known=[[rectangle(e['rendered_body_geometry']['visible_pixel_bounds'])[k] for k in ('x','y','width','height')] for e in controls]
        truth=next((b for e,b in zip(controls,known) if e['is_focused']),None)
        boxes=[]
        for candidate in proposal['report']['candidates']:
            b=candidate['bounds'];boxes.append([b['x']*w,b['y']*h,b['width']*w,b['height']*h])
        mapped=[]
        for x,y,bw,bh in boxes:
            l,t,r,b=mapping['offsets'] if frame['profile']=='hcf' else [0]*4
            if bw+l+r>0 and bh+t+b>0:mapped.append([x-l,y-t,bw+l+r,bh+t+b])
        arms={}
        for name,candidates in [('known-box',known),('raw-proposal',boxes),('mapped-proposal',mapped)]:
            scores=[]
            if candidates:
                q.require(len(candidates)<=128,'native_proposal_limit')
                items=[dict(id=str(i),path=str(path),sha256=frame['sha256'],bounds=b) for i,b in enumerate(candidates)]
                reply=focus_runtime.invoke(items,image_root=Path('/Volumes/training-drive/data/NUIAK'))
                arrays=[]
                for item in reply['results']:
                    with Image.open(io.BytesIO(base64.b64decode(item['png'],validate=True))) as image:
                        arrays.append(np.array(image.convert('RGB'),copy=True))
                with torch.no_grad():
                    scores=torch.sigmoid(model(torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255)).reshape(-1).tolist()
            arms[name]=dict(scores=scores,boxes=candidates,outcome=outcome(scores,candidates,truth))
        q.require(frame['profile']!='standard' or arms['raw-proposal']==arms['mapped-proposal'],'standard_changed')
        results.append(dict(id=frame['id'],group=frame['case'],profile=frame['profile'],noFocus=truth is None,arms=arms))
    losses=[r['id'] for r in results if r['arms']['raw-proposal']['outcome'] in ('correct','correct-abstention')
            and r['arms']['mapped-proposal']['outcome'] not in ('correct','correct-abstention')]
    q.save(OUT/'selection.json',dict(rows=results,threshold=.85,lostRawSuccesses=losses,modelAccepted=False,
        scope='Inspected native groups. Known boxes are diagnostic only. No-focus means no annotated control has native focus.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='selection.json',sha256=q.digest(OUT/'selection.json'))]))
