"""Terminal-only matched evaluation of Run018; no training or checkpoint selection."""
import argparse
import csv
import math
import dataclasses
import translation170 as t
import shared_transfer
e=t.e;h=t.h
OUT=t.OUT/'matched-positive-area-v1'
from eval_phase6a import DEGENERATE_POLICY
SETTINGS=dict(e.e.PREDICTION_SETTINGS,postprocessing=DEGENERATE_POLICY)

def check_rows(rows,args,control_args):
    expected=dict(control_args,translate=.35,name=t.RUN.name,save_dir=str(t.RUN))
    # Runtime-only save_dir may be absent in some Ultralytics versions.
    expected.pop('save_dir',None)
    h.require(all(args.get(k)==v for k,v in expected.items()),'nonmatched_settings')
    h.require(len(rows)==5 and [str(x['epoch']) for x in rows]==['1','2','3','4','5'],'epoch_count')
    required={'epoch','time','train/box_loss','train/cls_loss','train/dfl_loss',
              'val/box_loss','val/cls_loss','val/dfl_loss','metrics/mAP50(B)','metrics/mAP50-95(B)'}
    h.require(all(required<=x.keys() for x in rows),'missing_epoch_metrics')
    h.require(all(all(math.isfinite(float(v)) for v in x.values()) for x in rows),'nonfinite_epochs')

def ready():
    control,refs=e.ready('r017-repaired')
    protocol=h.read(t.OUT/'protocol.json');receipt=h.read(t.OUT/'completion.json')
    for doc in (protocol,receipt):h.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'seal')
    h.require(receipt['exitCode']==0,'incomplete')
    checkpoint=h.checked(h.ROOT,receipt['checkpoint'],256*1024**2)
    h.require(checkpoint.resolve()==(t.RUN/'weights/last.pt').resolve(),'wrong_checkpoint')
    h.require(h.sha(control)==protocol['control']['sha256'],'changed_control')
    args=shared_transfer.document(t.RUN/'args.yaml')
    old=shared_transfer.document(control.parent.parent/'args.yaml')
    with (t.RUN/'results.csv').open() as f:rows=list(csv.DictReader(f))
    check_rows(rows,args,old)
    pinned=[h.checked(h.ROOT,ref,256*1024**2) for ref in protocol['evaluation']]
    h.require(pinned==refs,'evaluation_reference_mismatch')
    return checkpoint,refs

def infer():
    checkpoint,refs=ready()
    h.require(not OUT.exists(),'evaluation_output_collision')
    OUT.mkdir()
    control,_=e.ready('r017-repaired')
    h.write(OUT/'protocol.json',dict(settings=SETTINGS,checkpoints=[h.ref(control),h.ref(checkpoint)],
        manifests=[h.ref(refs[i]) for i in (0,3)],
        sources=[h.ref(__file__),h.ref(h.ROOT/'scripts/eval_phase6a.py'),h.ref(h.ROOT/'scripts/eval_run013.py')],
        firstFailedExportsPreserved=True,independentEvaluation=False),sealed=True)
    for arm,model in [('018',checkpoint),('017',control)]:
        for name,manifest in [('combined',refs[0]),('page',refs[3])]:
            e.e.export_predictions(manifest,model,OUT/(arm+'-'+name+'-predictions.json'),'mps',discard_degenerate=True)

def report():
    checkpoint,refs=ready();names=e.e.load_names();sha=h.sha(checkpoint)
    protocol=h.read(OUT/'protocol.json')
    h.require(protocol['seal']==h.digest({k:v for k,v in protocol.items() if k!='seal'}),'evaluation_protocol_seal')
    h.require(protocol['settings']==SETTINGS,'evaluation_settings_changed')
    for ref in protocol['sources']+protocol['checkpoints']+protocol['manifests']:
        h.checked(h.ROOT,ref,256*1024**2)
    candidate=h.read(OUT/'018-combined-predictions.json',256*1024**2)
    control=h.read(OUT/'017-combined-predictions.json',256*1024**2)
    control_checkpoint,_=e.ready('r017-repaired');control_sha=h.sha(control_checkpoint)
    results={}
    for i,name in enumerate(('combined','withheld','addon')):
        request=e.e.load_request(refs[i],41);results[name]={}
        for arm,doc,digest in [('018',candidate,sha),('017',control,control_sha)]:
            sub=e.e.subset(doc,request) if i else doc
            e.e.validated_artifact(sub,request,digest,expected_settings=SETTINGS);results[name][arm]=e.e.score(sub,request,names)
    request=e.e.load_request(refs[3],41);page={}
    for arm,path in [('018',OUT/'018-page-predictions.json'),('017',OUT/'017-page-predictions.json')]:
        doc=h.read(path,256*1024**2)
        e.e.validated_artifact(doc,request,sha if arm=='018' else control_sha,expected_settings=SETTINGS)
        strata={}
        catalog=h.read(e.r.repair.PROBES/'compose155-catalog.json')['rows']
        h.require({x['id'] for x in catalog}=={x.image_id for x in request.images},'catalog_membership')
        for axis in ('family','native','dark','pages','left','seed'):
            for value in sorted({x[axis] for x in catalog}):
                ids={x['id'] for x in catalog if x[axis]==value}
                sub=dataclasses.replace(request,images=tuple(x for x in request.images if x.image_id in ids))
                scored=e.e.score(e.e.subset(doc,sub),sub,names)
                strata[f'{axis}={value}']=next(x for x in scored['perClass'] if x['class']=='pageControl')
        page[arm]=dict(score=e.e.score(doc,request,names),geometry=e.page_geometry(doc,request,names.index('pageControl')),strata=strata)
    h.require(not (OUT/'evaluation.json').exists(),'report_collision')
    h.write(OUT/'evaluation.json',dict(checkpoint=h.ref(checkpoint),results=results,page=page,settings=SETTINGS,
        source=h.ref(__file__),predictions=[h.ref(OUT/(a+'-'+n+'-predictions.json')) for a in ('018','017') for n in ('combined','page')],
        independentEvaluation=False,productionEligible=False),sealed=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['infer','report']);a=p.parse_args();globals()[a.mode]()
