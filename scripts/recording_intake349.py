"""Verify a private recorder archive and reuse the existing recording audit."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from PIL import Image
import human_recording_audit as audit
import shared_transfer as transfer
from focus_surface_intake import safe_members

h=audit.h


def extract(archive,output):
    output=h.fresh(output)
    with tarfile.open(archive) as stream:
        members,total=safe_members(stream)
        h.require(total<=1_000_000_000 and shutil.disk_usage(output.parent).free>=total+5_000_000_000,'storage_budget')
        kept=[m for m in members if not any(p.startswith('._') for p in Path(m.name).parts)]
        roots={Path(m.name).parts[0] for m in kept};h.require(len(roots)==1,'archive_roots')
        output.mkdir()
        for member in kept:
            target=output/member.name
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                with stream.extractfile(member) as source,target.open('xb') as dest:shutil.copyfileobj(source,dest)
    return output/next(iter(roots)),dict(members=len(members),expandedBytes=total,extractedMembers=len(kept))


def run(offer_path,output):
    offer_path=h.local(offer_path);output=h.fresh(output);offer=transfer.document(offer_path)
    h.require(offer.get('version')==2 and type(offer.get('files')) is list,'offer_version')
    archives=[f for f in offer['files'] if f['file'].endswith('-original-recording.tar.gz')]
    h.require(len(archives)==1,'archive_count');entry=archives[0]
    archive=offer_path.parent/Path(entry['file']).name
    transfer.verified(archive,entry);output.mkdir(parents=True)
    source,extraction=extract(archive,output/'extracted')
    manifest=h.read(source/'manifest.json');h.require(manifest.get('schemaVersion')==2,'recording_schema')
    events_path=source/'events.jsonl';inventory_path=source/'files.jsonl'
    h.require(events_path.stat().st_size<=64*1024*1024 and inventory_path.stat().st_size<=2*1024*1024,'metadata_size')
    events=[json.loads(line) for line in events_path.read_text().splitlines() if line]
    inventory=[json.loads(line) for line in inventory_path.read_text().splitlines() if line]
    h.require(0<len(inventory)<=1000,'image_count')
    verified={}
    for item in inventory:
        rel=Path(item['path'])
        h.require(not rel.is_absolute() and len(rel.parts)==2 and rel.parts[0]=='images' and
                  rel.name=='frame-'+item['sha256']+'.png','image_path')
        h.require(item['sha256'] not in verified,'duplicate_inventory')
        path=source/rel;transfer.verified(path,item)
        with Image.open(path) as image:
            h.require(image.format=='PNG' and 0<image.width*image.height<=16_000_000,'image_dimensions')
            image.load();pixels=image.convert('RGB')
            digest=hashlib.sha256(str(pixels.size).encode()+pixels.tobytes()).hexdigest()
            verified[item['sha256']]=dict(image=h.ref(path),size=list(image.size),decodedRGBSHA256=digest)
    frame_map={}
    for event in events:
        if 'frame' not in event:continue
        frame=event['frame']['_0'];v=verified.get(frame['sha256'])
        h.require(v is not None,'unlisted_frame_image')
        dimensions=frame['dimensions']
        h.require(v['size']==[dimensions['width'],dimensions['height']],'frame_dimensions_disagree')
        h.require(frame['frameID'] not in frame_map,'duplicate_frame')
        frame_map[frame['frameID']]=dict(v,sequence=frame['sequenceNumber'],role=frame['role'])
    h.require(len(frame_map)==manifest['frameCount'],'manifest_frame_count')
    batch=dict(version='human-recording-review-batch-v1',**h.FLAGS,sessionID=manifest['sessionID'],
        sourceDeviceID=manifest['targetDeviceID'],manifest=h.ref(source/'manifest.json'),events=h.ref(events_path))
    h.write(output/'audit-input.json',batch,sealed=True)
    result=audit.run(output/'audit-input.json',output/'event-audit.json')
    transfer.verified(archive,entry)
    receipt=dict(version='recording-intake349-v1',**h.FLAGS,offer=h.ref(offer_path),archive=h.ref(archive),
        extraction=extraction,source=str(source.relative_to(h.ROOT)),frames=frame_map,counts=result['counts'],
        privacy='Private local evidence. Do not publish images or OCR.',
        decodedHashDefinition='SHA256 of Python tuple size text followed by RGB bytes; diagnostic version 1.')
    h.write(output/'intake.json',receipt,sealed=True)
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('offer');p.add_argument('output');args=p.parse_args()
    print(json.dumps(run(args.offer,args.output)['counts']))
