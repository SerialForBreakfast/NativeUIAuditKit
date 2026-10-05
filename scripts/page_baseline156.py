"""Existing exporter/AP implementation, new page-only development membership."""
import argparse
import json
from pathlib import Path
import artifact_storage
import numpy as np
import eval_run013 as e
from compose155 import BASE,catalog


def prepare():
    audit=e.read(BASE/'compose155-audit/report.json');rows=audit['rows']
    if audit['accepted']!=96 or audit['duplicateCount'] or {r['id'] for r in rows}!={r['id'] for r in catalog()}:raise ValueError('qualified_membership')
    names=e.load_names();cid=names.index('pageControl');out=BASE/'page156-labels';out.mkdir()
    images=[]
    for r in rows:
        x,y,w,h=r['visualBox'];scale=r['scale'];width=r['width'];height=r['height']
        label=out/(r['id']+'.txt')
        with label.open('x') as f:f.write(f'{cid} {(x+w/2)*scale/width:.9f} {(y+h/2)*scale/height:.9f} {w*scale/width:.9f} {h*scale/height:.9f}\n')
        images.append(dict(imageID=r['id'],imagePath='compose155-capture/'+r['id']+'.png',
            labelPath='page156-labels/'+label.name,imageSHA256=r['sha256'],labelSHA256=e.sha256_file(label)))
    manifest=BASE/'page156-manifest.json'
    e.save(manifest,dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='compose155-page-development',images=images))
    e.load_request(manifest,41)
    checkpoint=e.CHECKPOINT
    if e.sha256_file(checkpoint)!='88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7':raise ValueError('checkpoint')
    e.save(BASE/'page156-freeze.json',dict(checkpoint=str(checkpoint),checkpointSHA256=e.sha256_file(checkpoint),
        manifestSHA256=e.sha256_file(manifest),auditSHA256=e.sha256_file(BASE/'compose155-audit/report.json'),
        settings=e.PREDICTION_SETTINGS,role='development',scope='pageControl only; other class metrics unavailable'))


def infer():
    freeze=e.read(BASE/'page156-freeze.json');manifest=BASE/'page156-manifest.json';checkpoint=Path(freeze['checkpoint'])
    if e.sha256_file(manifest)!=freeze['manifestSHA256'] or e.sha256_file(checkpoint)!=freeze['checkpointSHA256']:raise ValueError('changed_inputs')
    e.export_predictions(manifest,checkpoint,BASE/'page156-predictions.json','cpu')


def report():
    freeze=e.read(BASE/'page156-freeze.json')
    if e.sha256_file(BASE/'compose155-audit/report.json')!=freeze['auditSHA256']:raise ValueError('changed_labels')
    rows=e.read(BASE/'compose155-audit/report.json')['rows'];by={r['id']:r for r in rows}
    artifact=e.read(BASE/'page156-predictions.json');verify_artifact(artifact,freeze)
    results=artifact['results'];cid=e.load_names().index('pageControl')
    if len(results)!=96 or {r['imageID'] for r in results}!=set(by) or any(r['status']=='failed' for r in results):raise ValueError('incomplete_inference')
    cases=[];groups={}
    for p in results:
        r=by[p['imageID']];x,y,w,h=r['visualBox'];s=r['scale'];gt=[x*s,y*s,(x+w)*s,(y+h)*s]
        ds=[d for d in p['detections'] if d['classID']==cid]
        matches=[d for d in ds if d['score']>=.25 and e.iou_xyxy(gt,d['xyxyPixels'])>=.5]
        cases.append(dict(id=p['imageID'],groundTruth=gt,pageDetections=ds,operationalHit=bool(matches),
            operationalFalsePositives=sum(d['score']>=.25 for d in ds)-int(bool(matches))))
        keys=['all',r['family'],'native' if r['native'] else 'manual','dark' if r['dark'] else 'light']
        if r['native']:keys.append('prominent' if r['prominent'] else 'automatic-disabled')
        for key in keys:groups.setdefault(key,[]).append(cases[-1])
    summary={}
    for key,rs in groups.items():
        gt={cid:{r['id']:[tuple(r['groundTruth'])] for r in rs}}
        ds=sorted([(r['id'],d['score'],tuple(d['xyxyPixels'])) for r in rs for d in r['pageDetections']],key=lambda v:-v[1])
        summary[key]=dict(count=len(rs),customAP50=e.compute_ap_at_iou(gt,{cid:ds},cid,.5),
            operationalHits=sum(r['operationalHit'] for r in rs),operationalFalsePositives=sum(r['operationalFalsePositives'] for r in rs))
    e.save(BASE/'page156-report.json',dict(summary=summary,cases=cases,role='development',otherClassMetrics=None,
        officialMetrics=False,modelGatePassed=False,predictionSHA256=e.sha256_file(BASE/'page156-predictions.json')))
    print(json.dumps(summary,indent=2))


def verify_artifact(artifact,freeze):
    if artifact['model']['checkpointSHA256']!=freeze['checkpointSHA256'] or artifact['corpus']['inputManifestSHA256']!=freeze['manifestSHA256'] or artifact['settings']!=freeze['settings']:
        raise ValueError('prediction_identity')
    if artifact['categoryMap']['sha256']!=e.sha256_file(e.CATEGORY_MAP):raise ValueError('category_identity')


def diagnose():
    source=BASE/'page156-report.json';doc=e.read(source);rows=[]
    for r in doc['cases']:
        g=r['groundTruth'];ds=r['pageDetections']
        if not ds:continue
        best=max(ds,key=lambda v:e.iou_xyxy(g,v['xyxyPixels']));b=best['xyxyPixels']
        rows.append(dict(id=r['id'],bestIoU=e.iou_xyxy(g,b),score=best['score'],
            widthRatio=(b[2]-b[0])/(g[2]-g[0]),verticalCenterErrorPixels=abs((b[1]+b[3]-g[1]-g[3])/2),
            centerInside=g[0]<=(b[0]+b[2])/2<=g[2] and g[1]<=(b[1]+b[3])/2<=g[3]))
    e.save(BASE/'page156-diagnosis.json',dict(sourceSHA256=e.sha256_file(source),rows=rows,
        imagesWithCandidates=len(rows),candidateCenterInside=sum(r['centerInside'] for r in rows),
        medianWidthRatio=float(np.median([r['widthRatio'] for r in rows])) if rows else None,
        interpretation='Many candidates share the indicator location but boxes are too wide. Consistent with old container labels, not proof of sole cause. Missing candidates also remain; geometry repair alone is not guaranteed to solve recall.'))


def inventory():
    old=e.read(e.ROOT/'reports/work/IOS-R013-EVAL/preflight.json');freeze=e.read(e.ROOT/'reports/work/IOS-R013-EVAL/freeze.json')
    if e.sha256_file(e.ROOT/'reports/work/IOS-R013-EVAL/preflight.json')!=freeze['auditSHA256']:raise ValueError('inventory_pin')
    current=e.read(e.ROOT/'reports/work/REAL-TRANSFER-42/ios-export-verified.json')['rows']
    by={Path(r['image']['path']).stem:r for r in current};members=[]
    for r in old['members']:
        if r['split']!='train' or r['family'] not in ('KitchenSink','UIKitControls') or 18 not in r['classes']:continue
        row=by[Path(r['imageID']).stem];image=artifact_storage.resolve_input(e.ROOT/row['image']['path'])
        label=artifact_storage.resolve_input(e.ROOT/row['label']['path']);ann=image.with_suffix('.json')
        if e.sha256_file(image)!=row['image']['sha256'] or e.sha256_file(label)!=row['label']['sha256']:raise ValueError('current_bytes')
        a=e.read(ann)
        if a['imageSHA256']!=row['image']['sha256'] or a['generatorProfile']['templateFamily']!=r['family']:raise ValueError('recipe_binding')
        members.append(dict(id=Path(r['imageID']).stem,family=r['family'],image=row['image'],label=row['label'],
            annotationSHA256=e.sha256_file(ann),recipe=a['generatorProfile'],imageConfiguration=a['image']))
    if len(members)!=900 or len({r['id'] for r in members})!=900:raise ValueError('repair_membership')
    e.save(BASE/'page156-repair-inventory.json',dict(count=900,members=members,role='train',
        executed=False,unresolved='UIKitControls automatic-interactive rendering not qualified; no annotation rewrite'))
    print('verified repair inventory',len(members))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','infer','report','inventory','diagnose']);globals()[p.parse_args().mode]()
