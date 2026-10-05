"""Pinned prediction reuse and source-defined input exposure audit; no inference."""
import collections
import time
from pathlib import Path
import diagnose181 as d
h,e,p,f=d.h,d.e,d.p,d.f
OUT=h.ROOT/'reports/work/IOS-DIAG-185/artifacts'
LATEST=h.ROOT/'reports/work/IOS-REPLAY-184/artifacts/experiment'
TARGETS=('sheet','cancelAction','mapView','scrollIndicator','pageControl')


def changes(before,after):
    h.require([x['id'] for x in before]==[x['id'] for x in after],'case_order')
    rows=[];totals=collections.Counter()
    for x,y in zip(before,after):
        item=dict(id=x['id'],**d.associate(x['falsePredictions'],y['falsePredictions']),
            lostHits=sorted(set(x['hitIndices'])-set(y['hitIndices'])),
            gainedHits=sorted(set(y['hitIndices'])-set(x['hitIndices'])))
        totals.update({k:len(item[k]) for k in ('spatiallyRetained','introduced','resolved','lostHits','gainedHits')})
        rows.append(item)
    h.require(totals['spatiallyRetained']+totals['resolved']==sum(x['fp'] for x in before)
        and totals['spatiallyRetained']+totals['introduced']==sum(x['fp'] for x in after),'fp_conservation')
    return dict(totals=dict(totals),cases=rows)


def geometry(case):
    box=case['sourceBox'];candidate=case.get('bestIoUCandidate')
    if candidate is None:return None
    b=candidate['xyxyPixels'];w=box[2]-box[0];ht=box[3]-box[1]
    h.require(w>0 and ht>0,'truth_geometry')
    return dict(centerXErrorInWidths=((b[0]+b[2])-(box[0]+box[2]))/(2*w),
        centerYErrorInHeights=((b[1]+b[3])-(box[1]+box[3]))/(2*ht),
        widthRatio=(b[2]-b[0])/w,heightRatio=(b[3]-b[1])/ht,
        iou=case['bestIoU'],confidence=candidate['score'])


def exposure(doc):
    from PIL import Image
    from ultralytics.data.base import BaseDataset
    import inspect
    rows=sorted(doc['rows'],key=lambda x:x['id'].replace('/','__')+'.png')
    dataset=BaseDataset.__new__(BaseDataset)
    dataset.ni=len(rows);dataset.batch_size=doc['args']['batch'];dataset.imgsz=doc['args']['imgsz']
    dataset.stride=32;dataset.pad=0.;dataset.labels=[];dataset.im_files=[]
    counts=collections.Counter();frames=collections.Counter();page_sizes=[]
    for row in rows:
        path=h.checked(h.ROOT,row['image']);h.checked(h.ROOT,row['annotation'])
        with Image.open(path) as im:width,height=im.size
        labels=[[float(v) for v in line.split()] for line in h.checked(h.ROOT,row['label']).read_text().splitlines() if line.strip()]
        ids=[int(v[0]) for v in labels];counts.update(ids);frames.update(set(ids))
        dataset.labels.append(dict(shape=(height,width),id=row['id'],labels=labels))
        dataset.im_files.append(str(path))
        for v in labels:
            if int(v[0])==e.load_names().index('pageControl'):
                scale=doc['args']['imgsz']/max(width,height)
                page_sizes.append(dict(id=row['id'],width=v[3]*width*scale,height=v[4]*height*scale))
    BaseDataset.set_rectangle(dataset)
    names=e.load_names();epochs=doc['args']['epochs']
    return dict(source=h.ref(Path(inspect.getfile(BaseDataset))),stride=32,pad=0,
        batchShapes=dataset.batch_shapes.tolist(),batchIDs=[[x['id'] for x in dataset.labels[i:i+dataset.batch_size]] for i in range(0,len(rows),dataset.batch_size)],
        totalInputPixelsPerEpoch=int(sum(dataset.batch_shapes[dataset.batch[i]].prod() for i in range(len(rows)))),
        classPresentations={names[c]:dict(imagesPerEpoch=frames[c],instancesPerEpoch=n,instancesAcrossRun=n*epochs) for c,n in counts.items()},
        pageResizedBoxes=page_sizes)


def fit_protocol(doc,reference,args):
    """Resolve legacy175 membership from the pinned successor's unchanged fit set."""
    selected=[row for row in reference['rows'] if row['id'] in doc['metadata']]
    h.require(len(selected)==216 and {r['id'] for r in selected}==set(doc['metadata']),'fit_membership')
    h.require(all(reference['metadata'][k]==v for k,v in doc['metadata'].items()),'changed_fit_metadata')
    h.require(args['epochs']==20 and args['batch']==8 and args['imgsz']==640 and args['rect'] is True,'fit_settings')
    return dict(doc,rows=selected,args=args)


def run():
    h.require(not OUT.exists(),'output_collision');started=time.monotonic()
    prior=f.d.inputs();old=p.sealed(f.OUT/'evaluation.json');r21=p.sealed(d.r.OUT/'evaluation.json');r22=p.sealed(LATEST/'evaluation.json')
    protocols={arm:p.sealed(base/'protocol.json') for arm,base in [('020',f.OUT),('021',d.r.OUT),('022',LATEST)]}
    for evaluation in (r21,r22):h.checked(h.ROOT,evaluation['protocol'])
    import yaml
    saved=f.RUN/'args.yaml'
    protocols['020']=fit_protocol(protocols['020'],protocols['022'],yaml.safe_load(saved.read_text()))
    exposures={k:exposure(v) for k,v in protocols.items()}
    names=e.load_names();arms={};refs=[]
    configs=[('019',f.d.completed.OUT,protocols['022']['initializer']['sha256']),('020',f.OUT,old['checkpoint']['sha256']),
             ('021',d.r.OUT,r21['checkpoint']['sha256']),('022',LATEST,r22['checkpoint']['sha256'])]
    for arm,base,sha in configs:
        arms[arm]={}
        for kind,index in [('combined',0),('page',3)]:
            path=base/(kind+'-predictions.json');refs.append(h.ref(path))
            req=e.load_request(h.checked(h.ROOT,prior['evaluationManifests'][index]),41)
            artifact=h.read(path,256*1024**2);e.validated_artifact(artifact,req,sha,expected_settings=f.d.completed.SETTINGS)
            predictions={x['imageID']:x['detections'] for x in artifact['results']}
            expected=(r22 if arm=='022' else r21)['results'][kind] if arm in ('021','022') else old['results'][kind][arm]
            classes={};totals={}
            for metric in expected['perClass']:
                name=metric['class'];cid=names.index(name);cases=[]
                for image in req.images:
                    gt=f.d.prior.truth(image,cid);pred=[x for x in predictions[image.image_id] if x['classID']==cid]
                    cases.append(dict(id=image.image_id,truth=gt,**d.detailed(gt,pred)))
                totals[name]=d.reconcile(cases,metric)
                if name in TARGETS:classes[name]=cases
            arms[arm][kind]=dict(totals=totals,cases=classes)
    comparisons={}
    for a,b in [('019','022'),('020','022'),('021','022')]:
        comparisons[a+'-'+b]={kind+'/'+name:changes(arms[a][kind]['cases'][name],arms[b][kind]['cases'][name]) for kind in ('combined','page') for name in arms[a][kind]['cases']}
    fits={'019':old['fitCases']['019'],'020':old['fitCases']['020'],'021':r21['fitCases'],'022':r22['fitCases']};fit={}
    for arm,cases in fits.items():
        fit[arm]=[dict(**c,geometry=geometry(c)) for c in cases]
    report=dict(arms=arms,changes=comparisons,fit=fit,exposure=exposures,
        references=refs+[h.ref(x/'evaluation.json') for x in (f.OUT,d.r.OUT,LATEST)],
        sources=[h.ref(__file__),h.ref(d.__file__),h.ref(saved)],seconds=time.monotonic()-started,
        inferenceLaunched=False,trainingLaunched=False,independentEvaluation=False)
    OUT.mkdir(parents=True);h.write(OUT/'diagnosis.json',report,sealed=True)
    print({k:{n:v['totals'] for n,v in values.items()} for k,values in comparisons.items()},flush=True)


if __name__=='__main__':run()
