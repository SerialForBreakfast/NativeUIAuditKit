"""Frozen CPU-only composition of existing refinement and extra-ROI evidence."""
import argparse
import collections
import copy
import time
import roi194
import roi197_compare as extra

h,p,e,r=extra.h,extra.p,extra.e,extra.r
BASE=h.ROOT/'reports/work/IOS-STYLE-210/artifacts/training01'
OUT=h.ROOT/'reports/work/IOS-STYLE-210/artifacts/composition01'
RULE='refine-then-original-extra-dedup-v1'


def compose(base,refined,expanded,decisions,cid):
    """Inputs come from validated artifacts and existing merges, never labels."""
    ids=[v['imageID'] for v in base]
    h.require(len(ids)==len(set(ids)),'duplicate_base')
    for rows in (refined,expanded,decisions):
        h.require([v['imageID'] for v in rows]==ids,'composition_membership')
    result=[];counts=collections.Counter()
    for original,corrected,more,decision in zip(base,refined,expanded,decisions):
        for row in (original,corrected,more):
            h.require(row['status'] in ('ok','empty'),'failed_input')
            h.require(bool(row['detections'])==(row['status']=='ok'),'status_detections')
            h.require((row['width'],row['height'])==(original['width'],original['height']),'dimensions')
        h.require(type(decision['added']) is bool,'added_type')
        h.require([v for v in corrected['detections'] if v['classID']!=cid]==
                  [v for v in original['detections'] if v['classID']!=cid],'non_page_change')
        n=len(original['detections']);ds=more['detections']
        h.require(ds[:n]==original['detections'] and len(ds)==n+int(decision['added']),'extra_mutation')
        updated=copy.deepcopy(corrected)
        if decision['added']:
            donor=ds[-1]
            h.require(donor['classID']==cid and donor['score']>=.25,'invalid_donor')
            duplicate=any(v['classID']==cid and v['score']>=.25 and
                          e.iou_xyxy(v['xyxyPixels'],donor['xyxyPixels'])>=.5
                          for v in corrected['detections'])
            if duplicate:counts['suppressed']+=1
            else:
                updated['detections'].append(copy.deepcopy(donor));updated['status']='ok'
                counts['added']+=1
        else:counts['no_extra']+=1
        result.append(updated)
    return dict(results=result),dict(counts)


def collect():
    parent=r.c.inputs();arms={};refs=[]
    for arm in ('control','treatment'):
        path=BASE/arm
        proposal=p.sealed(path/'proposal.json')
        ep=p.sealed(path/'extra-proposal/protocol.json')
        end=p.sealed(path/'candidate/completion.json')
        h.require(end['exitCode']==0 and end['checkpoint']==ep['checkpoint'],'candidate_identity')
        h.checked(h.ROOT,end['checkpoint'],256*1024**2)
        h.require(ep['settings']==r.c.SETTINGS,'settings_changed')
        for ref in proposal['sources']+ep['sources']:h.checked(h.ROOT,ref,256*1024**2)
        refs += [h.ref(path/x) for x in ('proposal.json','extra-proposal/protocol.json','candidate/completion.json')]
        refs.append(end['checkpoint'])
        arms[arm]=dict(proposal=proposal,extra=ep)
        for kind in ('fit','page','combined'):
            refs += [h.ref(path/'candidate'/(kind+'-predictions.json')),
                     h.ref(path/'extra-proposal'/(kind+'-predictions.json')),
                     proposal['evaluation'][kind]['manifest'],ep['plans'][kind]['manifest']]
    refs += list(parent['manifests'].values())+list(parent['reused']['022'].values())
    refs += [h.ref(__file__),h.ref(roi194.__file__),h.ref(extra.__file__),h.ref(extra.s.__file__),
             h.ref(extra.s.a.__file__),h.ref(r.__file__),h.ref(e.__file__)]
    return parent,arms,refs


def load_kind(parent,arm,doc,kind):
    req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
    base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),
        req,parent['checkpoints']['022']['sha256'],expected_settings=r.c.SETTINGS)
    crops=[]
    for directory,plan in (('candidate',doc['proposal']['evaluation'][kind]),
                           ('extra-proposal',doc['extra']['plans'][kind])):
        crop_req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        crops.append(e.validated_artifact(h.read(BASE/arm/directory/(kind+'-predictions.json'),256*1024**2),
            crop_req,doc['extra']['checkpoint']['sha256'],expected_settings=r.c.SETTINGS))
    return req,base,crops


def prepare():
    h.require(not OUT.exists(),'output_collision')
    parent,arms,refs=collect()
    for arm,doc in arms.items():
        for kind in ('fit','page','combined'):load_kind(parent,arm,doc,kind)
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json',dict(rule=RULE,inputs=refs,roles=dict(fit='training_fit',
        page='development',combined='retained_evaluation_not_new_independent_final'),
        training=False,inference=False,productionEligible=False),sealed=True)


def report():
    h.require(not (OUT/'evaluation.json').exists(),'output_collision')
    protocol=p.sealed(OUT/'protocol.json');h.require(protocol['rule']==RULE,'unsupported_rule')
    for ref in protocol['inputs']:h.checked(h.ROOT,ref,256*1024**2)
    start=time.monotonic();parent,arms,refs=collect();h.require(refs==protocol['inputs'],'inputs_changed')
    names=e.load_names();cid=names.index('pageControl');results={}
    metadata=p.sealed(r.c.g.CONTROL/'protocol.json')['metadata']
    for arm,doc in arms.items():
        scores={};accounting={};cases=None
        for kind in ('fit','page','combined'):
            req,base,crops=load_kind(parent,arm,doc,kind)
            refined=roi194.merge(base['results'],doc['proposal']['evaluation'][kind]['records'],crops[0]['results'],cid)
            expanded,decisions=extra.merge(base['results'],doc['extra']['plans'][kind]['records'],crops[1]['results'],cid)
            derived,accounting[kind]=compose(base['results'],refined['results'],expanded['results'],decisions,cid)
            images={im.image_id:im for im in req.images}
            for row in derived['results']:roi194.normalize_detections(row['detections'],images[row['imageID']],41)
            scores[kind]=e.score(derived,req,names)
            baseline=e.score(base,req,names)
            for before,after in zip(baseline['perClass'],scores[kind]['perClass']):
                if before['class']!='pageControl':h.require(before==after,'non_page_metric_change')
            if kind=='fit':cases=r.c.g.r.f.d.pages(req,derived,cid,metadata)
        strata={k:dict(collections.Counter(v['disposition'] for v in cases if v['metadata']['placement']==k))
                for k in ('leading','center','trailing')}
        assessment=r.c.g.r.assess(scores,strata,p.sealed(r.c.g.r.f.OUT/'evaluation.json'))
        results[arm]=dict(scores=scores,accounting=accounting,strata=strata,assessment=assessment)
    # No partial result is published when either arm or any partition fails.
    h.write(OUT/'evaluation.json',dict(arms=results,protocol=h.ref(OUT/'protocol.json'),
        seconds=time.monotonic()-start,productionEligible=False,independentEvaluation=False),sealed=True)
    for arm,v in results.items():
        print(arm,v['assessment'])
        for kind,score in v['scores'].items():print(kind,next(x for x in score['perClass'] if x['class']=='pageControl'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','report'])
    globals()[parser.parse_args().mode]()
