"""Frozen native training repair: plan, verified retrieval, independent pixel audit."""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import numpy as np
from PIL import Image,ImageDraw
import artifact_storage as storage
import human_annotation_review as h
from compose155 import BASE as PROBES, TARGET, bounds
from page_regeneration41 import checked_annotation, checked_export_labels

BASE=h.ROOT/'reports/work/NATIVE-159/artifacts'
CATALOG=BASE/'catalog.json'


def check_measurement(actual, reported, scale):
    """Reuse context157's one-decoded-pixel independent measurement contract."""
    a=np.asarray(actual,dtype=float);b=np.asarray(reported,dtype=float)
    h.require(a.shape==b.shape==(4,) and scale in (2,3) and
        np.isfinite(a).all() and np.isfinite(b).all() and
        np.all(a[2:]>0) and np.all(b[2:]>0),'measurement_shape')
    edges=lambda x:np.array([x[0],x[1],x[0]+x[2],x[1]+x[3]])
    delta=(edges(a)-edges(b))*scale
    h.require(np.max(np.abs(delta))<=1+1e-6,'measurement_mismatch')
    return delta.tolist()


def members(doc):
    rows=doc['members']
    h.require(doc['version']=='native-page-repair-v1' and doc['target']==TARGET and doc['split']=='train', 'catalog_identity')
    h.require(len(rows)==900 and len({r['id'] for r in rows})==900 and
        Counter(r['family'] for r in rows)=={'UIKitControls':700,'KitchenSink':200}, 'catalog_membership')
    return rows


def prepare():
    audit=h.read(PROBES/'context157-audit/report.json')
    h.require(audit['complete'] and audit['accepted']==24,'native_qualification')
    original=h.read(PROBES/'page156-repair-inventory.json');rows=[]
    for m in original['members']:
        image=storage.resolve_input(h.ROOT/m['image']['path']);ann=image.with_suffix('.json')
        label=storage.resolve_input(h.ROOT/m['label']['path'])
        h.require(h.sha(image)==m['image']['sha256'] and h.sha(label)==m['label']['sha256'] and
            h.sha(ann)==m['annotationSHA256'],'changed_original')
        p=m['recipe'];v=m['imageConfiguration']
        rows.append(dict(id=m['id'],family=m['family'],seed=p['seed'],width=v['pixelWidth'],height=v['pixelHeight'],
            scale=v['scale'],colorScheme=v['colorScheme'],dynamicTypeSize=v['dynamicTypeSize'],locale=v['locale'],
            layoutDirection=v['layoutDirection'],deviceName=v['deviceName'],
            simulatorState={**p['simulatorState'],'cellularMode':'notSupported' if p['simulatorState']['cellularBars']==0 else 'active'},
            accessibilityFlags={k:v.get(k,False) for k in ('reduceTransparency','increaseContrast','boldText','buttonShapes','onOffLabels','smartInvert','classicInvert')},
            original=m))
    sources=[h.ref(p) for root in ('NativeUIDatasetGenerator','GeneratorRunner/GeneratorRunnerTests')
        for p in sorted((h.ROOT/root).rglob('*.swift'))]
    doc=dict(version='native-page-repair-v1',target=TARGET,split='train',members=rows,sources=sources,
        qualification=h.ref(PROBES/'context157-audit/report.json'))
    members(doc);BASE.mkdir(parents=True,exist_ok=True);h.require(not CATALOG.exists(),'catalog_collision')
    h.write(CATALOG,doc);print(h.sha(CATALOG))


def preflight():
    doc=h.read(CATALOG);members(doc)
    for ref in doc['sources']:h.checked(h.ROOT,ref)
    h.checked(h.ROOT,doc['qualification'])
    h.require(shutil.disk_usage(h.ROOT).free>6*1024**3,'insufficient_space')
    print('preflight verified sources, qualification, catalog',h.sha(CATALOG))


def retrieve(path):
    source=Path(path)
    h.require(source.is_absolute() and source.resolve()==source and source.name=='native-page159' and
        source.parent.name=='Documents' and TARGET in source.parts and 'CoreSimulator' in source.parts,'source_path')
    names={'receipt.json'}|{r['id']+s for r in members(h.read(CATALOG)) for s in ('.png','-hidden.png','.json')}
    h.require({p.name for p in source.iterdir()}==names,'capture_membership')
    paths=[source/name for name in sorted(names)]
    h.require(all(p.is_file() and not p.is_symlink() for p in paths),'unsafe_file')
    size=sum(p.stat().st_size for p in paths)
    h.require(size<2*1024**3 and shutil.disk_usage(h.ROOT).free>size+5*1024**3,'retrieval_space')
    out=BASE/'capture';out.mkdir();copied=[]
    for p in paths:
        sha=h.sha(p);dest=out/p.name;shutil.copyfile(p,dest)
        h.require(h.sha(dest)==sha,'copy_hash');copied.append(h.ref(dest))
    h.write(BASE/'retrieval.json',dict(source=str(source),bytes=size,files=copied))
    print('retrieved',len(paths),'files',size,'bytes')


def audit():
    import validate_reconstructed_corpus as validator
    schema=validator.read_json(validator.SCHEMA)
    doc=h.read(CATALOG);recipes=members(doc);root=BASE/'capture';receipt=h.read(root/'receipt.json')
    h.require(receipt['version']=='native-page-repair-receipt-v1' and receipt['target']==TARGET and
        receipt['catalogSHA256']==h.sha(CATALOG),'receipt_identity')
    rows=receipt['rows'];h.require([r['id'] for r in rows]==[r['id'] for r in recipes],'receipt_membership')
    seen={};duplicates=[];verified=[];counts=Counter()
    for recipe,row in zip(recipes,rows):
        arrays=[]
        for suffix,key in [('', 'sha256'),('-hidden','hiddenSHA256')]:
            p=root/(row['id']+suffix+'.png');h.require(h.sha(p)==row[key],'capture_hash')
            with Image.open(p) as im:
                h.require(im.format=='PNG' and im.size==(recipe['width'],recipe['height']),'dimensions')
                arrays.append(np.array(im.convert('RGB')))
        h.require(row['scale']==recipe['scale'],'scale')
        measured=bounds(*arrays,row['frame'],row['scale'])
        delta=check_measurement(measured,row['body'],row['scale'])
        image=root/(row['id']+'.png');ann=image.with_suffix('.json')
        a,body,pixel=checked_annotation(recipe,image,ann,native_body=row['body'])
        validator.check_schema(a,schema,schema)
        if pixel in seen:duplicates.append([seen[pixel],row['id']])
        seen[pixel]=row['id'];counts.update(e['elementType'] for e in a['elements'])
        compatible_pixel=hashlib.sha256(str((recipe['width'],recipe['height'])).encode()+arrays[0].tobytes()).hexdigest()
        verified.append(dict(id=row['id'],image=h.ref(image),annotation=h.ref(ann),hidden=h.ref(root/(row['id']+'-hidden.png')),
            decodedSHA256=pixel,pixelSHA256=compatible_pixel,body=body,family=recipe['family'],
            independentBody=measured,edgeDeltaPixels=delta))
    h.write(BASE/'audit.json',dict(version='native-repair-audit-v1',rows=verified,count=len(verified),
        duplicates=duplicates,classSupport=dict(counts),catalog=h.ref(CATALOG),receipt=h.ref(root/'receipt.json'),
        role='training-patch-pending-full-corpus-audit',eligible=not duplicates))
    examples=[]
    for family in ('UIKitControls','KitchenSink'):
        for scale in (2,3):
            candidates=[(recipe,row) for recipe,row in zip(recipes,verified) if recipe['family']==family and recipe['scale']==scale]
            for index in (0,len(candidates)//2,len(candidates)-1):
                recipe,row=candidates[index];im=Image.open(h.checked(h.ROOT,row['image'])).convert('RGB')
                b=row['body'];x,y,w,ht=[b[k]*scale for k in ('x','y','width','height')]
                top=max(0,int(y-35*scale));bottom=min(im.height,int(y+ht+35*scale))
                strip=im.crop((0,top,im.width,bottom));d=ImageDraw.Draw(strip)
                d.rectangle((x,y-top,x+w,y+ht-top),outline='red',width=2)
                strip.thumbnail((400,160));examples.append((f"{family} {row['id']} scale{scale}",strip))
    preview=Image.new('RGB',(800,6*190),'#888888');d=ImageDraw.Draw(preview)
    for i,(name,im) in enumerate(examples):
        x=i%2*400;y=i//2*190;preview.paste(im,(x,y));d.text((x,y+165),name,fill='white')
    preview.save(BASE/'representatives.png')
    print('audited',len(verified),'duplicates',len(duplicates))


def stage():
    audit=h.read(BASE/'audit.json');h.require(audit['eligible'] and audit['count']==900,'patch_not_eligible')
    root=BASE/'export-input';root.mkdir();(root/'train').mkdir()
    for row in audit['rows']:
        for key in ('image','annotation'):
            source=h.checked(h.ROOT,row[key]);(root/'train'/source.name).symlink_to(source)
    print(root)


def overlay():
    """Verify selected bytes, reuse hash-bound old decoded-pixel audit; never mutate r8."""
    from export_coco import load_category_map,CATEGORY_MAP
    categories,names=load_category_map(CATEGORY_MAP)
    audit=h.read(BASE/'audit.json');h.require(audit['eligible'] and audit['count']==900,'patch_not_eligible')
    h.checked(h.ROOT,audit['catalog']);h.checked(h.ROOT,audit['receipt'])
    recipes={r['id']:r for r in members(h.read(CATALOG))};patch={r['id']:r for r in audit['rows']}
    h.require(len(patch)==900 and set(patch)==set(recipes),'patch_membership')
    export=BASE/'yolo';h.require({p.stem for p in (export/'train/images').iterdir()}==set(patch) and
        {p.stem for p in (export/'train/labels').iterdir()}==set(patch),'patch_export_membership')
    oldbase=h.ROOT/'reports/work/REAL-TRANSFER-42'
    oldaudit=h.read(oldbase/'ios-audit.json',64*1024**2);oldexport=h.read(oldbase/'ios-export-verified.json',64*1024**2)
    h.require(not oldaudit['duplicateGroups'] and not oldaudit['crossSplitGroups'],'old_corpus_duplicates')
    h.checked(h.ROOT,oldaudit['manifest'],64*1024**2)
    h.require(len(oldaudit['rows'])==len(oldexport['rows'])==19740,'old_membership')
    rows=[];seen={};duplicates=[];paths={'train':[],'val':[],'test':[]}
    for i,(old,exp) in enumerate(zip(oldaudit['rows'],oldexport['rows'])):
        split='val' if old['split']=='validation' else old['split'];name=Path(old['name']).name;stem=Path(name).stem
        h.require(exp['split']==split and Path(exp['image']['path']).name==name,'old_order')
        oldimage=h.checked(h.ROOT,exp['image']);oldlabel=h.checked(h.ROOT,exp['label'])
        h.require(h.sha(oldimage.with_suffix('.json'))==old['annotationSHA256'] and
            exp['image']['sha256']==old['imageSHA256'],'old_evidence_binding')
        changed=stem in patch
        if changed:
            h.require(split=='train' and old['family']==recipes[stem]['family'] and
                recipes[stem]['original']['image']==exp['image'],'replacement_scope')
            new=patch[stem];image=h.checked(h.ROOT,new['image']);ann=h.checked(h.ROOT,new['annotation'])
            label=export/'train/labels'/(stem+'.txt');yoloimage=export/'train/images'/name
            checked_export_labels(h.read(ann),label.read_text(),categories)
            pixel=new['pixelSHA256'];image_ref=new['image'];label_ref=h.ref(label);ann_ref=new['annotation']
        else:
            image=oldimage;label=oldlabel;pixel=old['pixelSHA256'];image_ref=exp['image'];label_ref=exp['label']
            ann_ref=dict(path=str(Path(exp['image']['path']).with_suffix('.json')),sha256=old['annotationSHA256'])
            yoloimage=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r8'/split/'images'/name
        h.require(yoloimage.resolve()==image and label.is_file(),'yolo_path_binding')
        key=split+'/'+name
        if pixel in seen:duplicates.append([seen[pixel],key])
        seen[pixel]=key;paths[split].append(str(yoloimage))
        rows.append(dict(id=key,split=split,family=old['family'],replaced=changed,image=image_ref,
            annotation=ann_ref,label=label_ref,pixelSHA256=pixel))
        if i%2000==0:print('overlay verified',i+1,'/19740',flush=True)
    manualpatch=h.read(h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/page-corpus-patch.json',16*1024**2)
    manualids={Path(r['imageID']).stem for r in manualpatch['members']}
    preserved=[r for r in rows if Path(r['id']).stem in manualids and r['split']=='train' and not r['replaced']]
    h.require(len(manualids)==len(preserved)==666,'manual_patch_changed')
    original_manual={Path(r['imageID']).stem:r for r in manualpatch['members']}
    for row in preserved:
        original=original_manual[Path(row['id']).stem]
        h.require(row['image']['sha256']==original['image']['sha256'] and
            row['annotation']['sha256']==original['annotation']['sha256'] and
            row['label']['sha256']==original['label']['sha256'],'manual_patch_bytes_changed')
    h.require(Counter(r['split'] for r in rows)=={'train':14540,'val':2800,'test':2400} and
        sum(r['replaced'] for r in rows)==900 and not duplicates,'overlay_membership_or_leakage')
    dest=BASE/'overlay';dest.mkdir()
    for split,lines in paths.items():
        with (dest/(split+'.txt')).open('x') as f:f.write('\n'.join(lines)+'\n')
    import yaml
    with (dest/'data.yaml').open('x') as f:yaml.safe_dump(dict(path=str(dest),train='train.txt',val='val.txt',test='test.txt',names=names),f)
    h.write(dest/'manifest.json',dict(version='ios-native-page-overlay-v1',rows=rows,count=len(rows),
        sources=[h.ref(BASE/'audit.json'),h.ref(oldbase/'ios-audit.json'),h.ref(oldbase/'ios-export-verified.json')],
        replaced=900,manualPreserved=666,evaluationPreserved=5200,duplicates=duplicates,
        note='Training-only native patch; recipe ancestry and evaluation roles unchanged; model gates unassessed.'))
    print('verified complete19740overlay;900replaced;5200evaluation/666manual preserved')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','preflight','retrieve','audit','stage','overlay']);p.add_argument('--source')
    args=p.parse_args()
    if args.mode=='retrieve':retrieve(args.source)
    else:globals()[args.mode]()
