"""Prepare retained observer evidence and compare fixed crop models. No training admission."""
import base64
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import time
import research_queue as q
from template_adapters395 import document, resolve_inputs, verified_export, vision
from template_inputs398 import checked, pin
from focus_surface_intake import safe_members

OUT = None


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*'))
        if p.is_file() and p.name!='artifact-receipt.json']))


def records(frames, cohorts):
    """Cross-check producer labels and scores without treating them as an independent audit."""
    q.require(frames and len({f['id'] for f in frames}) == len(frames), 'consumer_frames')
    rows=[]
    for name, data in cohorts.items():
        truth, observed, frame_truth=data
        q.require(len({r['id'] for r in truth})==len(truth), 'consumer_duplicate_crop')
        scores={r['id']:r for r in observed['results']}
        q.require(len(scores)==len(observed['results']) and set(scores)=={r['id'] for r in truth}, 'consumer_scores')
        labels={r['id']:r for r in frame_truth}
        selected=[f for f in frames if f['cohort']==name]
        q.require(set(labels)=={f['id'] for f in selected}, 'consumer_frame_labels')
        q.require({r['frame'] for r in truth}==set(labels), 'consumer_crop_frames')
        for f in selected:
            subset=[r for r in truth if r['frame']==f['id']]
            q.require(labels[f['id']]['profile']=='Standard', 'consumer_profile')
            focused=[r for r in subset if r['focused'] is True]
            focus=labels[f['id']]['focus_id']
            q.require(len(focused)==1 and focused[0]['id']==f['id']+'-'+focus, 'consumer_focus_conflict')
            for row in subset:
                q.require(type(row['focused']) is bool and row['profile']=='Standard' and
                          row['source']=='native_body_presentation_layer' and row['geometry_role']=='rendered_control_body', 'consumer_label_source')
                score=scores[row['id']]
                q.require(type(score['probability']) in (int,float) and 0<=score['probability']<=1, 'consumer_probability')
                q.require(len(score['modelInputRGBSHA256'])==64 and all(c in '0123456789abcdef' for c in score['modelInputRGBSHA256']), 'consumer_rgb_hash')
                rows.append(dict(id=row['id'],frame=f['id'],cohort=name,group='retained-stingray-catalog-seed83',
                    role='development',profile='standard',family=row['family'],label=int(row['focused']),bounds=row['bounds'],
                    image=dict(path=f['path'],sha256=f['sha256']),peerScore=score['probability'],
                    peerRGBSHA256=score['modelInputRGBSHA256']))
    q.require(len({r['id'] for r in rows})==len(rows) and len(rows)<=128, 'consumer_membership')
    return rows


def prepare():
    from PIL import Image
    cfg=q.load(OUT.parents[2]/'spec.json')['template']; refs=resolve_inputs(cfg,OUT)
    source=checked(refs['archive'])
    with tarfile.open(source) as archive:
        members,total=safe_members([m for m in archive if m.name not in ('.','./')])
        q.require(total<=80_000_000, 'consumer_archive_budget')
        members={str(PurePosixPath(m.name)):m for m in members if m.isfile() and
                 not any(p.startswith('._') for p in PurePosixPath(m.name).parts)}
        def raw(name):
            q.require(name in members,'consumer_missing_member')
            return archive.extractfile(members[name]).read()
        manifest=json.loads(raw('manifest.json'))
        names=[f['path'] for f in manifest['files']]
        q.require(len(set(names))==len(names) and set(names)==set(members)-{'manifest.json'},'consumer_manifest')
        for ref in manifest['files']:
            data=raw(ref['path'])
            q.require(len(data)==ref['bytes'] and hashlib.sha256(data).hexdigest()==ref['sha256'],'consumer_member_changed')
        frames=json.loads(raw('frames.json')); contract=json.loads(raw('model-contract.json'))
        q.require(contract['focusThreshold']==.85 and contract['ambiguityThreshold']==.7,'consumer_thresholds')
        cohorts={name:(json.loads(raw(name+'/truth.json')),json.loads(raw(name+'/model-actual-0.json')),
                      json.loads(raw(name+'/frame-truth.json'))) for name in {f['cohort'] for f in frames}}
        rows=records(frames,cohorts)
        folder=OUT/'images'; folder.mkdir()
        for f in frames:
            data=raw(f['path']); q.require(hashlib.sha256(data).hexdigest()==f['sha256'],'consumer_image_changed')
            with Image.open(io.BytesIO(data)) as image:
                w,h=image.size; q.require(0<w*h<=40_000_000,'consumer_image_size')
            dest=folder/(f['sha256']+'.png')
            if not dest.exists(): dest.write_bytes(data)
            for row in rows:
                if row['frame']!=f['id']: continue
                from detector_native_inputs import bounds
                row['bounds']=bounds(row['bounds'],w,h); row['image']=pin(dest)
        for name in cohorts:
            q.save(OUT/(name+'.json'),dict(version='consumer-crops-v1',rows=[r for r in rows if r['cohort']==name],
                archive=refs['archive'],contract=contract,trainingEligible=False,labelEvidence='producer-reported native bodies and focus; original scene brackets absent'))
        q.save(OUT/'benchmark_summary.json',dict(frames=len(frames),crops=len(rows),groups=1,modelAccepted=False,
            trainingEligible=False,limitation='Inspected Standard development evidence. Native scene brackets are not included; labels are producer-reported.'))
    receipt()


def summarize(rows,scores):
    q.require(len(rows)==len(scores) and len({r['id'] for r in rows})==len(rows),'consumer_score_count')
    crops=[]; frames=[]
    for r,s in zip(rows,scores):
        q.require(type(s) in (int,float) and 0<=s<=1,'consumer_probability')
        prediction=True if s>=.85 else False if s<.7 else None
        category='abstention' if prediction is None else ('tp' if r['label'] else 'fp') if prediction else ('fn' if r['label'] else 'tn')
        crops.append(dict(r,score=s,category=category))
    for ident in dict.fromkeys(r['frame'] for r in rows):
        subset=[r for r in crops if r['frame']==ident]; chosen=[r for r in subset if r['score']>=.85]
        result='miss' if len(chosen)!=1 else 'correct' if chosen[0]['label'] else 'wrong'
        r=subset[0]
        frames.append(dict(id=ident,sha256=r['image']['sha256'],group=r['group'],role=r['role'],profile=r['profile'],family=r['family'],
            outcome=result,aboveThreshold=len(chosen)))
    return dict(version='consumer-scores-v1',rows=frames,crops=crops,counts=dict(Counter(r['category'] for r in crops)),
        modelAccepted=False,focusThreshold=.85,ambiguityThreshold=.7,frameRule='Select exactly one score >=0.85; otherwise abstain.',
        limitation='Known native body boxes, producer-reported labels, inspected development groups. No no-focus or deployment qualification.')


def score():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']; refs=resolve_inputs(cfg,OUT)
    data=document(refs['membership']); backend=cfg['parameters']['backend']; start=time.monotonic()
    q.require(data['version']=='consumer-crops-v1' and data['trainingEligible'] is False,'consumer_role')
    rows=data['rows']; q.require(0<len(rows)<=16 and all(r['role']=='development' for r in rows),'consumer_budget')
    items=[dict(id=r['id'],path=str(checked(r['image'])),sha256=r['image']['sha256'],bounds=r['bounds']) for r in rows]
    tool=checked(refs['tool'])
    if backend=='vision':
        export,compiled=verified_export(refs['model'])
        q.require(export['checkpoint']['sha256']==data['contract']['sourceCheckpointSHA256'],'consumer_baseline_identity')
        q.require(tool==q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool','consumer_vision_tool')
        reply=vision(items,compiled,OUT,'consumer')
        scores=[r['probability'] for r in reply['results']]
        parity=dict(rgbMatches=sum(r['modelInputRGBSHA256']==old['peerRGBSHA256'] for r,old in zip(reply['results'],rows)),
            maxScoreDifference=max(abs(s-r['peerScore']) for s,r in zip(scores,rows)),tolerance=.01)
        q.save(OUT/'observed.json',reply)
    elif backend=='pytorch':
        import torch
        import numpy as np
        from PIL import Image
        import focus_runtime
        from train_focus_ring_detector import load_mobilenetv4_conv_small
        focus_runtime.TOOL=tool; reply=focus_runtime.invoke(items); arrays=[]
        for r in reply['results']:
            with Image.open(io.BytesIO(base64.b64decode(r['png'],validate=True))) as image:
                q.require(image.size==(256,256),'consumer_crop_size'); arrays.append(np.array(image.convert('RGB'),copy=True))
        torch.set_num_threads(2)
        model=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
        model.load_state_dict(torch.load(checked(refs['model']),map_location='cpu',weights_only=True)['state_dict'],strict=True)
        with torch.no_grad(): scores=torch.sigmoid(model(torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255)).reshape(-1).tolist()
        hashes=[hashlib.sha256(b'(256, 256)\0'+a.tobytes()).hexdigest() for a in arrays]
        parity=dict(rgbMatches=sum(h==r['peerRGBSHA256'] for h,r in zip(hashes,rows)),
                    maxScoreDifference=max(abs(s-r['peerScore']) for s,r in zip(scores,rows)),
                    diagnosticOnly=True,reason='PyTorch versus peer Vision is not a model-only comparison.')
    else: raise ValueError('consumer_backend')
    result=summarize(rows,scores); result.update(inputs=refs,backend=backend,peerParity=parity,wallSeconds=time.monotonic()-start)
    q.save(OUT/'benchmark_summary.json',result)
    if backend=='vision': q.require(parity['rgbMatches']==len(rows) and parity['maxScoreDifference']<=.01,'consumer_peer_parity')
    receipt()
