"""Bounded read-only current-runtime diagnostic; no capture, recipe or input."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
app=Path('/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app')
fixture=Path('/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/9026ECA9-77DB-4AE6-8FE6-BB239E9571FA/data/Containers/Bundle/Application/67B1AD5E-E458-4382-85E9-534812B7D153/TVTestRigFixture.app')
helper=app/'Contents/Helpers/aatv'
prefix=[str(helper),'--json','--timeout-ms','15000']
commands={
    'status':prefix+['status'],
    'readiness':prefix+['simulator','readiness','--simulator-udid','9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'],
    'device':['curl','--fail','--silent','--show-error','--max-time','5','http://127.0.0.1:8080/device'],
    'scene':['curl','--fail','--silent','--show-error','--max-time','5','http://127.0.0.1:8080/scene']}
ledger=[]
for name,command in commands.items():
    start=time.monotonic()
    with (HERE/(name+'.json')).open('x') as out, (HERE/(name+'.stderr')).open('x') as err:
        try: code=subprocess.run(command,stdout=out,stderr=err,timeout=25,env={**os.environ,'TMPDIR':str(ROOT/'.build/debug-output/focus-launch/tmp')}).returncode
        except subprocess.TimeoutExpired: code=124
    ledger.append({'name':name,'command':command,'exitCode':code,'seconds':time.monotonic()-start})
    print(json.dumps(ledger[-1]),flush=True)
paths=[helper,app/'Contents/MacOS/TVTestRig.debug.dylib',fixture/'TVTestRigFixture.debug.dylib']
with (HERE/'checks.json').open('x') as f:
    json.dump({'commands':ledger,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},f,indent=2)
