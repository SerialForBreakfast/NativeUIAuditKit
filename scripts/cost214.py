"""Audit actual composed detector workload; no new inference or metric selection."""
import collections
import time
import compose_style210 as c
import precision211 as precision

h,p,e = c.h,c.p,c.e
OUT=h.ROOT/'reports/work/IOS-COST-214/artifacts/audit01.json'


def workload(base, refinement, extra):
    ids=[r['imageID'] for r in base]
    h.require(len(ids)==len(set(ids)), 'duplicate_base')
    for records in (refinement,extra):
        h.require([r['imageID'] for r in records]==ids, 'record_membership')
    rows=[]
    for image, ref, more in zip(base,refinement,extra):
        windows=[v['window'] for v in ref['proposals']]
        if more['cropID'] is not None: windows.append(more['window'])
        for x in windows:
            h.require(len(x)==4 and all(type(v)==int for v in x) and
                      0<=x[0]<x[2]<=image['width'] and 0<=x[1]<x[3]<=image['height'], 'window_geometry')
        unique=set(tuple(x) for x in windows)
        rows.append(dict(imageID=image['imageID'], refinement=len(ref['proposals']),
            extra=int(more['cropID'] is not None), crops=len(windows), uniqueWindows=len(unique),
            decodedRGBBytes=sum((x[2]-x[0])*(x[3]-x[1])*3 for x in windows)))
    total=sum(r['crops'] for r in rows)
    return dict(frames=len(rows),cropCalls=total,maxCrops=max((r['crops'] for r in rows),default=0),
        meanCrops=total/len(rows) if rows else 0,
        distribution=dict(collections.Counter(r['crops'] for r in rows)),
        sameFrameDuplicateWindows=sum(r['crops']-r['uniqueWindows'] for r in rows),
        decodedRGBBytes=sum(r['decodedRGBBytes'] for r in rows), rows=rows)


def run():
    h.require(not OUT.exists(), 'output_collision')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();parent,arms,refs=c.collect();results={}
    for arm,doc in arms.items():
        records={}
        for kind in ('fit','page','combined'):
            req,base,crops=c.load_kind(parent,arm,doc,kind)
            cid=e.load_names().index('pageControl')
            # Real merges reject inconsistent proposals, bounds and crop membership.
            precision.merge(base['results'],doc['proposal']['evaluation'][kind]['records'],crops[0]['results'],cid)
            c.extra.merge(base['results'],doc['extra']['plans'][kind]['records'],crops[1]['results'],cid)
            records[kind]=workload(base['results'],doc['proposal']['evaluation'][kind]['records'],doc['extra']['plans'][kind]['records'])
        timings={}
        for name,path in [('refinement',c.BASE/arm/'candidate/inference.json'),
                          ('extra',c.BASE/arm/'extra-proposal/execution.json')]:
            doc_time=p.sealed(path);refs.append(h.ref(path));timings[name]=doc_time['seconds']
        results[arm]=dict(partitions=records,recordedBatchSeconds=timings,
                          timingScope='Includes exporter/load/report overhead; not live per-screen latency')
    h.write(OUT,dict(arms=results,inputs=refs+[h.ref(__file__),h.ref(precision.__file__)],
        seconds=time.monotonic()-start,inferenceExecuted=False,modelGatePassed=False),sealed=True)
    for arm,v in results.items():
        print(arm,v['recordedBatchSeconds'])
        for key,value in v['partitions'].items(): print(key,{k:v for k,v in value.items() if k!='rows'})


if __name__=='__main__':run()
