"""Fixed proposal and selective OCR experiments; outputs remain diagnostic-only."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image
import human_annotation_review as h
import real_model_scorecard as s
from human_auto_boxes import detect
from compare_annotation_proposals import validate_boxes

BASE=h.ROOT/'reports/work/REAL-MODEL-SCORECARD-36/production'


def inside(text_box, body):
    x,y,w,v=text_box;X,Y,W,V=body
    return X<=x+w/2<=X+W and Y<=y+v/2<=Y+V


def union(*groups):
    result=[]
    for group in groups:
        for b in group:
            if not any(s.iou(b,c)>=.9 for c in result):result.append(b)
    return result


def ocr_rows(boxes, text):
    return [b for b in boxes if b[2]/b[3]>=3 and any(
        t['confidence']>=.5 and inside(t['bounds'],b) for t in text)]


def semantic_hint(text, body):
    words=[t['text'].strip().casefold() for t in text if t.get('text') and
           t['confidence']>=.5 and inside(t['bounds'],body)]
    return 'cancelAction' if 'cancel' in words else None


def ios_samples():
    root=h.ROOT/'reports/work/IOS-R013-EVAL';dataset=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r7'
    predictions=h.read(root/'candidate_predictions.json',128*1024*1024)
    names=h.taxonomy();h.require(h.sha(h.CATEGORY)==predictions['categoryMap']['sha256'],'changed_taxonomy')
    from model_priority_preflight import yolo_box
    counts=Counter();chosen=[]
    for row in sorted(predictions['results'],key=lambda r:r['imageID']):
        if all(counts[n]==12 for n in ('secondaryButton','cancelAction')):break
        label_path=row['imageID'].replace('/images/','/labels/').replace('.png','.txt')
        label=h.checked(dataset,dict(path=label_path,sha256=row['labelSHA256']))
        truth=[yolo_box(l,row['width'],row['height']) for l in label.read_text().splitlines() if l.strip()]
        for cid,body in truth:
            name=names[cid]
            if name not in ('secondaryButton','cancelAction') or counts[name]>=12:continue
            proposals=[(d,s.bounds(dict(zip(('x','y','width','height'),
                [d['xyxyPixels'][0],d['xyxyPixels'][1],d['xyxyPixels'][2]-d['xyxyPixels'][0],
                 d['xyxyPixels'][3]-d['xyxyPixels'][1]])))) for d in row['detections'] if d['score']>=.25]
            proposals.sort(key=lambda x:(-s.iou(body,x[1]),-x[0]['score']))
            if not proposals or s.iou(body,proposals[0][1])<.5:continue
            # The retained YOLO dataset links to its reconstructed in-project originals.
            # Pin the resolved source; generic harvest intake remains link-free.
            image=h.local(dataset/row['imageID'])
            h.require(h.sha(image)==row['imageSHA256'],'changed_ios_image')
            d,b=proposals[0];counts[name]+=1
            chosen.append(dict(id='ios-'+Path(row['imageID']).stem,image=h.ref(image),truth=name,
                predictedRole=names[d['classID']],predictedBounds=b,truthBounds=body,label=h.ref(label)))
            break
    h.require(len(chosen)==24 and len({r['id'] for r in chosen})==24,'ios_sample_incomplete')
    return chosen


def geometry(boxes, frame, threshold):
    matches=s.matching([c['bounds'] for c in frame['controls']],boxes,threshold)
    focused=[i for i,c in enumerate(frame['controls']) if c['state']=='focused']
    return dict(reviewed=len(frame['controls']),located=len(matches),focused=len(focused),
                focusedLocated=sum(i in matches for i in focused),proposals=len(boxes),
                unreviewedProposals=len(boxes)-len(matches))


def run(output, tool, replay=False):
    out=h.local(output);tool=h.local(tool);frames=s.load_frames(s.INVENTORY);ios=ios_samples()
    requests=[dict(id=f['sha256'],path=str(h.checked(h.ROOT,f['image'])),sha256=f['sha256']) for f in frames]
    requests += [dict(id=r['id'],path=str(h.checked(h.ROOT,r['image'])),sha256=r['image']['sha256']) for r in ios]
    sources=[h.ref(h.ROOT/'scripts'/n) for n in ('vision_annotation_probe.swift','human_auto_boxes.py','proposal_recovery.py')]
    protocol=dict(version='proposal-recovery-v1',**h.FLAGS,requests=requests,ios=ios,
        inventory=h.ref(s.INVENTORY),binary=h.ref(tool),sources=sources,
        baseline=[h.ref(BASE/f'{i:03d}.json') for i in range(len(frames))])
    if not replay:
        h.fresh(out);out.mkdir(parents=True);h.write(out/'protocol.json',protocol,sealed=True)
        started=time.monotonic()
        for chunk,offset in enumerate(range(0,len(requests),40)):
            proc=subprocess.run([str(tool)],input=json.dumps(dict(version=1,root=str(h.ROOT),frames=requests[offset:offset+40])),
                text=True,capture_output=True,timeout=max(1,600-(time.monotonic()-started)),
                env={**os.environ,'TMPDIR':str(h.ROOT/'.build/debug-output/focus-launch/tmp')})
            (out/f'vision-{chunk}.json').write_text(proc.stdout);(out/f'vision-{chunk}.stderr').write_text(proc.stderr)
            h.require(proc.returncode==0,'vision_failed_retained')
        h.write(out/'timing.json',dict(visionWallSeconds=time.monotonic()-started,pid=os.getpid()))
    else:
        prior=h.sealed(out/'protocol.json','proposal-recovery-v1')
        for key in ('requests','ios','inventory','binary','baseline'):
            h.require(prior[key]==protocol[key],'replay_inputs_changed')
    native=[]
    for chunk in range((len(requests)+39)//40):native+=h.read(out/f'vision-{chunk}.json')['results']
    h.require([r['id'] for r in native]==[r['id'] for r in requests],'native_membership_mismatch')
    for expected,observed in zip(requests,native):
        h.require(expected['sha256']==observed['sha256'] and not observed['errors'],'native_frame_failed')
    started=time.monotonic();rows=[]
    for i,(f,v) in enumerate(zip(frames,native)):
        with Image.open(h.checked(h.ROOT,f['image'])) as image:
            h.require(image.size==(v['width'],v['height']),'dimensions_changed')
            raster=[[x,y,X-x,Y-y] for (x,y),(X,Y) in detect(image)]
        vision=[];rejected=0
        for p in v['rectangles']:
            try:validate_boxes([p['bounds']],v['width'],v['height'])
            except ValueError:rejected+=1
            else:vision.append(p['bounds'])
        old=h.read(BASE/f'{i:03d}.json');h.require(old['inputSHA256']==f['sha256'],'baseline_changed')
        yolo=[s.bounds(e['boundingBoxPixels']) for e in old['runtime']['result']['elements']]
        arms=dict(yolo=yolo,raster=raster,vision=vision,ocrSupportedRows=ocr_rows(raster,v['text']),
                  yoloRaster=union(yolo,raster),allGeometry=union(yolo,raster,vision))
        rows.append(dict(image=f['image'],screen=f['screen'],arms=arms,rejectedVision=rejected,
            suppressedDuplicates=len(yolo)+len(raster)+len(vision)-len(arms['allGeometry']),
            metrics={name:{str(t):geometry(boxes,f,t) for t in (.5,.75)} for name,boxes in arms.items()}))
        h.require(time.monotonic()-started+h.read(out/'timing.json')['visionWallSeconds']<600,'processing_budget')
    hints=[]
    for r,v in zip(ios,native[len(frames):]):
        hint=semantic_hint(v['text'],r['predictedBounds'])
        hints.append(dict(**r,hint=hint,correctHint=hint==r['truth'] if hint else None,
            coarseButton=r['predictedRole'] in ('primaryButton','secondaryButton','cancelAction','destructiveButton')))
    totals={arm:{str(t):{key:sum(r['metrics'][arm][str(t)][key] for r in rows)
                  for key in rows[0]['metrics'][arm][str(t)]} for t in (.5,.75)} for arm in rows[0]['arms']}
    result=dict(version='proposal-recovery-result-v1',**h.FLAGS,protocol=h.ref(out/'protocol.json'),
        raw=[h.ref(out/f'vision-{i}.json') for i in range((len(requests)+39)//40)],
        frames=rows,totals=totals,ios=hints,rasterAndScoringSeconds=time.monotonic()-started,
        iosSummary=dict(samples=len(hints),originalExact=sum(r['truth']==r['predictedRole'] for r in hints),
            coarseButton=sum(r['coarseButton'] for r in hints),hinted=sum(r['hint'] is not None for r in hints),
            correctHints=sum(r['correctHint'] is True for r in hints),wrongHints=sum(r['correctHint'] is False for r in hints)))
    if replay and (out/'result.json').exists():
        prior=h.sealed(out/'result.json','proposal-recovery-result-v1')
        h.require(all(prior[k]==result[k] for k in ('protocol','raw','frames','totals','ios','iosSummary')),
                  'replay_changed')
        print('Retained Vision output replay matches proposal and iOS results.');return
    h.write(out/'result.json',result,sealed=True)
    lines=['# Proposal recovery and selective semantics','',
      'Reused development data. These are proposal recall figures, not focus selection or precision.',
      '', '| Arm | Body matches /583 | Focused matches /46 | Proposals |', '|---|---:|---:|---:|']
    for arm,values in totals.items():
        d=values['0.5'];lines.append(f"| {arm} | {d['located']} | {d['focusedLocated']} | {d['proposals']} |")
    lines += ['',f"Selective iOS result: `{result['iosSummary']}`.",
        'Cancel is a selective hint; other labels abstain. No truth relabeling or semantic accuracy extrapolation.']
    (out/'result.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(totals=totals,ios=result['iosSummary'])))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--tool',required=True);p.add_argument('--replay',action='store_true')
    a=p.parse_args();run(a.output,a.tool,a.replay)
