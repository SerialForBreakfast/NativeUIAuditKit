"""Export only admitted ARTWORK204 training frames through the existing exporter."""
import argparse
from pathlib import Path
import subprocess
import sys
from artwork200_campaign import sha, write
from artwork204_campaign import recipes
from shared_transfer import document, require
from export_coco import load_category_map, CATEGORY_MAP
from page_regeneration41 import checked_export_labels

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/ARTWORK-204/artifacts'
PLAN='78b2ee5dbd0e55766f413ae8a54e16f4052ccea656ad09b03889c9f9c5843b89'
QUALIFIED='f80282bc0a3103313ba6842c48b81e340cd2c17c1763211ec143a74b907c45fe'


def select(rows):
    expected=recipes()
    require(len(rows)==96 and all({k:r.get(k) for k in e}==e for r,e in zip(rows,expected)), 'qualified_membership')
    selected=[r for r in rows if r['dataRole']=='train']
    require(len(selected)==60 and len({r['id'] for r in selected})==60,'training_membership')
    return selected


def export(out):
    out=out.absolute()
    require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(),'output_collision_or_boundary')
    qualification=BASE/'native-qualified01.json';plan=BASE/'native-input01/campaign.json'
    require(sha(qualification)==QUALIFIED and sha(plan)==PLAN,'admission_changed')
    doc=document(qualification);rows=select(doc['rows']);frames=BASE/'native-execution01/frames'
    for row in doc['rows']:
        require(sha(frames/(row['id']+'.png'))==row['imageSHA256'] and
                sha(frames/(row['id']+'.json'))==row['sidecarSHA256'],'source_changed')
    stage=out/'source/train';stage.mkdir(parents=True)
    for row in rows:
        for suffix in ('.png','.json'):
            (stage/(row['id']+suffix)).symlink_to(frames/(row['id']+suffix))
    destination=out/'dataset'
    command=[sys.executable,str(ROOT/'scripts/export_coco.py'),'--dataset',str(stage.parent),'--output',str(destination)]
    with (out/'export.log').open('x') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    require(result.returncode==0,'export_failed')
    names,_=load_category_map(CATEGORY_MAP)
    require(len(names)==41,'taxonomy_changed')
    for split in ('val','test'):
        require(not list((destination/split/'images').iterdir()) and not list((destination/split/'labels').iterdir()),'role_drift')
    require({p.stem for p in (destination/'train/labels').iterdir()}=={r['id'] for r in rows},'export_membership')
    entries=[];count=0
    for row in rows:
        image=destination/'train/images'/(row['id']+'.png');label=destination/'train/labels'/(row['id']+'.txt')
        annotation=frames/(row['id']+'.json')
        require(sha(image)==row['imageSHA256'],'changed_pixels')
        checked_export_labels(document(annotation),label.read_text(),names)
        count+=len(label.read_text().splitlines())
        entries.append(dict(id=row['id'],role='train',family=row['family'],
            image=dict(path=str(image.relative_to(ROOT)),sha256=sha(image)),
            label=dict(path=str(label.relative_to(ROOT)),sha256=sha(label)),
            annotation=dict(path=str(annotation.relative_to(ROOT)),sha256=sha(annotation))))
    write(out/'membership.json',dict(schemaVersion='artwork204-training-export-v1',rows=entries,
        qualificationSHA256=QUALIFIED,planSHA256=PLAN,classMapSHA256=sha(CATEGORY_MAP),
        sourceSHA256=sha(__file__),exporterSHA256=sha(ROOT/'scripts/export_coco.py'),
        annotations=count,excludedValidation=24,excludedDiagnostic=12,trainingLaunched=False))
    return dict(images=len(entries),annotations=count)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    print(export(p.parse_args().output))
