"""Cached proposal failure accounting; never changes prediction thresholds or boxes."""
import collections
import time
import roi196 as r
h,p,e=r.h,r.p,r.e


def classify(truths,detections,cid):
    page=[d for d in detections if d['classID']==cid]
    operating=sorted([d for d in page if d['score']>=.25],key=lambda d:-d['score'])
    used=set();false=[];hits=[]
    for d in operating:
        overlaps=[e.iou_xyxy(d['xyxyPixels'],t) for t in truths]
        available=[i for i,v in enumerate(overlaps) if i not in used and v>=.5]
        if available:
            index=max(available,key=overlaps.__getitem__);used.add(index);hits.append(index)
        else:false.append('duplicate' if max(overlaps,default=0)>=.5 else 'geometry' if max(overlaps,default=0)>0 else 'no_overlap')
    missed=[]
    for i,t in enumerate(truths):
        if i in used:continue
        local=[d for d in page if e.iou_xyxy(d['xyxyPixels'],t)>0]
        good=[d for d in local if e.iou_xyxy(d['xyxyPixels'],t)>=.5]
        reason='assignment_conflict' if any(d['score']>=.25 for d in good) else 'low_confidence' if good else 'geometry' if local else 'no_overlapping_exported_proposal'
        missed.append(dict(truthIndex=i,reason=reason,maxIoU=max((e.iou_xyxy(d['xyxyPixels'],t) for d in page),default=0),
                           maxOverlappingScore=max((d['score'] for d in local),default=None)))
    return dict(truths=len(truths),exported=len(page),operating=len(operating),truePositives=len(hits),
        falsePositives=false,misses=missed,exportFloorCountCeiling=min(len(truths),len(page)))


def run():
    out=r.OUT/'proposal-recall.json';h.require(not out.exists(),'output_collision');start=time.monotonic()
    parent=r.r.c.inputs();cid=e.load_names().index('pageControl');rows=[];summaries={};sources=[]
    for kind,ref in parent['manifests'].items():
        req=e.load_request(h.checked(h.ROOT,ref),41);path=h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2)
        doc=e.validated_artifact(h.read(path,256*1024**2),req,parent['checkpoints']['022']['sha256'],expected_settings=r.r.c.SETTINGS)
        predictions={v['imageID']:v for v in doc['results']};cases=[]
        for im in req.images:
            row=dict(kind=kind,imageID=im.image_id,**classify(r.r.c.g.r.f.d.prior.truth(im,cid),predictions[im.image_id]['detections'],cid));cases.append(row)
        summaries[kind]=dict(images=len(cases),truths=sum(v['truths'] for v in cases),TP=sum(v['truePositives'] for v in cases),
            FP=dict(collections.Counter(reason for v in cases for reason in v['falsePositives'])),
            FN=dict(collections.Counter(m['reason'] for v in cases for m in v['misses'])),
            exportedCountCeiling=sum(v['exportFloorCountCeiling'] for v in cases),exportedProposals=sum(v['exported'] for v in cases))
        rows.extend(cases);sources.extend([ref,h.ref(path)])
    h.write(out,dict(summaries=summaries,rows=rows,sources=sources+[h.ref(__file__)],seconds=time.monotonic()-start,
        interpretation='Greedy IoU0.5/confidence0.25 diagnostic. Export-floor count ceiling is optimistic, not deployable recall. No threshold tuning or oracle crops.',
        inferenceLaunched=False,trainingLaunched=False),sealed=True)
    print(summaries,flush=True)


if __name__=='__main__':run()
