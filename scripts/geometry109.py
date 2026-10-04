"""Whole-bank extent diagnosis and fixed geometry comparison preparation."""
import argparse
from pathlib import Path
import time
import numpy as np
import diagnose_retention105 as diagnosis

r=diagnosis.r; h=r.d.h
METRIC=h.ROOT/'reports/work/RANK-METRIC-108/artifacts/verified/evaluation.json'


def truth_by_frame(rows):
    result={}
    for row in rows:
        for image,box in zip(row['images'],row['boxes']):
            values=result.setdefault(image['sha256'],[])
            if box not in values:values.append(box)
    return result


def audit(output):
    start=time.monotonic(); out=h.fresh(output)
    protocol,bank,inputs,data,rows,positives=diagnosis.load()
    truth=truth_by_frame(rows)
    metric=r.sealed(METRIC,'metric108-evaluation-v1')
    h.require(metric['sources']['bank']==protocol['bank'] and metric['sources']['supervision']==protocol['supervision'],
              'geometry_metric_binding')
    controls={'DTM020':r.sealed(h.checked(h.ROOT,protocol['reference']),'native-ranking-reference-v1'),
              'DTM027':r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/retention105-dtm027/result.json',r.VERSION)}
    picks={}
    for name,doc in controls.items():
        h.require([v['id'] for v in doc['results']]==[v['id'] for v in rows],'geometry_control_membership')
        picks[name]={im['sha256']:pick for row,value in zip(rows,doc['results']) for im,pick in zip(row['images'],value['selected'])}
    metric_frames={v['frameID']:v for v in metric['details']['sameFrameExcluded']}
    old={im['sha256'] for row in rows[:73] if row['split']=='train' for im in row['images']}
    frames=[]
    for frame in inputs['frames']:
        boxes=truth[frame['id']]
        # Report a conservative interval; do not select a replacement truth.
        quality=[min(r.iou(c['bounds'],box) for box in boxes) for c in frame['candidates']]
        h.require({c['id'] for c,q in zip(frame['candidates'],quality) if q>=.5}==set(positives[frame['id']]),'geometry_positive_parity')
        scores=metric_frames[frame['id']]['candidates']
        h.require([v['candidateID'] for v in scores]==[c['id'] for c in frame['candidates']],'geometry_metric_membership')
        chosen={name:values[frame['id']] for name,values in picks.items()}
        chosen['metric108']=r.choose(frame['candidates'],[v['score'] for v in scores])
        best=max(quality); measurements={}
        for name,candidate in chosen.items():
            x,y,w,z=candidate['bounds']
            overlaps=[r.iou(candidate['bounds'],box) for box in boxes]; overlap=min(overlaps)
            measurements[name]=dict(candidateID=candidate['id'],iou=overlap,regret=best-overlap,
                iouRange=[min(overlaps),max(overlaps)],
                extentByAnnotation=[dict(widthRatio=w/tw,heightRatio=z/th,
                    centerError=[(x+w/2-tx-tw/2)/tw,(y+z/2-ty-th/2)/th]) for tx,ty,tw,th in boxes])
        frames.append(dict(frameID=frame['id'],group='settingsDevelopment' if frame['split']=='development' else 'oldTrain' if frame['id'] in old else 'newTrain',
            truthVariants=boxes,geometryConsistent=len(boxes)==1,maxIoU=best,positiveCount=sum(q>=.5 for q in quality),
            positiveIoURange=max(q for q in quality if q>=.5)-min(q for q in quality if q>=.5),
            candidates=[dict(**c,iou=q,iouRange=[q,max(r.iou(c['bounds'],box) for box in boxes)]) for c,q in zip(frame['candidates'],quality)],models=measurements))
    summary={}
    for group in ('oldTrain','newTrain','settingsDevelopment'):
        subset=[f for f in frames if f['group']==group]
        summary[group]=dict(frames=len(subset),proposalCovered=sum(f['maxIoU']>=.5 for f in subset),
            conflictingGeometry=sum(not f['geometryConsistent'] for f in subset),
            maxBelow075=sum(f['maxIoU']<.75 for f in subset),multiplePositives=sum(f['positiveCount']>1 for f in subset),
            positiveSpreadAbove01=sum(f['positiveIoURange']>.1 for f in subset),
            models={name:dict(correct=sum(f['models'][name]['iou']>=.5 for f in subset),
                meanIoU=float(np.mean([f['models'][name]['iou'] for f in subset])),
                meanRegret=float(np.mean([f['models'][name]['regret'] for f in subset])),
                regretAbove01=sum(f['models'][name]['regret']>.1 for f in subset)) for name in chosen})
    out.mkdir(parents=True)
    conflicts=[]
    for frame in frames:
        if frame['geometryConsistent']:continue
        occurrences=[]
        for row in rows:
            for endpoint,image in enumerate(row['images']):
                if image['sha256']!=frame['frameID']:continue
                h.checked(h.ROOT,image)
                source=row['evidence'][0]; raw=h.read(h.checked(h.ROOT,source))
                cap=raw['endpoints'][endpoint]['capture_endpoint']
                h.require(cap['frame_png_sha256']==image['sha256'],'geometry_raw_image_binding')
                scenes=[]
                for position in ('before_scene','after_scene'):
                    scene=cap[position]
                    focused=[v for v in scene['elements'] if v.get('is_focused')]
                    h.require(len(focused)==1,'geometry_raw_focus')
                    geometry=focused[0]['rendered_body_geometry']
                    h.require(geometry['visible_pixel_bounds']==row['boxes'][endpoint],'geometry_consumer_source_divergence')
                    scenes.append(dict(position=position,generation=scene['observation_generation'],
                        settled=scene['is_settled'],elementID=focused[0]['element_id'],geometry=geometry))
                occurrences.append(dict(pairID=row['id'],endpoint=endpoint,image=image,source=source,
                    box=row['boxes'][endpoint],scenes=scenes,correlation=cap['correlation'],
                    frameReceivedHostNS=cap['frame_received_host_ns']))
        conflicts.append(dict(frameID=frame['frameID'],truthVariants=frame['truthVariants'],occurrences=occurrences))
    report=dict(version='geometry109-audit-v1',**h.FLAGS,sourceProtocol=h.ref(diagnosis.READY/'rank-protocol.json'),
        bank=protocol['bank'],supervision=protocol['supervision'],metric=h.ref(METRIC),
        summary=summary,frames=frames,conflicts=conflicts,
        geometryTrainingEligible=all(f['geometryConsistent'] for f in frames if f['group']!='settingsDevelopment'),
        elapsedSeconds=time.monotonic()-start,implementation=h.ref(Path(__file__)))
    h.write(out/'audit.json',report,sealed=True); print(summary); return report


def prepare(output,audit_path):
    """Produce a reviewable protocol; blocked geometry never gets launch approval."""
    out=h.fresh(output); path=h.local(audit_path)
    diagnostic=h.sealed(path,'geometry109-audit-v1')
    previous,_,inputs,_,rows,_=diagnosis.load()
    h.require(diagnostic['bank']==previous['bank'] and diagnostic['supervision']==previous['supervision'],
              'geometry_audit_binding')
    doc={k:v for k,v in previous.items() if k not in ('protocolSHA256','pins','configuration')}
    doc.update(configuration=r.GEOMETRY_CONFIG,pins=r.pins(),geometryAudit=h.ref(path))
    doc['protocolSHA256']=h.digest(doc)
    out.mkdir(parents=True);h.write(out/'protocol.json',doc)
    try:
        report,_=r.load_protocol(out/'protocol.json',r.ARM,'geometry109-candidate')
    except ValueError as error:
        if not str(error).startswith('geometry_truth_conflict:'):raise
        report=dict(launchEligible=False,blockers=[str(error)],protocolSHA256=doc['protocolSHA256'],
            configurationValid=True,trainingLaunched=False,approvalCreated=False,
            conflictingFrameIDs=[v['frameID'] for v in diagnostic['conflicts']])
    h.write(out/'preflight.json',report,sealed=True); print(report); return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--prepare-from-audit')
    a=p.parse_args()
    prepare(a.output,a.prepare_from_audit) if a.prepare_from_audit else audit(a.output)
