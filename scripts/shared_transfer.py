"""Exact NUIAK SMB transactions. Default is read-only; never mounts or extracts."""
import argparse
import ctypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
SHARE=Path('/Volumes/SharedStatusFile')


def require(ok,reason):
    if not ok:raise ValueError(reason)


def mapping(loader,node):
    out={}
    for key,value in node.value:
        key=loader.construct_object(key)
        require(type(key) is str and key not in out,'duplicate_key')
        out[key]=loader.construct_object(value)
    return out


class Unique(yaml.SafeLoader):pass
Unique.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)


def document(path):
    require(path.stat().st_size<=1_048_576,'metadata_size')
    raw=path.read_bytes();require(len(raw)<=1_048_576,'metadata_size')
    depth=0;count=0
    for e in yaml.parse(raw):
        count+=1;require(count<=20000,'metadata_events')
        require(not isinstance(e,yaml.events.AliasEvent),'metadata_alias')
        if isinstance(e,(yaml.events.MappingStartEvent,yaml.events.SequenceStartEvent)):
            depth+=1;require(depth<=32,'metadata_depth')
        elif isinstance(e,(yaml.events.MappingEndEvent,yaml.events.SequenceEndEvent)):depth-=1
    return yaml.load(raw,Loader=Unique)


def path_under(root,relative):
    require(type(relative) is str and relative and not Path(relative).is_absolute() and
            str(Path(relative))==relative and '..' not in Path(relative).parts,'relative_path')
    path=root/relative
    require(path.resolve()==path and path.is_relative_to(root) and path!=root,'symlink_or_boundary')
    require(path.parent.is_dir(),'parent_missing')
    return path


def mounted():
    require(SHARE.is_mount() and SHARE.resolve()==SHARE,'mount_missing')
    lines=subprocess.check_output(['/sbin/mount'],text=True).splitlines()
    require(any(re.search(r'@(sillycon\.local|192\.168\.1\.39)/SharedStatusFile on '+re.escape(str(SHARE))+r' \(smbfs(?:,|\))',s)
                for s in lines),'wrong_mount')


def verified(path,tx):
    require(path.resolve()==path and path.is_file(),'file_missing_or_symlink')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        before=os.fstat(f.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_size==tx['bytes'],'size_or_type')
        digest=hashlib.sha256()
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
        after=os.fstat(f.fileno())
    require((before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),'source_changed')
    require(digest.hexdigest()==tx['sha256'],'hash_mismatch')


def exclusive_rename(source,dest):
    require(sys.platform=='darwin','exclusive_rename_platform')
    lib=ctypes.CDLL(None,use_errno=True)
    rename=lib.renamex_np;rename.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
    if rename(os.fsencode(source),os.fsencode(dest),0x4)!=0:
        code=ctypes.get_errno();raise OSError(code,os.strerror(code))


def staging_path(dest,tx):
    return dest.with_name('.nuiak-transfer-'+hashlib.sha256((tx['requestID']+tx['sharedPath']).encode()).hexdigest()[:24]+'.partial')


def copy_verified(source,dest,tx):
    verified(source,tx)
    if dest.exists():verified(dest,tx);return 'already_verified'
    stage=staging_path(dest,tx)
    require(stage.resolve()==stage,'staging_symlink')
    if stage.exists():verified(stage,tx)
    else:
        require(shutil.disk_usage(dest.parent).free>=tx['bytes']+1_048_576,'insufficient_space')
        # Interrupted/failed staging is preserved, never deleted by time or retry.
        fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as src,stage.open('xb') as out:
            require(stat.S_ISREG(os.fstat(src.fileno()).st_mode),'source_type')
            remaining=tx['bytes']
            while remaining:
                chunk=src.read(min(1024*1024,remaining));require(chunk,'source_truncated')
                out.write(chunk);remaining-=len(chunk)
            require(not src.read(1),'source_grew');out.flush();os.fsync(out.fileno())
        verified(stage,tx)
    verified(source,tx)
    exclusive_rename(stage,dest);verified(dest,tx)
    return 'copied_and_verified'


def transaction(path):
    require(path.resolve()==path and path.is_relative_to(ROOT),'transaction_boundary')
    tx=document(path)
    require(type(tx) is dict and set(tx)=={'version','requestID','sharedPath','localPath','bytes','sha256','receiptPath'} and
            type(tx['version']) is int and tx['version']==1,'transaction_contract')
    require(type(tx['requestID']) is str and re.fullmatch('[A-Za-z0-9._-]{1,160}',tx['requestID']),'request_id')
    require(type(tx['bytes']) is int and tx['bytes']>0,'byte_count')
    require(type(tx['sha256']) is str and re.fullmatch('[0-9a-f]{64}',tx['sha256']),'hash')
    shared=path_under(SHARE,tx['sharedPath']);local=path_under(ROOT,tx['localPath'])
    require(tx['sharedPath'].split('/')[0] in ('nuiak','tvtestrig'),'namespace')
    require(Path(tx['sharedPath']).name not in ('status.yaml','reservations.yaml','Instructions.md','SharedStatusSkill.md'),'protected_coordination_file')
    if tx['receiptPath'] is not None:
        require(tx['receiptPath'].startswith('tvtestrig/'),'receipt_owner')
        path_under(SHARE,tx['receiptPath'])
    return tx,shared,local


def receipt_matches(path,tx):
    r=document(path)
    require(type(r) is dict and type(r.get('schema_version')) is int and r['schema_version']==1 and
            r.get('request_id')==tx['requestID'] and r.get('from')=='TVTestRig' and r.get('to')=='NUIAK' and
            r.get('state')=='copied_and_verified','receipt_identity')
    a=r.get('artifact',{})
    require(a.get('file')==tx['sharedPath'] and type(a.get('verified_bytes')) is int and
            a['verified_bytes']==tx['bytes'] and a.get('verified_sha256')==tx['sha256'],'receipt_artifact')


def run(path,action='inspect',execute=False):
    mounted();tx,shared,local=transaction(path)
    result=dict(version=1,requestID=tx['requestID'],action=action,executed=False,
                sharedPath=tx['sharedPath'],bytes=tx['bytes'],sha256=tx['sha256'],trainingEligible=False)
    if action in ('publish','cleanup'):require(tx['sharedPath'].startswith('nuiak/'),'write_namespace')
    if action=='receive':require(tx['sharedPath'].startswith('tvtestrig/'),'read_namespace')
    for name,p in [('local',local),('shared',shared)]:
        if p.exists():verified(p,tx);result[name]='verified'
        else:result[name]='absent'
    stage=staging_path(shared if tx['sharedPath'].startswith('nuiak/') else local,tx)
    result['staging']={'path':str(stage),'state':'absent'}
    if stage.exists() or stage.is_symlink():
        try:verified(stage,tx);result['staging']['state']='verified_complete'
        except ValueError as error:result['staging'].update(state='invalid_preserved',reason=str(error))
    receipt=path_under(SHARE,tx['receiptPath']) if tx['receiptPath'] else None
    result['receipt']='missing'
    if receipt and receipt.exists():receipt_matches(receipt,tx);result['receipt']='verified'
    if action in ('publish','cleanup'):require(result['local']=='verified','original_missing')
    if action=='receive':require(result['shared']=='verified','source_missing')
    if action=='cleanup':require(result['receipt']=='verified','matching_receipt_required')
    result['state']='inspected' if action=='inspect' else 'inputs_verified_execution_not_proven'
    if not execute or action=='inspect':return result
    # No mount repair/fallback; recheck immediately before external mutation/access.
    mounted()
    if action=='publish':result['state']=copy_verified(local,shared,tx)
    elif action=='receive':
        result['state']=copy_verified(shared,local,tx)
        result['receiverReceipt']=dict(schema_version=1,request_id=tx['requestID'],
            id='nuiak-receipt-'+tx['requestID'],**{'from':'NUIAK','to':'TVTestRig'},state='copied_and_verified',
            created_at=datetime.now(timezone.utc).isoformat(),
            artifact=dict(file=tx['sharedPath'],verified_bytes=tx['bytes'],verified_sha256=tx['sha256']),intake='not_assessed')
    elif shared.exists():
        receipt_matches(receipt,tx);verified(local,tx);verified(shared,tx)
        shared.unlink();require(not shared.exists(),'cleanup_ambiguous');result['state']='shared_copy_removed_original_retained'
    else:result['state']='receipt_verified_shared_already_absent'
    result['executed']=True
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('transaction',type=Path)
    p.add_argument('--action',choices=['inspect','publish','receive','cleanup'],default='inspect')
    p.add_argument('--execute',action='store_true');args=p.parse_args()
    try:print(json.dumps(run(args.transaction.absolute(),args.action,args.execute),indent=2))
    except (ValueError,OSError,KeyError,TypeError,yaml.YAMLError) as e:
        print(json.dumps(dict(rejected=True,reason=str(e))));raise SystemExit(2)
