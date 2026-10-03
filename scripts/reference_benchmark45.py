"""Fixed-model reference-screen diagnostics; native labels remain provisional."""
import argparse
from collections import Counter, defaultdict
import os
from pathlib import Path
import subprocess
import sys
import time
import human_annotation_review as h
from real_model_scorecard import bounds, iou, matching
from real_fullscreen42 import xywh
from train_fullscreen_focus import runtime_identity


def select_frames(batch):
    """Deduplicate decoded images, rejecting contradictory annotations."""
    groups = {}
    for frame in batch['frames']:
        h.require(frame['disposition'] == 'imported' and frame['sourceRole'] == 'calibration', 'reference_role')
        controls = sorted([dict(id=c['sourceElementID'], bounds=c['bounds'], state=c['state'],
                                **{'class':c['class']}) for c in frame['proposals']], key=lambda c:c['id'])
        h.require(sum(c['state']=='focused' for c in controls)==1, 'reference_focus')
        key=frame['pixelSHA256'];family=frame['recipe']['appearance']['referencePack']['screen']
        row=dict(image=frame['image'], pixelSHA256=key, controls=controls, family=family,
                 aliases=[frame['id']], conditions=[frame['evidenceKind']])
        if key in groups:
            old=groups[key]
            h.require(old['controls']==controls and old['family']==family, 'duplicate_label_conflict')
            old['aliases'].append(frame['id']);old['conditions'].append(frame['evidenceKind'])
        else:groups[key]=row
    return sorted(groups.values(),key=lambda f:f['pixelSHA256'])


def arm_score(frame, boxes, selected):
    target=next(c['bounds'] for c in frame['controls'] if c['state']=='focused')
    best=max((iou(b,target) for b in boxes),default=0.)
    known_unfocused=0;unreviewed=0
    for box in selected:
        matches=[c for c in frame['controls'] if iou(box,c['bounds'])>=.5]
        if matches and all(c['state']=='unfocused' for c in matches):known_unfocused+=1
        if not matches:unreviewed+=1
    outcome=('none' if not selected else 'multiple' if len(selected)>1 else
             'known_focus' if iou(selected[0],target)>=.5 else
             'known_unfocused' if known_unfocused else 'unreviewed_geometry')
    return dict(localized={str(t):best>=t for t in (.5,.7,.9)}, bestIoU=best,
                proposals=len(boxes),selected=len(selected),selection=outcome,
                selectedOnKnownUnfocused=known_unfocused,unreviewedSelections=unreviewed,
                knownControlsLocalized=len(matching([c['bounds'] for c in frame['controls']],boxes,.5)),
                knownControls=len(frame['controls']))


def score(frame, candidate, production):
    h.require(production['status']=='success' and production['inputSHA256']==frame['image']['sha256'],
              'production_image_or_status')
    config=production['configuration'];result=production['runtime']['result'];execution=result['focusExecution']
    h.require(config['platform']=='tvOS' and config['ocr'] is False and config['minConfidence']==.5 and
              execution['backend']=='coreML' and execution['modelScoringComplete'], 'production_configuration')
    boxes=[xywh(d) for d in candidate if d['score']>=.25]
    elements=result['elements'];prior=[bounds(e['boundingBoxPixels']) for e in elements]
    selected=[b for b,e in zip(prior,elements) if e['state'].get('isFocused') is True]
    return dict(family=frame['family'],aliases=frame['aliases'],conditions=frame['conditions'],
                candidate=arm_score(frame,boxes,boxes),production=arm_score(frame,prior,selected),
                lowConfidenceCandidateBestIoU=max((iou(xywh(d),next(c['bounds'] for c in frame['controls']
                    if c['state']=='focused')) for d in candidate),default=0.))


def summary(rows):
    groups=defaultdict(list)
    for row in rows:groups[row['family']].append(row)
    groups['all']=rows
    result={}
    for family,items in groups.items():
        result[family]={}
        for arm in ('candidate','production'):
            result[family][arm]=dict(frames=len(items),sourceFrameEntries=sum(len(r['aliases']) for r in items),
                localized={t:sum(r[arm]['localized'][t] for r in items) for t in ('0.5','0.7','0.9')},
                sourceEntryWeightedLocalized50=sum(len(r['aliases'])*r[arm]['localized']['0.5'] for r in items),
                selections=dict(Counter(r[arm]['selection'] for r in items)),
                selectedOnKnownUnfocused=sum(r[arm]['selectedOnKnownUnfocused'] for r in items),
                unreviewedSelections=sum(r[arm]['unreviewedSelections'] for r in items),
                knownControls=sum(r[arm]['knownControls'] for r in items),
                knownControlsLocalized=sum(r[arm]['knownControlsLocalized'] for r in items))
    return result


def prepare_environment():
    # Ultralytics falls back to /tmp when the configured parent is absent.
    # Materialize and check it before importing the library, not after its warning.
    for name, leaf in (('YOLO_CONFIG_DIR','yolo-config'),('MPLCONFIGDIR','matplotlib'),('TORCH_HOME','torch')):
        path=h.ROOT/'.build/debug-output'/leaf
        path.mkdir(parents=True,exist_ok=True)
        h.require(path.resolve().is_relative_to(h.ROOT) and os.access(path,os.W_OK),'cache_unavailable')
        os.environ[name]=str(path)
    (Path(os.environ['YOLO_CONFIG_DIR'])/'Ultralytics').mkdir(exist_ok=True)


def run(batch_path, output, *, replay=False, resume=False):
    from fixture_batch_review import validate
    batch_path=h.local(batch_path);output=h.local(output)
    batch=validate(batch_path);frames=select_frames(batch)
    h.require(0<len(frames)<=72, 'image_budget')
    fit=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/run/training-complete.json'
    checkpoint=h.read(fit)['checkpoint'];weights=h.checked(h.ROOT,checkpoint)
    binary=h.ROOT/'.build/debug/nativeui-audit'
    protocol=dict(version='reference-benchmark-v1',batch=h.ref(batch_path),frames=frames,
                  checkpoint=checkpoint,binary=h.ref(binary),runtime=runtime_identity(),
                  candidate=dict(imgsz=640,confidence=.25,candidateConfidence=.001,nms=.7,device='mps'),
                  production=dict(platform='tvOS',confidence=.5,ocr=False),
                  labels='provisional observed native calibration; human review pending')
    h.require(not (replay and resume),'conflicting_execution_mode')
    if replay or resume:h.require(h.read(output/'protocol.json')==protocol,'changed_protocol')
    else:
        h.fresh(output);output.mkdir(parents=True);h.write(output/'protocol.json',protocol)
    if not replay:
        prepare_environment()
        os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false')
        def offline(event,args):
            if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
        sys.addaudithook(offline)
        from ultralytics import YOLO
        start=time.monotonic();model=YOLO(str(weights))
        h.require(model.names=={0:'focusedControl'},'candidate_taxonomy')
        reused=0
        for i,f in enumerate(frames):
            saved=output/f'{i:03d}.json';prior=output/f'{i:03d}-production.json'
            if resume and (saved.exists() or prior.exists()):
                h.require(saved.is_file() and prior.is_file(),'incomplete_prediction_pair')
                retained=h.read(saved)
                h.require(retained['image']==f['image'] and retained['exitCode']==0,'resume_image_binding')
                score(f,retained['candidate'],h.read(prior));reused+=1
                continue
            path=h.checked(h.ROOT,f['image']);tick=time.monotonic()
            result=model.predict(source=str(path),imgsz=640,conf=.001,iou=.7,device='mps',save=False,verbose=False)[0]
            detections=[dict(box=b,score=s) for b,s in zip(result.boxes.xyxy.cpu().tolist(),result.boxes.conf.cpu().tolist())]
            candidate_seconds=time.monotonic()-tick
            command=[str(binary),'scan',str(path),'--platform','tvOS','--min-confidence','0.5',
                     '--no-ocr','--strict','--root',str(h.ROOT)]
            tick=time.monotonic()
            proc=subprocess.run(command,cwd=h.ROOT,text=True,capture_output=True,timeout=90,
                env={**os.environ,'TMPDIR':str(h.ROOT/'.build/debug-output/focus-launch/tmp')})
            (output/f'{i:03d}-production.json').write_text(proc.stdout)
            (output/f'{i:03d}.stderr').write_text(proc.stderr)
            h.write(output/f'{i:03d}.json',dict(image=f['image'],candidate=detections,exitCode=proc.returncode,
                candidateSeconds=candidate_seconds,productionSeconds=time.monotonic()-tick))
            h.require(proc.returncode==0,'production_failure_retained')
            h.require(sum(p.stat().st_size for p in output.iterdir())<=128*1024**2,'output_limit')
            print(f'{i+1}/{len(frames)} in {time.monotonic()-start:.1f}s',flush=True)
        h.write(output/'execution.json',dict(pid=os.getpid(),seconds=time.monotonic()-start,images=len(frames),
                                           reusedPredictionPairs=reused,newPredictionPairs=len(frames)-reused))
    rows=[];refs=[];identities=[];timings=Counter()
    for i,f in enumerate(frames):
        a=output/f'{i:03d}.json';p=output/f'{i:03d}-production.json';d=h.read(a);production=h.read(p)
        h.require(d['image']==f['image'] and d['exitCode']==0,'prediction_binding')
        rows.append(score(f,d['candidate'],production));refs.extend([h.ref(a),h.ref(p)])
        e=production['runtime']['result']['focusExecution']
        identities.append(dict(detector=production['runtime']['detector'],focusDigest=e.get('modelDigest'),
                               policy=e['policy'],threshold=e.get('threshold')))
        timings.update(candidateSeconds=d['candidateSeconds'],productionSeconds=d['productionSeconds'])
    h.require(all(i==identities[0] for i in identities),'production_model_changed')
    report=dict(version='reference-model-scorecard-v1',**h.FLAGS,protocol=h.ref(output/'protocol.json'),
                rawPredictions=refs,productionIdentity=identities[0],rows=rows,summary=summary(rows),timings=dict(timings),
                limitations=['Native labels remain provisional until human review.',
                    'Unmatched predictions on excluded/partial controls remain unreviewed.',
                    'Operating systems differ in threshold and training; not an isolated architecture comparison.',
                    'Reference renderer calibration is not independent real-app evaluation.'])
    if replay:h.require(h.read(output/'scorecard.json')==report,'replay_mismatch')
    else:h.write(output/'scorecard.json',report)
    print(report['summary'])
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True)
    p.add_argument('--output',required=True);p.add_argument('--replay',action='store_true');p.add_argument('--resume',action='store_true')
    a=p.parse_args();run(a.batch,a.output,replay=a.replay,resume=a.resume)
