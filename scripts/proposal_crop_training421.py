"""Matched production crops from verified training-only detector correspondences.

Keep exposure and development pixels unchanged. This is a conditional training
comparison on supported controls, not a claim that missing proposals are solved.
"""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs
from detector_case_match411 import iou
from detector_native_inputs import bounds
import hcf_study371 as study

OUT = None


def xyxy(b):
    return [b[0],b[1],b[0]+b[2],b[1]+b[3]]


def correspondences(documents, frames):
    known={(r['sha256'],k):(r,b) for r in frames if r['role']=='train' for k,b in r['boxes'].items()}
    accepted={}; excluded=0
    for doc in documents:
        q.require(doc.get('version')=='training-proposals-v1' and doc.get('role')=='train','offset_role')
        for m in doc['matches']:
            key=(m['imageSHA256'],m['control'])
            q.require(m.get('role')=='train' and key in known,'offset_source')
            frame,body=known[key]
            q.require(m['group']==frame['group'] and m['body']==body,'offset_body_changed')
            proposal=bounds(m['proposal'],frame['width'],frame['height'])
            # IoU 0.1 was diagnostic correspondence only. Require body overlap for crop labels.
            if iou(xyxy(body),xyxy(proposal)) < .5:
                excluded+=1;continue
            q.require(key not in accepted,'offset_duplicate')
            accepted[key]=proposal
    q.require(accepted,'offset_no_supported_controls')
    return accepted,excluded


def changed_box(row, frame, accepted, arm):
    # Existing jitter is part of the retained control. Do not compose two interventions.
    if 'jitter' in row:return None
    key=(frame['sha256'],row['control'])
    if key not in accepted:return None
    body=row['box']
    q.require(body==frame['boxes'][row['control']], 'offset_crop_body')
    if arm=='measured':return accepted[key]
    if arm=='jitter':
        # Existing generic jitter: fixed seed, 8 px per edge. Match changed-row exposure, not magnitude.
        sides=study.jitter_sides(371,frame['sha256']+':'+row['control'],0,8)
        return study.jitter_box(body,sides)
    q.require(arm=='unchanged','offset_arm')
    return body


def prepare():
    import focus_runtime as runtime
    from native_control_membership import validate_rows
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];refs=resolve_inputs(cfg,OUT)
    arm=cfg['parameters']['arm'];q.require(arm in ('unchanged','measured','jitter'),'offset_arm')
    crops=document(refs['membership'])
    validate_rows(crops['rows'])
    q.require(crops['preprocessing']==runtime.RUNTIME_PREPROCESSING,'offset_preprocessing')
    runtime.TOOL=checked(refs['tool'])
    q.require(runtime.identity()['sourceSHA256']==crops['runtime']['sourceSHA256'],'offset_crop_source')
    frames={f['id']:f for f in crops['frames']}
    accepted,excluded=correspondences([document(refs[k]) for k in ('button','row','tab')],list(frames.values()))
    root=study.verify_storage(crops['storage'])
    items={}; changes={}; changed=0
    for row in crops['rows']:
        if row['role']!='train' or row['family'] not in ('button','row','tab'):continue
        frame=frames[row['frame']]
        q.require(frame['role']=='train' and frame['group']==row['group'],'offset_group_role')
        q.require(row['label']==int(row['control']==frame['focus']),'offset_label')
        box=changed_box(row,frame,accepted,arm)
        if box is None:continue
        image=Path(frame['path'])
        q.require(image.resolve().is_relative_to(root) and q.digest(image)==frame['sha256'],'offset_image')
        key=q.text_digest(dict(image=frame['sha256'],box=box))
        items[key]=dict(id=key,path=str(image),sha256=frame['sha256'],bounds=box)
        changes[row['id']]=(key,box);changed+=1
    q.require(changed,'offset_no_exposure')
    folder=OUT/'crops';folder.mkdir()
    rendered={}
    for batch in runtime.bounded_batches(list(items.values()),shared_images=True):
        reply=runtime.invoke(batch,image_root=root)
        for item,(path,sha) in zip(batch,study.write_crops(batch,reply['results'],folder)):
            rendered[item['id']]=(path,sha)
    rows=[]
    for row in crops['rows']:
        if row['id'] not in changes:rows.append(row);continue
        key,box=changes[row['id']];path,sha=rendered[key]
        if arm=='unchanged':q.require(study.decoded_pixels(path)==study.decoded_pixels(Path(row['path'])),'offset_control_crop_changed')
        rows.append(dict(row,path=str(path),sha256=sha,box=box,proposalIntervention=arm))
    q.require(len(rows)==len(crops['rows']),'offset_exposure_changed')
    q.require([r for r in rows if r['role']=='development']==[r for r in crops['rows'] if r['role']=='development'],'offset_development_changed')
    validate_rows(rows)
    q.save(OUT/'crops.json',dict(crops,rows=rows,intervention=dict(arm=arm,inputs=refs,changedRows=changed)))
    q.save(OUT/'benchmark_summary.json',dict(arm=arm,changedRows=changed,uniqueChangedCrops=len(items),
        acceptedCorrespondences=len(accepted),excludedLowOverlap=excluded,trainingRows=sum(r['role']=='train' for r in rows),
        developmentUnchanged=True,modelAccepted=False,limitation='Conditional on unique IoU >= 0.5 matches. No inferred offsets for missing boxes.'))
    names=['crops.json','benchmark_summary.json']+['crops/'+p.name for p in folder.glob('*.png')]
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]))


def qualify_labels():
    """Verify source scene coverage without inventing complete general-UI labels."""
    from native_control_admission import validate_partition
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];refs=resolve_inputs(cfg,OUT)
    admission=document(refs['admission'])
    q.require(admission.get('trainingAdmitted') is True,'label_admission')
    partition=validate_partition(admission['rows'])
    scenes={}
    for ref in admission['sources']:
        artifact=document(ref);path=Path(artifact['path'])
        q.require(q.digest(path)==artifact['sha256'],'label_source_changed')
        for frame in q.load(path)['frames']:
            scene=frame['before']['scene'];scenes[frame['sha256']]=scene
    counts={};classes=set()
    for row in admission['rows']:
        q.require(q.digest(Path(row['path']))==row['sha256'],'label_image_changed')
        scene=scenes[row['sha256']];elements={e['id']:e for e in scene['elements']}
        q.require(set(row['boxes'])==set(scene['focus_observation']['plannedFocusIDs']),'label_focusable_coverage')
        q.require(scene['focus_observation']['verified'] is True and scene['focus_observation']['observedID']==row['focus'],'label_focus_observed')
        for key,box in row['boxes'].items():
            e=elements[key];geometry=e['rendered_body_geometry']
            q.require(geometry['availability']=='measured' and geometry['full_pixel_bounds']==box,'label_body_geometry')
            cls=e.get('taxonomy_class');q.require(isinstance(cls,str) and cls,'label_taxonomy_missing');classes.add(cls)
        counts[row['role']]=counts.get(row['role'],0)+1
    result=dict(partition=partition,frames=counts,classes=sorted(classes),focusableLabelsVerified=True,
        generalUILabelsComplete=False,calibrationGroups=0,detectorTrainingReady=False,modelAccepted=False,
        decision='Focusable control labels pass. Freeze the detector target scope and qualify separate calibration membership before T89 training.',
        limitation='Scene focusable coverage does not establish exhaustive labels for text, containers, or other UI objects.')
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
