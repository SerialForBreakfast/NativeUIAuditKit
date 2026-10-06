"""Package a representative admitted detector workload; never launch training."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import tarfile
from PIL import Image
import roi196 as source

PIXEL_ENCODING = 'sha256(utf8(str((width, height))) + Pillow.convert(RGB).tobytes()); uint8 row-major; no EXIF transpose'
LIMITS = dict(maxMembers=1100, maxExpandedBytes=60000000,
              defaultMemberBytes=32000000, memberOverrides={'initializer.pt':41000000})


def pixel_sha(image):
    rgb = image.convert('RGB')
    return hashlib.sha256(str(rgb.size).encode('utf-8') + rgb.tobytes()).hexdigest()


def check_bounds(files):
    if len(files) > LIMITS['maxMembers'] or sum(f['bytes'] for f in files) > LIMITS['maxExpandedBytes']:
        raise ValueError('archive_total_bounds')
    if any(f['bytes'] < 0 or f['bytes'] > LIMITS['memberOverrides'].get(f['path'], LIMITS['defaultMemberBytes']) for f in files):
        raise ValueError('archive_member_bounds')


def select(images, lineage, count=512):
    byid = {r['id']: r for r in lineage}
    if len(byid) != len(lineage) or len({i.image_id for i in images}) != len(images):
        raise ValueError('duplicate_membership')
    if len(images) < count or any(i.image_id not in byid for i in images):
        raise ValueError('incomplete_lineage')
    return sorted(images, key=lambda i: hashlib.sha256(i.image_id.encode()).hexdigest())[:count]


def build(output):
    h, p, e = source.h, source.p, source.e
    output = output.absolute()
    h.require(output.is_relative_to(h.ROOT) and output.resolve() == output and not output.exists(), 'output_boundary_collision')
    h.require(shutil.disk_usage(h.ROOT).free > 4*1024**3, 'storage_reserve')
    proposal = p.sealed(source.OUT/'proposal.json')
    h.require(proposal['configurationReady'] and proposal['runID'] == '026' and
              len(proposal['rows']) == 1173, 'source_not_ready')
    req = e.load_request(h.checked(h.ROOT, proposal['membership']), 41)
    chosen = select(req.images, proposal['rows'])
    cp = h.checked(h.ROOT, proposal['initializer'], 256*1024**2)
    total = sum(i.image_path.stat().st_size+i.label_path.stat().st_size for i in chosen)+cp.stat().st_size
    h.require(total < 1024**3, 'payload_budget')
    output.mkdir(parents=True); payload=output/'payload';payload.mkdir()
    (payload/'images').mkdir();(payload/'labels').mkdir()
    rows=[];seen=set(); lineage={r['id']:r for r in proposal['rows']}
    for n,i in enumerate(chosen):
        with Image.open(i.image_path) as im:
            im.load(); pixel=pixel_sha(im)
        h.require(pixel not in seen, 'duplicate_pixels');seen.add(pixel)
        image=f'images/{n:04d}.png';label=f'labels/{n:04d}.txt'
        shutil.copyfile(i.image_path,payload/image);shutil.copyfile(i.label_path,payload/label)
        h.require(h.sha(payload/image)==h.sha(i.image_path) and h.sha(payload/label)==h.sha(i.label_path),'copy_changed')
        rows.append(dict(id=i.image_id,image=image,label=label,role='train',pixelSHA256=pixel,
                         lineage=lineage[i.image_id]))
    shutil.copyfile(cp,payload/'initializer.pt')
    h.require(h.sha(payload/'initializer.pt') == proposal['initializer']['sha256'],'checkpoint_copy')
    manifest=dict(version='worker198-detector-input-v1',purpose='throughput_not_accuracy',
        trainingLaunchReady=False,pixelHashEncoding=PIXEL_ENCODING,extractionLimits=LIMITS,
        examples=rows,sourceProposal=h.ref(source.OUT/'proposal.json'),
        sourceMembership=proposal['membership'],initializerSHA256=proposal['initializer']['sha256'],
        classNames=e.load_names(),localUltralytics=importlib.metadata.version('ultralytics'),
        preprocessing=dict(imgsz=640,letterbox=True,augmentation=False),
        configuration= {k:proposal['args'][k] for k in ('optimizer','lr0','nbs','amp','rect','seed','workers')},
        blockers=['worker_version_parity','instrumented_optimizer_cadence','parity_tolerance','reviewed_benchmark_runner'],
        files=[dict(path=str(f.relative_to(payload)),bytes=f.stat().st_size,sha256=h.sha(f))
               for f in sorted(payload.rglob('*')) if f.is_file()])
    h.write(payload/'manifest.json',manifest)
    check_bounds(manifest['files']+[dict(path='manifest.json',bytes=(payload/'manifest.json').stat().st_size)])
    archive=output/'nuiak-worker198-detector512-v1.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for f in sorted(payload.rglob('*')):
            if f.is_file():tar.add(f,arcname=str(f.relative_to(payload)),recursive=False)
    with tarfile.open(archive) as tar:
        members=tar.getmembers();h.require(len(members)==1026 and all(m.isfile() for m in members),'archive_members')
        for entry in manifest['files']:
            raw=tar.extractfile(entry['path']).read()
            h.require(len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],'archive_replay')
    tx=dict(version=2,peer='joe-big-dog/NUIAK',requestID='nuiak-20261006-worker198-detector512',
        sharedPath='nuiak/'+archive.name,localPath=str(archive.relative_to(h.ROOT)),
        bytes=archive.stat().st_size,sha256=h.sha(archive),receiptPath='joe-big-dog/worker198-detector512-receipt.json')
    h.write(output/'transaction.json',tx);print(json.dumps(tx))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args().output)
