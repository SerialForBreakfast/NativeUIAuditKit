"""Matched terminal evaluation; existing metric and prediction contracts only."""
import argparse
import dataclasses
import time
import placement173 as p
h=p.h;e=p.control.e
OUT=p.OUT/'evaluation'
SETTINGS=p.comparison.SETTINGS


def infer():
    checkpoint,refs=p.ready();protocol=p.sealed(p.OUT/'protocol.json')
    h.require(not OUT.exists(),'evaluation_collision');OUT.mkdir()
    h.write(OUT/'protocol.json',dict(checkpoint=h.ref(checkpoint),settings=SETTINGS,
        controlPredictions=protocol['controlPredictions'],manifests=[h.ref(r) for r in refs],
        sources=[h.ref(__file__)]+[h.ref(h.ROOT/name) for name in ('scripts/eval_run013.py','scripts/eval_phase6a.py')]),sealed=True)
    for name,index in [('combined',0),('page',3)]:
        started=time.perf_counter()
        e.export_predictions(refs[index],checkpoint,OUT/(name+'-predictions.json'),'mps',discard_degenerate=True)
        h.write(OUT/(name+'-export-timing.json'),dict(seconds=time.perf_counter()-started,
            method='wall export including input validation, model load and inference; not model-only latency',
            output=h.ref(OUT/(name+'-predictions.json')),controlTimingComparable=False),sealed=True)


def assess(results,page):
    old=results['combined']['017'];new=results['combined']['019']
    regressions={}
    for name in ('cancelAction','mapView'):
        a=next(r for r in old['perClass'] if r['class']==name)
        b=next(r for r in new['perClass'] if r['class']==name)
        regressions[name]=dict(controlFP=a['fp'],candidateFP=b['fp'],nonRegression=b['fp']<=a['fp'])
    strata={key:dict(controlTP=page['017']['strata'][key]['tp'],candidateTP=page['019']['strata'][key]['tp'])
        for key in ('left=True','native=True')}
    aggregate=dict(controlAP50=old['metrics']['map50'],candidateAP50=new['metrics']['map50'],
        nonRegression=new['metrics']['map50']>=old['metrics']['map50'])
    improved=all(v['candidateTP']>v['controlTP'] for v in strata.values())
    return dict(falsePositives=regressions,pageSupport=strata,
        aggregate=aggregate,localizationImproved=improved,
        developmentSuccess=improved and aggregate['nonRegression'] and all(v['nonRegression'] for v in regressions.values()),
        productionEligible=False,independentEvaluation=False)


def report():
    checkpoint,refs=p.ready();protocol=p.sealed(OUT/'protocol.json');launch=p.sealed(p.OUT/'protocol.json')
    h.require(protocol['settings']==SETTINGS,'settings_changed')
    for ref in protocol['sources']+protocol['manifests']+[protocol['checkpoint']]+protocol['controlPredictions']:
        h.checked(h.ROOT,ref,256*1024**2)
    names=e.load_names();sha=h.sha(checkpoint)
    controls=[h.read(h.checked(h.ROOT,r,256*1024**2),256*1024**2) for r in protocol['controlPredictions']]
    candidates=[h.read(OUT/(name+'-predictions.json'),256*1024**2) for name in ('combined','page')]
    hashes={'017':launch['control']['sha256'],'019':sha};results={}
    for index,name in enumerate(('combined','withheld','addon')):
        request=e.load_request(refs[index],41);results[name]={}
        for arm,doc in [('017',controls[0]),('019',candidates[0])]:
            sub=e.subset(doc,request) if index else doc
            e.validated_artifact(sub,request,hashes[arm],expected_settings=SETTINGS)
            results[name][arm]=e.score(sub,request,names)
    request=e.load_request(refs[3],41);catalog=h.read(p.control.r.repair.PROBES/'compose155-catalog.json')['rows']
    h.require({r['id'] for r in catalog}=={im.image_id for im in request.images},'page_membership')
    page={}
    for arm,doc in [('017',controls[1]),('019',candidates[1])]:
        e.validated_artifact(doc,request,hashes[arm],expected_settings=SETTINGS);strata={}
        for axis in ('family','native','dark','pages','left','seed'):
            for value in sorted({r[axis] for r in catalog}):
                ids={r['id'] for r in catalog if r[axis]==value}
                sub=dataclasses.replace(request,images=tuple(im for im in request.images if im.image_id in ids))
                strata[f'{axis}={value}']=next(r for r in e.score(e.subset(doc,sub),sub,names)['perClass'] if r['class']=='pageControl')
        page[arm]=dict(score=e.score(doc,request,names),strata=strata,geometry=p.control.page_geometry(doc,request,names.index('pageControl')))
    verdict=assess(results,page)
    timings={}
    for name in ('combined','page'):
        path=OUT/(name+'-export-timing.json');record=p.sealed(path)
        h.checked(h.ROOT,record['output'],256*1024**2)
        h.require(record['output']==h.ref(OUT/(name+'-predictions.json')) and record['seconds']>0,'timing_identity')
        timings[name]=dict(record,record=h.ref(path))
    h.write(OUT/'evaluation.json',dict(results=results,page=page,assessment=verdict,settings=SETTINGS,
        exportTiming=timings,
        checkpoint=h.ref(checkpoint),predictions=protocol['controlPredictions']+[h.ref(OUT/(name+'-predictions.json')) for name in ('combined','page')],
        protocol=h.ref(OUT/'protocol.json'),independentEvaluation=False,productionEligible=False),sealed=True)
    print('Evaluated all2496records; no production qualification')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['infer','report']);args=parser.parse_args();globals()[args.mode]()
