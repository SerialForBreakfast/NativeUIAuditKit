"""One approved exact-target install/launch; no boot, restart or re-signing."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
TARGET='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
APP=ROOT/'.build/debug-output/fixture-stage-20260923/TVTestRigFixture.app'
records=[]
def run(args,timeout=30):
    start=time.monotonic()
    result=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    records.append({'args':args,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'seconds':time.monotonic()-start})
    if result.returncode: raise RuntimeError(result.stderr)
    return result.stdout
try:
    inv=json.loads(subprocess.check_output(['xcrun','simctl','list','devices','available','-j'],text=True))
    selected=[{'runtime':runtime,**d} for runtime,ds in inv['devices'].items() for d in ds if d['udid']==TARGET]
    assert len(selected)==1 and selected[0]['state']=='Booted' and 'tvOS' in selected[0]['runtime'], selected
    records.append({'selected':selected})
    occupied=subprocess.run(['lsof','-nP','-iTCP:8080','-sTCP:LISTEN'],capture_output=True,text=True)
    assert occupied.returncode==1 and not occupied.stdout, 'endpoint_occupied_or_unknown'
    # One bounded repair of metadata observed to reappear after staging. Preserve
    # all other attributes; no re-sign, permissions change or automatic retry.
    for path in [APP,*APP.rglob('*')]:
        names=subprocess.check_output(['xattr',str(path)],text=True).splitlines()
        for name in ('com.apple.FinderInfo','com.apple.ResourceFork'):
            if name in names: run(['xattr','-d',name,str(path)],10)
    run(['codesign','--verify','--deep','--strict',str(APP)])
    assert hashlib.sha256((APP/'TVTestRigFixture.debug.dylib').read_bytes()).hexdigest()=='46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095'
    run(['xcrun','simctl','install',TARGET,str(APP)],60)
    run(['xcrun','simctl','launch',TARGET,'com.showblender.TVTestRigFixture'],30)
finally:
    with (HERE/'install-receipt-2.json').open('x') as f: json.dump(records,f,indent=2)
    print(json.dumps(records,indent=2))
