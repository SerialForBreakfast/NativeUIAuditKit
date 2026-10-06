"""Plan and independently validate the frozen native artwork development campaign."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from shared_transfer import document, require

TARGET = 'F3EF9DB8-0B0F-4757-B653-D1628269F6FF'
REVIEWED = {'thumbnail-03':'849d71d158a536ce137c4be3a39ffa0312b42b0133386289badb6d908718b9b6',
            'thumbnail-04':'095a0931594d948250042e0459387f8d08a69428fb345709cf34281a2414a8e3'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def recipes():
    return [dict(id=f'{a}-{b}-{c}-{s}-{d}', layout=a, theme=b, density=c, seed=s, condition=d)
            for a,b,c,s,d in itertools.product(('grid','detail'),('light','dark'),('low','high'),
                                               range(200,204),('procedural','low','busy'))]


def prepare(source, out, reviewed=REVIEWED):
    """Only these independently reviewed retained images, no automatic general admission."""
    source, out = Path(source), Path(out)
    require(not out.exists(), 'output_collision')
    assets = []
    for name in ('thumbnail-04','thumbnail-03'):
        path = source/(name+'.png')
        require(path.is_file() and not path.is_symlink(), 'asset_file')
        require(sha(path)==reviewed[name], 'unreviewed_bytes')
        with Image.open(path) as im:
            require(im.format == 'PNG' and im.size == (1216,832), 'asset_dimensions')
            im.load()
        assets.append(dict(id='image201/'+name,path=path.name,sha256=sha(path),bytes=path.stat().st_size,
            width=1216,height=832,ancestryGroup='IMAGE201-thumbnail',dataRole='development',
            rightsStatus='verified',reviewStatus='verified',rightsEvidence=['LOCAL-IMAGE201 retained model/base licences',
            'reports/work/IOS-ASSET-200/review.md'],reviewEvidence=['reports/work/IOS-ASSET-200/review.md']))
    out.mkdir(parents=True)
    for a in assets: shutil.copyfile(source/a['path'], out/a['path'])
    write(out/'catalog.json', dict(schemaVersion='ios-generator-artwork-v1',assets=assets))
    write(out/'campaign.json',dict(schemaVersion='ios-artwork-campaign-v1',target=TARGET,
        catalogSHA256=sha(out/'catalog.json'),lowAsset=assets[0]['id'],busyAsset=assets[1]['id'],recipes=recipes()))


def validate(root, inputs):
    root, inputs = Path(root), Path(inputs)
    plan = document(inputs/'campaign.json'); catalog = document(inputs/'catalog.json')
    split = plan['schemaVersion']=='ios-artwork-campaign-v2'
    if split:
        from artwork204_campaign import check
        check(plan,catalog,inputs)
    else:
        require(catalog['schemaVersion']=='ios-generator-artwork-v1' and plan['schemaVersion']=='ios-artwork-campaign-v1' and plan['target']==TARGET and
                plan['recipes']==recipes() and plan['catalogSHA256']==sha(inputs/'catalog.json'), 'plan')
    planned=plan['recipes']
    assets={a['id']:a for a in catalog['assets']}
    for a in ([] if split else assets.values()):
        require(a['path'] in ('thumbnail-03.png','thumbnail-04.png') and sha(inputs/a['path'])==a['sha256'], 'asset_hash')
        require(a['dataRole']=='development' and a['rightsStatus']==a['reviewStatus']=='verified', 'asset_role')
    expected={f'shard-{s}.json' for s in (0,1)} | {r['id']+s for r in planned for s in ('.png','.json','.record.json')}
    require({p.name for p in root.iterdir()}==expected, 'membership')
    require(all(p.is_file() and not p.is_symlink() for p in root.iterdir()), 'file_type')
    rows=[]; seconds=0; pixel_hashes={}; groups={}
    for shard in (0,1):
        receipt=document(root/f'shard-{shard}.json')
        require(receipt.get('complete') is True and receipt.get('schemaVersion')==('ios-artwork-shard-v2' if split else 'ios-artwork-shard-v1') and
                receipt.get('shard')==shard and receipt.get('planSHA256')==sha(inputs/'campaign.json') and
                len(receipt['frames'])==48, 'completion')
        seconds+=receipt['seconds']
        for recipe,record in zip(planned[48*shard:48*(shard+1)],receipt['frames']):
            key=recipe['id']; png=root/(key+'.png'); ann=root/(key+'.json')
            require(record==document(root/(key+'.record.json')) and record['recipe']==recipe and
                record['planSHA256']==sha(inputs/'campaign.json') and record['dataRole']==recipe.get('dataRole','development'), 'record')
            require(record['imageSHA256']==sha(png) and record['sidecarSHA256']==sha(ann), 'hash')
            a=document(ann)
            require(a['imageSHA256']==sha(png) and a['image']['colorScheme']==recipe['theme'], 'annotation_metadata')
            with Image.open(png) as im:
                require(im.format=='PNG' and im.size==(1179,2556), 'dimensions')
                pixels=np.array(im.convert('RGB'))
            digest=hashlib.sha256(pixels.tobytes()).hexdigest()
            pixel_hashes.setdefault(digest,[]).append(key)
            elements={e['id']:e for e in a['elements']}
            require(len(elements)==len(a['elements']), 'duplicate_element')
            for e in elements.values():
                x,y,w,h=[e['boundsPixels'][k] for k in ('x','y','width','height')]
                require(all(np.isfinite([x,y,w,h])) and 0<=x<x+w<=1179 and 0<=y<y+h<=2556, 'element_bounds')
            targets={k:v for k,v in elements.items() if k.startswith('imageView_thumb_') or k=='imageView_hero'}
            count=(4 if recipe['density']=='low' else 6) if recipe['layout']=='grid' else 1
            require(len(targets)==count, 'targets')
            group=key.rsplit('-',1)[0]
            if recipe['condition']=='procedural':
                require(not record['bindings'], 'procedural_bindings')
                groups[group]=(pixels,elements)
                changed=outside=0
            else:
                baseline,base_elements=groups[group]
                require(elements==base_elements, 'annotation_drift')
                require(len(record['bindings'])==count and {b['elementID'] for b in record['bindings']}==set(targets), 'bindings')
                mask=np.zeros(pixels.shape[:2],dtype=bool)
                diff=np.any(pixels!=baseline,axis=2)
                for b in record['bindings']:
                    asset=assets[recipe['assetID'] if split else (plan['lowAsset'] if recipe['condition']=='low' else plan['busyAsset'])]
                    require(b['assetID']==asset['id'] and b['sha256']==asset['sha256'] and
                            b['ancestryGroup']==asset['ancestryGroup'] and b['placement']=='fill', 'asset_binding')
                    e=targets[b['elementID']]; v=[e['boundsPoints'][k] for k in ('x','y','width','height')]
                    require(np.allclose(v,b['viewportPoints'],rtol=0,atol=1e-8), 'viewport')
                    x,y,w,h=v; scale=max(w/asset['width'],h/asset['height']); aw,ah=asset['width']*scale,asset['height']*scale
                    require(np.allclose([x+(w-aw)/2,y+(h-ah)/2,aw,ah],b['contentExtentPoints'],rtol=0,atol=1e-8), 'content_extent')
                    x,y,w,h=[e['boundsPixels'][k] for k in ('x','y','width','height')]
                    mask[y:y+h,x:x+w]=True
                    require(np.any(diff[y:y+h,x:x+w]), 'unchanged_artwork')
                outside=int(np.count_nonzero(diff & ~mask)); changed=int(diff.sum())
                require(outside==0, 'outside_artwork_change')
                if recipe['condition'] in ('busy','t2'):del groups[group]
            rows.append(dict(**recipe,imageSHA256=sha(png),sidecarSHA256=sha(ann),pixelSHA256=digest,
                             changedPixels=changed,outsideChanges=outside,elementCount=len(elements)))
    if split:
        roles={r['id']:r['dataRole'] for r in planned}
        require(all(len({roles[k] for k in members})==1 for members in pixel_hashes.values()), 'cross_role_pixels')
    return dict(schemaVersion='ios-artwork-validation-v2' if split else 'ios-artwork-validation-v1',frames=len(rows),captureSeconds=seconds,
        scenesPerCaptureHour=len(rows)*3600/seconds,rows=rows,
        duplicateGroups=[v for v in pixel_hashes.values() if len(v)>1],
        dataRole='recipe_bound' if split else 'development',ancestryGroups=sorted({a['ancestryGroup'] for a in assets.values()}),
        trainingAdmission='not_assessed',modelGate='not_assessed')


def evaluate(root, inputs, out):
    """One pinned reference, once per frame; existing exporter/scorer, no training."""
    import time
    import eval_run013 as e
    from dataclasses import replace
    root,inputs,out=Path(root),Path(inputs),Path(out)
    require(not out.exists(), 'output_collision')
    accepted=validate(root,inputs)
    require(accepted['dataRole']=='development','split_campaign_requires_assigned_evaluation')
    checkpoint=Path(__file__).resolve().parents[1]/'NativeUITrainer/yolo_runs/replay184-r022/weights/last.pt'
    checkpoint_hash='d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d'
    require(sha(checkpoint)==checkpoint_hash,'checkpoint')
    names=e.load_names(); out.mkdir(parents=True);(out/'images').mkdir();(out/'labels').mkdir()
    rows=[]
    for r in accepted['rows']:
        key=r['id']; source=root/(key+'.png');label=out/'labels'/(key+'.txt')
        shutil.copyfile(source,out/'images'/source.name)
        with label.open('x') as f:f.write(e.expected_label(document(root/(key+'.json')),names))
        rows.append(dict(imageID=key,imagePath='images/'+source.name,labelPath='labels/'+label.name,
                         imageSHA256=sha(source),labelSHA256=sha(label)))
    manifest=out/'manifest.json'
    write(manifest,dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='ios-artwork200-development',images=rows))
    settings=dict(e.PREDICTION_SETTINGS,imgsz=640)
    from eval_phase6a import DEGENERATE_POLICY
    settings['postprocessing']=DEGENERATE_POLICY
    write(out/'protocol.json',dict(checkpoint=str(checkpoint),checkpointSHA256=checkpoint_hash,
        manifestSHA256=sha(manifest),settings=settings,planSHA256=sha(inputs/'campaign.json'),
        dataRole='development',budget='96 images; one fixed model; no threshold tuning or training'))
    start=time.monotonic()
    e.export_predictions(manifest,checkpoint,out/'predictions.json','mps',imgsz=640,discard_degenerate=True)
    report(root,inputs,out,inference_seconds=time.monotonic()-start)


def report(root, inputs, out, inference_seconds=None):
    import eval_run013 as e
    from dataclasses import replace
    root,inputs,out=Path(root),Path(inputs),Path(out)
    require(not (out/'evaluation.json').exists(),'output_collision')
    accepted=validate(root,inputs);names=e.load_names()
    protocol=document(out/'protocol.json');manifest=out/'manifest.json'
    require(sha(manifest)==protocol['manifestSHA256'] and
            sha(inputs/'campaign.json')==protocol['planSHA256'], 'evaluation_binding')
    request=e.load_request(manifest,len(names))
    require({im.image_id:im.image_sha256 for im in request.images}==
            {r['id']:r['imageSHA256'] for r in accepted['rows']},'evaluation_membership')
    # Prediction payloads are larger than coordination metadata; retain the existing
    # evaluator's schema validation, with a separate finite read budget.
    require((out/'predictions.json').stat().st_size<=32*1024*1024,'prediction_budget')
    data=e.read(out/'predictions.json')
    e.validated_artifact(data,request,protocol['checkpointSHA256'],expected_settings=protocol['settings'])
    scores={}
    for layout,condition in itertools.product(('grid','detail'),('procedural','low','busy')):
        ids={r['id'] for r in accepted['rows'] if r['layout']==layout and r['condition']==condition}
        selected=replace(request,images=tuple(im for im in request.images if im.image_id in ids))
        scores[layout+'/'+condition]=e.score(e.subset(data,selected),selected,names)
    write(out/'evaluation.json',dict(inferenceSeconds=inference_seconds,scores=scores,
        predictionSHA256=sha(out/'predictions.json'),checkpointSHA256=protocol['checkpointSHA256'],
        productionEligible=False,interpretation='Matched development appearance sensitivity, not unseen-app evaluation; only two related artworks.'))


def review_sheet(root, out, selected=None):
    from PIL import ImageDraw
    root,out=Path(root),Path(out)
    require(not out.exists(),'output_collision')
    if selected is None:selected=[r for r in recipes() if r['seed']==200 and r['condition']=='busy']
    require(len(selected)==8,'review_sheet_count')
    canvas=Image.new('RGB',(4*354,2*800),'#222222')
    for index,r in enumerate(selected):
        with Image.open(root/(r['id']+'.png')) as original:im=original.convert('RGB')
        draw=ImageDraw.Draw(im)
        for e in document(root/(r['id']+'.json'))['elements']:
            x,y,w,h=[e['boundsPixels'][k] for k in ('x','y','width','height')]
            draw.rectangle((x,y,x+w,y+h),outline='red',width=3)
        im.thumbnail((354,767));x=(index%4)*354;y=(index//4)*800
        canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x+3,y+775),r['id'],fill='white')
    canvas.save(out)


def diagnose(out):
    """Case-linked best-candidate diagnostic; not a replacement for AP matching."""
    from collections import Counter, defaultdict
    import eval_run013 as e
    out=Path(out); require(not (out/'diagnosis.json').exists(),'output_collision')
    protocol=document(out/'protocol.json'); names=e.load_names()
    request=e.load_request(out/'manifest.json',len(names))
    require(sha(out/'manifest.json')==protocol['manifestSHA256'],'manifest_hash')
    require((out/'predictions.json').stat().st_size<=32*1024*1024,'prediction_budget')
    data=e.read(out/'predictions.json')
    e.validated_artifact(data,request,protocol['checkpointSHA256'],expected_settings=protocol['settings'])
    indexed={r['imageID']:r for r in data['results']};cases=[];counts=defaultdict(Counter)
    for im in request.images:
        for index,line in enumerate(im.label_path.read_text().splitlines()):
            cid,x,y,w,h=map(float,line.split());cid=int(cid)
            box=[(x-w/2)*im.width,(y-h/2)*im.height,(x+w/2)*im.width,(y+h/2)*im.height]
            candidates=[d for d in indexed[im.image_id]['detections'] if d['classID']==cid and e.iou_xyxy(box,d['xyxyPixels'])>=.5]
            confidence=max((d['score'] for d in candidates),default=0)
            state='operating_match' if confidence>=.25 else 'low_confidence' if candidates else 'no_exported_iou_match'
            group='/'.join([im.image_id.split('-')[0],im.image_id.split('-')[-1],names[cid]])
            counts[group][state]+=1
            cases.append(dict(imageID=im.image_id,labelIndex=index,category=names[cid],state=state,bestMatchingConfidence=confidence))
    write(out/'diagnosis.json',dict(groups=dict(counts),cases=cases,predictionSHA256=sha(out/'predictions.json'),
        limitations='Per-truth best-candidate diagnostic, not one-to-one AP. No exported match does not prove no internal model proposal. Two artworks, one subject family; no causal clutter claim.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    prep=sub.add_parser('prepare');prep.add_argument('source',type=Path);prep.add_argument('out',type=Path)
    val=sub.add_parser('validate');val.add_argument('root',type=Path);val.add_argument('inputs',type=Path);val.add_argument('out',type=Path)
    ev=sub.add_parser('evaluate');ev.add_argument('root',type=Path);ev.add_argument('inputs',type=Path);ev.add_argument('out',type=Path)
    rep=sub.add_parser('report');rep.add_argument('root',type=Path);rep.add_argument('inputs',type=Path);rep.add_argument('out',type=Path)
    rev=sub.add_parser('review');rev.add_argument('root',type=Path);rev.add_argument('out',type=Path)
    diag=sub.add_parser('diagnose');diag.add_argument('out',type=Path)
    a=p.parse_args()
    if a.cmd=='prepare':prepare(a.source,a.out)
    elif a.cmd=='validate':write(a.out,validate(a.root,a.inputs))
    elif a.cmd=='evaluate':evaluate(a.root,a.inputs,a.out)
    elif a.cmd=='report':report(a.root,a.inputs,a.out)
    elif a.cmd=='diagnose':diagnose(a.out)
    else:review_sheet(a.root,a.out)
