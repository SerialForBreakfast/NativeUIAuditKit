"""Frozen-label geometry and role audit; no inference, rendering or data mutation."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import artifact_storage
from prediction_artifact import _validate_label, canonical_sha256

ROOT=Path(__file__).resolve().parents[1]
TARGETS={'pageControl','scrollIndicator','imageView','listRow','toggle','secondaryButton','cancelAction'}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok,reason):
    if not ok:raise ValueError(reason)


def safe(root,relative):
    path=Path(relative)
    require(not path.is_absolute() and '..' not in path.parts and str(path)==relative,'member_path')
    return root/path


def geometry(values,width,height):
    require(len(values)==4 and width>0 and height>0 and all(np.isfinite(values)),'geometry')
    _,_,w,h=values
    require(0<w<=1 and 0<h<=1,'geometry_extent')
    pw,ph=w*width,h*height
    return [w,h,pw/ph,min(pw,ph)*640/max(width,height),min(pw,ph)*1280/max(width,height)]


def summarize(rows):
    values=np.asarray(rows,float)
    return dict(count=len(rows),columns=['widthFraction','heightFraction','aspectRatio','shortEdge640','shortEdge1280'],
                minimum=values.min(axis=0).tolist(),median=np.median(values,axis=0).tolist(),
                maximum=values.max(axis=0).tolist(),shortEdgeBelow3At640=int((values[:,3]<3).sum()))


def run(output):
    require(output.is_absolute() and output.is_relative_to(ROOT) and not output.exists(),'output_collision_or_boundary')
    started=time.monotonic();base=ROOT/'reports/work/IOS-R013-EVAL'
    freeze=json.loads((base/'freeze.json').read_text());preflight=base/'preflight.json'
    require(digest(preflight)==freeze['auditSHA256'],'preflight_changed')
    inventory=json.loads(preflight.read_text());members=inventory['members']
    require(inventory['integrityPassed'] and not inventory['errors'] and
            len(members)==inventory['memberCount']==19740 and canonical_sha256(members)==inventory['inventorySHA256'],'inventory')
    category=ROOT/'Research/schemas/category_map.json';require(digest(category)==freeze['categoryMapSHA256'],'category_changed')
    categories=json.loads(category.read_text())['categories'];names=[row['name'] for row in categories]
    require([row['id'] for row in categories]==list(range(41)),'category_ids')
    dataset=artifact_storage.resolve_input(Path(inventory['dataset']))
    source=artifact_storage.resolve_input(Path(inventory['source']))
    support={split:Counter() for split in ('train','val','test')};families=defaultdict(Counter)
    sizes=defaultdict(list);text=defaultdict(Counter);sidecars=0
    for i,row in enumerate(members):
        split,family=row['split'],row['family'];require(split in support,'split')
        label=safe(dataset,row['imageID'].replace('/images/','/labels/')).with_suffix('.txt')
        require(digest(label)==row['labelSHA256'],'label_changed')
        _validate_label(label,row['imageID'],41)
        records=[line.split() for line in label.read_text().splitlines() if line.strip()]
        require([int(v[0]) for v in records]==row['classes'],'class_inventory_changed')
        for values in records:
            name=names[int(values[0])];support[split][name]+=1;families[(split,family)][name]+=1
            if name in TARGETS:sizes[(split,family,name)].append(geometry(list(map(float,values[1:])),row['width'],row['height']))
        if any(names[n] in ('secondaryButton','cancelAction') for n in row['classes']):
            sidecar=safe(source,row['source']).with_suffix('.json');require(digest(sidecar)==row['sidecarSHA256'],'sidecar_changed')
            doc=json.loads(sidecar.read_text());sidecars+=1
            require(doc['generatorProfile']['templateFamily']==family,'sidecar_family')
            for el in doc['elements']:
                name=el.get('elementType')
                if name in ('secondaryButton','cancelAction') and not el.get('excluded',False):
                    value=el.get('visibleText')
                    text[(split,family,name)][value if isinstance(value,str) and value else '<not-recorded>']+=1
        if (i+1)%4000==0:print('verified',i+1,flush=True)
    observed={s:{n:support[s][n] for n in names} for s in support}
    require(observed==inventory['classSupport'],'support_changed')
    matrix={name:{split:dict(instances=support[split][name],families=sorted(f for (s,f),counts in families.items() if s==split and counts[name]))
                  for split in support} for name in names}
    sources=['CardDetailTemplate.swift','GalleryPageTemplate.swift','OnboardingPageTemplate.swift',
             'KitchenSinkTemplate.swift','UIKitGeneratorViewController.swift','RichContentFeedTemplate.swift']
    report=dict(version='ios-label-audit149-v1',sourceSHA256=digest(Path(__file__)),preflightSHA256=digest(preflight),
        labelsVerified=len(members),buttonSidecarsVerified=sidecars,coverage=matrix,
        geometry=[dict(split=s,family=f,category=n,**summarize(v)) for (s,f,n),v in sorted(sizes.items())],
        buttonText=[dict(split=s,family=f,category=n,counts=dict(v)) for (s,f,n),v in sorted(text.items())],
        currentGeneratorHashes={name:digest(ROOT/'NativeUIDatasetGenerator/Templates'/name) for name in sources},
        historicalRendererIdentityProven=False,pixelsRevalidated=False,inferenceRun=False,trainingRun=False,
        seconds=time.monotonic()-started)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as out:json.dump(report,out,indent=2,allow_nan=False)
    print('complete',report['labelsVerified'],'labels',sidecars,'sidecars',report['seconds'],'seconds',flush=True)


def current(output):
    require(output.is_absolute() and output.is_relative_to(ROOT) and not output.exists(),'output_collision_or_boundary')
    started=time.monotonic()
    baseline=ROOT/'reports/work/IOS-R013-EVAL/preflight.json'
    old=json.loads(baseline.read_text());freeze=json.loads((baseline.parent/'freeze.json').read_text())
    require(digest(baseline)==freeze['auditSHA256'],'preflight_changed')
    by={Path(row['imageID']).stem:row for row in old['members']}
    require(len(by)==19740,'duplicate_inventory')
    retained=ROOT/'reports/work/REAL-TRANSFER-42/ios-export-verified.json'
    lineage_path=retained.parent/'ios-lineage.json';lineage=json.loads(lineage_path.read_text())
    target=artifact_storage.resolve_input(ROOT/lineage['target']['path'])
    require(digest(target)==lineage['target']['sha256'],'current_manifest_changed')
    rows=json.loads(retained.read_text())['rows'];require(len(rows)==19740,'current_membership')
    sizes=defaultdict(list);changed=[];seen=set();evaluation=0
    for row in rows:
        logical=safe(ROOT,row['label']['path']);label=artifact_storage.resolve_input(logical)
        key=label.stem;require(key in by and key not in seen,'current_duplicate_or_unknown');seen.add(key)
        previous=by[key];require(row['split']==previous['split'],'current_split_changed')
        require(digest(label)==row['label']['sha256'],'current_label_changed')
        if row['split']!='train':
            require(row['label']['sha256']==previous['labelSHA256'],'evaluation_label_changed');evaluation+=1
        if row['label']['sha256']!=previous['labelSHA256']:changed.append(key)
        _validate_label(label,key,41)
        values=[line.split() for line in label.read_text().splitlines() if line.strip()]
        # Regeneration changes annotation ordering, not class-instance membership.
        require(Counter(int(v[0]) for v in values)==Counter(previous['classes']),'current_classes_changed')
        for v in values:
            if int(v[0])==18:sizes[(row['split'],previous['family'])].append(geometry(list(map(float,v[1:])),previous['width'],previous['height']))
    replaced={Path(row['name']).stem for row in lineage['rows'] if row['replaced']}
    require(set(changed)==replaced and len(changed)==666 and evaluation==5200,'repair_or_evaluation_membership')
    report=dict(version='ios-current149-v1',sourceSHA256=digest(Path(__file__)),oldInventorySHA256=digest(baseline),
        exportEvidenceSHA256=digest(retained),lineageSHA256=digest(lineage_path),labelsVerified=len(rows),
        repairedLabels=len(changed),unchangedEvaluationLabels=evaluation,
        pageControl=[dict(split=s,family=f,**summarize(v)) for (s,f),v in sorted(sizes.items())],
        pixelsRevalidated=False,inferenceRun=False,trainingRun=False,seconds=time.monotonic()-started)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as out:json.dump(report,out,indent=2,allow_nan=False)
    print(report,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--current',action='store_true');args=p.parse_args()
    (current if args.current else run)(args.output.absolute())
