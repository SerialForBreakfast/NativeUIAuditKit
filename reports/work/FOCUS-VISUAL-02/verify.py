"""One integrated offline verification, with project-local explicit output/cache paths."""
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
options = ["--disable-automatic-resolution", "--cache-path", str(ROOT/".build/swiftpm-cache"),
           "--config-path", str(ROOT/".build/swiftpm-config"), "--security-path", str(ROOT/".build/swiftpm-security")]
commands = [("python",[sys.executable,"-m","unittest","test_focus_visual_comparison","-v"],ROOT/"scripts"),
            ("swift-build",["swift","build",*options],ROOT),
            ("swift-test",["swift","test",*options],ROOT)]
if len(sys.argv) > 1: commands = commands[1:]
results=[]
for label,command,cwd in commands:
    start=time.monotonic()
    with (HERE/(label+".log")).open("x") as log:
        result=subprocess.run(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    results.append({"label":label,"command":command,"exitCode":result.returncode,"seconds":time.monotonic()-start})
    print(json.dumps(results[-1]),flush=True)
    if result.returncode: break
with (HERE/"verification.json").open("x") as f: json.dump(results,f,indent=2)
raise SystemExit(any(r["exitCode"] for r in results))
