"""Validate and package the frozen full-frame delta; no training or capture."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tarfile
from PIL import Image
import fullframe_replay_baseline as baseline
import prepare_replay216 as replay
from generator_asset_plan import inventory_metadata
from annotation_schema_validation import validate_sidecar_structure
from page_regeneration41 import checked_export_labels
from artwork200_campaign import sha, write
from shared_transfer import require

ROOT = replay.ROOT
PARENT = ROOT/'reports/work/REPLAY-216/artifacts/input02/payload/manifest.json'
PARENT_PIN = 'f85849b93293c7535d076488e500efa15de32ac761195c313fcf9f3cc26225ba'
LINEAGE = ROOT/'reports/work/REPLAY-216/artifacts/evaluation-lineage02.json'
LINEAGE_PIN = '87fc95bd82954ebd3848ef9b4b909c47689d16f79a45207e81a471b4be0fb37a'
LIMITS = dict(maxMembers=600, maxExpandedBytes=512*1024**2, maxMemberBytes=16*1024**2)


def slots(previous, full):
    require(set(previous)=={'control','treatment'}, 'arms')
    control,treatment=previous['control'],previous['treatment']
    require(len(control)==len(treatment)==1569 and control[:1509]==treatment[:1509]
            and len(set(control[:1509]))==1509 and len(set(treatment))==1569
            and set(control[1509:])<=set(control[:1509]), 'parent_slots')
    require(len(full)==len(set(full))==189 and not set(full)&set(control+treatment), 'fullframe_slots')
    return {k:v[:1509]+full+v[1509:] for k,v in previous.items()}


def check_reserved(rows, reserved, parent_hashes, parent_groups, crop_pixels):
    forbidden_groups={r.get('group',Path(r['id']).stem) for r in reserved}|set(parent_groups)
    forbidden_pixels={r['pixelSHA256'] for r in reserved}|set(crop_pixels)
    ids=set();groups=set();pixels=set()
    for r in rows:
        group=r.get('group',Path(r['id']).stem)
        require(r['split']=='train', 'not_training')
        require(r['id'] not in ids and group not in groups and r['pixelSHA256'] not in pixels, 'duplicate_fullframe')
        require(group not in forbidden_groups and r['pixelSHA256'] not in forbidden_pixels
                and r['image']['sha256'] not in parent_hashes, 'reserved_overlap')
        ids.add(r['id']);groups.add(group);pixels.add(r['pixelSHA256'])


def archive_bounds(members):
    require(len(members)<=LIMITS['maxMembers'] and all(m.isfile() and
            0<=m.size<=LIMITS['maxMemberBytes'] for m in members) and
            sum(m.size for m in members)<=LIMITS['maxExpandedBytes'], 'archive_budget')


def source_family(row, annotation):
    family=annotation['generatorProfile']['templateFamily']
    require(isinstance(family,str) and bool(family) and row.get('family',family)==family, 'family_binding')
    return family


def prepare(out):
    out=out.absolute()
    require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(), 'output_boundary_collision')
    pins={PARENT:PARENT_PIN,baseline.POOL:baseline.POOL_PIN,LINEAGE:LINEAGE_PIN,
          baseline.audit.MEMBERSHIP:baseline.audit.PIN,replay.PAYLOAD/'manifest.json':replay.PIN}
    require(all(sha(p)==v for p,v in pins.items()), 'source_changed')
    require(shutil.disk_usage(ROOT).free>3*1024**3, 'space')
    old=inventory_metadata(PARENT);pool=inventory_metadata(baseline.POOL)
    lineage=inventory_metadata(LINEAGE)
    membership=baseline.audit.source.p.sealed(baseline.audit.MEMBERSHIP)['rows']
    original={r['id']:r for r in membership}
    rows=pool['rows'];require(len(rows)==pool['selectedCount']==189, 'membership')
    require(all(r==original.get(r['id']) for r in rows), 'membership_binding')
    native=inventory_metadata(replay.PAYLOAD/'manifest.json')
    require(old['initializerSHA256']==native['initializerSHA256']==baseline.PIN and
            old['classNames']==native['classNames']==baseline.a.evaluation.load_names(), 'taxonomy_initializer')
    requests=replay.checked_requests(ROOT/'reports/work/ARTWORK-204/artifacts/evaluation213-input01')
    require({k:r.content_sha256 for k,r in requests.items()}==old['evaluationContentSHA256'], 'evaluation_changed')
    reserved_pixels=[]
    for key in ('native','page','combined'):
        for image in requests[key].images:
            with Image.open(image.image_path) as im:reserved_pixels.append(replay.pixel_sha(im))
    parent_rows=[r for key in ('page','combined') for r in lineage['plans'][key]['rows']]
    check_reserved(rows,[r for r in membership if r['split']!='train'],
        {r['parentImageSHA256'] for r in parent_rows},
        {r['group'] for r in parent_rows if r['group'] is not None},reserved_pixels)
    categories={name:i for i,name in enumerate(old['classNames'])}
    paths=[];examples=[];support={name:0 for name in categories}
    for n,row in enumerate(rows):
        bound={k:baseline.audit.source.h.checked(ROOT,row[k]) for k in ('image','annotation','label')}
        annotation=inventory_metadata(bound['annotation']);validate_sidecar_structure(annotation)
        require(annotation['imageSHA256']==row['image']['sha256'], 'annotation_image_binding')
        checked_export_labels(annotation,bound['label'].read_text(),categories)
        with Image.open(bound['image']) as im:
            im.load();require(replay.pixel_sha(im)==row['pixelSHA256'], 'pixel_binding')
            dimensions=list(im.size)
        for line in bound['label'].read_text().splitlines():
            if line.strip():support[old['classNames'][int(line.split()[0])]]+=1
        examples.append(dict(id='full217-'+Path(row['id']).stem,role='train',
            image=f'images/{n:04d}.png',label=f'labels/{n:04d}.txt',annotation=f'annotations/{n:04d}.json',
            pixelSHA256=row['pixelSHA256'],dimensions=dimensions,
            lineage=dict(sourceID=row['id'],group=row.get('group',Path(row['id']).stem),family=source_family(row,annotation)),
            imageSHA256=row['image']['sha256'],labelSHA256=row['label']['sha256'],annotationSHA256=row['annotation']['sha256']))
        paths.append(bound)
    plan=slots(old['slots'],[r['id'] for r in examples])
    require(sum(p.stat().st_size for row in paths for p in row.values())<LIMITS['maxExpandedBytes']-4*1024**2,'input_budget')
    payload=out/'payload'
    for name in ('images','labels','annotations'):(payload/name).mkdir(parents=True)
    for row,bound in zip(examples,paths):
        for kind,src in bound.items():
            shutil.copyfile(src,payload/row[kind]);require(sha(payload/row[kind])==row[kind+'SHA256'], 'copy_changed')
    manifest=dict(schemaVersion='worker217-fullframe-v1',parentManifestSHA256=PARENT_PIN,
        nativeManifestSHA256=replay.PIN,originalResidentManifestSHA256=replay.PARENT_PIN,
        proposalSHA256=baseline.POOL_PIN,sourceMembershipSHA256=baseline.audit.PIN,
        evaluationLineageSHA256=LINEAGE_PIN,initializerSHA256=baseline.PIN,
        classNames=old['classNames'],pixelHashEncoding=replay.PIXEL_ENCODING,
        examples=examples,slots=plan,runs=dict(control='033',treatment='034'),configuration=old['configuration'],
        expectedBatchesPerEpoch=440,expectedOptimizerUpdates=275,extractionLimits=LIMITS,
        evaluationContentSHA256=old['evaluationContentSHA256'],
        role='Existing admitted train; same fullframes in both arms; no new evaluation membership',
        validation='Reuse original512 training-only diagnostic order from216; fixed-last, no selection',
        files=[dict(path=str(p.relative_to(payload)),bytes=p.stat().st_size,sha256=sha(p))
               for p in sorted(payload.rglob('*')) if p.is_file()])
    write(payload/'manifest.json',manifest)
    archive=out/'worker217-fullframe01.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in sorted(payload.rglob('*')):
            if p.is_file():t.add(p,arcname=str(p.relative_to(payload)),recursive=False)
    with tarfile.open(archive) as t:
        members=t.getmembers();archive_bounds(members);require(len(members)==568,'archive_count')
        for ref in manifest['files']:
            raw=t.extractfile(ref['path']).read()
            require(len(raw)==ref['bytes'] and hashlib.sha256(raw).hexdigest()==ref['sha256'],'archive_replay')
    require(archive.stat().st_size<=LIMITS['maxExpandedBytes'],'compressed_budget')
    require(all(sha(p)==v for p,v in pins.items()), 'source_changed_after_copy')
    old_groups={r['lineage']['group'] for r in old['examples']}
    write(out/'audit.json',dict(fullframes=189,commonROI=1509,slotsPerArm=1758,
        instances=support,unsupported=[k for k,v in support.items() if not v],
        reservedPixelOrKnownGroupOverlap=0,unknownPageEvaluationGroups=sum(r['group'] is None for r in parent_rows),
        fullframeGroupsAlreadyInROI=sum(r['lineage']['group'] in old_groups for r in examples),
        sourceSHA256=sha(__file__),manifestSHA256=sha(payload/'manifest.json'),
        trainingLaunched=False,modelGatePassed=False))
    tx=dict(requestID='nuiak-20261006-worker217-fullframe',sharedPath='nuiak/'+archive.name,
        localPath=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=sha(archive))
    write(out/'transaction.json',tx)
    return tx


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(prepare(parser.parse_args().out))
