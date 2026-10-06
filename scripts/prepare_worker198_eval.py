"""Portable inference-only ROI197 inputs; reuse exporter, never infer or train here."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

import prediction_artifact as artifact


def digest(path):
    return artifact.sha256_file(path)


def copy_request(request, destination):
    destination.mkdir(parents=True, exist_ok=False)
    rows=[]
    for index, image in enumerate(request.images):
        row={'imageID':image.image_id}
        for kind,source,expected,suffix in (
                ('image',image.image_path,image.image_sha256,'.png'),
                ('label',image.label_path,image.label_sha256,'.txt')):
            target=destination/(f'{index:04d}'+suffix)
            if digest(source)!=expected:raise ValueError('source_changed')
            shutil.copyfile(source,target)
            if digest(target)!=expected:raise ValueError('copy_changed')
            row[kind+'Path']=target.name;row[kind+'SHA256']=expected
        rows.append(row)
    path=destination/'input.json'
    path.write_text(json.dumps(dict(formatVersion=artifact.INPUT_FORMAT_VERSION,
        corpusID=request.corpus_id,images=rows),indent=2)+'\n')
    copied=artifact.load_request(path,41)
    if copied.content_sha256!=request.content_sha256:raise ValueError('relocation_changed_membership')
    return path


def check_limits(entries):
    if len(entries)>1300 or sum(e['bytes'] for e in entries)>200*1024**2:
        raise ValueError('archive_total_budget')
    if len({e['path'] for e in entries})!=len(entries):raise ValueError('duplicate_path')
    for e in entries:
        path=Path(e['path'])
        if path.is_absolute() or '..' in path.parts or e['bytes']<0 or e['bytes']>50*1024**2:
            raise ValueError('archive_member_budget_or_path')


def build(output):
    import train_style210 as training
    import roi197_compare as comparison
    h,p=training.h,training.p
    output=output.absolute()
    h.require(output.is_relative_to(h.ROOT) and output.resolve()==output and not output.exists(),'output_boundary_collision')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    training.configure('control');checkpoint,_=training.previous.runner.ready()
    frozen=p.sealed(comparison.OUT/'protocol.json')
    for ref in frozen['sources']+[frozen['screen']]:h.checked(h.ROOT,ref,256*1024**2)
    requests={k:artifact.load_request(h.checked(h.ROOT,v['manifest']),41) for k,v in frozen['plans'].items()}
    h.require({k:len(v.images) for k,v in requests.items()}=={'fit':135,'page':37,'combined':413},'unexpected_membership')
    output.mkdir(parents=True);payload=output/'payload';payload.mkdir()
    plans={}
    for kind,request in requests.items():
        path=copy_request(request,payload/'inputs'/kind)
        plans[kind]=dict(path=str(path.relative_to(payload)),count=len(request.images),
            contentSHA256=request.content_sha256,originalManifest=frozen['plans'][kind]['manifest'],
            role='fit_diagnostic' if kind=='fit' else 'frozen_evaluation',trainingEligible=False)
    sources=['scripts/eval_phase6a.py','scripts/prediction_artifact.py','scripts/centroid_distribution.py',
             'Research/schemas/category_map.json']
    for name in sources:
        target=payload/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(h.ROOT/name,target);h.require(digest(target)==digest(h.ROOT/name),'source_copy')
    shutil.copyfile(checkpoint,payload/'control027.pt')
    h.require(digest(payload/'control027.pt')==digest(checkpoint),'checkpoint_copy')
    (payload/'proposal-mapping.json').write_text(json.dumps(frozen,indent=2)+'\n')
    entries=[dict(path=str(f.relative_to(payload)),bytes=f.stat().st_size,sha256=digest(f))
        for f in sorted(payload.rglob('*')) if f.is_file()]
    manifest=dict(version='worker198-eval-v1',purpose='frozen_inference_only',trainingEligible=False,
        plans=plans,checkpoint=dict(path='control027.pt',sha256=digest(checkpoint)),files=entries,
        sourceProtocol=h.ref(comparison.OUT/'protocol.json'),
        settings=dict(device='0',imgsz=640,discard_degenerate=True),
        limits=dict(maxMembers=1300,maxExpandedBytes=200*1024**2,maxMemberBytes=50*1024**2))
    (payload/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    all_entries=entries+[dict(path='manifest.json',bytes=(payload/'manifest.json').stat().st_size,sha256=digest(payload/'manifest.json'))]
    check_limits(all_entries)
    archive=output/'nuiak-worker198-eval027-v1.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for entry in all_entries:tar.add(payload/entry['path'],arcname=entry['path'],recursive=False)
    with tarfile.open(archive) as tar:
        members=tar.getmembers();h.require(len(members)==len(all_entries) and all(m.isfile() for m in members),'archive_members')
        for entry in all_entries:
            data=tar.extractfile(entry['path']).read()
            h.require(len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],'archive_replay')
    tx=dict(version=2,peer='joe-big-dog/NUIAK',requestID='nuiak-20261006-worker198-eval027',
        sharedPath='nuiak/'+archive.name,localPath=str(archive.relative_to(h.ROOT)),bytes=archive.stat().st_size,
        sha256=digest(archive),receiptPath='joe-big-dog/worker198-eval027-receipt.json')
    h.write(output/'transaction.json',tx);print(json.dumps(tx))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args().output)
