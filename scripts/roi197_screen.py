"""Materialize and falsify the frozen one-extra-ROI rule on training sources only."""
import argparse
import copy
import time
import roi197 as a
import roi196 as candidate

h,p,e,r = a.h,a.p,a.e,a.r
OUT=h.ROOT/'reports/work/IOS-PROPOSAL-197/artifacts/screen01'


def prepare():
    h.require(not OUT.exists(),'output_collision')
    support=p.sealed(a.OUT/'support.json')
    for ref in support['sources']:h.checked(h.ROOT,ref,256*1024**2)
    parent=r.c.inputs();req=e.load_request(h.checked(h.ROOT,parent['manifests']['fit']),41)
    images={im.image_id:im for im in req.images}
    end=p.sealed(candidate.OUT/'candidate/completion.json')
    h.require(end['exitCode']==0,'candidate_failed')
    checkpoint=h.checked(h.ROOT,end['checkpoint'],256*1024**2)
    h.require(h.sha(checkpoint)=='de3ffdeec3c4767edc2d4bea0059294a26d87b6c9fc03b9d684de769ed3dd638','checkpoint')
    entries=[];records=[];old=r.OUT;r.OUT=OUT
    try:
        OUT.mkdir(parents=True)
        for i,row in enumerate(support['rows']):
            if row['candidateWindow'] is None:continue
            im=images[row['imageID']];key=f'fit-{i:04d}'
            entry,audit=r.save_crop(im,row['candidateWindow'],OUT/'crops',key)
            entries.append(entry);records.append(dict(row,cropID=key,audit=audit))
    finally:r.OUT=old
    h.require(len(entries)==135,'membership_count')
    h.write(OUT/'input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi197-fit-screen',images=entries))
    e.load_request(OUT/'input.json',41)
    h.write(OUT/'protocol.json',dict(checkpoint=h.ref(checkpoint),support=h.ref(a.OUT/'support.json'),
        membership=h.ref(OUT/'input.json'),base=parent['reused']['022']['fit'],original=parent['manifests']['fit'],
        records=records,settings=r.c.SETTINGS,sources=[h.ref(__file__),h.ref(a.__file__),h.ref(r.__file__)],
        outputBudgetBytes=512*1024**2,training=False,scope='train-fit falsification only'),sealed=True)


def protocol():
    d=p.sealed(OUT/'protocol.json')
    for ref in d['sources']+[d['checkpoint'],d['support'],d['membership'],d['base'],d['original']]:
        h.checked(h.ROOT,ref,256*1024**2)
    return d


def infer():
    d=protocol();start=time.monotonic()
    e.export_predictions(h.checked(h.ROOT,d['membership']),h.checked(h.ROOT,d['checkpoint'],256*1024**2),
                         OUT/'predictions.json','mps',discard_degenerate=True)
    h.write(OUT/'inference.json',dict(seconds=time.monotonic()-start,checkpoint=d['checkpoint']),sealed=True)


def admit(base,crop,cid):
    chosen,reason=a.candidate(base,cid)
    if chosen is None:return None,reason
    h.require(crop['status'] in ('ok','empty'),'failed_crop')
    roi=r.window(base['width'],base['height'],chosen[1]['xyxyPixels'])
    h.require(crop['width']==roi[2]-roi[0] and crop['height']==roi[3]-roi[1],'crop_dimensions')
    donors=[]
    for d in crop['detections']:
        if d['classID']!=cid or d['score']<.25:continue
        box=r.restore(d['xyxyPixels'],roi)
        if e.iou_xyxy(box,chosen[1]['xyxyPixels'])>=.25:donors.append(dict(d,xyxyPixels=box))
    if len(donors)!=1:return None,'no_unique_donor'
    if any(e.iou_xyxy(donors[0]['xyxyPixels'],v['xyxyPixels'])>=.5 for _,v in r.proposals(base,cid)):
        return None,'duplicate_operating'
    return donors[0],'added'


def report():
    d=protocol();dest=OUT/'report.json';h.require(not dest.exists(),'output_collision')
    req=e.load_request(h.checked(h.ROOT,d['membership']),41)
    crops=e.validated_artifact(h.read(OUT/'predictions.json',256*1024**2),req,d['checkpoint']['sha256'],expected_settings=d['settings'])
    parent=r.c.inputs();original=e.load_request(h.checked(h.ROOT,d['original']),41)
    base=e.validated_artifact(h.read(h.checked(h.ROOT,d['base'],256*1024**2),256*1024**2),original,
        parent['checkpoints']['022']['sha256'],expected_settings=d['settings'])
    bycrop={x['imageID']:x for x in crops['results']};bybase={x['imageID']:x for x in base['results']}
    images={im.image_id:im for im in original.images};cid=e.load_names().index('pageControl');rows=[]
    for record in d['records']:
        b=bybase[record['imageID']];donor,reason=admit(b,bycrop[record['cropID']],cid)
        truths=r.c.g.r.f.d.prior.truth(images[record['imageID']],cid)
        new_hit=bool(donor and any(e.iou_xyxy(donor['xyxyPixels'],truths[i])>=.5 for i in record['missingTruthIndices']))
        rows.append(dict(imageID=record['imageID'],reason=reason,added=donor,
            negative=not record['candidateHasVisiblePage'],partial=record['candidateHasVisiblePage'] and record['candidateContainsAny']==0,
            recoversMissing=new_hit,addedMatchesAny=bool(donor and any(e.iou_xyxy(donor['xyxyPixels'],t)>=.5 for t in truths))))
    negative_fp=sum(v['negative'] and v['added'] is not None for v in rows)
    recovered=sum(v['recoversMissing'] for v in rows)
    h.write(dest,dict(rows=rows,negativeCases=sum(v['negative'] for v in rows),negativeFalseAdmissions=negative_fp,
        partialCases=sum(v['partial'] for v in rows),added=sum(v['added'] is not None for v in rows),
        recoveredMissing=recovered,addedWithoutTruthMatch=sum(v['added'] is not None and not v['addedMatchesAny'] for v in rows),
        negativeScreenPassed=negative_fp==0,retainedEvaluationReady=negative_fp==0 and recovered>0,
        protocol=h.ref(OUT/'protocol.json'),predictions=h.ref(OUT/'predictions.json'),
        modelQualified=False,scope='Fit-only screen; truth overlap diagnostic is not full AP or independent evaluation.'),sealed=True)
    print({k:v for k,v in p.sealed(dest).items() if k not in ('rows','protocol','predictions')})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','infer','report']);args=parser.parse_args()
    globals()[args.mode]()
