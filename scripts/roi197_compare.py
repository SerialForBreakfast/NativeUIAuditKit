"""Frozen one-extra-proposal comparison after the fit-only falsification screen."""
import argparse
import collections
import copy
import time
import roi197_screen as s

h,p,e,r=s.h,s.p,s.e,s.r
OUT=h.ROOT/'reports/work/IOS-PROPOSAL-197/artifacts/comparison01'


def prepare():
    h.require(not OUT.exists(),'output_collision')
    screen=p.sealed(s.OUT/'report.json');h.require(screen['retainedEvaluationReady'],'screen_failed')
    sd=s.protocol();parent=r.c.inputs();cid=e.load_names().index('pageControl');plans={}
    OUT.mkdir(parents=True)
    for kind,ref in parent['manifests'].items():
        req=e.load_request(h.checked(h.ROOT,ref),41)
        base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),
            req,parent['checkpoints']['022']['sha256'],expected_settings=r.c.SETTINGS)
        byid={v['imageID']:v for v in base['results']};entries=[];records=[]
        for i,im in enumerate(req.images):
            chosen,reason=s.a.candidate(byid[im.image_id],cid)
            row=dict(imageID=im.image_id,reason=reason,cropID=None)
            if chosen:
                key=f'{kind}-{i:04d}';roi=r.window(im.width,im.height,chosen[1]['xyxyPixels'])
                row.update(cropID=key,window=roi)
                if kind!='fit':
                    old=r.OUT;r.OUT=OUT
                    try:entry,_=r.save_crop(im,roi,OUT/'crops'/kind,key)
                    finally:r.OUT=old
                    entries.append(entry)
            records.append(row)
        if kind=='fit':manifest=h.ref(s.OUT/'input.json')
        else:
            path=OUT/(kind+'-input.json')
            h.write(path,dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi197-'+kind,images=entries))
            e.load_request(path,41);manifest=h.ref(path)
        plans[kind]=dict(manifest=manifest,records=records)
    h.require(sum(v.stat().st_size for v in OUT.rglob('*') if v.is_file())<2*1024**3,'budget')
    h.write(OUT/'protocol.json',dict(plans=plans,checkpoint=sd['checkpoint'],screen=h.ref(s.OUT/'report.json'),
        sources=[h.ref(__file__),h.ref(s.__file__),h.ref(s.a.__file__),h.ref(r.__file__)],
        settings=r.c.SETTINGS,fitPredictions=h.ref(s.OUT/'predictions.json')),sealed=True)


def protocol():
    d=p.sealed(OUT/'protocol.json')
    for ref in d['sources']+[d['checkpoint'],d['screen'],d['fitPredictions']]:h.checked(h.ROOT,ref,256*1024**2)
    return d


def infer():
    d=protocol();start=time.monotonic()
    for kind,plan in d['plans'].items():
        if kind=='fit':continue
        e.export_predictions(h.checked(h.ROOT,plan['manifest']),h.checked(h.ROOT,d['checkpoint'],256*1024**2),
            OUT/(kind+'-predictions.json'),'mps',discard_degenerate=True)
    h.write(OUT/'inference.json',dict(seconds=time.monotonic()-start),sealed=True)


def merge(base,records,crops,cid):
    bycrop={v['imageID']:v for v in crops};byrecord={v['imageID']:v for v in records}
    expected=[v['cropID'] for v in records if v['cropID'] is not None]
    h.require(len(bycrop)==len(crops)==len(expected) and set(bycrop)==set(expected),'crop_membership')
    h.require(len(byrecord)==len(records)==len(base) and set(byrecord)=={v['imageID'] for v in base},'base_membership')
    result=[];decisions=[]
    for row in base:
        record=byrecord[row['imageID']];updated=copy.deepcopy(row);donor=None;reason=record['reason']
        if record['cropID'] is not None:
            donor,reason=s.admit(row,bycrop[record['cropID']],cid)
            if donor:updated['detections'].append(donor);updated['status']='ok'
        result.append(updated);decisions.append(dict(imageID=row['imageID'],reason=reason,added=bool(donor)))
    return dict(results=result),decisions


def report():
    d=protocol();h.require(not (OUT/'evaluation.json').exists(),'output_collision')
    parent=r.c.inputs();names=e.load_names();cid=names.index('pageControl');scores={};accounting={}
    control=p.sealed(r.c.g.CONTROL/'evaluation.json');metadata=p.sealed(r.c.g.CONTROL/'protocol.json')['metadata']
    for kind,plan in d['plans'].items():
        req=e.load_request(h.checked(h.ROOT,parent['manifests'][kind]),41)
        base=e.validated_artifact(h.read(h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2),256*1024**2),
            req,parent['checkpoints']['022']['sha256'],expected_settings=d['settings'])
        crop_req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        path=h.checked(h.ROOT,d['fitPredictions'],256*1024**2) if kind=='fit' else OUT/(kind+'-predictions.json')
        crops=e.validated_artifact(h.read(path,256*1024**2),crop_req,d['checkpoint']['sha256'],expected_settings=d['settings'])
        derived,decisions=merge(base['results'],plan['records'],crops['results'],cid)
        scores[kind]=e.score(derived,req,names);accounting[kind]=dict(collections.Counter(v['reason'] for v in decisions))
        h.write(OUT/(kind+'-derived.json'),dict(derived,decisions=decisions),sealed=True)
        for before,after in zip(control['results'][kind]['perClass'],scores[kind]['perClass']):
            if before['class']!='pageControl':h.require(before==after,'non_page_change')
        if kind=='fit':cases=r.c.g.r.f.d.pages(req,derived,cid,metadata)
    strata={k:dict(collections.Counter(v['disposition'] for v in cases if v['metadata']['placement']==k)) for k in ('leading','center','trailing')}
    assessment=r.c.g.r.assess(scores,strata,p.sealed(r.c.g.r.f.OUT/'evaluation.json'))
    h.write(OUT/'evaluation.json',dict(results=scores,accounting=accounting,strata=strata,assessment=assessment,
        protocol=h.ref(OUT/'protocol.json'),productionEligible=False),sealed=True)
    print('assessment',assessment)
    for kind,result in scores.items():print(kind,next(v for v in result['perClass'] if v['class']=='pageControl'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','infer','report']);globals()[parser.parse_args().mode]()
