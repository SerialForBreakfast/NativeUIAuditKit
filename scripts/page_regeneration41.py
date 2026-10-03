"""Prepare exact old-member recipes and verify a new page-dot corpus patch."""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import shutil
from PIL import Image
import human_annotation_review as h

BASE=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
SOURCE=h.ROOT/'NativeUITrainer/reconstructed_corpora/ios-41class-r7-combined'


def prepare():
    planpath=h.ROOT/'reports/work/CONTROL-ELIGIBILITY-39/pages/regeneration-plan.json'
    plan=h.read(planpath);rows=[]
    for m in plan['members']:
        h.require(m['split']=='train' and m['family'] in ('MediaCardGrid','ProgressActivity'),'unexpected_member')
        rel=m['imageID'].replace('/images/','/');image=h.local(SOURCE/rel);ann=image.with_suffix('.json')
        h.require(h.sha(image)==m['imageSHA256'],'old_image_changed')
        a=h.read(ann);p=a['generatorProfile'];v=a['image']
        h.require(p['seed']==m['seed'] and p['templateFamily']==m['family'] and
            a['imageSHA256']==m['imageSHA256'],'old_recipe_mismatch')
        state={**p['simulatorState'],'cellularMode':'notSupported' if p['simulatorState']['cellularBars']==0 else 'active'}
        rows.append(dict(id=image.stem,family=m['family'],seed=m['seed'],width=m['width'],height=m['height'],
            scale=v['scale'],colorScheme=v['colorScheme'],dynamicTypeSize=v['dynamicTypeSize'],
            locale=v['locale'],layoutDirection=v['layoutDirection'],deviceName=v['deviceName'],
            simulatorState=state,accessibilityFlags={k:v.get(k,False) for k in
                ('reduceTransparency','increaseContrast','boldText','buttonShapes','onOffLabels','smartInvert','classicInvert')},
            oldImage=h.ref(image),oldAnnotation=h.ref(ann),oldLabelSHA256=m['labelSHA256']))
    h.require(len(rows)==666 and len({r['id'] for r in rows})==666,'membership_count')
    h.write(BASE/'page-recipes.json',dict(version='page-dot-regeneration-v1',members=rows,
        sourcePlan=h.ref(planpath),approvedBy='Maintainer approved tranche41',split='train'))
    print(h.sha(BASE/'page-recipes.json'))


def checked_annotation(recipe,image,ann):
    a=h.read(ann);meta=a['image'];scale=meta['scale']
    h.require(a['imageSHA256']==h.sha(image) and a['generatorProfile']['seed']==recipe['seed'] and
        a['generatorProfile']['templateFamily']==recipe['family'],'regenerated_identity')
    h.require(meta['pixelWidth']==recipe['width'] and meta['pixelHeight']==recipe['height'] and scale==recipe['scale'],
        'sidecar_dimensions')
    with Image.open(image) as im:
        h.require(im.format=='PNG' and im.size==(recipe['width'],recipe['height']),'regenerated_dimensions')
        pixel=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
    dots=[e for e in a['elements'] if e['id']=='pageControl_0']
    h.require(len(dots)==1,'page_dot_missing')
    box=dots[0]['boundsPoints'];h.require(any(abs(box['width']-w)<1 for w in (25,40,55,70)) and
        abs(box['height']-10)<1,'page_dot_not_intrinsic')
    h.require(box['x']>=0 and box['y']>=0 and (box['x']+box['width'])*scale<=recipe['width']+.5 and
        (box['y']+box['height'])*scale<=recipe['height']+.5,'page_dot_outside_image')
    h.require(len({e['id'] for e in a['elements']})==len(a['elements']),'duplicate_elements')
    for e in a['elements']:
        b=e['boundsPoints'];p=e['boundsPixels'];v=e['boundsVisionNormalized']
        h.require(all(math.isfinite(x) for rect in (b,p,v) for x in rect.values()),'nonfinite_bounds')
        h.require(all(abs(p[k]-b[k]*scale)<=.50001 for k in b),'pixel_coordinate_mismatch')
        h.require(all(0<=v[k]<=1 for k in v),'normalized_bounds')
        width=recipe['width']/scale;height=recipe['height']/scale
        left=max(0,min(width,b['x']));right=max(0,min(width,b['x']+b['width']))
        top=max(0,min(height,b['y']));bottom=max(0,min(height,b['y']+b['height']))
        expected=dict(x=left/width,y=1-bottom/height,width=max(0,right-left)/width,height=max(0,bottom-top)/height)
        h.require(all(abs(v[k]-expected[k])<1e-6 for k in v),'normalized_conversion_mismatch')
    return a,box,pixel


def verify(directory):
    root=h.local(directory);catalog=h.read(BASE/'page-recipes.json');receipt=h.read(root/'receipt.json')
    h.require(receipt['count']==666 and receipt['catalogSHA256']==h.sha(BASE/'page-recipes.json'),'capture_receipt')
    h.require(receipt['runtimeOS'] not in ('','unknown'),'missing_runtime')
    rows=[];pixels={};types=Counter()
    expected={'receipt.json'}
    for recipe in catalog['members']:
        image=root/(recipe['id']+'.png');ann=image.with_suffix('.json')
        a,box,pixel=checked_annotation(recipe,image,ann)
        expected.update((image.name,ann.name));pixels.setdefault(pixel,[]).append(recipe['id'])
        for e in a['elements']:types[e['elementType']]+=1
        rows.append(dict(id=recipe['id'],image=h.ref(image),annotation=h.ref(ann),dotBounds=box))
    h.require({p.name for p in root.iterdir()}==expected,'unexpected_corpus_files')
    h.write(BASE/'page-qa.json',dict(version='page-dot-regeneration-qa-v1',count=len(rows),split='train',
        runtimeOS=receipt['runtimeOS'],captureSeconds=receipt['seconds'],rows=rows,classSupport=dict(types),
        duplicateGroups=[v for v in pixels.values() if len(v)>1],
        note='New corpus patch, original evidence preserved; training export and validation coverage separate.'))
    print('Verified',len(rows),'new images and labels.')


def export(directory):
    source=Path(directory)
    h.require(source.is_absolute() and source.resolve()==source and source.name=='page-regeneration-41'
        and source.parent.name=='Documents' and 'CoreSimulator' in source.parts,'unexpected_simulator_export_root')
    rows=h.read(BASE/'page-recipes.json')['members']
    names=['receipt.json']+[r['id']+ext for r in rows for ext in ('.png','.json')]
    h.require({p.name for p in source.iterdir()}==set(names),'unexpected_export_files')
    paths=[source/name for name in names]
    h.require(all(p.is_file() and not p.is_symlink() for p in paths),'unsafe_export_member')
    size=sum(p.stat().st_size for p in paths)
    h.require(size<2*1024**3 and shutil.disk_usage(h.ROOT).free>size+5*1024**3,'export_space')
    target=BASE/'page-corpus';h.require(not target.exists(),'export_exists');target.mkdir()
    receipts=[]
    for path in paths:
        before=h.sha(path);dest=target/path.name;shutil.copyfile(path,dest)
        h.require(h.sha(dest)==before,'export_hash_mismatch');receipts.append(h.ref(dest))
    h.write(BASE/'page-export.json',dict(source=str(source),bytes=size,files=receipts))
    print('Exported',len(paths),'files;',size,'bytes.')


def stage_export():
    """Supply the existing exporter a split directory without copying pixels."""
    qa=h.read(BASE/'page-qa.json');root=h.ROOT/'.build/debug-output/page-dot-export-41'
    h.require(not root.exists(),'export_index_exists');(root/'train').mkdir(parents=True)
    for row in qa['rows']:
        for kind in ('image','annotation'):
            source=h.checked(h.ROOT,row[kind]);(root/'train'/source.name).symlink_to(source)
    print(root)


def checked_export_rows(recipes,rows):
    h.require(len(recipes)==len(rows)==666 and
        len({r['id'] for r in recipes})==666 and len({r['id'] for r in rows})==666,
        'export_membership_count')
    h.require([r['id'] for r in recipes]==[r['id'] for r in rows],'qa_recipe_order')
    return zip(recipes,rows)


def checked_export_labels(annotation,text,categories):
    from export_coco import DROP_TYPES,vision_to_yolo,element_type,bounds_vision
    expected=[]
    for element in annotation['elements']:
        kind=element_type(element);bounds=bounds_vision(element)
        if kind in DROP_TYPES or kind not in categories or not bounds:continue
        converted=vision_to_yolo(bounds)
        if converted is not None:
            expected.append(f"{categories[kind]} "+' '.join(f'{v:.6f}' for v in converted))
    h.require(text.splitlines()==expected,'export_labels_mismatch')


def verify_export(directory):
    from export_coco import load_category_map,CATEGORY_MAP,vision_to_yolo
    root=h.local(directory);categories,_=load_category_map(CATEGORY_MAP)
    recipes=h.read(BASE/'page-recipes.json')['members'];qa=h.read(BASE/'page-qa.json');rows=[]
    pairs=checked_export_rows(recipes,qa['rows'])
    expected_names={r['id'] for r in recipes}
    h.require({p.stem for p in (root/'train/labels').iterdir()}==expected_names and
        {p.stem for p in (root/'train/images').iterdir()}==expected_names,'export_files_mismatch')
    for recipe,row in pairs:
        h.require(recipe['id']==row['id'],'qa_recipe_order')
        path=root/'train/labels'/(row['id']+'.txt');lines=[line.split() for line in path.read_text().splitlines()]
        dots=[list(map(float,line[1:])) for line in lines if int(line[0])==categories['pageControl']]
        ann=h.read(h.checked(h.ROOT,row['annotation']))
        checked_export_labels(ann,path.read_text(),categories)
        expected=vision_to_yolo(next(e['boundsVisionNormalized'] for e in ann['elements'] if e['id']=='pageControl_0'))
        h.require(len(dots)==1 and max(abs(a-b) for a,b in zip(dots[0],expected))<=.00000051,'export_dot_mismatch')
        image=root/'train/images'/(row['id']+'.png')
        h.require(image.resolve()==h.checked(h.ROOT,row['image']),'export_image_changed')
        rows.append(dict(imageID='train/images/'+image.name,originalImage=recipe['oldImage'],
            originalLabelSHA256=recipe['oldLabelSHA256'],image=row['image'],annotation=row['annotation'],label=h.ref(path)))
    sources=[h.ref(p) for p in sorted((h.ROOT/'NativeUIDatasetGenerator').rglob('*.swift'))]
    sources.append(h.ref(h.ROOT/'GeneratorRunner/GeneratorRunnerTests/KitchenSinkValidationTest.swift'))
    result=dict(version='ios-page-dot-corpus-patch-v1',members=rows,
        split='train',runtimeOS=qa['runtimeOS'],count=666,sources=sources,
        categoryMap=h.ref(CATEGORY_MAP),exporter=h.ref(h.ROOT/'scripts/export_coco.py'),
        note='Verified replacement patch; old corpus and all evaluation membership remain unchanged.')
    destination=BASE/'page-corpus-patch.json'
    if destination.exists():h.require(h.read(destination)==result,'existing_patch_changed')
    else:h.write(destination,result)
    print('Verified666replacement YOLO labels using the existing exporter.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','verify','export','stage_export','verify_export']);p.add_argument('--directory')
    a=p.parse_args()
    if a.mode in ('prepare','stage_export'):globals()[a.mode]()
    else:globals()[a.mode](a.directory)
