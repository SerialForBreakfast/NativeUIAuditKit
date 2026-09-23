"""One direct-lane smoke after fresh shared-runtime ownership checks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HELPER = '/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv'
TARGET = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
for name, args in [('direct-status', ['status']), ('direct-readiness', ['simulator', 'readiness', '--simulator-udid', TARGET])]:
    r = subprocess.run([HELPER, '--json', '--timeout-ms', '15000', *args], capture_output=True, text=True, timeout=25)
    with (HERE / (name+'.json')).open('x') as f: f.write(r.stdout)
    assert r.returncode == 0
    v = json.loads(r.stdout)
    assert v['success']
    if name == 'direct-status':
        s = v['data']['status']['_0']
        assert not s.get('commandActive') and not s.get('observationActive') and not s.get('queuedCommandCount')
    else:
        s = v['data']['simulatorReadiness']['_0']
        assert s['can_run'] and s['target']['simulator_udid'] == TARGET
        assert all(o['state'] == 'clear' for o in s['ownership'])
out = ROOT / 'dataset/tvos_captures/direct-dialog-20260922-2147'
args = [sys.executable, 'scripts/direct_tvos_capture.py', '--execute', '--catalog',
        'reports/work/TVGEN/smoke-catalog.json', '--target', TARGET, '--endpoint',
        'http://127.0.0.1:8080', '--output', str(out)]
start = time.monotonic()
with (HERE/'direct-smoke.stdout').open('x') as stdout, (HERE/'direct-smoke.stderr').open('x') as stderr:
    r = subprocess.run(args, stdout=stdout, stderr=stderr, timeout=180,
                       env={**os.environ, 'TMPDIR': str(ROOT/'.build/debug-output/focus-launch/tmp')})
with (HERE/'direct-smoke-execution.json').open('x') as f:
    json.dump({'command': args, 'exitCode': r.returncode, 'seconds': time.monotonic()-start}, f, indent=2)
print('direct smoke exit', r.returncode)
