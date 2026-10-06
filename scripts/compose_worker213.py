"""Test returned extra-ROI donors in the unchanged full-frame composition."""
import argparse
from pathlib import Path
import collections
import compose_style210 as c
import precision211 as precision
import evaluate_artwork213 as worker
from artwork200_campaign import sha, write

h,p,e=c.h,c.p,c.e
BASE=h.ROOT/'reports/work/WORKER-213/artifacts/return01'


def composed(base,refined,records,predictions,cid,request):
    expanded,decisions=c.extra.merge(base['results'],records,predictions['results'],cid)
    result,counts=c.compose(base['results'],refined['results'],expanded['results'],decisions,cid)
    images={im.image_id:im for im in request.images}
    for before,after in zip(base['results'],result['results']):
        h.require([d for d in before['detections'] if d['classID']!=cid]==
                  [d for d in after['detections'] if d['classID']!=cid],'non_page_changed')
        c.roi194.normalize_detections(after['detections'],images[after['imageID']],41)
    return result,counts


def run(out,profile='213'):
    h.require(profile in ('213','216'),'profile')
    source=BASE if profile=='213' else h.ROOT/'reports/work/REPLAY-216/artifacts/return01'
    out=worker.fresh(out);parent,arms,refs=c.collect();fixed=arms['treatment']
    requests=worker.checked_requests(h.ROOT/'reports/work/ARTWORK-204/artifacts/evaluation213-input01')
    names=e.load_names();cid=names.index('pageControl');results={};fit_passed=False
    checkpoints={arm:(source/'payload/checkpoints'/(arm+'-last.pt') if profile=='213'
                     else source/'payload'/arm/'last.pt') for arm in ('control','treatment')}
    expected={'control':'9b47181af6c241c60792875d7a61d26a08c4e31cf116970c7c56bb07e48147d3',
              'treatment':'684ed20a2fd0dcd542eb083e0bb318d2b24918e394512536da0de3364546aa83'}
    if profile=='216':expected={'control':'da414f856ad1ef017d41c24a64ac250104cef87cc9180e3745eca4ed956905f6',
                               'treatment':'742184c2b4622f9d29fa918f0d4c9307f49f0e26d2bb169285fe11c491b7ddba'}
    for arm,path in checkpoints.items():h.require(sha(path)==expected[arm],'checkpoint_changed')
    metadata=p.sealed(c.r.c.g.CONTROL/'protocol.json')['metadata']
    for kind in ('fit','page','combined'):
        if kind!='fit' and not fit_passed:break
        req,base,crops=c.load_kind(parent,'treatment',fixed,kind)
        source_req=e.load_request(h.checked(h.ROOT,fixed['extra']['plans'][kind]['manifest']),41)
        h.require(source_req.content_sha256==requests[kind].content_sha256,'window_membership_changed')
        refined,_=precision.merge(base['results'],fixed['proposal']['evaluation'][kind]['records'],crops[0]['results'],cid)
        alternatives={'reference028':crops[1]}
        for arm in ('control','treatment'):
            path=source/'mapped-predictions'/arm/(kind+'.json')
            alternatives[arm]=e.validated_artifact(e.read(path),requests[kind],expected[arm],
                expected_settings=dict(e.PREDICTION_SETTINGS,postprocessing=worker.DEGENERATE_POLICY))
            refs.append(h.ref(path))
        scores={}
        for arm,predictions in alternatives.items():
            merged,counts=composed(base,refined,fixed['extra']['plans'][kind]['records'],predictions,cid,req)
            metric=e.score(merged,req,names)
            for before,after in zip(e.score(base,req,names)['perClass'],metric['perClass']):
                if before['class']!='pageControl':h.require(before==after,'non_page_metric_change')
            entry=dict(score=metric,accounting=counts)
            if kind=='fit':
                cases=c.r.c.g.r.f.d.pages(req,merged,cid,metadata)
                entry['strata']={key:dict(collections.Counter(x['disposition'] for x in cases if x['metadata']['placement']==key)) for key in ('leading','center','trailing')}
            scores[arm]=entry
        results[kind]=scores
        if kind=='fit':
            fit_passed=all(row['score']['perClass'][cid]['tp']==216 and row['score']['perClass'][cid]['fp']<=24 for row in scores.values())
    assessments={}
    if fit_passed:
        reference=p.sealed(c.r.c.g.r.f.OUT/'evaluation.json')
        for arm in ('reference028','control','treatment'):
            assessments[arm]=c.r.c.g.r.assess({k:v[arm]['score'] for k,v in results.items()},results['fit'][arm]['strata'],reference)
    write(out,dict(profile=profile,results=results,assessments=assessments,fitPassed=fit_passed,inputs=refs,
        sourceSHA256=sha(Path(__file__)),checkpointSHA256=expected,
        scope='Fixed022fullframe plus028refinement plus211aliases; vary extra donor only',
        inferenceExecuted=False,modelGatePassed=False,productionEligible=False))
    return {key:{arm:row['score']['perClass'][cid] for arm,row in value.items()} for key,value in results.items()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    parser.add_argument('--profile',choices=['213','216'],default='213')
    print(run(**vars(parser.parse_args())))
