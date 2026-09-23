"""One authorized simulator dialog job. No automatic retries or broader capture."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
UDID='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
APP=Path('/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app')
HELPER=APP/'Contents/Helpers/aatv'
PREFIX=[str(HELPER),'--json','--timeout-ms','15000']
env={**os.environ,'TMPDIR':str(ROOT/'.build/debug-output/focus-launch/tmp')}
def command(name,args,timeout=25):
    start=time.monotonic()
    with (HERE/(name+'.json')).open('x') as out,(HERE/(name+'.stderr')).open('x') as err:
        try: code=subprocess.run(args,stdout=out,stderr=err,timeout=timeout,env=env).returncode
        except subprocess.TimeoutExpired: code=124
    with (HERE/(name+'-execution.json')).open('x') as f:
        json.dump({'command':args,'exitCode':code,'seconds':time.monotonic()-start},f,indent=2)
    if code: raise SystemExit(f'{name}:exit{code}; completion may be uncertain, do not retry mutation')
    value=json.loads((HERE/(name+'.json')).read_text())
    if value.get('success') is False: raise SystemExit(name+':typed_failure')
    return value
def cli(name,args,timeout=25): return command(name,PREFIX+args,timeout)
def http(name,route): return command(name,['curl','--fail','--silent','--show-error','--max-time','5','http://127.0.0.1:8080/'+route])
def readiness(name):
    r=cli(name,['simulator','readiness','--simulator-udid',UDID])['data']['simulatorReadiness']['_0']
    if not r.get('can_run') or r['target']['simulator_udid']!=UDID or r['target']['state']!='Booted' or any(v['state']!='clear' for v in r.get('ownership',[])):
        raise SystemExit('target_not_ready_or_ownership_unclear')
    return r
def status(name):
    s=cli(name,['status'])['data']['status']['_0']
    if s.get('commandActive') or s.get('observationActive') or s.get('queuedCommandCount'): raise SystemExit('coordinator_occupied')
    return s
phase=sys.argv[1]
if phase=='start':
    # Passive process/listener correlation is repeated immediately before mutation.
    process=subprocess.check_output(['ps','-axo','pid,command'],text=True)
    listeners=subprocess.check_output(['lsof','-nP','-iTCP:8080','-sTCP:LISTEN'],text=True)
    listener_rows=listeners.splitlines()[1:]
    pids={r.split()[1] for r in listener_rows}
    matches=[r for r in process.splitlines() if r.split(maxsplit=1)[0] in pids and '/'+UDID+'/' in r and '/TVTestRigFixture.app/TVTestRigFixture' in r]
    if len(matches)!=1: raise SystemExit('endpoint_target_ambiguity')
    fixture=Path(matches[0].split(maxsplit=1)[1]).parent/'TVTestRigFixture.debug.dylib'
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (HELPER,APP/'Contents/MacOS/TVTestRig.debug.dylib',fixture)}
    with (HERE/'runtime.json').open('x') as f: json.dump({'process':matches[0],'listener':listeners,'hashes':hashes},f,indent=2)
    status('status-before'); readiness('readiness-before'); http('device-before','device'); http('scene-before','scene')
    recipe={'schema_version':1,'archetype':'action_dialog','theme':'high_contrast','density':'regular','element_count':2,'seed':7,'step_index':0}
    prepared=cli('prepare',['fixture','prepare','--recipe-json',json.dumps(recipe,separators=(',',':'))])['data']['fixtureJob']['_0']
    if not prepared.get('storageReady') or prepared['state']!='prepared': raise SystemExit('storage_not_ready')
    job=prepared['jobID']
    with (HERE/'job.json').open('x') as f: json.dump({'jobID':job,'startedEpoch':time.time(),'operationLimitSeconds':600},f)
    print(json.dumps(cli('start',['fixture','run-job',job,'--simulator-udid',UDID,'--fixture-url','http://127.0.0.1:8080'])),flush=True)
elif phase=='poll':
    job=json.loads((HERE/'job.json').read_text())
    # Operator inspects terminal status; after deadline issue one cancellation only.
    name=sys.argv[2]
    result=cli(name,['fixture','job-status',job['jobID']])
    print(json.dumps(result),flush=True)
    if time.time()-job['startedEpoch']>600 and result['data']['fixtureJob']['_0']['state'] not in ('completed','failed','cancelled'):
        print(json.dumps(cli('deadline-cancel',['fixture','cancel-job',job['jobID']])),flush=True)
elif phase=='export':
    job=json.loads((HERE/'job.json').read_text())
    state=cli('pre-export-status',['fixture','job-status',job['jobID']])['data']['fixtureJob']['_0']
    if state['state']!='completed': raise SystemExit('not_completed_no_export')
    parent=ROOT/'dataset/tvos_captures/ttr-smoke-20260922-2119'; parent.mkdir(parents=True,exist_ok=False)
    print(json.dumps(cli('export',['fixture','export-job',job['jobID'],'--output-dir',str(parent/'bundle')],120)),flush=True)
elif phase=='postflight':
    http('device-after','device'); http('scene-after','scene'); readiness('readiness-after'); status('status-after')
    print('postflight HTTP responsive, readiness and coordinator checked')
else: raise SystemExit('unknown_phase')
