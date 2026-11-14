"""Build the pinned CORPUS640 renderer without starting a Simulator."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).resolve().with_name('main.swift')
EXPECTED='73ff3834488aae24ade150fb171eec79102181460c97ba406ee7bde46096d1d5'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,help='New build directory inside the project')
    args=parser.parse_args()
    dest=(ROOT/args.output).resolve()
    if not dest.is_relative_to(ROOT) or dest==ROOT or dest.exists():
        parser.error('Output must be a new directory inside the project')
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:
        raise SystemExit('Generator SHA-256 differs from the captured source')
    dest.mkdir(parents=True);app=dest/'Study.app';app.mkdir();cache=dest/'module-cache';cache.mkdir();tmp=dest/'tmp';tmp.mkdir()
    env=os.environ.copy();env.update(TMPDIR=str(tmp),CLANG_MODULE_CACHE_PATH=str(cache),SWIFT_MODULECACHE_PATH=str(cache))
    sdk=subprocess.check_output(['xcrun','--sdk','appletvsimulator','--show-sdk-path'],text=True,env=env).strip()
    command=['xcrun','--sdk','appletvsimulator','swiftc','-sdk',sdk,'-target','arm64-apple-tvos26.0-simulator','-module-cache-path',str(cache),str(SOURCE),'-o',str(app/'Study')]
    with (dest/'build.log').open('w') as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,env=env)
    shutil.copyfile(SOURCE.with_name('Info.plist'),app/'Info.plist')
    subprocess.run(['codesign','--force','--sign','-',str(app)],check=True,env=env)
    (dest/'build-receipt.json').write_text(json.dumps({'sourceSHA256':EXPECTED,'executableSHA256':hashlib.sha256((app/'Study').read_bytes()).hexdigest()},indent=2)+'\n')
    print('Built:',app)

if __name__=='__main__':main()
