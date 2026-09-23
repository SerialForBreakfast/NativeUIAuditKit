"""User-authorized copy-only metadata repair; never re-sign or alter the source."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'TVTestRig/.local-work/nuiak-admission-2026-09-22/fixture-signed/DerivedData/Build/Products/Debug-appletvsimulator/TVTestRigFixture.app'
DEST = ROOT/'.build/debug-output/fixture-stage-20260923/TVTestRigFixture.app'

def hashes(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink(): raise ValueError('unexpected_symlink')
        if path.is_file(): result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def attributes(path):
    names = subprocess.check_output(['xattr',str(path)],text=True).splitlines()
    return {name:subprocess.check_output(['xattr','-px',name,str(path)],text=True).strip() for name in names}

if DEST.exists(): raise ValueError('output_collision')
before = hashes(SOURCE)
assert before['TVTestRigFixture.debug.dylib'] == '46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095'
source_attrs = attributes(SOURCE)
shutil.copytree(SOURCE, DEST, copy_function=shutil.copy2)
removed = []
for path in [DEST, *DEST.rglob('*')]:
    for name in ('com.apple.FinderInfo', 'com.apple.ResourceFork'):
        if name in attributes(path):
            subprocess.run(['xattr','-d',name,str(path)],check=True,timeout=10)
            removed.append({'path':str(path.relative_to(DEST)), 'attribute':name})
assert hashes(DEST) == before == hashes(SOURCE)
assert source_attrs == attributes(SOURCE)
command=['codesign','--verify','--deep','--strict',str(DEST)]
result=subprocess.run(command,capture_output=True,text=True,timeout=30)
receipt={'source':str(SOURCE),'destination':str(DEST),'fileSHA256':before,
         'removedFromCopyOnly':removed,'sourceBytesAndRootAttributesUnchanged':True,
         'verification':{'command':command,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},
         'resigned':False,'installed':False}
with (HERE/'stage-receipt.json').open('x') as stream: json.dump(receipt,stream,indent=2)
print(json.dumps(receipt,indent=2))
raise SystemExit(result.returncode)
