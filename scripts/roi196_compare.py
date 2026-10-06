"""Summarize terminal026 against022/025, preserving the fixed decision rule."""
import collections
import statistics
import roi196 as r
import roi195 as geometry
h,p,e=r.h,r.p,r.e
PREVIOUS=h.ROOT/'reports/work/IOS-ROI-194/artifacts/attempt02'


def run():
    r.configure();dest=r.OUT/'comparison.json';h.require(not dest.exists(),'output_collision')
    current=p.sealed(r.runner.OUT/'evaluation.json');prior=p.sealed(PREVIOUS/'evaluation.json')
    diagnosis=p.sealed(geometry.OUT/'diagnosis.json');parent=r.r.c.inputs();cid=e.load_names().index('pageControl')
    summary={};transfers={}
    for kind in ('fit','page','combined'):
        def metrics(doc):
            score=doc['results'][kind];page=next(v for v in score['perClass'] if v['class']=='pageControl')
            return dict(aggregate=score['metrics'],imageCount=score['imageCount'],page=page)
        summary[kind]=dict(run025=metrics(prior),run026=metrics(current))
        req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
        images={im.image_id:im for im in req.images}
        old={v['imageID']:v for v in p.sealed(PREVIOUS/(kind+'-derived.json'))['results']}
        new=p.sealed(r.runner.OUT/(kind+'-derived.json'))['results'];rows=[]
        families={v['imageID']:v['family'] for v in diagnosis['images'] if v['kind']==kind}
        for row in new:
            h.require(len(row['detections'])==len(old[row['imageID']]['detections']),'count_changed')
            truth=r.r.c.g.r.f.d.prior.truth(images[row['imageID']],cid)
            for a,b in zip(old[row['imageID']]['detections'],row['detections']):
                if a['classID']!=cid:h.require(a==b,'non_page_changed');continue
                rows.append(dict(family=families[row['imageID']],**geometry.compare_row(a,b,truth)))
        transfers[kind]={f:geometry.summarize([v for v in rows if v['family']==f]) for f in sorted({v['family'] for v in rows})}
    h.write(dest,dict(scores=summary,geometry025to026=transfers,assessment=current['assessment'],strata=current['strata'],
        sources=[h.ref(r.runner.OUT/'evaluation.json'),h.ref(PREVIOUS/'evaluation.json'),h.ref(geometry.OUT/'diagnosis.json'),h.ref(__file__)],
        conclusion='Development comparison only; immutable proposal ceilings and non-page failures prevent standalone promotion.',productionEligible=False),sealed=True)
    print('assessment',current['assessment']);print('strata',current['strata']);print('scores',summary)


if __name__=='__main__':run()
