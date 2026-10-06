"""Audit admitted replay and export only missing worker inputs; never train."""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import tarfile
from PIL import Image
import roi_style210 as source
from prepare_worker198 import pixel_sha, PIXEL_ENCODING
from evaluate_artwork213 import checked_requests, PAYLOAD, PIN
from generator_asset_plan import inventory_metadata
from artwork200_campaign import sha, write
from shared_transfer import require

ROOT = source.h.ROOT
PARENT = ROOT/'reports/work/WORKER-198/artifacts/detector512-export01/payload'
PARENT_PIN = '0ef6e17a6113e9449a45a889502bb731e24160220949eee966cf1a7908f79040'
SOURCE_PIN = 'ef5592873f5c2f17acc557d8b7114e2cb8d2b1f8e1c23c051adcad54633db3f1'
LIMITS = dict(maxMembers=2100, maxExpandedBytes=512*1024**2, maxMemberBytes=16*1024**2)


def slot_plan(old, native):
    require(len(old)==len(set(old))==1509 and len(native)==len(set(native))==60
            and not set(old)&set(native), 'slot_membership')
    repeats=sorted(old,key=lambda key:(hashlib.sha256(key.encode()).hexdigest(),key))[:60]
    return dict(control=old+repeats,treatment=old+native)


def resident_match(row, image, refs):
    require(row['role']=='train' and refs[row['image']]['sha256']==image.image_sha256
            and refs[row['label']]['sha256']==image.label_sha256,'resident_changed')


def check_pixels(pixels, reserved):
    require(len(pixels)==len(set(pixels)), 'duplicate_pixels')
    require(not set(pixels)&set(reserved), 'reserved_overlap')


def check_archive(members):
    require(len(members)<=LIMITS['maxMembers'] and all(m.isfile() and 0<=m.size<=LIMITS['maxMemberBytes'] for m in members)
            and sum(m.size for m in members)<=LIMITS['maxExpandedBytes'],'archive_budget')


def prepare(out):
    out=out.absolute()
    require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(),'output_boundary_collision')
    require(shutil.disk_usage(ROOT).free>3*1024**3,'space')
    comparison=source.OUT/'comparison.json'
    require(sha(comparison)==SOURCE_PIN and sha(PARENT/'manifest.json')==PARENT_PIN and sha(PAYLOAD/'manifest.json')==PIN,'source_changed')
    doc=source.p.sealed(comparison)
    old=source.p.sealed(source.h.checked(ROOT,doc['oldProposal']))
    require(doc['role']=='train' and old['configurationReady'] and old['runID']=='026','admission')
    for ref in [doc['admission'],doc['source'],doc['initializer']]:
        source.h.checked(ROOT,ref,256*1024**2)
    images=[]
    for key in ('oldMembership','cropMembership'):
        images.extend(source.e.load_request(source.h.checked(ROOT,doc[key]),41).images)
    require(len(images)==1509 and len({i.image_id for i in images})==1509,'membership')
    lineage={r['id']:r for r in old['rows']+doc['lineage']}
    require(len(lineage)==1509 and set(lineage)=={i.image_id for i in images},'lineage')
    parent=inventory_metadata(PARENT/'manifest.json'); supplement=inventory_metadata(PAYLOAD/'manifest.json')
    require(parent['classNames']==supplement['classNames']==source.e.load_names(),'taxonomy')
    require(parent['initializerSHA256']==doc['initializer']['sha256']==supplement['initializerSHA256'],'initializer')
    for root,manifest in [(PARENT,parent),(PAYLOAD,supplement)]:
        for ref in manifest['files']:
            path=root/ref['path']
            require(path.resolve()==path and path.is_relative_to(root) and path.stat().st_size==ref['bytes'] and sha(path)==ref['sha256'],'resident_bytes')
    resident={r['id']:r for r in parent['examples']};refs={r['path']:r for r in parent['files']}
    require(len(resident)==512 and set(resident)<={i.image_id for i in images},'resident_membership')
    evaluation=checked_requests(ROOT/'reports/work/ARTWORK-204/artifacts/evaluation213-input01')
    reserved=[];fit_pixels=[]
    for key in ('native','fit','page','combined'):
        for image in evaluation[key].images:
            with Image.open(image.image_path) as im:
                (fit_pixels if key=='fit' else reserved).append(pixel_sha(im))
    native=[r for r in supplement['examples'] if r['role']=='train']
    pixels=[];rows=[];support={'resident512':Counter(),'full1509':Counter()}
    for image in images:
        with Image.open(image.image_path) as im:
            pixel=pixel_sha(im)
            legacy=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
        require(legacy==lineage[image.image_id]['pixelSHA256'],'lineage_pixels')
        pixels.append(pixel)
        if image.image_id in resident:resident_match(resident[image.image_id],image,refs)
        for line in image.label_path.read_text().splitlines():
            category=int(line.split()[0]);support['full1509'][category]+=1
            if image.image_id in resident:support['resident512'][category]+=1
        rows.append(dict(id=image.image_id,role='train',pixelSHA256=pixel,
                         imageSHA256=image.image_sha256,labelSHA256=image.label_sha256,
                         lineage={k:lineage[image.image_id][k] for k in ('parent','group','window')},
                         storage='resident198' if image.image_id in resident else 'supplement216'))
    check_pixels(pixels+[r['pixelSHA256'] for r in native],reserved)
    plan=slot_plan([i.image_id for i in images],[r['id'] for r in native])
    payload=out/'payload';(payload/'images').mkdir(parents=True);(payload/'labels').mkdir()
    for n,(row,image) in enumerate(zip(rows,images)):
        if row['storage']=='resident198':
            row.update(image=resident[row['id']]['image'],label=resident[row['id']]['label'])
            continue
        for kind,src in [('image',image.image_path),('label',image.label_path)]:
            rel=f'{kind}s/{n:04d}'+('.png' if kind=='image' else '.txt')
            shutil.copyfile(src,payload/rel)
            require(sha(payload/rel)==row[kind+'SHA256'],'copy_changed');row[kind]=rel
    manifest=dict(schemaVersion='worker216-replay-v1',parentManifestSHA256=PARENT_PIN,
        nativeManifestSHA256=PIN,sourceComparisonSHA256=SOURCE_PIN,initializerSHA256=parent['initializerSHA256'],
        classNames=parent['classNames'],pixelHashEncoding=PIXEL_ENCODING,extractionLimits=LIMITS,
        examples=rows,slots=plan,runs=dict(control='031',treatment='032'),
        configuration=supplement['configuration'],expectedBatchesPerEpoch=393,expectedOptimizerUpdates=245,
        evaluationContentSHA256={k:r.content_sha256 for k,r in evaluation.items()},
        preservedAncestry='Existing accepted ROI196/STYLE210 train roles and groups unchanged; no new source admission',
        files=[dict(path=str(p.relative_to(payload)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(payload.rglob('*')) if p.is_file()])
    write(payload/'manifest.json',manifest)
    archive=out/'worker216-replay01.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in sorted(payload.rglob('*')):
            if p.is_file():t.add(p,arcname=str(p.relative_to(payload)),recursive=False)
    with tarfile.open(archive) as t:
        check_archive(t.getmembers());require(len(t.getmembers())==1995,'archive_count')
        for ref in manifest['files']:
            raw=t.extractfile(ref['path']).read()
            require(len(raw)==ref['bytes'] and hashlib.sha256(raw).hexdigest()==ref['sha256'],'archive_replay')
    write(out/'audit.json',dict(trainingUnique=1569,replay=1509,residentReused=512,newTransferred=997,
        evaluationRecords=621,duplicatePixels=0,reservedPixelOverlap=0,
        fitTrainingPixelOverlap=len(set(pixels)&set(fit_pixels)),
        fitRole='Training-derived fit diagnostic, not independent evaluation',
        classSupport={name:{str(i):counts[i] for i in range(41)} for name,counts in support.items()},
        manifestSHA256=sha(payload/'manifest.json'),sourceSHA256=sha(Path(__file__)),modelGatePassed=False))
    tx=dict(requestID='nuiak-20261006-worker216-replay',sharedPath='nuiak/'+archive.name,
            localPath=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=sha(archive))
    write(out/'transaction.json',tx);return tx


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(prepare(parser.parse_args().out))
