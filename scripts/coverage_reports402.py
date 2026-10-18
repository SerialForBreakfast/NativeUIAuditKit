"""Report retained class risks and new native mapping evidence without promotion."""
from pathlib import Path
import time
import math
import research_queue as q
from template_adapters395 import document, resolve_inputs, command
from template_inputs398 import checked
OUT=None


def rectangle(value):
    if isinstance(value,list):
        q.require(len(value)==4, 'body_shape')
        value=dict(zip(('x','y','width','height'),value))
    q.require(isinstance(value,dict) and set(value)=={'x','y','width','height'}, 'body_shape')
    q.require(all(type(v) in (int,float) and math.isfinite(v) for v in value.values()) and
              value['width']>0 and value['height']>0, 'body_values')
    return value


def class_report(inputs, params):
    doc=document(inputs['evaluation']); name=params['className']
    left={r['class']:r for r in doc['baseline']['perClass']}
    right={r['class']:r for r in doc['populations']['withheld']['perClass']}
    if name=='supported':
        return dict(classes=[class_report(inputs,dict(className=n)) for n in sorted(left) if left[n]['support']],
                    unsupported=[n for n in sorted(right) if not right[n]['support']],modelAccepted=False,
                    nextAction='Use class-specific failures to prepare matched data. Keep the 41-class release gate closed.')
    q.require(name in left and name in right, 'class_missing')
    a,b=left[name],right[name]
    q.require(a['support']==b['support'], 'support_changed')
    delta={key:None if a[key] is None or b[key] is None else b[key]-a[key]
           for key in ('ap50','precision','recall','tp','fp','fn')}
    action=('Prepare reviewed labels for this unsupported class.' if not b['support'] else
            'Inspect missed controls before new training.' if b['fn']>b['fp'] else
            'Inspect false detections and matched negative examples before new training.')
    return dict(className=name,baseline=a,candidate=b,delta=delta,nextAction=action,
        modelAccepted=False,previousSuccessesPreserved=None,
        limitation='Retained reported metrics only. Cases already inspected. Per-case preservation requires matched predictions and labels.')


CAPTURE_VERSIONS=('native-hcf402-v1','native-controls-t45-v1')


def native_report(inputs, params):
    artifact=document(inputs['capture']); source=Path(artifact['path'])
    q.require(source.resolve()==source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'), 'capture_scope')
    q.require(q.digest(source)==artifact['sha256'], 'capture_changed')
    capture=q.load(source);plan=artifact['plan'];mapping=document(inputs['mapping'])
    q.require(capture['complete'] and capture['cleanup'], 'capture_incomplete')
    # B405-168: T45 control captures share the native frame schema, so the same report applies.
    q.require(plan['version'] in CAPTURE_VERSIONS, 'capture_version')
    q.require(not {c['group'] for c in plan['cases']} & set(mapping['fitGroups']+mapping['evaluationGroups']), 'group_reuse')
    requests=[]
    for frame in capture['frames']:
        path=q.local_path(source.parent,frame['path'])
        q.require(q.digest(path)==frame['sha256'], 'image_changed')
        requests.append(dict(id=frame['id'],path=str(path),sha256=frame['sha256']))
    q.save(OUT/'inputs.json',requests)
    command([str(checked(inputs['kernel'])),str(OUT/'inputs.json'),str(OUT/'raw.json')],OUT,'rings',timeout=500)
    raw=q.load(OUT/'raw.json')
    q.require([r['id'] for r in raw]==[r['id'] for r in requests], 'result_membership')
    from hcf_spatial_audit import body_bounds
    from hcf_compare371 import iou
    rows=[]
    for frame,value in zip(capture['frames'],raw):
        q.require(value['sha256']==frame['sha256'], 'result_hash')
        scene=frame['before']['scene'];w,h=scene['scene_width'],scene['scene_height']
        q.require([w,h]==[3840,2160], 'mapping_resolution')
        boxes=[]
        for candidate in value['report']['candidates']:
            b=candidate['bounds'];boxes.append([b['x']*w,b['y']*h,b['width']*w,b['height']*h])
        corrected=[]
        for x,y,bw,bh in boxes:
            l,t,r,b=mapping['offsets'] if frame['profile']=='hcf' else [0]*4
            if bw+l+r>0 and bh+t+b>0:corrected.append([x-l,y-t,bw+l+r,bh+t+b])
        focused=[e for e in scene['elements'] if e['is_focused']]
        q.require(len(focused)==(0 if frame['focus'] is None else 1), 'focus_count')
        if focused:
            geometry=focused[0]['rendered_body_geometry']
            q.require(geometry['availability']=='measured' and geometry['source']=='native_body_presentation_layer', 'body_unmeasured')
            body=rectangle(geometry['visible_pixel_bounds'])
            after=next(e for e in frame['after']['scene']['elements'] if e['element_id']==frame['focus'])
            q.require(rectangle(after['rendered_body_geometry']['visible_pixel_bounds'])==body, 'body_changed')
        else:body=None
        rows.append(dict(id=frame['id'],group=frame['case'],profile=frame['profile'],noFocus=body is None,
            proposals=len(boxes),rawBestIoU=max((iou(dict(zip(('x','y','width','height'),b)),body) for b in boxes),default=0) if body else None,
            mappedBestIoU=max((iou(dict(zip(('x','y','width','height'),b)),body) for b in corrected),default=0) if body else None))
    q.require(len(rows)==plan['expectedFrames'], 'frame_count')
    return dict(rows=rows,modelAccepted=False,standardMappingUnchanged=True,
        noFocusProposalFrames=sum(r['noFocus'] and r['proposals']>0 for r in rows),
        limitation='Proposal geometry only. A decorative proposal is not a wrong selection. Crop decisions remain separate.')


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(cfg,OUT)
        result=(class_report if cfg['id']=='T33' else native_report)(inputs,cfg['parameters'])
        q.save(OUT/'report.json',result)
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=p.name,sha256=q.digest(p)) for p in OUT.iterdir() if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',modelAccepted=False,code=str(error)[:500]));raise
