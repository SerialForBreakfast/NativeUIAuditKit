"""Receive this completed smoke through documented read-only IPC; never capture."""
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOB = '697018C6-FAB6-4524-A691-1BE4507C8F7F'
HELPER = '/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv'
OUT = ROOT / 'dataset/tvos_captures/ttr-smoke-20260922-2119/ipc-received'
started = time.monotonic()

def request(args):
    if time.monotonic() - started > 300:
        raise RuntimeError('transfer deadline; preserve partial output')
    r = subprocess.run([HELPER, '--json', '--timeout-ms', '15000', 'fixture', *args], capture_output=True, text=True, timeout=25)
    if r.returncode:
        raise RuntimeError(f'IPC exit {r.returncode}: {r.stderr[-1000:]}')
    v = json.loads(r.stdout)
    if not v.get('success'):
        raise RuntimeError('IPC unsuccessful')
    return v

manifest = request(['job-manifest', JOB])
report = manifest['data']['fixtureJob']['_0']
assert report['jobID'] == JOB and report['state'] == 'completed'
files = report['files']
assert 0 < len(files) <= 4096
assert len({f['path'] for f in files}) == len(files)
assert sum(f['bytes'] for f in files) <= 256 * 1024 * 1024
for f in files:
    p = PurePosixPath(f['path'])
    assert not p.is_absolute() and '..' not in p.parts and str(p) == f['path']
    assert '\\' not in f['path'] and 0 <= f['bytes'] <= 32 * 1024 * 1024
assert OUT.parent.resolve() == OUT.parent and not OUT.exists()
OUT.mkdir()
(HERE / 'receive-manifest.json').write_text(json.dumps(manifest, indent=2))
for f in files:
    payload = bytearray()
    while len(payload) < f['bytes']:
        c = request(['read-job', JOB, '--path', f['path'], '--offset', str(len(payload))])['data']['fixtureJobChunk']['_0']
        b = base64.b64decode(c['data'], validate=True)
        assert c['jobID'] == JOB and c['path'] == f['path'] and c['offset'] == len(payload)
        assert 0 < len(b) <= min(262144, f['bytes'] - len(payload))
        assert hashlib.sha256(b).hexdigest() == c['sha256']
        payload.extend(b)
    assert hashlib.sha256(payload).hexdigest() == f['sha256']
    path = OUT / f['path']
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(payload)
    print(f['path'], len(payload), 'verified', flush=True)
# A transfer receipt is separate from, and never replaces, the producer receipt.
(HERE / 'receive-result.json').write_text(json.dumps({'jobID': JOB, 'files': files, 'seconds': time.monotonic()-started, 'destination': str(OUT), 'transport': 'documented fixture read-job IPC', 'writer': 'NUA caller; no app-container access', 'complete': True}, indent=2))
