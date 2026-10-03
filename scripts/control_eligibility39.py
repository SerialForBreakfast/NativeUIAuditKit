"""Replay fixed proposal eligibility and audit page-group coverage, without inference."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import statistics

import human_annotation_review as h
import real_model_scorecard as s
from local_diagnostics38 import decision
from model_priority_preflight import yolo_box

OUT=h.ROOT/'reports/work/CONTROL-ELIGIBILITY-39'
SOURCE=h.ROOT/'reports/work/PROPOSAL-RECOVERY-37/comparison/result.json'
SCORES=h.ROOT/'reports/work/LOCAL-DIAGNOSTICS-38/focus-v3'


def contains_center(outer, inner):
    x,y,w,v=outer;X,Y,W,V=inner
    return x<=X+W/2<=x+w and y<=Y+V/2<=y+v


def eligible(box, anchors):
    """Conservative fixed refinement, not a detector of unanchored controls."""
    if not any(s.iou(box,a)>=.5 for a in anchors):return False
    inside=[a for a in anchors if contains_center(box,a)]
    for i,a in enumerate(inside):
        for b in inside[i+1:]:
            if s.iou(a,b)==0:return False
    return True


def outcome(boxes, scores, controls):
    if not boxes:return dict(outcome='no_candidates',winner=None,probability=None,targetBest=None)
    return decision(boxes,scores,controls)


def replay(output):
    out=h.fresh(output);out.mkdir(parents=True)
    source=h.sealed(SOURCE,'proposal-recovery-result-v1');frames={f['sha256']:f for f in s.load_frames(s.INVENTORY)}
    base=h.ROOT/'reports/work/REAL-MODEL-SCORECARD-36/production'
    docs={h.read(p)['inputSHA256']:(p,h.read(p)) for p in base.glob('[0-9][0-9][0-9].json')}
    rows=[];refs=[h.ref(SOURCE),h.ref(s.INVENTORY),h.ref(Path(__file__))];groups=defaultdict(list)
    for index,r in enumerate(source['frames']):
        f=frames[r['image']['sha256']];h.checked(h.ROOT,f['image'])
        path,doc=docs[f['sha256']];refs.append(h.ref(path));result=doc['runtime']['result']
        allowed={v['observationID'] for v in result['focusExecution']['candidates'] if v['disposition']=='scored'}
        original=[s.bounds(e['boundingBoxPixels']) for e in result['elements']]
        anchors=[s.bounds(e['boundingBoxPixels']) for e in result['elements'] if e['id'] in allowed]
        boxes=r['arms']['allGeometry'];raw=[]
        paths=sorted(SCORES.glob(f'{index:03d}-*.json'),key=lambda p:int(p.stem.split('-')[1]))
        for p in paths:refs.append(h.ref(p));raw+=h.read(p)['results']
        h.require([int(v['id']) for v in raw]==list(range(len(boxes))),'score_membership_changed')
        probabilities=[v['probability'] for v in raw]
        arms=dict(geometry=list(range(len(boxes))),
            rolePreserving=[i for i,b in enumerate(boxes) if b not in original or b in anchors],
            supportedRefinement=[i for i,b in enumerate(boxes) if b in anchors or (b not in original and eligible(b,anchors))])
        measurements={}
        for name,indices in arms.items():
            selected=[boxes[i] for i in indices];scores=[probabilities[i] for i in indices]
            target=next(c['bounds'] for c in f['controls'] if c['state']=='focused')
            measurements[name]=dict(candidates=len(indices),targetLocated=any(s.iou(b,target)>=.5 for b in selected),
                **outcome(selected,scores,f['controls']))
        # A directory is a conservative acquisition batch, not proof of independence.
        group=str(Path(f['image']['path']).parent);groups[group].append(f['sha256'])
        rows.append(dict(image=f['sha256'],screen=f['screen'],complete=f['complete'],acquisitionBatch=group,arms=measurements))
    totals={}
    for arm in ('geometry','rolePreserving','supportedRefinement'):
        totals[arm]=dict(candidates=sum(r['arms'][arm]['candidates'] for r in rows),
            targetLocated=sum(r['arms'][arm]['targetLocated'] for r in rows),
            allOutcomes=dict(Counter(r['arms'][arm]['outcome'] for r in rows)),
            completeOutcomes=dict(Counter(r['arms'][arm]['outcome'] for r in rows if r['complete'])))
    result=dict(version='control-eligibility-diagnostic-v1',**h.FLAGS,inputs=refs,rows=rows,totals=totals,
        grouping=dict(acquisitionBatches=dict(groups),untouchedEvaluationFrames=0,
            reason='All46 frames informed prior development. Batch names do not establish independent app/layout ancestry.'))
    h.write(out/'result.json',result,sealed=True);print(totals)


def summary(values):
    return dict(count=len(values),min=min(values),median=statistics.median(values),max=max(values)) if values else dict(count=0)


def geometry_diagnosis(truth, detections):
    if not detections:return dict(bestIoU=0,score=None,widthRatio=None,heightRatio=None)
    def box(d):
        x,y,X,Y=d['xyxyPixels'];return [x,y,X-x,Y-y]
    best=max(detections,key=lambda d:s.iou(truth,box(d)));b=box(best)
    return dict(bestIoU=s.iou(truth,b),score=best['score'],widthRatio=b[2]/truth[2],heightRatio=b[3]/truth[3],bounds=b)


def pages(output):
    out=h.fresh(output);out.mkdir(parents=True)
    base=h.ROOT/'reports/work/IOS-R013-EVAL';pre=h.read(base/'preflight.json',64*1024*1024)
    dataset=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r7';cid=h.taxonomy().index('pageControl')
    stats=defaultdict(lambda:dict(frames=0,width=[],height=[],aspect=[],inputHeight=[],labels=[]));refs=[]
    for m in pre['members']:
        if cid not in m['classes']:continue
        p=dataset/m['imageID'].replace('/images/','/labels/').replace('.png','.txt')
        label=h.checked(h.ROOT,dict(path=str(p.relative_to(h.ROOT)),sha256=m['labelSHA256']))
        truth=[b for c,b in (yolo_box(l,m['width'],m['height']) for l in label.read_text().splitlines() if l.strip()) if c==cid]
        h.require(bool(truth),'support_manifest_conflict')
        st=stats[m['split']+'/'+m['family']];st['frames']+=1;st['labels'].append(h.ref(label))
        for b in truth:
            st['width'].append(b[2]);st['height'].append(b[3]);st['aspect'].append(b[2]/b[3]);st['inputHeight'].append(b[3]*640/max(m['width'],m['height']))
    coverage={k:dict(frames=v['frames'],labels=v['labels'],**{name:summary(v[name]) for name in ('width','height','aspect','inputHeight')}) for k,v in stats.items()}
    prior=h.ROOT/'reports/work/LOCAL-DIAGNOSTICS-38/ios';protocol=h.read(prior/'protocol.json');rows=[]
    for size in protocol['sizes']:
        predpath=prior/f'predictions-{size}.json';refs.append(h.ref(predpath));pred=h.read(predpath)
        h.require([r['imageID'] for r in pred]==[m['imageID'] for m in protocol['members']],'prediction_membership')
        for m,r in zip(protocol['members'],pred):
            h.checked(h.ROOT,m['image']);label=h.checked(h.ROOT,m['label'])
            truths=[b for c,b in (yolo_box(l,m['width'],m['height']) for l in label.read_text().splitlines() if l.strip()) if c==cid]
            for b in truths:
                rows.append(dict(imageID=m['imageID'],family=m['family'],size=size,truth=b,
                    **geometry_diagnosis(b,[d for d in r['detections'] if d['classID']==cid])))
    files=['NativeUIPageControlView.swift','GalleryPageTemplate.swift','OnboardingPageTemplate.swift',
           'UIKitControlsViewController.swift','UIKitGeneratorViewController.swift','KitchenSinkTemplate.swift',
           'MediaCardGridTemplate.swift','ProgressActivityTemplate.swift']
    refs += [h.ref(h.ROOT/'NativeUIDatasetGenerator/Templates'/name) for name in files]
    totals={str(size):dict(bestOverlapAt50=sum(r['bestIoU']>=.5 for r in rows if r['size']==size),
        widthRatio=summary([r['widthRatio'] for r in rows if r['size']==size and r['widthRatio'] is not None]),
        heightRatio=summary([r['heightRatio'] for r in rows if r['size']==size and r['heightRatio'] is not None])) for size in protocol['sizes']}
    h.write(out/'audit.json',dict(version='page-control-audit-v1',**h.FLAGS,inputs=[h.ref(base/'preflight.json'),*refs],
        coverage=coverage,rows=rows,summary=totals),sealed=True)
    print({k:{x:v for x,v in r.items() if x!='labels'} for k,r in coverage.items()});print(totals)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['replay','pages']);p.add_argument('--output',required=True)
    a=p.parse_args();globals()[a.mode](a.output)
