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


def summarize(rows, scores, references=None):
    """Keep the legacy selector. Score no-focus only with an explicit reference."""
    q.require(len(rows)==len(scores) and len({r['id'] for r in rows})==len(rows),'consumer_score_count')
    explicit = references is not None
    if references is None:
        references = [dict(id=ident, focusState='focused') for ident in dict.fromkeys(r['frame'] for r in rows)]
    q.require(len({f['id'] for f in references})==len(references) and
              {r['frame'] for r in rows}<={f['id'] for f in references}, 'consumer_frame_references')
    refs={f['id']:f for f in references}; crops=[]; frames=[]
    for r,s in zip(rows,scores):
        q.require(type(s) in (int,float) and 0<=s<=1,'consumer_probability')
        state=refs[r['frame']]['focusState']
        q.require(state in ('focused','no_focus','unknown'), 'consumer_focus_state')
        q.require(r.get('label') in (0,1,None) and (state=='unknown' or type(r['label']) is int), 'consumer_label')
        prediction=True if s>=.85 else False if s<.7 else None
        category=('unknown' if state=='unknown' else 'abstention' if prediction is None else
                  ('tp' if r['label'] else 'fp') if prediction else ('fn' if r['label'] else 'tn'))
        crops.append(dict(r,score=s,category=category))
    for ident,reference in refs.items():
        subset=[r for r in crops if r['frame']==ident]; high=[r for r in subset if r['score']>=.85]
        state=reference['focusState']; q.require(state in ('focused','no_focus','unknown'),'consumer_focus_state')
        if explicit and state!='unknown':
            q.require(sum(r['label'] for r in subset)==(1 if state=='focused' else 0), 'consumer_frame_label_conflict')
        selected=high[0] if len(high)==1 else None
        if state=='unknown': result='unknown'
        elif state=='no_focus': result='false_selection' if selected else 'correct_abstention'
        else: result='miss' if selected is None else 'correct' if selected['label'] else 'wrong'
        r=subset[0] if subset else reference
        frames.append(dict(id=ident,sha256=r['image']['sha256'],group=r['group'],role=r['role'],profile=r['profile'],family=r['family'],
            focusState=state,outcome=result,aboveThreshold=len(high),selected=selected['id'] if selected else None,
            abstentionReason=None if selected else 'multiple' if high else 'none'))
    return dict(version='consumer-scores-v1',rows=frames,crops=crops,counts=dict(Counter(r['category'] for r in crops)),
        frameCounts=dict(Counter(r['outcome'] for r in frames)),scoredFrames=sum(f['focusState']!='unknown' for f in frames),
        unknownReferenceFrames=sum(f['focusState']=='unknown' for f in frames),
        modelAccepted=False,resultsProvisional=True,trainingEligible=False,focusThreshold=.85,ambiguityThreshold=.7,
        frameRule='Select exactly one score >=0.85; otherwise abstain.',
        limitation='Supplied native body boxes only. Explicit no-focus references are scored; unknown references are excluded. No full-screen or deployment qualification.')


def sdk_membership(data, tool):
    """Check retained SDK labels and crops without changing their data role."""
    from sdk_episode_labels530 import normalize
    q.require(set(data)=={'version','sourceCrops'} and data['version']=='consumer-sdk-crops-v1','consumer_sdk_manifest')
    source=document(data['sourceCrops'])
    q.require(source['trainingEligible'] is False and source['modelAccepted'] is False,'consumer_sdk_role')
    rows=source['rows']; frames=source['frames']
    q.require(0<len(rows)<=16 and 0<len(frames)<=16,'consumer_sdk_budget')
    q.require(len({r['id'] for r in rows})==len(rows) and len({f['sourceFrameID'] for f in frames})==len(frames),'consumer_sdk_duplicates')
    import focus_runtime
    q.require(source['preprocessing']==focus_runtime.RUNTIME_PREPROCESSING,'consumer_sdk_preprocessing')
    pairs={f['pair']['path']:f['pair'] for f in frames}; expected=[]
    for pair in pairs.values():
        expected.extend(normalize(dict(version='sdk-episode-crops-v1',id='consumer-sdk-review',episodes=pair,tool=tool))['frames'])
    q.require(frames==expected,'consumer_sdk_frame_lineage')
    expected_rows={f['id']+f'-control-{i:03}':(f,c) for f in frames for i,c in enumerate(f['controls'])}
    q.require(set(expected_rows)=={r['id'] for r in rows},'consumer_sdk_membership')
    result=[]; references=[]
    for f in frames:
        q.require(f['role']=='review_only' and f['trainingEligible'] is False and f['profile']=='unknown','consumer_sdk_frame_role')
        checked(f['image'])
        references.append(dict(id=f['sourceFrameID'],focusState=f['frameFocusState'],image=f['image'],
            role=f['role'],profile=f['profile'],group=f['group'],family=f['family'],sourceRole=f['sourceRole']))
    for r in rows:
        f,c=expected_rows[r['id']]
        q.require(r['frame']==f['sourceFrameID'] and r['control']==c['identity']['id'] and
                  r['label']==int(c['identity']['id']==f['focusID']) and type(r['label']) is int and
                  r['sourceImage']==f['image'] and r['box']==c['pixelBounds'] and r['pair']==f['pair'] and
                  r['identity']==c['identity'] and r['role']==f['role'] and r['profile']==f['profile'] and
                  r['group']==f['group'] and r['family']==f['family'] and r['trainingEligible'] is False,'consumer_sdk_row_lineage')
        crop=pin(Path(r['path']));q.require(crop['sha256']==r['sha256'],'consumer_sdk_crop_hash')
        result.append(dict(r,image=r['sourceImage'],bounds=r['box'],expectedCropSHA256=r['sha256'],sourceRole=f['sourceRole']))
    return result,references


def pytorch_scores(rows, model_ref, tool, verify_crops=False):
    import torch
    import numpy as np
    from PIL import Image
    import focus_runtime
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    items=[dict(id=r['id'],path=str(checked(r['image'])),sha256=r['image']['sha256'],bounds=r['bounds']) for r in rows]
    old=focus_runtime.TOOL;focus_runtime.TOOL=tool;arrays=[];observed=[]
    try:
        for batch in focus_runtime.bounded_batches(items,shared_images=True):
            observed.extend(focus_runtime.invoke(batch,image_root=q.ROOT)['results'])
        for r,actual in zip(rows,observed):
            raw=base64.b64decode(actual['png'],validate=True)
            if verify_crops:q.require(hashlib.sha256(raw).hexdigest()==r['expectedCropSHA256'],'consumer_sdk_recrop_parity')
            with Image.open(io.BytesIO(raw)) as image:
                q.require(image.size==(256,256),'consumer_crop_size');arrays.append(np.array(image.convert('RGB'),copy=True))
        runtime=focus_runtime.identity()
    finally:focus_runtime.TOOL=old
    torch.set_num_threads(2)
    model=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
    model.load_state_dict(torch.load(checked(model_ref),map_location='cpu',weights_only=True)['state_dict'],strict=True)
    with torch.no_grad(): scores=torch.sigmoid(model(torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255)).reshape(-1).tolist()
    hashes=[hashlib.sha256(b'(256, 256)\0'+a.tobytes()).hexdigest() for a in arrays]
    return scores,hashes,runtime


def score():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']; refs=resolve_inputs(cfg,OUT)
    data=document(refs['membership']); backend=cfg['parameters']['backend']; start=time.monotonic()
    sdk=data.get('version')=='consumer-sdk-crops-v1'; references=None
    tool=checked(refs['tool'])
    if sdk:
        q.require(backend=='pytorch','consumer_sdk_backend')
        rows,references=sdk_membership(data,refs['tool'])
    else:
        q.require(data['version']=='consumer-crops-v1' and data['trainingEligible'] is False,'consumer_role')
        rows=data['rows']; q.require(0<len(rows)<=16 and all(r['role']=='development' for r in rows),'consumer_budget')
    items=[dict(id=r['id'],path=str(checked(r['image'])),sha256=r['image']['sha256'],bounds=r['bounds']) for r in rows]
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
        scores,hashes,runtime=pytorch_scores(rows,refs['model'],tool,verify_crops=sdk)
        parity=(dict(cropMatches=len(rows),diagnosticOnly=True,runtime=runtime,
                     reason='Production crop PNGs match retained derivatives. PyTorch inference is not TTR execution.') if sdk else
                dict(rgbMatches=sum(h==r['peerRGBSHA256'] for h,r in zip(hashes,rows)),
                     maxScoreDifference=max(abs(s-r['peerScore']) for s,r in zip(scores,rows)),
                     diagnosticOnly=True,reason='PyTorch versus peer Vision is not a model-only comparison.'))
        q.save(OUT/'model-inputs.json',dict(model=refs['model'],runtime=runtime,
            rows=[dict(id=r['id'],modelInputRGBSHA256=h) for r,h in zip(rows,hashes)]))
    else: raise ValueError('consumer_backend')
    result=summarize(rows,scores,references); result.update(inputs=refs,backend=backend,peerParity=parity,wallSeconds=time.monotonic()-start,
        model=refs['model'],scope='review-only native supplied boxes' if sdk else 'retained development supplied boxes')
    if backend=='pytorch':
        for row,digest in zip(result['crops'],hashes):row['modelInputRGBSHA256']=digest
    q.save(OUT/'benchmark_summary.json',result)
    if backend=='vision': q.require(parity['rgbMatches']==len(rows) and parity['maxScoreDifference']<=.01,'consumer_peer_parity')
    receipt()


def sdk_input_pins(data, tool):
    """Pin the complete native lineage during T63 compilation."""
    rows,frames=sdk_membership(data,tool)
    refs=[data['sourceCrops']]
    source=document(data['sourceCrops'])
    for f in source['frames']:
        refs.extend([f['image'],f['pair']])
        for episode in document(f['pair'])['episodes']:
            for frame in episode['frames']:refs.extend(frame.values())
    refs.extend(pin(Path(r['path'])) for r in rows)
    return list({r['path']:r for r in refs}.values())



def unique_input_summary(crops):
    """Count actual model inputs separately from related frames and crop presentations."""
    groups={};missing=[]
    for row in crops:
        digest=row.get('modelInputRGBSHA256')
        if digest is None:
            missing.append(row['id']);continue
        q.require(isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'consumer_input_hash')
        value=groups.setdefault(digest,dict(labels=set(),ids=[],groups=set()))
        label=None if row.get('category')=='unknown' else row.get('label')
        value['labels'].add(label);value['ids'].append(row['id']);value['groups'].add(row['group'])
    conflicts=[dict(sha256=d,ids=v['ids']) for d,v in groups.items() if len(v['labels']-{None})>1]
    return dict(presentations=len(crops),uniqueModelInputs=len(groups),
        uniquePositiveInputs=sum(v['labels']-{None}=={1} for v in groups.values()),
        uniqueNegativeInputs=sum(v['labels']-{None}=={0} for v in groups.values()),
        unknownReferencePresentations=sum(r.get('category')=='unknown' or r.get('label') is None for r in crops),
        conflictingLabels=conflicts,missingInputIdentity=missing,
        limitation='Unique tensors are not independent scenes. Preserve every presentation and construction group.')


def compare_reports(baseline, candidate):
    """Compare fixed supplied-box decisions. Preserve all failed or unknown cases."""
    for key in ('version','focusThreshold','ambiguityThreshold','frameRule','scope','backend'):
        q.require(baseline[key]==candidate[key],'consumer_comparison_settings')
    q.require(baseline['inputs']['membership']==candidate['inputs']['membership'] and
              baseline['inputs']['tool']==candidate['inputs']['tool'],'consumer_comparison_inputs')
    a={r['id']:r for r in baseline['crops']}; b={r['id']:r for r in candidate['crops']}
    q.require(len(a)==len(baseline['crops']) and len(b)==len(candidate['crops']) and set(a)==set(b),'consumer_comparison_membership')
    for ident in a:
        q.require({k:v for k,v in a[ident].items() if k not in ('score','category')}==
                  {k:v for k,v in b[ident].items() if k not in ('score','category')},'consumer_comparison_crop_changed')
    baseline_crops,candidate_crops=a,b
    a={r['id']:r for r in baseline['rows']}; b={r['id']:r for r in candidate['rows']}
    q.require(len(a)==len(baseline['rows']) and len(b)==len(candidate['rows']) and set(a)==set(b),'consumer_comparison_frames')
    rows=[]; success={'correct','correct_abstention'}; wrong={'wrong','false_selection'}
    for ident,before in a.items():
        after=b[ident]
        q.require(all(before[k]==after[k] for k in ('sha256','group','role','profile','family','focusState')),'consumer_comparison_reference')
        rows.append(dict(id=ident,group=before['group'],role=before['role'],profile=before['profile'],
            focusState=before['focusState'],baseline=before['outcome'],candidate=after['outcome'],
            gained=before['outcome'] not in success and after['outcome'] in success,
            lost=before['outcome'] in success and after['outcome'] not in success,
            newWrong=before['outcome'] not in wrong and after['outcome'] in wrong))
    success_crops={'tp','tn'}
    gained_crops=[i for i in baseline_crops if baseline_crops[i]['category'] not in success_crops and candidate_crops[i]['category'] in success_crops]
    lost_crops=[i for i in baseline_crops if baseline_crops[i]['category'] in success_crops and candidate_crops[i]['category'] not in success_crops]
    input_summary=unique_input_summary(list(baseline_crops.values()))
    return dict(rows=rows,baselineModel=baseline['model'],candidateModel=candidate['model'],
        inputSummary=input_summary,gainedCrops=gained_crops,lostCrops=lost_crops,
        uniqueGainedModelInputs=len({baseline_crops[i]['modelInputRGBSHA256'] for i in gained_crops if baseline_crops[i].get('modelInputRGBSHA256')}),
        uniqueLostModelInputs=len({baseline_crops[i]['modelInputRGBSHA256'] for i in lost_crops if baseline_crops[i].get('modelInputRGBSHA256')}),
        counts={key:sum(r[key] for r in rows) for key in ('gained','lost','newWrong')},
        baselineCounts=baseline['frameCounts'],candidateCounts=candidate['frameCounts'])


def compare():
    refs=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    keys=sorted(k.removeprefix('baseline_') for k in refs if k.startswith('baseline_'))
    q.require(keys and set(refs)=={side+'_'+key for side in ('baseline','candidate') for key in keys},'consumer_comparison_pairs')
    reports=[dict(cohort=key,**compare_reports(document(refs['baseline_'+key]),document(refs['candidate_'+key]))) for key in keys]
    rows=[r for report in reports for r in report['rows']]
    input_rows=[r for key in keys for r in document(refs['baseline_'+key])['crops']]
    q.require(len({r['id'] for r in rows})==len(rows),'consumer_comparison_duplicate_frames')
    q.save(OUT/'benchmark_summary.json',dict(version='consumer-comparison-v1',reports=reports,inputs=refs,
        frames=len(rows),groups=len({r['group'] for r in rows}),inputSummary=unique_input_summary(input_rows),
        counts={key:sum(r[key] for r in rows) for key in ('gained','lost','newWrong')},
        modelAccepted=False,resultsProvisional=True,trainingEligible=False,
        limitation='Review-only supplied native boxes. Related frames and cohorts share groups. Unknown profiles prevent profile qualification. No full-screen claim.'))
    receipt()
