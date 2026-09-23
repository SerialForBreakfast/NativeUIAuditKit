"""Bounded offline package verification with project-local outputs/caches."""
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
env = dict(os.environ, TMPDIR=str(ROOT / '.build/debug-output/focus-launch/tmp'),
           CLANG_MODULE_CACHE_PATH=str(ROOT / '.build/module-cache'),
           SWIFT_MODULECACHE_PATH=str(ROOT / '.build/module-cache'))
options = ['--disable-automatic-resolution', '--cache-path', str(ROOT / '.build/swiftpm-cache'),
           '--config-path', str(ROOT / '.build/swiftpm-config'),
           '--security-path', str(ROOT / '.build/swiftpm-security')]
results = []
for action in ('build', 'test'):
    start = time.monotonic()
    command = ['swift', action, *options]
    with (HERE / f'swift-{action}.log').open('x') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    results.append({'command': command, 'exitCode': result.returncode, 'seconds': time.monotonic()-start})
    if result.returncode:
        break
with (HERE / 'swift-verification.json').open('x') as stream:
    json.dump(results, stream, indent=2)
print(json.dumps(results, indent=2))
raise SystemExit(any(r['exitCode'] for r in results))
