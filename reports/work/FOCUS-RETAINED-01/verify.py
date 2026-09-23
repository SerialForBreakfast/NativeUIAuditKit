"""Final offline verification; project-local outputs and no runtime operations."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"),
         CLANG_MODULE_CACHE_PATH=str(ROOT/".build/module-cache"),SWIFT_MODULECACHE_PATH=str(ROOT/".build/module-cache"))
opts=["--disable-automatic-resolution","--cache-path",str(ROOT/".build/swiftpm-cache"),
      "--config-path",str(ROOT/".build/swiftpm-config"),"--security-path",str(ROOT/".build/swiftpm-security")]
commands=[("python",[sys.executable,"-m","unittest","test_focus_retained_review","test_direct_tvos_resume","test_direct_tvos_capture","-v"],ROOT/"scripts"),
          ("swift-build",["swift","build",*opts],ROOT),("swift-test",["swift","test",*opts],ROOT)]
rows=[]
for label,command,cwd in commands:
    start=time.monotonic()
    with (HERE/(label+".log")).open("x") as f: r=subprocess.run(command,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
    rows.append({"command":command,"exitCode":r.returncode,"seconds":time.monotonic()-start})
    print(json.dumps(rows[-1]),flush=True)
    if r.returncode: break
with (HERE/"verification.json").open("x") as f: json.dump(rows,f,indent=2)
raise SystemExit(any(r["exitCode"] for r in rows))
