"""Offline integrated checks; all explicit outputs and caches stay project-local."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    HERE = HERE / sys.argv[1]
    HERE.mkdir(exist_ok=False)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"),
           CLANG_MODULE_CACHE_PATH=str(ROOT/".build/module-cache"), SWIFT_MODULECACHE_PATH=str(ROOT/".build/module-cache"))
modules = ["test_ttr_sidecar_v2", "test_harvest_bundle_validation", "test_focus_consumer_integration",
           "test_focus_launch", "test_focus_ring_baseline", "test_direct_tvos_capture", "test_direct_tvos_resume"]
options = ["--disable-automatic-resolution", "--cache-path", str(ROOT/".build/swiftpm-cache"),
           "--config-path", str(ROOT/".build/swiftpm-config"), "--security-path", str(ROOT/".build/swiftpm-security")]
commands = [("swift-build", ["swift","build",*options], ROOT),
            ("python",[sys.executable,"-m","unittest",*modules,"-v"],ROOT/"scripts"),
            ("swift-test", ["swift","test",*options], ROOT)]
results=[]
for label, command, cwd in commands:
    start=time.monotonic()
    with (HERE/(label+".log")).open("x") as log:
        r=subprocess.run(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    results.append({"label":label,"command":command,"exitCode":r.returncode,"seconds":time.monotonic()-start})
    print(json.dumps(results[-1]),flush=True)
    if r.returncode: break
with (HERE/"verification.json").open("x") as out: json.dump(results,out,indent=2)
raise SystemExit(any(r["exitCode"] for r in results))
