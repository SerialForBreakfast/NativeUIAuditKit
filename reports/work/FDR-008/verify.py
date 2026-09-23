"""Offline package checks after diagnostic reporting changes."""
import json
import os
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
env=dict(os.environ,TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"),
         CLANG_MODULE_CACHE_PATH=str(ROOT/".build/module-cache"),SWIFT_MODULECACHE_PATH=str(ROOT/".build/module-cache"))
opts=["--disable-automatic-resolution","--cache-path",str(ROOT/".build/swiftpm-cache"),
      "--config-path",str(ROOT/".build/swiftpm-config"),"--security-path",str(ROOT/".build/swiftpm-security")]
results=[]
for action in ("build","test"):
    command=["swift",action,*opts]; start=time.monotonic()
    with (HERE/("swift-"+action+".log")).open("x") as f:
        r=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
    results.append({"command":command,"exitCode":r.returncode,"seconds":time.monotonic()-start})
    if r.returncode: break
with (HERE/"verification.json").open("x") as f: json.dump(results,f,indent=2)
print(json.dumps(results)); raise SystemExit(any(r["exitCode"] for r in results))
