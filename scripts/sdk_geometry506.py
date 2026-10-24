"""Compare detector geometry on review-only SDK packets. Never assign class labels."""
import math
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from sdk_dataset505 import audit
from sdk_packet502 import review
from detector_case_match411 import iou
import detector_inference412 as inference

OUT = None


def matches(elements, predictions):
    boxes = []
    for item in predictions:
        b = item['boundingBoxPixels']; v = [b[k] for k in ('x','y','width','height')]
        q.require(all(type(x) in (int,float) and math.isfinite(x) for x in v) and v[2]>0 and v[3]>0,
                  'sdk_prediction_geometry')
        boxes.append([v[0],v[1],v[0]+v[2],v[1]+v[3]])
    rows = []
    for item in elements:
        if not item['geometryAvailable'] or not item['observedVisibleEnabled']:
            continue
        x,y,w,h = item['pixelBounds']; overlaps = [iou([x,y,x+w,y+h],b) for b in boxes]
        best = max(overlaps, default=0)
        rows.append(dict(id=item['identity']['id'],bestIoU=best,covered=best>=0.5,
                         candidates=sum(v>=0.5 for v in overlaps)))
    return rows


def prepare(request):
    fields={'version','id','manifest','models','confidence','imageSize'}
    q.require(fields<=set(request)<=fields|{'cachedGeneral'},'sdk_geometry_fields')
    q.require(request['version']=='sdk-geometry-request-v1' and q.ID.fullmatch(request['id']), 'sdk_geometry_version')
    q.require(set(request['models'])=={'scoped','general'},'sdk_geometry_models')
    q.require(request['confidence']==0.25 and request['imageSize']==1280,'sdk_geometry_settings')
    corpus=audit(checked(request['manifest']))
    frames=[]
    for case in corpus['cases']:
        for frame in case['frames']:
            e=q.load(checked(frame['evidence'])); r=review(e,checked(frame['image']))
            q.require(r['reviewable'],'sdk_geometry_unreviewable')
            frames.append(dict(case=case['id'],group=case['group'],split=case['split'],role=frame['role'],
                image=frame['image'],sha256=frame['image']['sha256'],width=e['width'],height=e['height'],
                elements=r['elements']))
    q.require(0<len(frames)<=16,'sdk_geometry_scope')
    for ref in request['models'].values():checked(ref)
    if 'cachedGeneral' in request:
        q.require(len(request['cachedGeneral'])==len(frames),'sdk_cache_count')
        for ref,frame in zip(request['cachedGeneral'],frames):
            d=q.load(checked(ref))
            q.require(d['inputSHA256']==frame['sha256'] and d['configuration']==dict(minConfidence=0.25,imageSize=1280)
                and d['runtime']['detector']==dict(engine='pytorch',weightsSHA256=request['models']['general']['sha256'],imageSize=1280,nmsIoU=inference.NMS_IOU),
                'sdk_cache_identity')
    return corpus,frames


def build(path):
    r=q.load(path);prepare(r)
    refs=[pin(path),r['manifest'],*r['models'].values(),pin(Path(__file__).resolve())]
    refs.extend(r.get('cachedGeneral',[]))
    return dict(version='research-spec-v2',id=r['id'],task='SDK506',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
        adapter=dict(type='python-callable',steps=['sdk_geometry506.run'],outputAttributes=['sdk_geometry506.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json',reads=[x['path'] for x in refs[:4]]),
        question='Which detector supplies boxes for the registered SDK controls on identical retained pixels?',
        hypothesis='Missing proposals explain some focus failures before classification runs.',
        controlledComparison='Same pixels, original roles, 1280 image size, 0.25 confidence, and existing NMS. Change only pinned detector.',
        decisionRule='Report case-linked coverage gains and losses at IoU 0.5. Do not infer precision or class accuracy from incomplete annotations.',
        nextActionByOutcome=dict(supported='Use recovered and missing control IDs to choose the next proposal correction.',
                                 contradicted='Preserve models and investigate localization before further training.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['inputs'][0]));corpus,frames=prepare(request)
    results={}; artifacts=[]; inference.OUT=OUT
    for name,ref in request['models'].items():
        raw=OUT/name;raw.mkdir()
        if name=='general' and 'cachedGeneral' in request:
            for i,cached in enumerate(request['cachedGeneral']):q.save(raw/('%03d.json'%i),q.load(checked(cached)))
            identity=q.load(checked(request['cachedGeneral'][0]))['runtime']['detector']
        else:
            identity=inference.pytorch(checked(ref),frames,request['confidence'],request['imageSize'],raw)
        rows=[]
        for i,frame in enumerate(frames):
            path=raw/('%03d.json'%i);d=q.load(path)
            q.require(d['inputSHA256']==frame['sha256'] and d['runtime']['detector']==identity,'sdk_prediction_identity')
            rows.append(dict(case=frame['case'],image=frame['image'],group=frame['group'],split=frame['split'],
                role=frame['role'],controls=matches(frame['elements'],d['runtime']['result']['elements'])))
            artifacts.append(path)
        results[name]=dict(model=ref,identity=identity,rows=rows)
    differences=[]
    for s,g in zip(results['scoped']['rows'],results['general']['rows']):
        q.require(s['image']==g['image'],'sdk_comparison_membership')
        for a,b in zip(s['controls'],g['controls']):
            q.require(a['id']==b['id'],'sdk_comparison_identity')
            differences.append(dict(case=s['case'],id=a['id'],scoped=a['covered'],general=b['covered'],
                gain=b['covered'] and not a['covered'],lost=a['covered'] and not b['covered']))
    report=dict(version='sdk-geometry-comparison-v1',models=results,cases=differences,
        gains=sum(r['gain'] for r in differences),losses=sum(r['lost'] for r in differences),
        ancestryGroups=corpus['ancestryGroups'],trainingEligible=False,modelAccepted=False,
        limitation='Registered-box coverage only. Matches are not one-to-one detection recall. No precision, taxonomy, focus-selection, or independent-app accuracy claim.')
    q.save(OUT/'benchmark_summary.json',report);artifacts.append(OUT/'benchmark_summary.json')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in artifacts]))
