"""Cached ROI transfer diagnosis and training-only coverage proposal."""
import collections
import math
import statistics
import time
from pathlib import Path
from PIL import Image
import roi194 as x

h,p,e=x.h,x.p,x.e
OUT=h.ROOT/'reports/work/IOS-ROI-195/artifacts'


def geometry(box,truth):
    width,height=truth[2]-truth[0],truth[3]-truth[1]
    h.require(width>0 and height>0,'invalid_truth')
    return dict(iou=e.iou_xyxy(box,truth),widthRatio=(box[2]-box[0])/width,heightRatio=(box[3]-box[1])/height,
        centerX=((box[0]+box[2])-(truth[0]+truth[2]))/(2*width),centerY=((box[1]+box[3])-(truth[1]+truth[3]))/(2*height))


def compare_row(before,after,truths):
    h.require(before['classID']==after['classID'] and before['score']==after['score'],'prediction_conservation')
    overlaps=[e.iou_xyxy(before['xyxyPixels'],t) for t in truths]
    index=max(range(len(truths)),key=overlaps.__getitem__) if overlaps and max(overlaps)>0 else None
    row=dict(changed=before['xyxyPixels']!=after['xyxyPixels'],operating=before['score']>=.25,score=before['score'],truthIndex=index)
    if index is None:return dict(row,disposition='no_overlap_truth')
    a,b=geometry(before['xyxyPixels'],truths[index]),geometry(after['xyxyPixels'],truths[index]);delta=b['iou']-a['iou']
    return dict(row,before=a,after=b,disposition='unchanged' if abs(delta)<1e-8 else 'improved' if delta>0 else 'regressed',
        crossings={str(t):int(b['iou']>=t)-int(a['iou']>=t) for t in (.5,.7,.9)},truthWidth=truths[index][2]-truths[index][0],truthHeight=truths[index][3]-truths[index][1])


def summarize(rows):
    paired=[v for v in rows if 'before' in v];changed=[v for v in paired if v['changed']]
    return dict(predictions=len(rows),changed=sum(v['changed'] for v in rows),operating=sum(v['operating'] for v in rows),
        dispositions=dict(collections.Counter(v['disposition'] for v in rows)),
        changedMedians={which:{k:statistics.median(v[which][k] for v in changed) if changed else None for k in ('iou','widthRatio','heightRatio','centerX','centerY')} for which in ('before','after')},
        crossings={str(t):dict(collections.Counter(v['crossings'][str(t)] for v in paired)) for t in (.5,.7,.9)})


def family(row,metadata):
    return row.get('family',metadata.get(row['id'],{}).get('family','unknown'))


def choose(rows,existing,evaluation):
    eval_hashes={v['image']['sha256'] for v in evaluation};eval_pixels={v['pixelSHA256'] for v in evaluation}
    eval_groups={v.get('group',Path(v['id']).stem) for v in evaluation};selected=[];counts=collections.Counter();seen=set()
    for row in sorted(rows,key=lambda v:v['id']):
        h.require(row['split']=='train','role_violation')
        group=row.get('group',Path(row['id']).stem)
        h.require(row['image']['sha256'] not in eval_hashes and row['pixelSHA256'] not in eval_pixels and group not in eval_groups,'evaluation_overlap')
        if row['id'] in existing or row['pixelSHA256'] in seen or counts[row['sourceFamily']]>=24:continue
        selected.append(row);seen.add(row['pixelSHA256']);counts[row['sourceFamily']]+=1
    return selected


def run():
    h.require(not OUT.exists(),'output_collision');start=time.monotonic();cp,proposal=x.ready();parent=x.r.c.inputs()
    prior=x.r.c.g.r.f.d.inputs();membership=p.sealed(h.checked(h.ROOT,prior['membership']))['rows']
    by_hash=collections.defaultdict(list)
    for row in membership:by_hash[(row['image']['sha256'],row['label']['sha256'])].append(row)
    metadata=p.sealed(x.r.c.g.CONTROL/'protocol.json')['metadata'];cid=e.load_names().index('pageControl')
    output=[];image_records=[];evaluation_hashes=set();evaluation_labels=set()
    for kind,plan in proposal['evaluation'].items():
        req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
        base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),req,parent['checkpoints']['022']['sha256'],expected_settings=x.r.c.SETTINGS)
        crops=e.validated_artifact(h.read(x.OUT/(kind+'-predictions.json'),256*1024**2),e.load_request(h.checked(h.ROOT,plan['manifest']),41),h.sha(cp),expected_settings=x.r.c.SETTINGS)
        derived=x.merge(base['results'],plan['records'],crops['results'],cid)
        h.require(derived['results']==p.sealed(x.OUT/(kind+'-derived.json'))['results'],'derived_changed')
        originals={v['imageID']:v for v in base['results']};updated={v['imageID']:v for v in derived['results']}
        for im in req.images:
            candidates=by_hash[(im.image_sha256,im.label_sha256)];families={family(v,metadata) for v in candidates}
            h.require(len(families)<=1,'ambiguous_family');fam=next(iter(families),'unknown')
            truths=x.r.c.g.r.f.d.prior.truth(im,cid);a=originals[im.image_id]['detections'];b=updated[im.image_id]['detections']
            h.require(len(a)==len(b),'prediction_count');count=0
            for i,(left,right) in enumerate(zip(a,b)):
                if left['classID']!=cid:h.require(left==right,'non_page_changed');continue
                detail=compare_row(left,right,truths);count+=1
                output.append(dict(kind=kind,imageID=im.image_id,family=fam,predictionIndex=i,**detail))
            image_records.append(dict(kind=kind,imageID=im.image_id,family=fam,truthCount=len(truths),predictions=count))
            if kind!='fit':evaluation_hashes.add(im.image_sha256);evaluation_labels.add(im.label_sha256)
    summaries={}
    for kind in proposal['evaluation']:
        subset=[v for v in output if v['kind']==kind];summaries[kind]=summarize(subset)
        summaries[kind]['families']={fam:summarize([v for v in subset if v['family']==fam]) for fam in sorted({v['family'] for v in subset})}
    coverage=collections.Counter();eligible=[];label_refs=[]
    for row in membership:
        if row['split']!='train':continue
        path=h.checked(h.ROOT,row['label']);labels=path.read_text().splitlines()
        count=sum(int(line.split()[0])==cid for line in labels if line.strip())
        if not count:continue
        fam=family(row,prior['metadata']);coverage[fam]+=1
        eligible.append(dict(row,sourceFamily=fam,pageInstances=count));label_refs.append(row['label'])
    existing={v['parent'] for v in proposal['rows']+proposal['duplicateAliases']}
    selected=choose(eligible,existing,[r for r in membership if r['split']!='train'])
    for row in selected:
        h.require(row['image']['sha256'] not in evaluation_hashes,'current_eval_overlap')
        image=h.checked(h.ROOT,row['image']);h.checked(h.ROOT,row['annotation'])
        with Image.open(image) as im:im.verify()
    OUT.mkdir(parents=True)
    h.write(OUT/'diagnosis.json',dict(summaries=summaries,rows=output,images=image_records,
        sources=[h.ref(__file__),h.ref(x.OUT/'evaluation.json'),h.ref(x.r.OUT/'proposal.json')],
        trainingCoverage=dict(coverage),proposedSourceCount=len(selected),membership=prior['membership'],seconds=time.monotonic()-start,
        inferenceLaunched=False,trainingLaunched=False,productionEligible=False),sealed=True)
    h.write(OUT/'coverage-proposal.json',dict(rows=selected,sourceMembership=prior['membership'],sourceLabels=label_refs,
        excludedExistingParents=sorted(existing),selection='first24source-ID-ordered distinct training pixels per family',
        status='source-qualified proposal only; crop membership not materialized',trainingLaunched=False),sealed=True)
    h.require(sum(v.stat().st_size for v in OUT.iterdir())<64*1024**2,'budget')
    print('coverage',dict(coverage),'selected',collections.Counter(v['sourceFamily'] for v in selected))
    print({k:{f:(v['changed'],v['dispositions'],v['changedMedians']) for f,v in s['families'].items()} for k,s in summaries.items()})


if __name__=='__main__':run()
