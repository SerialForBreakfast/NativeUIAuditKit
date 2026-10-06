"""Immutable worker213 supplement; reuse resident512 inputs and initializer."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tarfile
from PIL import Image
from export_artwork204 import ROOT,BASE,PLAN,QUALIFIED,select
from artwork204_campaign import recipes
from artwork200_campaign import sha,write
from shared_transfer import document,require
from generator_asset_plan import inventory_metadata
import eval_run013 as evaluation


def slots(old,new):
    require(len(old)==len(set(old))==512 and len(new)==len(set(new))==60 and not set(old)&set(new),'slot_membership')
    ranked=sorted(old,key=lambda x:(hashlib.sha256(x.encode()).hexdigest(),x))
    return dict(control=old+ranked[:60],treatment=old+new)


def prepare(out):
    out=out.absolute();require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(),'output_collision_boundary')
    parent=ROOT/'reports/work/WORKER-198/artifacts/detector512-export01/payload'
    old=inventory_metadata(parent/'manifest.json')
    require(len(old['examples'])==512 and old['initializerSHA256']=='d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d','parent_identity')
    require(all(r['role']=='train' for r in old['examples']) and old['classNames']==evaluation.load_names(),'parent_roles_taxonomy')
    for ref in old['files']:
        path=parent/ref['path'];require(path.is_relative_to(parent) and path.resolve()==path and path.stat().st_size==ref['bytes'] and sha(path)==ref['sha256'],'parent_bytes')
    q=BASE/'native-qualified01.json';require(sha(q)==QUALIFIED and sha(BASE/'native-input01/campaign.json')==PLAN,'qualification_changed')
    admitted=document(q);train=select(admitted['rows']);frames=BASE/'native-execution01/frames'
    old_pixels={r['pixelSHA256'] for r in old['examples']};new_pixels=set();rows=[]
    for row in admitted['rows']:
        key=row['id'];png=frames/(key+'.png');ann=frames/(key+'.json')
        require(sha(png)==row['imageSHA256'] and sha(ann)==row['sidecarSHA256'],'native_bytes')
        with Image.open(png) as im:
            rgb=im.convert('RGB');pixel=hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
        require(pixel not in old_pixels|new_pixels,'pixel_overlap');new_pixels.add(pixel)
        rows.append(dict(id=key,image='images/'+key+'.png',label='labels/'+key+'.txt',
            role=row['dataRole'],family=row['family'],pixelSHA256=pixel,sourceImageSHA256=sha(png),sourceAnnotationSHA256=sha(ann)))
    require(shutil.disk_usage(ROOT).free>2*1024**3,'space')
    payload=out/'payload';(payload/'images').mkdir(parents=True);(payload/'labels').mkdir()
    names=evaluation.load_names()
    for row in rows:
        source=frames/(row['id']+'.png');shutil.copyfile(source,payload/row['image'])
        require(sha(payload/row['image'])==row['sourceImageSHA256'],'copy_changed')
        with (payload/row['label']).open('x') as f:f.write(evaluation.expected_label(document(frames/(row['id']+'.json')),names))
    manifest=dict(schemaVersion='worker213-native-artwork-v1',parentManifestSHA256=sha(parent/'manifest.json'),
        initializerSHA256=old['initializerSHA256'],qualificationSHA256=QUALIFIED,planSHA256=PLAN,
        examples=rows,classNames=names,slots=slots([r['id'] for r in old['examples']],[r['id'] for r in train]),
        runs=dict(control='029',treatment='030'),trainingRole='train only;test wire role is abstract diagnostic',
        configuration=dict(epochs=10,batch=4,nbs=64,imgsz=640,optimizer='AdamW',lr0=.0001,lrf=1.,warmup_epochs=0,seed=42,amp=False),
        expectedBatchesPerEpoch=143,expectedOptimizerUpdates=89,
        files=[dict(path=str(p.relative_to(payload)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(payload.rglob('*')) if p.is_file()])
    write(payload/'manifest.json',manifest)
    archive=out/'worker213-native-artwork01.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in sorted(payload.rglob('*')):
            if p.is_file():t.add(p,arcname=str(p.relative_to(payload)),recursive=False)
    with tarfile.open(archive) as t:
        members=t.getmembers();require(len(members)==193 and all(m.isfile() and m.size<=4*1024**2 for m in members) and sum(m.size for m in members)<200*1024**2,'archive_budget')
        for ref in manifest['files']:
            raw=t.extractfile(ref['path']).read();require(len(raw)==ref['bytes'] and hashlib.sha256(raw).hexdigest()==ref['sha256'],'archive_replay')
    tx=dict(requestID='nuiak-20261006-worker213-artwork',sharedPath='nuiak/'+archive.name,
            localPath=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=sha(archive))
    write(out/'transaction.json',tx);return tx


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('out',type=Path);print(prepare(p.parse_args().out))
