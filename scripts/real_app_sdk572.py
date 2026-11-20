"""Bounded SDK metadata qualification. No screenshots, model inference, or input."""
from pathlib import Path
import base64
import json
import os
import selectors
import subprocess
import time
import research_queue as q
from experiment_templates import checked
OUT = None
TARGET = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
BUNDLES = {'com.jordankoch.NewsTV', 'com.geoffmyers.PhotoGuessingGame', 'org.jellyfin.swiftfin'}


def cli(config, args, name):
    helper=Path(config['helper']);q.require(helper.is_file() and q.digest(helper)==config['helperSHA256'],'sdk572_helper_changed')
    env=dict(os.environ);env.pop('TVTESTRIG_PROJECT',None)
    route=['--project',config['workspace']]if config.get('workspace')else []
    result=subprocess.run([str(helper),*route,'--json',*args],capture_output=True,text=True,timeout=45,env=env)
    q.save(OUT/(name+'.json'),dict(returnCode=result.returncode,stdout=result.stdout,stderr=result.stderr[-20000:]))
    value=json.loads(result.stdout)
    q.require(result.returncode==0 and value.get('success') is True,'sdk572_cli_failed:'+name)
    return next(iter(value['data'].values()))['_0']


def identity(process, log, seconds=45, prefix=b'REAL543_SDK '):
    selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
    deadline=time.monotonic()+seconds;pending=b'';total=0
    try:
        while time.monotonic()<deadline:
            for key,_ in selector.select(timeout=.2):
                data=os.read(key.fileobj.fileno(),65536)
                if not data:q.require(process.poll() is None,'sdk572_launch_exited');continue
                total+=len(data);q.require(total<=1_000_000,'sdk572_console_limit')
                log.write(data);log.flush();pending+=data
                while b'\n' in pending:
                    line,pending=pending.split(b'\n',1)
                    if line.startswith(prefix+b'{'):return json.loads(line[len(prefix):])
        raise ValueError('sdk572_identity_timeout')
    finally:selector.close()


def run():
    spec=q.load(OUT.parents[2]/'spec.json');config=q.load(checked(spec['template']['inputs']['configuration']))
    q.require(config['target']==TARGET and config['bundle'] in BUNDLES,'sdk572_scope')
    app=q.local_path(q.ROOT,config['app']);q.require(app.is_dir(),'sdk572_app_missing')
    for ref in config['sources']:checked(ref)
    ready=cli(config,['simulator','readiness','--simulator-udid',TARGET],'readiness')
    q.require(ready.get('can_run') is True and ready.get('ownership') and all(x['state']=='clear'for x in ready['ownership']),'sdk572_target_busy')
    installed=subprocess.run(['xcrun','simctl','install',TARGET,str(app)],capture_output=True,text=True,timeout=120)
    q.require(installed.returncode==0,'sdk572_install_failed:'+installed.stderr[-400:])
    key=base64.b64encode(os.urandom(32)).decode();env=dict(os.environ,SIMCTL_CHILD_TTR_SAMPLE_KEY=key,SIMCTL_CHILD_SIMULATOR_UDID=TARGET)
    result=dict(version='sdk572-metadata-v1',sdkRevision=config['sdkRevision'],app=config['bundle'],samples=[],captures=0,inputs=0,modelInference=0,metricsStatus='provisional',modelAccepted=False)
    workspace=Path(config['workspace']);q.require(workspace==Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig')),'sdk572_workspace')
    enrollment_root=workspace/'.local-work/nuiak572/enrollments';enrollment_root.mkdir(parents=True,exist_ok=True)
    enrollment=enrollment_root/(spec['id']+'-private.json');process=None
    try:
        with (OUT/'console.log').open('wb') as log:
            process=subprocess.Popen(['xcrun','simctl','launch','--console-pty',TARGET,config['bundle'],*config['arguments']],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
            seen=identity(process,log)
            q.require(seen['appID']==config['bundle'] and seen['endpoint']=='http://127.0.0.1:8097/diagnostics/sdk/probe','sdk572_enrollment_identity')
            fd=os.open(enrollment,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w')as f:json.dump(dict(appID=seen['appID'],processID=seen['processID'],runID=seen['runID'],secretBase64=key),f)
            for index in range(3):
                sample=cli(config,['sdk','snapshot','--endpoint',seen['endpoint'],'--enrollment',str(enrollment)],f'snapshot-{index}')
                result['samples'].append(sample)
                if index<2:time.sleep(1)
    finally:
        cleanup=subprocess.run(['xcrun','simctl','terminate',TARGET,config['bundle']],capture_output=True,text=True,timeout=30)
        if process is not None:
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        if enrollment.exists():enrollment.unlink()
        result['cleanupReturnCode']=cleanup.returncode
        q.save(OUT/'benchmark_summary.json',result)
    q.require(cleanup.returncode==0,'sdk572_cleanup_failed')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
