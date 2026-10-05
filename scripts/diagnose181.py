"""Complete fixed-threshold case audit; never trains or changes data roles."""
import collections
import time
import replay179 as r
h,e,p,f=r.h,r.e,r.p,r.f
OUT=h.ROOT/'reports/work/IOS-REPLAY-181/artifacts'
CLASSES=('sheet','cancelAction','scrollIndicator','pageControl')


def detailed(boxes,predictions):
    available=set(range(len(boxes)));hits=[];false=[]
    for d in sorted(predictions,key=lambda x:-x['score']):
        if d['score']<.25:continue
        overlap,j=max(((e.iou_xyxy(d['xyxyPixels'],boxes[i]),i) for i in available),default=(0,-1))
        if overlap>=.5:available.remove(j);hits.append(j)
        else:false.append(d)
    return dict(support=len(boxes),tp=len(hits),fp=len(false),fn=len(available),
        hitIndices=sorted(hits),missIndices=sorted(available),falsePredictions=false)


def associate(old,new):
    available=set(range(len(old)));retained=[];introduced=[]
    for j,d in enumerate(new):
        overlap,i=max(((e.iou_xyxy(d['xyxyPixels'],old[i]['xyxyPixels']),i) for i in available),default=(0,-1))
        if overlap>=.5:available.remove(i);retained.append([i,j])
        else:introduced.append(j)
    return dict(spatiallyRetained=retained,introduced=introduced,resolved=sorted(available))


def reconcile(cases,expected):
    total={k:sum(c[k] for c in cases) for k in ('support','tp','fp','fn')}
    h.require(all(total[k]==expected[k] for k in total),'count_reconciliation')
    return total


def run():
    h.require(not OUT.exists(),'output_collision');start=time.monotonic()
    r.ready();doc=r.inputs();prior=f.d.inputs()
    old=p.sealed(f.OUT/'evaluation.json');new=p.sealed(r.OUT/'evaluation.json')
    names=e.load_names();arms={};refs=[]
    for arm,base,sha in [('019',f.d.completed.OUT,doc['initializer']['sha256']),
                         ('020',f.OUT,old['checkpoint']['sha256']),('021',r.OUT,new['checkpoint']['sha256'])]:
        arms[arm]={}
        for kind,index in [('combined',0),('page',3)]:
            path=base/(kind+'-predictions.json');refs.append(h.ref(path))
            req=e.load_request(h.checked(h.ROOT,prior['evaluationManifests'][index]),41)
            artifact=h.read(path,256*1024**2)
            e.validated_artifact(artifact,req,sha,expected_settings=f.d.completed.SETTINGS)
            predictions={x['imageID']:x['detections'] for x in artifact['results']}
            expected=new['results'][kind] if arm=='021' else old['results'][kind][arm]
            result={}
            for name in (CLASSES if kind=='combined' else ('pageControl',)):
                cid=names.index(name);cases=[]
                for image in req.images:
                    gt=f.d.prior.truth(image,cid)
                    pred=[d for d in predictions[image.image_id] if d['classID']==cid]
                    detail=detailed(gt,pred)
                    cases.append(dict(id=image.image_id,dimensions=[image.width,image.height],truth=gt,
                        dispositions=[f.d.prior.classify(b,pred) for b in gt],**detail))
                metric=next(x for x in expected['perClass'] if x['class']==name)
                result[name]=dict(cases=cases,totals=reconcile(cases,metric),metric=metric)
            arms[arm][kind]=result
    changes={}
    for before,after in [('019','020'),('020','021'),('019','021')]:
        changes[before+'-'+after]={}
        for kind in ('combined','page'):
            for name,a in arms[before][kind].items():
                b=arms[after][kind][name];rows=[];totals=collections.Counter()
                h.require([x['id'] for x in a['cases']]==[x['id'] for x in b['cases']],'case_order')
                for x,y in zip(a['cases'],b['cases']):
                    match=associate(x['falsePredictions'],y['falsePredictions'])
                    item=dict(id=x['id'],**match,lostHits=sorted(set(x['hitIndices'])-set(y['hitIndices'])),
                        gainedHits=sorted(set(y['hitIndices'])-set(x['hitIndices'])))
                    totals.update({k:len(item[k]) for k in ('spatiallyRetained','introduced','resolved','lostHits','gainedHits')})
                    rows.append(item)
                h.require(totals['spatiallyRetained']+totals['resolved']==a['totals']['fp'] and
                    totals['spatiallyRetained']+totals['introduced']==b['totals']['fp'],'fp_conservation')
                changes[before+'-'+after][kind+'/'+name]=dict(totals=dict(totals),cases=rows)
    fit={}
    for arm,cases in [('019',old['fitCases']['019']),('020',old['fitCases']['020']),('021',new['fitCases'])]:
        fit[arm]=dict(collections.Counter('|'.join((x['metadata']['family'],x['metadata']['placement'],x['disposition'])) for x in cases))
    coverage={}
    for kind,rows in [('fit',doc['rows'][:216]),('replay',doc['rows'][216:])]:
        images=collections.Counter();instances=collections.Counter();negative=0
        for row in rows:
            label=h.checked(h.ROOT,row['label']).read_text().splitlines()
            ids=[int(x.split()[0]) for x in label if x.strip()]
            images.update(set(ids));instances.update(ids);negative+=not ids
        coverage[kind]=dict(images={names[k]:v for k,v in images.items()},instances={names[k]:v for k,v in instances.items()},emptyLabelImages=negative)
    OUT.mkdir(parents=True)
    h.write(OUT/'diagnosis.json',dict(arms=arms,changes=changes,fit=fit,coverage=coverage,
        source=h.ref(__file__),predictions=refs,references=[h.ref(f.OUT/'evaluation.json'),h.ref(r.OUT/'evaluation.json')],
        seconds=time.monotonic()-start,independentEvaluation=False,trainingLaunched=False),sealed=True)
    print({pair:{k:v['totals'] for k,v in groups.items()} for pair,groups in changes.items()},flush=True)


if __name__=='__main__':run()
