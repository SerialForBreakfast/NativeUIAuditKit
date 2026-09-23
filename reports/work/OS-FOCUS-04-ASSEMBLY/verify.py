"""Integrated offline validation once; no simulator or training."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
if len(sys.argv)>1:
    HERE=HERE/sys.argv[1]
    HERE.mkdir(exist_ok=False)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"),
         CLANG_MODULE_CACHE_PATH=str(ROOT/".build/module-cache"),SWIFT_MODULECACHE_PATH=str(ROOT/".build/module-cache"))
options=["--disable-automatic-resolution","--cache-path",str(ROOT/".build/swiftpm-cache"),
         "--config-path",str(ROOT/".build/swiftpm-config"),"--security-path",str(ROOT/".build/swiftpm-security")]
modules=["test_focus_mixed_assembly","test_focus_consumer_integration","test_focus_learning_experiment",
         "test_native_os_focus_dataset","test_focus_launch","test_ttr_sidecar_v2"]
commands=[("python",[sys.executable,"-m","unittest",*modules,"-v"],ROOT/"scripts"),
          ("swift-build",["swift","build",*options],ROOT), ("swift-test",["swift","test",*options],ROOT)]
results=[]
for label,cmd,cwd in commands:
    start=time.monotonic()
    with (HERE/(label+".log")).open("x") as f:
        r=subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
    results.append({"command":cmd,"label":label,"exitCode":r.returncode,"seconds":time.monotonic()-start})
    print(json.dumps(results[-1]),flush=True)
    if r.returncode: break
with (HERE/"verification.json").open("x") as f: json.dump(results,f,indent=2)
raise SystemExit(any(r["exitCode"] for r in results))
