"""Explicit, read-only logical artifact relocation. No symlinks or implicit mounts."""
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'reports/storage/locations.json'
VOLUME=Path('/Volumes/training-drive')
BASE=VOLUME/'data/NUIAK'
ALLOWED=('reports/work/','dataset/','NativeUITrainer/reconstructed_corpora/','.build/debug-output/')
_cache=None
_mounted=None


class StorageError(ValueError):pass


def require(ok,reason):
    if not ok:raise StorageError(reason)


def clean(path):
    path=Path(path).absolute()
    require(path.resolve()==path,'storage_symlink_or_traversal')
    return path


def mappings():
    global _cache
    if not REGISTRY.exists():return []
    clean(REGISTRY);stat=REGISTRY.stat();key=(str(REGISTRY),stat.st_mtime_ns,stat.st_size)
    if _cache is not None and _cache[0]==key:return _cache[1]
    require(stat.st_size<1024*1024,'storage_registry_size')
    def unique(items):
        out={}
        for k,v in items:require(k not in out,'storage_duplicate_key');out[k]=v
        return out
    doc=json.loads(REGISTRY.read_text(),object_pairs_hook=unique)
    require(isinstance(doc,dict) and set(doc)=={'version','device','mappings'} and doc['version']=='artifact-storage-v1' and
            isinstance(doc['mappings'],list),'storage_registry_version')
    require(isinstance(doc['device'],str) and doc['device'].startswith('/dev/disk'),'storage_device')
    result=[]
    for row in doc['mappings']:
        require(isinstance(row,dict) and set(row)=={'logical','physical'},'storage_mapping_fields')
        logical,physical=row['logical'],row['physical']
        require(isinstance(logical,str) and logical.startswith(ALLOWED) and '..' not in Path(logical).parts and
                not Path(logical).is_absolute() and str(Path(logical))==logical,'storage_logical_prefix')
        require(isinstance(physical,str) and physical.startswith('live/') and '..' not in Path(physical).parts and
                str(Path(physical))==physical,'storage_physical_prefix')
        a,b=clean(ROOT/logical),clean(BASE/physical)
        for x,y,_ in result:
            require(not(a.is_relative_to(x) or x.is_relative_to(a) or b.is_relative_to(y) or y.is_relative_to(b)),
                    'storage_overlapping_mapping')
        result.append((a,b,doc['device']))
    _cache=(key,result);return result


def mounted(device):
    global _mounted
    require(VOLUME.is_mount() and VOLUME.stat().st_dev!=ROOT.stat().st_dev,'storage_volume_unavailable')
    key=(device,VOLUME.stat().st_dev)
    if _mounted!=key:
        lines=subprocess.check_output(['/sbin/mount'],text=True).splitlines()
        require(any(line.startswith(device+' on '+str(VOLUME)+' (apfs, local,') for line in lines),'storage_wrong_volume')
        _mounted=key


def logical_path(path):
    path=clean(path)
    if path.is_relative_to(ROOT):return path
    for logical,physical,device in mappings():
        if path.is_relative_to(physical):
            mounted(device);return logical/path.relative_to(physical)
    raise StorageError('outside_project')


def resolve_input(path):
    path=logical_path(path)
    for logical,physical,device in mappings():
        if path.is_relative_to(logical):
            mounted(device)
            require(physical.is_dir(),'storage_root_missing')
            return clean(physical/path.relative_to(logical))
    return path


def local_output(path):
    path=clean(path)
    require(path.is_relative_to(ROOT),'outside_project')
    require(not any(path.is_relative_to(a) for a,_,_ in mappings()),'storage_read_only_prefix')
    return path


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',help='Logical repository input path to resolve; no writes')
    args=parser.parse_args()
    print(resolve_input(args.path))
