"""Run bounded, resumable authored-focus batches. Native HCF capture is not supported yet."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from PIL import Image
import human_annotation_review as h

VERSION='focus-batch-v1'
LAYOUTS=('shelf','grid','hero_detail','top_nav_shelf')
LOCK=h.ROOT/'.build/focus-batch-resource.lock'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    """Publish an owned checkpoint atomically. Preserve completed result files."""
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.partial')
    with tmp.open('x') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


@contextlib.contextmanager
def lock():
    LOCK.parent.mkdir(parents=True,exist_ok=True)
    with LOCK.open('a+') as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('resource_busy')
        yield f.fileno()


def inventory(folder):
    result=[]
    for p in sorted(folder.rglob('*')):
        h.require(not p.is_symlink(),'symlink_in_artifacts')
        if p.is_file():result.append(dict(path=str(p.relative_to(folder)),sha256=sha(p),bytes=p.stat().st_size))
    return result


def validate_jobs(jobs,timeout,max_bytes,min_free,max_load):
    h.require(0<len(jobs)<=100 and 1<=timeout<=600 and 1<=max_bytes<=2147483648 and
              min_free>=max_bytes and math.isfinite(max_load) and max_load>0,'invalid_budget')
    ids=set()
    for j in jobs:
        h.require(set(j)=={'id','layout','focusID'} and re.fullmatch('[a-zA-Z0-9_-]{1,64}',j['id']) and
            j['id'] not in ids and j['layout'] in LAYOUTS and
            (j['focusID'] is None or re.fullmatch('[a-zA-Z0-9_-]{1,64}',j['focusID'])),'invalid_job')
        ids.add(j['id'])


def plan(renderer,assets,jobs,output,timeout=60,max_bytes=268435456,min_free=2147483648,max_load=8):
    renderer=Path(renderer).resolve(strict=True);assets=h.local(assets)
    h.require(renderer.name=='render-headless-screen.swift','unsupported_renderer')
    h.require(assets.is_dir(),'assets_directory_missing')
    h.require(0<len(jobs)<=100 and 1<=timeout<=600 and 1<=max_bytes<=2147483648 and
              min_free>=max_bytes and math.isfinite(max_load) and max_load>0,'invalid_budget')
    validate_jobs(jobs,timeout,max_bytes,min_free,max_load)
    doc=dict(version=VERSION,sourceDomain='authored_headless',profile='renderer_default_not_native_hcf',
        trainingEligible=False,role='development',renderer=dict(path=str(renderer),sha256=sha(renderer)),
        assets=dict(path=str(assets),files=inventory(assets)),jobs=jobs,
        limits=dict(timeoutSeconds=timeout,maxOutputBytes=max_bytes,minFreeBytes=min_free,maxLoad=max_load),
        harnessSHA256=sha(__file__),python=sys.executable)
    h.write(h.fresh(output),doc)
    return doc


def verify_plan(path):
    d=h.read(h.local(path));h.require(d.get('version')==VERSION and d.get('sourceDomain')=='authored_headless',
                                    'unsupported_plan')
    limits=d['limits']
    validate_jobs(d['jobs'],limits['timeoutSeconds'],limits['maxOutputBytes'],limits['minFreeBytes'],limits['maxLoad'])
    h.require(d['trainingEligible'] is False and d['role']=='development' and
              d['profile']=='renderer_default_not_native_hcf' and 'scorer' not in d,'unsupported_data_role')
    h.require(d['harnessSHA256']==sha(__file__),'harness_changed')
    h.require(sha(d['renderer']['path'])==d['renderer']['sha256'],'renderer_changed')
    h.require(inventory(h.local(d['assets']['path']))==d['assets']['files'],'assets_changed')
    return d


def initialize(plan_path,root):
    verify_plan(plan_path);root=h.fresh(root);root.mkdir(parents=True)
    h.write(root/'plan.json',h.read(h.local(plan_path)))
    save(root/'state.json',dict(version=VERSION,planSHA256=sha(root/'plan.json'),state='ready',jobs={},attempts=[]))
    return root


def state(root):
    root=h.local(root);s=h.read(root/'state.json')
    h.require(s.get('version')==VERSION and s['planSHA256']==sha(root/'plan.json'),'changed_campaign')
    return s


def validate_output(folder,job):
    d=h.read(folder/(job['layout']+'_annotations.json'))
    h.require(d.get('schemaVersion')=='contract-v1-headless-focus' and d.get('layoutType')==job['layout'] and
              (d.get('canvasWidth'),d.get('canvasHeight'))==(1920,1080),'render_contract')
    nodes=d['nodes'];ids=[n['id'] for n in nodes]
    h.require(len(ids)==len(set(ids)) and 0<len(ids)<=256,'render_nodes')
    selected=[n['id'] for n in nodes if n['isFocused']]
    focus=d['focusedNodeID']
    h.require(isinstance(focus,str) and re.fullmatch('[a-zA-Z0-9_-]{1,64}',focus) and selected==[focus] and
              (job['focusID'] is None or focus==job['focusID']),'render_focus')
    for n in nodes:
        for key in ('unfocusedBounds','focusedBounds'):
            b=n[key];h.require(len(b)==4 and all(type(x) in (int,float) and math.isfinite(x) for x in b) and
                b[2]>0 and b[3]>0,'render_geometry')
    pixels=[]
    for name,key in [(job['layout']+'_unfocused.png','unfocusedImageSHA256'),
                     (job['layout']+'_focused_'+focus+'.png','focusedImageSHA256')]:
        p=folder/name;h.require(not p.is_symlink() and sha(p)==d[key],'render_image_hash')
        with Image.open(p) as im:
            h.require(im.format=='PNG' and im.size==(1920,1080),'render_image_size');im.load()
            pixels.append(hashlib.sha256(im.convert('RGB').tobytes()).hexdigest())
    h.require(pixels[0]!=pixels[1],'no_rendered_effect')
    return dict(files=inventory(folder),decodedPixelHashes=pixels,focusID=focus,
                trainingEligible=False,nativeHCF=False,geometry='authored_not_native_verified')


def check_result(folder,receipt):
    h.require(inventory(folder)==receipt['files'],'completed_output_changed')


def execute(command,root,log,seconds,limit,lock_fd):
    env=dict(os.environ,TMPDIR=str(root/'tmp'),CLANG_MODULE_CACHE_PATH=str(h.ROOT/'.build/ModuleCache'),
             OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
    with log.open('xb') as output:
        child=subprocess.Popen(command,cwd=h.ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,
                               start_new_session=True,pass_fds=(lock_fd,))
        started=time.monotonic()
        try:
            while child.poll() is None:
                reason=('cancelled' if (root/'STOP').exists() else
                        'operation_timeout' if time.monotonic()-started>seconds else
                        'output_limit' if sum(p.stat().st_size for p in root.rglob('*') if p.is_file())>limit else None)
                if reason:raise ValueError(reason)
                time.sleep(.2)
            h.require(child.returncode==0,'child_failed_'+str(child.returncode))
            h.require(sum(p.stat().st_size for p in root.rglob('*') if p.is_file())<=limit,'output_limit')
        finally:
            if child.poll() is None:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()


def run(root,max_jobs=100):
    root=h.local(root)
    h.require(type(max_jobs) is int and 1<=max_jobs<=100,'invalid_job_limit')
    with lock() as fd:
        s=state(root);d=verify_plan(root/'plan.json');limits=d['limits']
        if (root/'STOP').exists():return dict(state='cancelled',reason='Remove the owned STOP file before resuming.')
        for j in d['jobs']:
            old=s['jobs'].get(j['id'])
            if old and old['state']=='complete':check_result(root/old['folder'],old['receipt'])
        # The child inherits the lock. A dead parent cannot permit a second renderer.
        if any(v['state']=='running' for v in s['jobs'].values()):
            s['state']='needs_reconciliation';save(root/'state.json',s);return s
        if shutil.disk_usage(root).free<limits['minFreeBytes'] or os.getloadavg()[0]>limits['maxLoad']:
            s['state']='deferred_resources';save(root/'state.json',s);return s
        (root/'tmp').mkdir(exist_ok=True)
        binary=root/'renderer'
        try:
            if not s.get('binarySHA256'):
                binary=root/('renderer-'+uuid.uuid4().hex)
                execute(['/usr/bin/swiftc','-module-cache-path',str(h.ROOT/'.build/ModuleCache'),
                    d['renderer']['path'],'-o',str(binary)],root,root/('compile-'+uuid.uuid4().hex+'.log'),
                    limits['timeoutSeconds'],limits['maxOutputBytes'],fd)
                s['binarySHA256']=sha(binary);s['binaryPath']=binary.name;save(root/'state.json',s)
            binary=root/s['binaryPath']
            h.require(s.get('binarySHA256')==sha(binary),'unverified_renderer_binary')
            completed=0
            for j in d['jobs']:
                if s['jobs'].get(j['id'],{}).get('state')=='complete':continue
                if completed>=max_jobs:s['state']='paused_batch';break
                if (root/'STOP').exists():s['state']='cancelled';break
                if shutil.disk_usage(root).free<limits['minFreeBytes'] or os.getloadavg()[0]>limits['maxLoad']:
                    s['state']='deferred_resources';break
                attempt=j['id']+'-'+uuid.uuid4().hex;folder=root/attempt
                s['attempts'].append(attempt);s['jobs'][j['id']]=dict(state='running',folder=attempt)
                s['state']='running';save(root/'state.json',s)
                command=[str(binary),'--layout',j['layout'],'--resolution','1080p',
                    '--assets-dir',d['assets']['path'],'--output-dir',str(folder)]
                if j['focusID'] is not None:command+=['--focus-id',j['focusID']]
                execute(command,root,root/(attempt+'.log'),limits['timeoutSeconds'],limits['maxOutputBytes'],fd)
                verify_plan(root/'plan.json')
                receipt=validate_output(folder,j)
                s['jobs'][j['id']].update(state='complete',receipt=receipt);save(root/'state.json',s)
                completed+=1
            else:s['state']='complete'
        except (ValueError,OSError,KeyError) as error:
            s['state']='failed';s['error']=str(error)
            for v in s['jobs'].values():
                if v['state']=='running':v['state']='failed'
        save(root/'state.json',s)
        return s


def reconcile(root):
    root=h.local(root)
    with lock():
        s=state(root);d=verify_plan(root/'plan.json')
        for j in d['jobs']:
            row=s['jobs'].get(j['id'],{})
            if row.get('state')=='running':
                try:receipt=validate_output(root/row['folder'],j)
                except (ValueError,OSError,KeyError):row['state']='interrupted'
                else:row.update(state='complete',receipt=receipt)
        s['state']='ready';save(root/'state.json',s);return s


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('plan')
    for k in ('renderer','assets','jobs','output'):q.add_argument('--'+k,required=True)
    q.add_argument('--max-load',type=float,default=8)
    q=sub.add_parser('init');q.add_argument('--plan',required=True);q.add_argument('--root',required=True)
    for name in ('run','start','status','cancel','reconcile'):
        q=sub.add_parser(name);q.add_argument('--root',required=True)
        if name in ('run','start'):q.add_argument('--max-jobs',type=int,default=100)
    a=p.parse_args()
    if a.action=='plan':r=plan(a.renderer,a.assets,h.read(h.local(a.jobs)),a.output,max_load=a.max_load)
    elif a.action=='init':r=dict(root=str(initialize(a.plan,a.root)))
    elif a.action=='run':
        os.nice(10);r=run(a.root,a.max_jobs)
    elif a.action=='reconcile':r=reconcile(a.root)
    elif a.action=='cancel':
        root=h.local(a.root);state(root)
        (root/'STOP').touch(exist_ok=True);r=dict(state='cancel_requested')
    elif a.action=='start':
        root=h.local(a.root);state(root);verify_plan(root/'plan.json')
        with (root/('worker-'+uuid.uuid4().hex+'.log')).open('xb') as out:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'run','--root',str(root),
                '--max-jobs',str(a.max_jobs)],
                cwd=h.ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        r=dict(state='launched_not_accepted',pid=child.pid)
    else:r=state(a.root)
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
