"""Explicit copy/verify/reclaim for approved artifact trees; never edits the registry."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import artifact_storage as s
import corpus_retention as c


def run(source,receipt,mode):
    logical=Path(source).absolute();receipt=Path(receipt).absolute()
    s.require(logical.is_relative_to(s.ROOT) and str(logical.relative_to(s.ROOT)).startswith(s.ALLOWED),'migration_source')
    s.require(receipt.is_relative_to(s.ROOT/'reports/work') and receipt.resolve()==receipt,'migration_receipt')
    relative=logical.relative_to(s.ROOT)
    destination=s.BASE/'live'/relative
    s.mounted('/dev/disk25s1')
    s.clean(destination)
    if mode=='copy':
        s.require(not receipt.exists() and not destination.exists(),'migration_collision')
        doc=c.inventory(logical,exclude_finder_metadata=True)
        s.require(shutil.disk_usage(s.VOLUME).free>doc['totalBytes']+1024**3,'migration_space')
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(logical,destination,symlinks=True)
        c.verify(doc,destination);c.verify(doc,logical)
        receipt.parent.mkdir(parents=True,exist_ok=True)
        with receipt.open('x') as f:json.dump(dict(destination=str(destination),inventory=doc),f,indent=2)
        print(json.dumps(dict(source=str(relative),destination=str(destination),bytes=doc['totalBytes'],files=doc['fileCount'])),flush=True)
    else:
        doc=json.loads(receipt.read_text());s.require(doc['destination']==str(destination) and doc['inventory']['source']==str(relative),'migration_binding')
        s.require(s.resolve_input(logical)==destination,'migration_not_active')
        c.verify(doc['inventory'],destination);c.verify(doc['inventory'],logical)
        tracked=set(subprocess.check_output(['git','ls-files','-z','--',str(relative)],cwd=s.ROOT).decode().split('\0'))
        removed=0
        for member in doc['inventory']['members']:
            path=logical/member['path']
            if str(path.relative_to(s.ROOT)) in tracked:continue
            s.mounted('/dev/disk25s1')
            s.require(c.sha256(path)==member['sha256'],'migration_source_changed')
            path.unlink();removed+=member['bytes']
        for directory in sorted((p for p in logical.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
            if not any(directory.iterdir()):directory.rmdir()
        if not any(logical.iterdir()):logical.rmdir()
        print(json.dumps(dict(source=str(relative),removedBytes=removed,trackedFilesPreserved=len(tracked-{''}))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['copy','reclaim']);p.add_argument('--source',required=True);p.add_argument('--receipt',required=True)
    a=p.parse_args();run(a.source,a.receipt,a.mode)
