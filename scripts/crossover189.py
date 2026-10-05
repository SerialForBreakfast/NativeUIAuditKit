"""Four-cell resolution accounting through existing prediction contracts."""
import argparse
import collections
import time
import resolution187 as g
h,p,e=g.h,g.p,g.e
OUT=h.ROOT/'reports/work/IOS-CROSSOVER-189/artifacts'
SETTINGS=g.r.f.d.completed.SETTINGS


def prepare():
    h.require(not OUT.exists(),'output_collision');g.admission();g.r.ready()
    source={'022':g.CONTROL,'024':g.BASE};evaluations={k:p.sealed(v/'evaluation.json') for k,v in source.items()}
    manifests=dict(g.manifests());checks={k:h.ref(h.checked(h.ROOT,v['checkpoint'],256*1024**2)) for k,v in evaluations.items()}
    for path in manifests.values():e.load_request(path,41)
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json',dict(checkpoints=checks,manifests={k:h.ref(v) for k,v in manifests.items()},
        evaluations={k:h.ref(v/'evaluation.json') for k,v in source.items()},
        reused={k:{kind:h.ref(v/(kind+'-predictions.json')) for kind in manifests} for k,v in source.items()},
        settings=SETTINGS,sources=[h.ref(__file__),h.ref(g.__file__),h.ref(e.__file__),h.ref(h.ROOT/'scripts/eval_phase6a.py')],budgetBytes=512*1024**2,
        newArms=[['022',1280],['024',640]],productionEligible=False),sealed=True)


def inputs():
    doc=p.sealed(OUT/'protocol.json');h.require(doc['newArms']==[['022',1280],['024',640]] and doc['settings']==SETTINGS,'changed_experiment')
    refs=doc['sources']+list(doc['manifests'].values())+list(doc['evaluations'].values())+list(doc['checkpoints'].values())
    refs += [r for v in doc['reused'].values() for r in v.values()]
    for ref in refs:h.checked(h.ROOT,ref,256*1024**2)
    return doc


def infer():
    doc=inputs();h.require(not any(OUT.glob('*-predictions.json')),'output_collision');started=time.monotonic()
    for arm,size in doc['newArms']:
        for kind,ref in doc['manifests'].items():
            e.export_predictions(h.checked(h.ROOT,ref),h.checked(h.ROOT,doc['checkpoints'][arm],256*1024**2),OUT/f'{arm}-{size}-{kind}-predictions.json','mps',imgsz=size,discard_degenerate=True)
            h.require(sum(x.stat().st_size for x in OUT.iterdir() if x.is_file())<=doc['budgetBytes'],'output_budget')
    h.write(OUT/'inference.json',dict(seconds=time.monotonic()-started,source=h.ref(__file__),protocol=h.ref(OUT/'protocol.json')),sealed=True)


def transitions(old,new):
    indexed={x['id']:x for x in old};h.require(len(indexed)==len(old)==len(new) and set(indexed)=={x['id'] for x in new},'case_membership')
    return [dict(id=x['id'],before=indexed[x['id']]['disposition'],after=x['disposition']) for x in new]


def report():
    doc=inputs();h.require(not (OUT/'evaluation.json').exists(),'output_collision');results={};names=e.load_names()
    metadata=p.sealed(g.CONTROL/'protocol.json')['metadata'];reference=p.sealed(g.r.f.OUT/'evaluation.json')
    old=p.sealed(g.CONTROL/'evaluation.json');allrefs=[]
    for arm,size in [('022',640),('022',1280),('024',640),('024',1280)]:
        scores={};cases=[]
        for kind,ref in doc['manifests'].items():
            req=e.load_request(h.checked(h.ROOT,ref),41)
            path=h.checked(h.ROOT,doc['reused'][arm][kind],256*1024**2) if (arm,size) in [('022',640),('024',1280)] else OUT/f'{arm}-{size}-{kind}-predictions.json'
            data=h.read(path,256*1024**2);e.validated_artifact(data,req,doc['checkpoints'][arm]['sha256'],expected_settings=dict(SETTINGS,imgsz=size));allrefs.append(h.ref(path))
            scores[kind]=e.score(data,req,names)
            if kind=='fit':
                cases=g.r.f.d.pages(req,data,names.index('pageControl'),metadata)
                for row in cases:row['resizedWidth']*=size/640;row['resizedHeight']*=size/640
        strata={s:dict(collections.Counter(x['disposition'] for x in cases if x['metadata']['placement']==s)) for s in ('leading','center','trailing')}
        results[f'{arm}@{size}']=dict(results=scores,strata=strata,fitCases=cases,transitions=transitions(old['fitCases'],cases),assessment=g.r.assess(scores,strata,reference))
    h.write(OUT/'evaluation.json',dict(arms=results,predictions=allrefs,protocol=h.ref(OUT/'protocol.json'),productionEligible=False,
        interpretation='Same data, explicit train/inference resolution factors; development diagnosis, no selection on final holdout.'),sealed=True)
    print('Four-cell matched accounting complete',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','infer','report']);globals()[parser.parse_args().mode]()
