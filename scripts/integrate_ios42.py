"""Link the approved page-dot replacements into a new complete iOS corpus."""
import argparse
from collections import Counter,defaultdict
import os
from pathlib import Path
import time
import human_annotation_review as h
import validate_reconstructed_corpus as v
from export_coco import load_category_map,CATEGORY_MAP,vision_to_yolo,DROP_TYPES

BASE=h.ROOT/'reports/work/REAL-TRANSFER-42'
SOURCE=h.ROOT/'NativeUITrainer/reconstructed_corpora/ios-41class-r7-combined'
TARGET=h.ROOT/'NativeUITrainer/reconstructed_corpora/ios-41class-r8-page-dot'
PATCH=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/page-corpus-patch.json'
OLD_YOLO=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r7'
NEW_YOLO=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r8'
EXPECTED={'train':14540,'validation':2800,'test':2400}


def replacement_map(entries,patch):
    names=[e['fileName'] for e in entries]
    h.require(len(names)==len(set(names)),'duplicate_source_member')
    rows=patch['members'];mapped={}
    h.require(patch['version']=='ios-page-dot-corpus-patch-v1' and patch['split']=='train' and
        len(rows)==patch['count']==666,'patch_membership_count')
    for row in rows:
        name=row['imageID'].replace('/images/','/')
        h.require(name.startswith('train/') and name in names and name not in mapped,'invalid_patch_member')
        mapped[name]=row
    return mapped


def assemble():
    manifest=h.read(SOURCE/'manifest.json',64*1024**2);patch=h.read(PATCH,16*1024**2)
    replacements=replacement_map(manifest['entries'],patch)
    h.require(Counter(e['split'] for e in manifest['entries'])==EXPECTED,'changed_source_splits')
    for source in patch['sources']+[patch['categoryMap'],patch['exporter']]:h.checked(h.ROOT,source)
    h.require(TARGET.resolve()==TARGET and TARGET.is_relative_to(h.ROOT/'NativeUITrainer/reconstructed_corpora')
        and not TARGET.exists(),'new_corpus_destination_required');TARGET.mkdir(parents=True)
    for split in EXPECTED:(TARGET/split).mkdir()
    entries=[];lineage=[];started=time.monotonic()
    for e in manifest['entries']:
        name=e['fileName'];old=SOURCE/name;old_ann=old.with_suffix('.json')
        h.require(old.resolve()==old and old_ann.resolve()==old_ann and h.sha(old)==e['sha256'],'changed_source_image')
        current=dict(e);image=old;annotation=old_ann
        if name in replacements:
            row=replacements[name]
            h.require(h.checked(h.ROOT,row['originalImage'])==old,'wrong_replacement_source')
            image=h.checked(h.ROOT,row['image']);annotation=h.checked(h.ROOT,row['annotation'])
            h.checked(h.ROOT,row['label'])
            label=OLD_YOLO/row['imageID'].replace('/images/','/labels/').replace('.png','.txt')
            h.require(h.sha(label)==row['originalLabelSHA256'],'changed_original_label')
            current['sha256']=row['image']['sha256']
            current['priorGenerationDate']=current.pop('generationDate',None)
            current['regenerationEvidence']=h.ref(PATCH)
        destination=TARGET/name
        os.link(image,destination);os.link(annotation,destination.with_suffix('.json'))
        lineage.append(dict(name=name,split=e['split'],replaced=name in replacements,
            originalImage=h.ref(old),originalAnnotation=h.ref(old_ann),
            selectedImage=h.ref(image),selectedAnnotation=h.ref(annotation)))
        entries.append(current)
    h.write(TARGET/'manifest.json',dict(version='1.0',datasetVersion='ios-41class-r8-page-dot',
        imageCount=len(entries),entries=entries,parent=h.ref(SOURCE/'manifest.json'),patch=h.ref(PATCH)))
    h.write(BASE/'ios-lineage.json',dict(source=h.ref(SOURCE/'manifest.json'),patch=h.ref(PATCH),
        target=h.ref(TARGET/'manifest.json'),rows=lineage,seconds=time.monotonic()-started,
        pixelCopyBytes=0,note='Hard-linked immutable inputs; source and new view must not be edited in place.'))
    print('Linked',len(entries),'members; zero pixel-copy bytes.',flush=True)


def audit():
    manifest=h.read(TARGET/'manifest.json',64*1024**2);lineage=h.read(BASE/'ios-lineage.json',64*1024**2)
    h.require(h.ref(TARGET/'manifest.json')==lineage['target'],'changed_target_manifest')
    h.require(h.ref(SOURCE/'manifest.json')==lineage['source'],'changed_source_manifest')
    h.require(len(manifest['entries'])==len(lineage['rows'])==19740 and
        len({e['fileName'] for e in manifest['entries']})==19740 and
        Counter(e['split'] for e in manifest['entries'])==EXPECTED,'changed_audit_membership')
    schema=v.read_json(v.SCHEMA);pixels=defaultdict(list);rows=[];coverage=defaultdict(Counter)
    started=time.monotonic()
    for i,(e,l) in enumerate(zip(manifest['entries'],lineage['rows'])):
        h.require(e['fileName']==l['name'] and e['split']==l['split'],'membership_changed')
        info,classes,meta,warnings=v.inspect_pair(TARGET,e,schema)
        h.require(info['imageSHA256']==l['selectedImage']['sha256'] and
            info['annotationSHA256']==l['selectedAnnotation']['sha256'],'selected_bytes_changed')
        if not l['replaced']:
            h.require(info['imageSHA256']==l['originalImage']['sha256'] and
                info['annotationSHA256']==l['originalAnnotation']['sha256'],'unchanged_member_changed')
        pixels[info['pixelSHA256']].append(e['fileName'])
        coverage[e['split']].update(info['visibleClassCounts'])
        rows.append(dict(name=e['fileName'],family=e['templateFamily'],split=e['split'],**info))
        if i%2000==0:print('Audited',i+1,'/',len(manifest['entries']),flush=True)
    h.require(len(rows)==len(lineage['rows'])==19740,'incomplete_audit')
    duplicates=[m for m in pixels.values() if len(m)>1]
    report=dict(rows=rows,visibleClassSupport=dict(coverage),duplicateGroups=duplicates,
        crossSplitGroups=[m for m in duplicates if len({Path(n).parts[0] for n in m})>1],
        seconds=time.monotonic()-started,manifest=h.ref(TARGET/'manifest.json'),
        validator=h.ref(Path(v.__file__)),schema=h.ref(v.SCHEMA))
    h.write(BASE/'ios-audit.json',report)
    h.require(not duplicates,'duplicate_pixels_require_review')
    print('Audit passed',len(rows),dict(coverage),flush=True)


def verify_export():
    audit=h.read(BASE/'ios-audit.json',64*1024**2);lineage=h.read(BASE/'ios-lineage.json',64*1024**2)
    h.require(not audit['duplicateGroups'],'unqualified_corpus')
    categories,_=load_category_map(CATEGORY_MAP);rows=[];changes=[]
    for row,l in zip(audit['rows'],lineage['rows']):
        h.require(row['name']==l['name'],'lineage_order')
        split='val' if row['split']=='validation' else row['split'];name=Path(row['name']).name
        image=NEW_YOLO/split/'images'/name;label=NEW_YOLO/split/'labels'/Path(name).with_suffix('.txt')
        h.require(image.resolve()==TARGET/row['name'] and h.sha(image)==row['imageSHA256'],'export_image_changed')
        ann=h.read(TARGET/Path(row['name']).with_suffix('.json'));expected=[]
        for e in ann['elements']:
            kind=e['elementType'];box=vision_to_yolo(e['boundsVisionNormalized'])
            if kind in categories and kind not in DROP_TYPES and box is not None:
                expected.append(str(categories[kind])+' '+' '.join(f'{n:.6f}' for n in box))
        h.require(label.read_text().splitlines()==expected,'export_label_changed')
        oldlabel=OLD_YOLO/split/'labels'/label.name
        same=h.sha(oldlabel)==h.sha(label)
        if not l['replaced']:h.require(same,'unchanged_export_label_changed')
        else:changes.append(dict(name=row['name'],sameLabels=same,
            samePixels=l['originalImage']['sha256']==l['selectedImage']['sha256']))
        rows.append(dict(image=h.ref(image),label=h.ref(label),split=split))
    h.require(len(rows)==19740 and len(changes)==666,'export_membership_count')
    for split,count in [('train',14540),('val',2800),('test',2400)]:
        h.require(len(list((NEW_YOLO/split/'images').iterdir()))==count and
            len(list((NEW_YOLO/split/'labels').iterdir()))==count,'unexpected_export_member')
    h.write(BASE/'ios-export-verified.json',dict(rows=rows,changes=changes,counts=EXPECTED,
        yaml=h.ref(NEW_YOLO/'dataset.yaml'),exporter=h.ref(h.ROOT/'scripts/export_coco.py'),
        remainingValidationGap='Zero pageControl validation examples; reserve new development coverage before selecting page-control hyperparameters.'))
    print('Verified full19740-member export and unchanged evaluation labels.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['assemble','audit','verify_export']);globals()[p.parse_args().mode]()
