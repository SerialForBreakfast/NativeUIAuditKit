"""One frozen, label-free corroborated-alias test using retained predictions."""
import argparse
import collections
import copy
import math
import time
import compose_style210 as c

h,p,e,r=c.h,c.p,c.e,c.r
OUT=h.ROOT/'reports/work/IOS-PRECISION-211/artifacts/comparison01'
RULE='unique-donor-score-ordered-alias-v1'


def resolve(row,donors,cid):
    """Only independently unique donors enter; uncertain boxes remain unchanged."""
    selected=dict(r.proposals(row,cid))
    h.require(set(donors)<=set(selected),'donor_index')
    accepted=[];removed=set()
    for index in sorted(donors,key=lambda i:(-selected[i]['score'],i)):
        box=donors[index]
        h.require(len(box)==4 and all(math.isfinite(x) for x in box) and
                  0<=box[0]<box[2]<=row['width'] and 0<=box[1]<box[3]<=row['height'],'donor_bounds')
        if any(e.iou_xyxy(box,donors[j])>=.5 for j in accepted):removed.add(index)
        else:accepted.append(index)
    result=copy.deepcopy(row);detections=[]
    for i,d in enumerate(result['detections']):
        if i in removed:continue
        if i in donors:d['xyxyPixels']=list(donors[i])
        detections.append(d)
    result['detections']=detections
    result['status']='ok' if detections else 'empty'
    return result,dict(refined=len(accepted),suppressed=len(removed))


def merge(base,records,crops,cid):
    # Reuse all existing identity, geometry, failure and donor validation first.
    c.roi194.merge(base,records,crops,cid)
    lookup={v['imageID']:v for v in crops};plans={v['imageID']:v for v in records}
    results=[];counts=collections.Counter()
    for row in base:
        unique={}
        for item in plans[row['imageID']]['proposals']:
            i=item['proposalIndex'];original=row['detections'][i];donors=[]
            for d in lookup[item['id']]['detections']:
                if d['classID']==cid and d['score']>=.25:
                    box=r.restore(d['xyxyPixels'],item['window'])
                    if e.iou_xyxy(box,original['xyxyPixels'])>=.25:donors.append(box)
            if len(donors)==1:unique[i]=donors[0]
        result,count=resolve(row,unique,cid);results.append(result);counts.update(count)
    return dict(results=results),dict(counts)


def prepare():
    h.require(not OUT.exists(),'output_collision')
    parent,arms,refs=c.collect()
    refs += [h.ref(__file__),h.ref(c.r.c.g.CONTROL/'protocol.json'),h.ref(c.r.c.g.r.f.OUT/'evaluation.json')]
    for arm,doc in arms.items():
        for kind in ('fit','page','combined'):c.load_kind(parent,arm,doc,kind)
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json',dict(rule=RULE,inputs=refs,training=False,inference=False,
        independentEvaluation=False,productionEligible=False),sealed=True)


def report(fit_only=False):
    name='fit-screen.json' if fit_only else 'evaluation.json'
    h.require(not (OUT/name).exists(),'output_collision')
    protocol=p.sealed(OUT/'protocol.json');h.require(protocol['rule']==RULE,'unsupported_rule')
    for ref in protocol['inputs']:h.checked(h.ROOT,ref,256*1024**2)
    parent,arms,refs=c.collect()
    refs += [h.ref(__file__),h.ref(c.r.c.g.CONTROL/'protocol.json'),h.ref(c.r.c.g.r.f.OUT/'evaluation.json')]
    h.require(refs==protocol['inputs'],'inputs_changed')
    if not fit_only:
        screen=p.sealed(OUT/'fit-screen.json')
        h.require(screen['protocol']==h.ref(OUT/'protocol.json') and screen['fitPassed'],'fit_screen_failed')
    start=time.monotonic();names=e.load_names();cid=names.index('pageControl');result={}
    metadata=p.sealed(c.r.c.g.CONTROL/'protocol.json')['metadata']
    for arm,doc in arms.items():
        scores={};accounting={};cases=None
        for kind in (('fit',) if fit_only else ('fit','page','combined')):
            req,base,crops=c.load_kind(parent,arm,doc,kind)
            refined,counts=merge(base['results'],doc['proposal']['evaluation'][kind]['records'],crops[0]['results'],cid)
            expanded,decisions=c.extra.merge(base['results'],doc['extra']['plans'][kind]['records'],crops[1]['results'],cid)
            combined,extra_counts=c.compose(base['results'],refined['results'],expanded['results'],decisions,cid)
            images={im.image_id:im for im in req.images}
            for row in combined['results']:c.roi194.normalize_detections(row['detections'],images[row['imageID']],41)
            scores[kind]=e.score(combined,req,names);accounting[kind]=dict(aliases=counts,extras=extra_counts)
            before=e.score(base,req,names)
            for a,b in zip(before['perClass'],scores[kind]['perClass']):
                if a['class']!='pageControl':h.require(a==b,'non_page_metric_change')
            if kind=='fit':cases=r.c.g.r.f.d.pages(req,combined,cid,metadata)
        strata={k:dict(collections.Counter(v['disposition'] for v in cases if v['metadata']['placement']==k))
                for k in ('leading','center','trailing')}
        result[arm]=dict(scores=scores,accounting=accounting,strata=strata)
        if not fit_only:result[arm]['assessment']=r.c.g.r.assess(scores,strata,p.sealed(r.c.g.r.f.OUT/'evaluation.json'))
    fit_passed=all(next(v for v in x['scores']['fit']['perClass'] if v['class']=='pageControl')['tp']==216 and
                   next(v for v in x['scores']['fit']['perClass'] if v['class']=='pageControl')['fp']<=24 for x in result.values())
    h.write(OUT/name,dict(arms=result,protocol=h.ref(OUT/'protocol.json'),seconds=time.monotonic()-start,
        fitPassed=fit_passed,independentEvaluation=False,productionEligible=False),sealed=True)
    for arm,d in result.items():
        print(arm,d.get('assessment',{'fitPassed':fit_passed}))
        for kind,score in d['scores'].items():print(kind,next(v for v in score['perClass'] if v['class']=='pageControl'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','fit','report'])
    mode=parser.parse_args().mode
    if mode=='prepare':prepare()
    else:report(fit_only=mode=='fit')
