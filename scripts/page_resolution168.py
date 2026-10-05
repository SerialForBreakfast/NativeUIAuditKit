"""One preregistered resolution intervention; no training or corpus mutations."""
import argparse
import time
import eval_repair165 as r

h=r.h
OUT=h.ROOT/'reports/work/IOS-PAGE-168/host-attempt/artifacts'
SETTINGS=dict(r.e.PREDICTION_SETTINGS,imgsz=1280)

def run():
    checkpoint,refs=r.ready('r017-repaired')
    request=r.e.load_request(refs[3],41)
    baseline_path=r.r.ART/'r017-repaired-page-predictions.json'
    baseline=h.read(baseline_path,256*1024**2)
    r.e.validated_artifact(baseline,request,h.sha(checkpoint))
    h.require(len(request.images)==96,'membership')
    h.require(not OUT.exists(),'output_collision')
    import torch
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json',dict(checkpoint=h.ref(checkpoint),manifest=h.ref(refs[3]),
        baseline=h.ref(baseline_path),settings=SETTINGS,role='development',
        intervention='640 versus 1280 long edge; all other settings unchanged',
        sources=[h.ref(__file__)]+[h.ref(h.ROOT/p) for p in r.e.CODE]),sealed=True)
    torch.mps.reset_peak_memory_stats() if hasattr(torch.mps,'reset_peak_memory_stats') else None
    start=time.perf_counter()
    prediction=OUT/'predictions1280.json'
    r.e.export_predictions(refs[3],checkpoint,prediction,'mps',imgsz=1280)
    elapsed=time.perf_counter()-start
    candidate=h.read(prediction,256*1024**2)
    r.e.validated_artifact(candidate,request,h.sha(checkpoint),expected_settings=SETTINGS)
    names=r.e.load_names();cid=names.index('pageControl')
    catalog=h.read(h.ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts/compose155-catalog.json')
    h.require({x['id'] for x in catalog['rows']}=={x.image_id for x in request.images},'catalog_membership')
    output={}
    for name,doc in [('640',baseline),('1280',candidate)]:
        result=r.e.score(doc,request,names)
        geometry=r.page_geometry(doc,request,cid)
        strata={}
        # Full confidence-ordered matching per stratum, not oracle hit counts.
        import dataclasses
        for axis in ('family','native','dark','pages','left','seed'):
            for value in sorted({x[axis] for x in catalog['rows']}):
                ids={x['id'] for x in catalog['rows'] if x[axis]==value}
                subset_request=dataclasses.replace(request,images=tuple(x for x in request.images if x.image_id in ids))
                score=r.e.score(r.e.subset(doc,subset_request),subset_request,names)
                strata[f'{axis}={value}']=next(x for x in score['perClass'] if x['class']=='pageControl')
        output[name]=dict(page=next(x for x in result['perClass'] if x['class']=='pageControl'),geometry=geometry,strata=strata)
    h.write(OUT/'result.json',dict(results=output,prediction=h.ref(prediction),
        elapsedSeconds=elapsed,mpsAllocatedBytes=torch.mps.current_allocated_memory(),
        latencyScope='1280 export including model setup; no matched 640 timing or peak-memory claim',
        independentEvaluation=False,productionEligible=False),sealed=True)
    print({key:value['page'] for key,value in output.items()})

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args();run()
