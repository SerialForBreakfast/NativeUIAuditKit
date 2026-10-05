"""Complete retained-error accounting and a non-executing native batch plan."""
import collections
import itertools
import eval_translation170 as t
import native_repair159 as native
e=t.e.e;h=t.h
OUT=h.ROOT/'reports/work/IOS-DIAG-171/artifacts'


def truth(image,cid):
    boxes=[]
    for line in image.label_path.read_text().splitlines():
        if not line.strip():continue
        c,x,y,w,ht=map(float,line.split())
        if c==cid:boxes.append([(x-w/2)*image.width,(y-ht/2)*image.height,
                               (x+w/2)*image.width,(y+ht/2)*image.height])
    return boxes


def classify(box,candidates):
    matching=[d for d in candidates if e.iou_xyxy(box,d['xyxyPixels'])>=.5]
    label=('operating-hit' if any(d['score']>=.25 for d in matching) else
           'low-confidence-match' if matching else 'localization-miss' if candidates else 'absent')
    return dict(disposition=label,candidates=len(candidates),
        bestIoU=max((e.iou_xyxy(box,d['xyxyPixels']) for d in candidates),default=None),
        maxMatchingConfidence=max((d['score'] for d in matching),default=None))


def matches(boxes,candidates):
    available=set(range(len(boxes)));tp=fp=0
    for d in sorted(candidates,key=lambda x:-x['score']):
        if d['score']<.25:continue
        overlap,j=max(((e.iou_xyxy(d['xyxyPixels'],boxes[i]),i) for i in available),default=(0,-1))
        if overlap>=.5:tp+=1;available.remove(j)
        else:fp+=1
    return dict(support=len(boxes),tp=tp,fp=fp,fn=len(available))


def catalog(source):
    members=native.members(source);groups=collections.defaultdict(list)
    for row in members:groups[(row['family'],row['scale'],row['colorScheme'])].append(row)
    expected={(family,scale,theme) for family in ('UIKitControls','KitchenSink')
              for scale,theme in ((2,'light'),(3,'dark'))}
    h.require(set(groups)==expected,'unexpected_source_strata')
    rows=[]
    for key in sorted(groups):
        selected=sorted(groups[key],key=lambda r:r['id'])[:12]
        h.require(len(selected)==12,'insufficient_source_stratum')
        for source_row in selected:
            for placement,tint in itertools.product(('leading','center','trailing'),('system-blue','semantic-label')):
                rows.append(dict(id=f"placement171-{source_row['id']}-{placement}-{tint}",
                    group=source_row['id'],split='train',family=source_row['family'],scale=source_row['scale'],
                    theme=source_row['colorScheme'],placement=placement,tint=tint,recipe=source_row))
    h.require(len(rows)==288 and len({r['id'] for r in rows})==288,'plan_membership')
    return dict(version='native-placement-plan-v1',rows=rows,groups=48,frames=288,
        executionReady=False,trainingEligible=False,independentEvaluation=False,
        coverageLimitations=['Source scale2/light and scale3/dark are coupled; no independent scale/theme inference.'],
        requirements=['Extend existing full-annotation UIKit templates; never train from partial probe labels.',
            'Place full control within safe content margins; measure actual visible pixel center, not requested x.',
            'system-blue uses systemBlue/systemFill; semantic-label uses label/tertiaryLabel; verify resolved rendering.',
            'Use visible/hidden differencing with qualified one-pixel tolerance, retaining both images.',
            'Keep all parent/related seed/duplicate groups training-only; preserve existing validation/test.',
            'Qualify first complete matrix, then one bounded batch; no automatic retries or quota shrinking.'])


def run():
    h.require(not OUT.exists(),'output_collision')
    completed=h.read(t.OUT/'evaluation.json')
    h.require(completed['seal']==h.digest({k:v for k,v in completed.items() if k!='seal'}),'report_seal')
    for ref in completed['predictions']:h.checked(h.ROOT,ref,256*1024**2)
    cp,refs=t.ready();control,_=t.e.ready('r017-repaired');names=e.load_names()
    recipes=h.read(native.PROBES/'compose155-catalog.json')['rows'];indexed={r['id']:r for r in recipes}
    result={}
    for arm,checkpoint in [('017',control),('018',cp)]:
        result[arm]={};pages=[];class_cases={}
        for kind,manifest in [('page',refs[3]),('combined',refs[0])]:
            request=e.load_request(manifest,41);doc=h.read(t.OUT/(arm+'-'+kind+'-predictions.json'),256*1024**2)
            e.validated_artifact(doc,request,h.sha(checkpoint),expected_settings=t.SETTINGS)
            predictions={r['imageID']:r['detections'] for r in doc['results']}
            if kind=='page':
                h.require(set(indexed)==set(predictions),'probe_membership')
                for image in request.images:
                    cid=names.index('pageControl');gt=truth(image,cid);h.require(len(gt)==1,'probe_truth')
                    pages.append(dict(id=image.image_id,recipe=indexed[image.image_id],
                        **classify(gt[0],[d for d in predictions[image.image_id] if d['classID']==cid])))
            else:
                for name in ('cancelAction','mapView'):
                    cid=names.index(name);cases=[]
                    for image in request.images:
                        gt=truth(image,cid);pred=[d for d in predictions[image.image_id] if d['classID']==cid]
                        if gt or pred:cases.append(dict(id=image.image_id,**matches(gt,pred)))
                    totals={k:sum(r[k] for r in cases) for k in ('support','tp','fp','fn')}
                    expected=next(c for c in completed['results']['combined'][arm]['perClass'] if c['class']==name)
                    h.require(all(totals[k]==expected[k] for k in totals),'operational_reconciliation')
                    class_cases[name]=dict(totals=totals,cases=cases)
        cells={}
        for left,nat in itertools.product((False,True),repeat=2):
            subset=[r for r in pages if r['recipe']['left']==left and r['recipe']['native']==nat]
            h.require(len(subset)==24,'unbalanced_probe_cell')
            cells[f'left={left},native={nat}']=dict(collections.Counter(r['disposition'] for r in subset))
        result[arm]=dict(pageCases=pages,pageCells=cells,regressions=class_cases)
    source=h.read(native.CATALOG);plan=catalog(source)
    plan['sourceCatalog']=h.ref(native.CATALOG)
    OUT.mkdir(parents=True)
    h.write(OUT/'diagnosis.json',dict(arms=result,evaluation=h.ref(t.OUT/'evaluation.json'),source=h.ref(__file__),
        independentEvaluation=False),sealed=True)
    h.write(OUT/'native-batch-plan.json',plan,sealed=True)
    print({a:dict(cells=v['pageCells'],regressions={k:x['totals'] for k,x in v['regressions'].items()}) for a,v in result.items()})
    print('planned',plan['frames'],'frames from',plan['groups'],'training-only parent groups; not executable/admitted')


if __name__=='__main__':run()
