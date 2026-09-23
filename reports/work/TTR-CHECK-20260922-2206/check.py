"""Read-only changed-build boundary checks; no recipe, focus, capture or export."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
APP = Path('/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app')
FIXTURE = Path('/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/9026ECA9-77DB-4AE6-8FE6-BB239E9571FA/data/Containers/Bundle/Application/750AFF32-645A-4670-A5F8-28A2C93E411F/TVTestRigFixture.app')
TARGET = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
def run(name, args):
    start = time.monotonic()
    r = subprocess.run(args, capture_output=True, text=True, timeout=25)
    for suffix, value in [('stdout', r.stdout), ('stderr', r.stderr)]:
        with (HERE/(name+'.'+suffix)).open('x') as f: f.write(value)
    with (HERE/(name+'-execution.json')).open('x') as f:
        json.dump({'command': args, 'exitCode': r.returncode, 'seconds': time.monotonic()-start}, f)
    return r
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [APP/'Contents/Helpers/aatv', APP/'Contents/MacOS/TVTestRig.debug.dylib', FIXTURE/'TVTestRigFixture.debug.dylib']}
(HERE/'hashes.json').write_text(json.dumps(hashes, indent=2))
run('listener', ['lsof','-nP','-iTCP:8080','-sTCP:LISTEN'])
prefix = [str(APP/'Contents/Helpers/aatv'),'--json','--timeout-ms','15000']
run('status',prefix+['status'])
run('readiness',prefix+['simulator','readiness','--simulator-udid',TARGET])
for route in ('device','scene'):
    run(route,['curl','--fail','--silent','--show-error','--max-time','5','http://127.0.0.1:8080/'+route])
print(json.dumps(hashes,indent=2))
