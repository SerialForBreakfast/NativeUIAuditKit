"""Training-fit versus development generalization; no training or new data roles."""
import argparse
import collections
import dataclasses
import time
import diagnostic171 as prior
import eval_placement173 as completed
p=completed.p;h=p.h;e=completed.e
OUT=h.ROOT/'reports/work/IOS-DIAG-174/attempt02/artifacts'


def select_rows(membership,admission):
    ids=[r['id'] for r in admission['newTrainingRows']]
    h.require(len(ids)==264 and len(set(ids))==264,'admission_membership')
    rows=[r for r in membership['rows'] if r['id'] in set(ids)]
    h.require(len(rows)==264 and {r['id'] for r in rows}==set(ids),'training_membership')
    originals={r['id']:r for r in admission['newTrainingRows']}
    h.require(all(r['split']=='train' and all(r[k]==v for k,v in originals[r['id']].items()) for r in rows),'admission_changed')
    return sorted(rows,key=lambda r:r['id'])


def prepare():
    h.require(not OUT.exists(),'output_collision')
    candidate,refs=p.ready();launch=p.sealed(p.OUT/'protocol.json')
    membership=p.sealed(h.checked(h.ROOT,launch['membership']))
    admission=p.sealed(h.checked(h.ROOT,membership['admission']))
    rows=select_rows(membership,admission)
    plan=prior.OUT/'native-batch-plan.json';catalog=p.sealed(plan)
    indexed={r['id']:r for r in catalog['rows']}
    h.require(all(r['id'] in indexed for r in rows),'catalog_membership')
    evaluation=p.sealed(completed.OUT/'evaluation.json')
    for ref in evaluation['predictions']:h.checked(h.ROOT,ref,256*1024**2)
    entries=[];metadata={};sources=[]
    for row in rows:
        paths={k:h.checked(h.ROOT,row[k]) for k in ('image','label','annotation')}
        ann=h.read(paths['annotation']);info=indexed[row['id']]
        h.require(ann['image']['scale']==info['scale'] and ann['image']['colorScheme']==info['theme'],'source_context')
        metadata[row['id']]={k:info[k] for k in ('family','scale','theme','placement','tint','group')}
        sources.append((row,paths))
        entries.append(dict(imageID=row['id'],imagePath='inputs/'+row['id']+'.png',
            labelPath='inputs/'+row['id']+'.txt',imageSHA256=row['image']['sha256'],labelSHA256=row['label']['sha256']))
    OUT.mkdir(parents=True);(OUT/'inputs').mkdir()
    for row,paths in sources:
        (OUT/'inputs'/(row['id']+'.png')).symlink_to(paths['image'])
        (OUT/'inputs'/(row['id']+'.txt')).symlink_to(paths['label'])
    h.write(OUT/'input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='placement174-training-fit-only',images=entries))
    e.load_request(OUT/'input.json',41)
    h.write(OUT/'protocol.json',dict(manifest=h.ref(OUT/'input.json'),metadata=metadata,
        checkpoints={'017':launch['control'],'019':h.ref(candidate)},evaluation=h.ref(completed.OUT/'evaluation.json'),
        evaluationManifests=[h.ref(r) for r in refs],membership=launch['membership'],admission=membership['admission'],
        catalog=h.ref(plan),settings=completed.SETTINGS,
        sources=[h.ref(__file__),h.ref(prior.__file__),h.ref(e.__file__),h.ref(h.ROOT/'scripts/eval_phase6a.py')],
        dataRole='training-fit diagnostic, not evaluation admission',budgetBytes=1024**3,
        independentEvaluation=False,productionEligible=False),sealed=True)
    print('Prepared264training-only diagnostic members',flush=True)


def inputs():
    doc=p.sealed(OUT/'protocol.json')
    h.require(doc['settings']==completed.SETTINGS,'settings_changed')
    for ref in doc['sources']+[doc[k] for k in ('manifest','evaluation','membership','admission','catalog')]+list(doc['checkpoints'].values())+doc['evaluationManifests']:
        h.checked(h.ROOT,ref,256*1024**2)
    return doc


def infer():
    doc=inputs()
    h.require(not any((OUT/(arm+'-predictions.json')).exists() for arm in doc['checkpoints']),'prediction_collision')
    for arm,ref in doc['checkpoints'].items():
        start=time.perf_counter();dest=OUT/(arm+'-predictions.json')
        e.export_predictions(OUT/'input.json',h.checked(h.ROOT,ref,256*1024**2),dest,'mps',discard_degenerate=True)
        h.write(OUT/(arm+'-timing.json'),dict(seconds=time.perf_counter()-start,output=h.ref(dest),
            method='wall export including validation and model load, not model-only latency'),sealed=True)


def pages(request,document,cid,metadata):
    indexed={r['imageID']:r['detections'] for r in document['results']};cases=[]
    h.require(set(indexed)=={im.image_id for im in request.images},'case_membership')
    for image in request.images:
        gt=prior.truth(image,cid);h.require(len(gt)==1,'single_page_truth')
        box=gt[0];ratio=640/max(image.width,image.height)
        candidates=[r for r in indexed[image.image_id] if r['classID']==cid]
        best=max(candidates,key=lambda r:e.iou_xyxy(box,r['xyxyPixels']),default=None)
        cases.append(dict(id=image.image_id,metadata=metadata[image.image_id],
            **prior.classify(box,candidates),sourceBox=box,
            resizedWidth=(box[2]-box[0])*ratio,resizedHeight=(box[3]-box[1])*ratio,
            bestIoUCandidate=best,selection='oracle diagnostic, not model-selected output'))
    return cases


def report():
    doc=inputs();h.require(not (OUT/'diagnosis.json').exists(),'report_collision')
    base=p.sealed(h.checked(h.ROOT,doc['evaluation']));names=e.load_names();cid=names.index('pageControl')
    train=e.load_request(OUT/'input.json',41);probe=e.load_request(h.checked(h.ROOT,doc['evaluationManifests'][3]),41)
    retained=e.load_request(h.checked(h.ROOT,doc['evaluationManifests'][0]),41)
    catalog=h.read(p.control.r.repair.PROBES/'compose155-catalog.json')['rows'];probe_meta={r['id']:r for r in catalog}
    arms={};predrefs=[]
    for arm in ('017','019'):
        checkpoint=doc['checkpoints'][arm]['sha256'];prediction=OUT/(arm+'-predictions.json')
        new=h.read(prediction,256*1024**2);e.validated_artifact(new,train,checkpoint,expected_settings=doc['settings'])
        timing=p.sealed(OUT/(arm+'-timing.json'));h.require(timing['output']==h.ref(prediction) and timing['seconds']>0,'timing_identity')
        predrefs.append(h.ref(prediction));offset=0 if arm=='017' else 2
        old=h.read(h.checked(h.ROOT,base['predictions'][offset],256*1024**2),256*1024**2)
        pd=h.read(h.checked(h.ROOT,base['predictions'][offset+1],256*1024**2),256*1024**2)
        e.validated_artifact(old,retained,checkpoint,expected_settings=doc['settings'])
        e.validated_artifact(pd,probe,checkpoint,expected_settings=doc['settings'])
        cases=pages(train,new,cid,doc['metadata']);pcases=pages(probe,pd,cid,probe_meta)
        strata={}
        for axis in ('placement','tint','family','scale','theme'):
            for value in sorted({r['metadata'][axis] for r in cases}):
                selected=[r for r in cases if r['metadata'][axis]==value];ids={r['id'] for r in selected}
                req=dataclasses.replace(train,images=tuple(im for im in train.images if im.image_id in ids))
                strata[f'{axis}={value}']=dict(dispositions=dict(collections.Counter(r['disposition'] for r in selected)),
                    score=next(r for r in e.score(e.subset(new,req),req,names)['perClass'] if r['class']=='pageControl'))
        indexed={r['imageID']:r['detections'] for r in old['results']};regressions={}
        for name in ('cancelAction','mapView'):
            c=names.index(name);rcases=[]
            for im in retained.images:
                gt=prior.truth(im,c);ds=indexed[im.image_id];pred=[v for v in ds if v['classID']==c]
                if gt or pred:rcases.append(dict(id=im.image_id,**prior.matches(gt,pred),truth=gt,predictions=pred,
                    competing=[v for v in ds if v['classID']!=c and any(e.iou_xyxy(b,v['xyxyPixels'])>=.5 for b in gt)]))
            totals={k:sum(r[k] for r in rcases) for k in ('support','tp','fp','fn')}
            expected=next(r for r in base['results']['combined'][arm]['perClass'] if r['class']==name)
            h.require(all(totals[k]==expected[k] for k in totals),'retention_reconciliation')
            regressions[name]=dict(totals=totals,cases=rcases)
        arms[arm]=dict(trainingScore=e.score(new,train,names),trainingCases=cases,trainingStrata=strata,
            probeCases=pcases,regressions=regressions,timing=timing)
    changes={}
    for name in ('cancelAction','mapView'):
        indexed={a:{r['id']:r for r in arms[a]['regressions'][name]['cases']} for a in arms};rows=[]
        for key in sorted(set(indexed['017'])|set(indexed['019'])):
            a=indexed['017'].get(key,{});b=indexed['019'].get(key,{})
            delta={k:b.get(k,0)-a.get(k,0) for k in ('tp','fp','fn')}
            if any(delta.values()):rows.append(dict(id=key,delta=delta,control=a,candidate=b))
        changes[name]=rows
    h.write(OUT/'diagnosis.json',dict(arms=arms,changes=changes,protocol=h.ref(OUT/'protocol.json'),predictions=predrefs,
        independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file() and not f.is_symlink())<doc['budgetBytes'],'output_budget')
    print('Complete264training/96probe cases per arm and2400-image retention reconciliation')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','infer','report']);args=parser.parse_args();globals()[args.mode]()
