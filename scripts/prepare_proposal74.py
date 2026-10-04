"""Batch automatic rectangles once; keep inference inputs separate from supervision."""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from collections import Counter
import focus_direct_transition as d
from diagnose_proposals73 import vision_candidates,valid
from focus_recorded_transition_eval import iou


def targets(candidates,box):
    overlaps=[iou(c['bounds'],box) for c in candidates]
    positives=[c['id'] for c,v in zip(candidates,overlaps) if v>=.5]
    return dict(positiveIDs=positives,negativeIDs=[c['id'] for c,v in zip(candidates,overlaps) if v<.5],
        bestIoU=max(overlaps,default=0),missingPositive=not positives,ambiguousPositive=len(positives)>1)


def unique_frames(rows):
    frames={}
    for row in rows:
        for ref in row['images']:
            key=ref['sha256'];prior=frames.get(key)
            d.h.require(prior is None or (prior['split']==row['split'] and prior['size']==row['size']),'candidate_split_or_size_conflict')
            frames.setdefault(key,dict(image=ref,size=row['size'],split=row['split']))
    return frames


def validate_response(request,raw):
    d.h.require(raw.get('version')==1 and isinstance(raw.get('os'),str),'probe_version')
    d.h.require([r['id'] for r in raw['results']]==[r['id'] for r in request['frames']],'probe_membership')
    d.h.require(all(r['sha256']==f['sha256'] and not r['errors'] and r['text']==[]
        for r,f in zip(raw['results'],request['frames'])),'probe_failed_or_ocr_not_disabled')
    return raw['results']


def load_inputs(path):
    """Label-free ranker boundary. Supervision must be loaded separately by training."""
    doc=d.h.read(d.h.local(path))
    d.h.require(doc['version'] in ('transition-candidate-inputs-v1','transition-candidate-inputs-v2') and
        doc['seal']==d.h.digest({k:v for k,v in doc.items() if k!='seal'}),'candidate_inputs_seal')
    ids=[]
    for frame in doc['frames']:
        d.h.require(set(frame)=={'id','image','size','split','candidates','source'},'candidate_frame_fields')
        d.h.checked(d.h.ROOT,frame['image']);d.h.require(frame['id']==frame['image']['sha256'],'candidate_image_binding')
        d.h.require(all(set(c)=={'id','bounds'} for c in frame['candidates']),'candidate_truth_leak')
        d.h.require(frame['split'] in ('train','development') and len(frame['size'])==2 and
            all(type(v)is int and v>0 for v in frame['size']),'candidate_frame_metadata')
        d.h.require(len({c['id'] for c in frame['candidates']})==len(frame['candidates']),'candidate_ids')
        d.h.require(len(frame['candidates'])<=(80 if doc['version'].endswith('v2') else 40) and
            all(valid(c['bounds']) and c['bounds'][0]+c['bounds'][2]<=frame['size'][0] and
                c['bounds'][1]+c['bounds'][3]<=frame['size'][1] for c in frame['candidates']),'candidate_bounds_or_count')
        ids.append(frame['id'])
    d.h.require(len(ids)==len(set(ids)),'candidate_frame_duplicates')
    return doc


def verify_bank(root):
    """Verify retained outputs without re-decoding sources or invoking Vision again."""
    root=d.h.local(root);inputs=load_inputs(root/'inputs.json');report=d.h.sealed(root/'report.json','proposal74-bank-report-v1')
    d.h.checked(d.h.ROOT,report['inputs']);d.h.checked(d.h.ROOT,report['supervision'])
    supervision=d.h.read(root/'supervision.json');d.h.checked(d.h.ROOT,supervision['corpus']);d.h.checked(d.h.ROOT,supervision['admission'])
    native={};origins={}
    for index in range(report['nativeInvocations']):
        path=root/f'raw-{index}.json';request=d.h.read(root/f'request-{index}.json')
        for raw in validate_response(request,d.h.read(path)):
            d.h.require(raw['sha256'] not in native,'duplicate_native_output')
            native[raw['sha256']]=raw;origins[raw['sha256']]=d.h.ref(path)
    retained=d.h.read(d.h.checked(d.h.ROOT,inputs['retainedSource']))
    old={r['sha256']:r for r in retained['results']}
    for frame in inputs['frames']:
        raw=native[frame['id']] if frame['split']=='train' else old[frame['id']]
        d.h.require(vision_candidates(raw,frame['image'],frame['size'])==frame['candidates'],'candidate_raw_parity')
    missing=[v for v in supervision['labels'] if v['missingPositive']]
    counts=Counter(v['pairID'].split(':')[-1].rsplit('-',1)[0] for v in missing)
    evidence=dict(version='proposal74-bank-verification-v1',**d.h.FLAGS,
        artifacts=[d.h.ref(p) for p in sorted(root.iterdir()) if p.is_file()],
        probe=inputs['probe'],probeSource=inputs['probeSource'],frameOrigins=origins,
        rawCandidateParity=True,missingTrainingEndpoints=[v for v in missing if v['split']=='train'],
        missingFamilies=dict(counts),trainingLaunched=False)
    d.h.checked(d.h.ROOT,inputs['probe']);d.h.checked(d.h.ROOT,inputs['probeSource'])
    d.h.write(d.h.fresh(root/'verification.json'),evidence,sealed=True)
    print('verified',len(inputs['frames']),'frames; missing',len(missing));return evidence


def run(output,probe):
    start=time.monotonic();out=d.h.fresh(output);probe=d.h.local(probe)
    cp=d.h.ROOT/'reports/work/GENERALIZATION-65/admission/corpus.json'
    ap=d.h.ROOT/'reports/work/GENERALIZATION-65/admission/admission.json'
    corpus=d.h.read(cp);fresh=d.collect(corpus['sources']);d.h.require(corpus==fresh,'source_corpus_changed')
    rows=d.admitted(corpus,d.h.read(ap));d.h.require(Counter(r['split'] for r in rows)=={'train':32,'development':5},'membership')
    frames=unique_frames(rows);training=[(k,v) for k,v in frames.items() if v['split']=='train']
    d.h.require(0<len(training)<=64,'training_frame_budget')
    retained=d.h.sealed(d.h.ROOT/'reports/work/PROPOSALS-73/final.json','proposal73-diagnostic-v1')
    source=d.h.read(d.h.checked(d.h.ROOT,retained['visionSource']))
    old={r['sha256']:r for r in source['results']};probe_ref=d.h.ref(probe)
    source_ref=d.h.ref(d.h.ROOT/'scripts/vision_annotation_probe.swift')
    out.mkdir(parents=True);raw_by_hash={};execution=[]
    for index in range(0,len(training),40):
        group=training[index:index+40];paths=[d.h.checked(d.h.ROOT,f['image']) for _,f in group]
        common=Path(os.path.commonpath([str(p.parent) for p in paths]))
        # Every path was individually checked against repository/explicit SSD mappings.
        d.h.require(str(common)!='/' and all(p.is_relative_to(common) for p in paths),'probe_root')
        request=dict(version=1,root=str(common),rectanglesOnly=True,
            frames=[dict(id=k,path=str(p),sha256=k) for (k,_),p in zip(group,paths)])
        d.h.write(out/f'request-{index//40}.json',request)
        before=time.monotonic()
        result=subprocess.run([str(probe)],input=json.dumps(request),capture_output=True,text=True,timeout=180)
        receipt=dict(exitCode=result.returncode,seconds=time.monotonic()-before,stderr=result.stderr)
        d.h.write(out/f'execution-{index//40}.json',receipt);execution.append(receipt)
        d.h.require(result.returncode==0,'native_rectangle_failure')
        d.h.require(len(result.stdout.encode())<16*1024*1024,'probe_output_limit')
        raw=json.loads(result.stdout);d.h.write(out/f'raw-{index//40}.json',raw)
        for r in validate_response(request,raw):raw_by_hash[r['sha256']]=r
    d.h.checked(d.h.ROOT,probe_ref);d.h.checked(d.h.ROOT,source_ref)
    frame_inputs=[];raw_revisions=set()
    for key,frame in frames.items():
        raw=raw_by_hash[key] if frame['split']=='train' else old[key]
        candidates=vision_candidates(raw,frame['image'],frame['size']);raw_revisions.add(raw['rectangleRevision'])
        frame_inputs.append(dict(id=key,image=frame['image'],size=frame['size'],split=frame['split'],candidates=candidates,
            source='fresh-training-Vision' if frame['split']=='train' else 'retained-development-Vision'))
    d.h.require(len(raw_revisions)==1,'mixed_rectangle_revisions')
    by={f['id']:f for f in frame_inputs};labels=[]
    for row in rows:
        for endpoint,ref,box in zip(('before','after'),row['images'],row['boxes']):
            labels.append(dict(pairID=row['id'],endpoint=endpoint,frameID=ref['sha256'],split=row['split'],
                **targets(by[ref['sha256']]['candidates'],box)))
    inputs=dict(version='transition-candidate-inputs-v1',frames=frame_inputs,
        pairs=[dict(id=r['id'],split=r['split'],group=r['group'],frames=[v['sha256'] for v in r['images']]) for r in rows],
        sourceKind='automatic-Vision-rectangles',probe=probe_ref,probeSource=source_ref,
        rectangleRevision=next(iter(raw_revisions)),retainedSource=retained['visionSource'],executionAuthorized=False)
    d.h.write(out/'inputs.json',inputs,sealed=True)
    d.h.write(out/'supervision.json',dict(version='transition-candidate-supervision-v1',inputs=d.h.ref(out/'inputs.json'),
        corpus=d.h.ref(cp),admission=d.h.ref(ap),labels=labels,trainingLaunched=False),sealed=True)
    summaries={split:dict(endpoints=len(items),covered=sum(not r['missingPositive'] for r in items),
        ambiguous=sum(r['ambiguousPositive'] for r in items),withNegatives=sum(bool(r['negativeIDs']) for r in items))
        for split in ('train','development') for items in ([r for r in labels if r['split']==split],)}
    size=sum(p.stat().st_size for p in out.iterdir());d.h.require(size<256*1024*1024,'output_budget')
    report=dict(version='proposal74-bank-report-v1',**d.h.FLAGS,summary=summaries,
        uniqueTrainingImages=len(training),uniqueDevelopmentImages=len(frames)-len(training),nativeInvocations=len(execution),
        nativeSeconds=sum(v['seconds'] for v in execution),elapsedSeconds=time.monotonic()-start,outputBytes=size,
        inputs=d.h.ref(out/'inputs.json'),supervision=d.h.ref(out/'supervision.json'),
        completeTrainingProposalCoverage=summaries['train']['covered']==64,
        oracleBankCreated=False,limitation='Automatic rectangles only; missing positives retained. No oracle boxes injected, no ranker training or independent evaluation.')
    d.h.write(out/'report.json',report,sealed=True);print(summaries);print({k:report[k] for k in ('uniqueTrainingImages','nativeInvocations','nativeSeconds','elapsedSeconds')})
    return report


def inspect_calibration(proposal,output,probe):
    """Image-only proposal generation; pending roles never become training inputs."""
    from propose_native77 import verified_records, validate_proposal
    from human_auto_boxes import detect
    from compare_annotation_proposals import validate_boxes
    from PIL import Image
    start=time.monotonic();out=d.h.fresh(output);probe=d.h.local(probe)
    pending=d.h.read(d.h.local(proposal))
    if pending.get('version')=='collection102-role-proposal-v1':
        from evaluate_collection102 import validate_proposal as validate102, verified_records as records102
        validate102(pending);rows=records102()
    elif pending.get('version')=='native86-role-proposal-v1':
        from propose_native86 import validate_proposal as validate86, verified_records as records86
        validate86(pending);rows=records86()
    else:
        validate_proposal(pending)
        rows=verified_records(d.h.checked(d.h.ROOT,pending['source']))
    d.h.require([dict(r,requestedRole='train') for r in rows]==pending['members'],'calibration_membership_changed')
    retained=d.h.read(d.h.ROOT/'reports/work/PROPOSAL-RANK-74/bank/inputs.json')
    d.h.require(d.h.ref(probe)==retained['probe'] and
        d.h.ref(d.h.ROOT/'scripts/vision_annotation_probe.swift')==retained['probeSource'],'calibration_probe_changed')
    frames={}
    for row in rows:
        for ref in row['images']:frames.setdefault(ref['sha256'],dict(image=ref,size=row['size']))
    d.h.require(0<len(frames)<=120,'calibration_total_limit')
    paths=[d.h.checked(d.h.ROOT,f['image']) for f in frames.values()]
    common=Path(os.path.commonpath([str(p.parent) for p in paths]));d.h.require(str(common)!='/','calibration_root')
    requested=[dict(id=k,path=str(p),sha256=k) for k,p in zip(frames,paths)]
    out.mkdir(parents=True);native=[];seconds=0;raw_refs=[]
    for index in range(0,len(requested),40):
        suffix='' if index==0 else '-'+str(index//40)
        request=dict(version=1,root=str(common),rectanglesOnly=True,frames=requested[index:index+40])
        d.h.write(out/f'request{suffix}.json',request);before=time.monotonic()
        result=subprocess.run([str(probe)],input=json.dumps(request),capture_output=True,text=True,timeout=180,
            env={**os.environ,'TMPDIR':str(d.h.ROOT/'.build/debug-output/focus-launch/tmp')})
        elapsed=time.monotonic()-before;seconds+=elapsed
        d.h.write(out/f'execution{suffix}.json',dict(exitCode=result.returncode,seconds=elapsed,stderr=result.stderr))
        d.h.require(result.returncode==0 and len(result.stdout.encode())<16*1024*1024,'calibration_probe_failed')
        raw=json.loads(result.stdout);d.h.write(out/f'raw{suffix}.json',raw)
        native.extend(validate_response(request,raw));raw_refs.append(d.h.ref(out/f'raw{suffix}.json'))
    pools={}
    for (key,frame),record,path in zip(frames.items(),native,paths):
        vision=[dict(id='vision-'+c['id'],bounds=c['bounds']) for c in vision_candidates(record,frame['image'],frame['size'])]
        with Image.open(path) as image:corners=detect(image)
        boxes=[[x,y,r-x,b-y] for (x,y),(r,b) in corners];validate_boxes(boxes,*frame['size'])
        raster=[dict(id=f'raster-{i}',bounds=b) for i,b in enumerate(boxes)]
        pools[key]=dict(vision=vision,raster=raster,union=vision+raster)
    inputs=dict(version='calibration-proposals-v1',**d.h.FLAGS,source=d.h.ref(d.h.local(proposal)),
        frames=[dict(id=k,**v,candidates=pools[k]['union']) for k,v in frames.items()],
        probe=d.h.ref(probe),probeSource=retained['probeSource'],raw=d.h.ref(out/'raw.json'),rawBatches=raw_refs)
    d.h.write(out/'inputs.json',inputs,sealed=True)
    scores=[dict(pairID=r['id'],endpoint=endpoint,frameID=ref['sha256'],
        results={name:targets(pool,box) for name,pool in pools[ref['sha256']].items()})
        for r in rows for endpoint,ref,box in zip(('before','after'),r['images'],r['boxes'])]
    report=dict(version='native78-proposals-v1',**d.h.FLAGS,inputs=d.h.ref(out/'inputs.json'),
        summary={name:dict(endpoints=len(scores),covered=sum(not s['results'][name]['missingPositive'] for s in scores),
            ambiguous=sum(s['results'][name]['ambiguousPositive'] for s in scores)) for name in ('vision','raster','union')},
        scores=scores,uniqueImages=len(frames),nativeInvocations=len(raw_refs),nativeSeconds=seconds,
        elapsedSeconds=time.monotonic()-start,trainingLaunched=False,
        implementation=[d.h.ref(d.h.ROOT/'scripts'/n) for n in ('prepare_proposal74.py','human_auto_boxes.py','propose_native77.py','propose_native86.py')])
    for frame in frames.values():d.h.checked(d.h.ROOT,frame['image'])
    d.h.require(d.h.ref(probe)==retained['probe'],'calibration_probe_changed_after')
    d.h.write(out/'report.json',report,sealed=True);print(report['summary']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--probe');p.add_argument('--verify-only',action='store_true')
    p.add_argument('--calibration-proposal')
    a=p.parse_args()
    if a.calibration_proposal:
        d.h.require(not a.verify_only and a.probe is not None,'calibration_cli_mode')
        inspect_calibration(a.calibration_proposal,a.output,a.probe)
    elif a.verify_only:verify_bank(a.output)
    else:
        d.h.require(a.probe is not None,'probe_required');run(a.output,a.probe)
