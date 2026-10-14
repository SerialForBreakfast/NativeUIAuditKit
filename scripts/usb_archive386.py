"""Archive inactive artifacts with complete hash checks and explicit reclamation."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
import corpus_retention as c
import research_queue as q
import usb_training386 as u


def archive(source, receipt, reclaim=False, restore=False):
    source=Path(source).absolute();receipt=Path(receipt).absolute()
    q.require(source.resolve()==source and source.is_relative_to(q.ROOT/'reports/work'), 'archive_source')
    q.require(receipt.resolve()==receipt and receipt.is_relative_to(q.ROOT/'reports/work')
              and not receipt.is_relative_to(source), 'archive_receipt')
    u.verify_volume()
    if restore:
        doc=q.load(receipt);inv=doc['inventory'];dest=Path(doc['destination'])
        q.require(doc['volumeUUID']==u.UUID and inv['source']==str(source.relative_to(q.ROOT)),'archive_identity')
        q.require(dest.resolve()==dest and dest.is_relative_to(u.VOLUME/'data/NUIAK/archive-20261014'),'archive_destination')
        c.verify(inv,dest)
        q.require(shutil.disk_usage(q.ROOT).free >= inv['totalBytes'] + q.STORAGE_MARGIN,'restore_space')
        for member in inv['members']:
            path=source/member['path']
            q.require(path.resolve()==path,'restore_link')
            if path.exists():
                q.require(q.digest(path)==member['sha256'],'restore_existing_conflict')
                continue
            u.copy_checked(dest/member['path'],path)
        c.verify(inv,source)
        return dict(restored=True,bytes=inv['totalBytes'],receipt=str(receipt))
    if not reclaim:
        q.require(not receipt.exists(),'archive_receipt_exists')
        inv=c.inventory(source,exclude_finder_metadata=True)
        dest=u.VOLUME/'data/NUIAK/archive-20261014'/source.relative_to(q.ROOT)
        q.require(dest.resolve()==dest and not dest.exists(),'archive_collision')
        usage=shutil.disk_usage(u.VOLUME)
        q.require(usage.free-inv['totalBytes'] >= usage.total*.2,'archive_reserve')
        start=time.monotonic();dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(source,dest)
        for member in inv['members']:
            with (dest/member['path']).open('rb') as stream:os.fsync(stream.fileno())
        c.verify(inv,dest);c.verify(inv,source)
        receipt.parent.mkdir(parents=True,exist_ok=True)
        doc=dict(version='usb-archive-v1',inventory=inv,destination=str(dest),volumeUUID=u.UUID,
                 seconds=time.monotonic()-start,backup=False,reclaimed=False)
        q.save(receipt,doc)
        q.save(dest.parent/(dest.name+'-receipt.json'),doc)
        return doc
    doc=q.load(receipt);inv=doc['inventory'];dest=Path(doc['destination'])
    q.require(doc['volumeUUID']==u.UUID and inv['source']==str(source.relative_to(q.ROOT)),'archive_identity')
    q.require(dest.resolve()==dest and dest.is_relative_to(u.VOLUME/'data/NUIAK/archive-20261014'),'archive_destination')
    c.verify(inv,dest);c.verify(inv,source)
    for member in inv['members']:
        with (dest/member['path']).open('rb') as stream:os.fsync(stream.fileno())
    tracked=set(subprocess.check_output(['git','ls-files','-z','--',str(source.relative_to(q.ROOT))],cwd=q.ROOT).decode().split('\0'))
    removed=0
    for member in inv['members']:
        path=source/member['path']
        if str(path.relative_to(q.ROOT)) in tracked:continue
        q.require(u.VOLUME.is_mount(),'usb_disconnected')
        q.require(q.digest(path)==member['sha256'] and q.digest(dest/member['path'])==member['sha256'],'archive_changed')
        path.unlink();removed+=member['bytes']
    q.save(receipt.with_name(receipt.stem+'-reclaimed.json'),dict(receiptSHA256=q.digest(receipt),removedBytes=removed,
           restore='Copy verified members to their original paths before historical replay.',backup=False))
    return dict(removedBytes=removed,receipt=str(receipt))


if __name__=='__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('receipt')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--reclaim',action='store_true');mode.add_argument('--restore',action='store_true')
    a=p.parse_args();r=archive(a.source,a.receipt,a.reclaim,a.restore)
    print(json.dumps({k:v for k,v in r.items() if k!='inventory'}))
