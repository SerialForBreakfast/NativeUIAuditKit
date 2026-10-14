"""Measure matched PNG reads and decoding. Do not claim cold-disk throughput."""
from pathlib import Path
import hashlib
import time
from PIL import Image
import research_queue as q
import usb_training386 as u


def run():
    u.verify_volume()
    local=q.ROOT/'reports/work/USB386/decode-probe'
    remote=u.BASE/'decode-probe-386'
    q.require(not local.exists() and not remote.exists(),'probe_exists')
    local.mkdir(parents=True);remote.mkdir(parents=True)
    catalog=q.QUEUE/'jobs/hcf371r4-40-catalog/attempts/1/out/admission.json'
    rows=q.load(catalog)['rows']
    # Only training images enter this storage check. No audit pixels are read.
    selected=[r for r in rows if r['role']=='train'][:8]
    q.require(len(selected)==8,'probe_membership')
    timings=[]
    for index,row in enumerate(selected):
        source=Path(row['path']);q.require(q.digest(source)==row['sha256'],'probe_source')
        name=f'{index}.png'
        for folder in (local,remote):u.copy_checked(source,folder/name)
        identities=[]
        for repeat in range(2):
            for label,folder in (('local',local),('usb',remote)):
                start=time.perf_counter()
                with Image.open(folder/name) as im:
                    rgb=im.convert('RGB');pixels=rgb.tobytes();size=rgb.size
                seconds=time.perf_counter()-start
                identities.append((hashlib.sha256(pixels).hexdigest(),size))
                timings.append(dict(image=row['id'],storage=label,repeat=repeat,seconds=seconds,bytes=(folder/name).stat().st_size))
        q.require(len(set(identities))==1,'decode_mismatch')
    report=dict(version='usb-decode-probe-v1',volumeUUID=u.UUID,catalogSHA256=q.digest(catalog),images=8,
                pixelParity=True,rows=timings,limitation='OS caches remain warm. This measures PNG read and decode, not training throughput or cold disk speed.')
    q.save(local.parent/'decode-probe.json',report)
    print('8 training images: decoded pixels match; timings saved.')


if __name__=='__main__':run()
