"""Execute the single authorized FDR-008 candidate, retain logs, never retry."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
command=[sys.executable,"-u",str(ROOT/"scripts/train_focus_ring_detector.py"),
         "--experiment-protocol",str(ROOT/"reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json"),
         "--experiment-approval",str(HERE/"approval.json"),"--experiment-arm","warm-stretch",
         "--name","fdr008-mixed-appearance","--execute","--experiment-id","FDR-008"]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"),
         TORCH_HOME=str(ROOT/"NativeUITrainer/.torch"),MPLCONFIGDIR=str(ROOT/"NativeUITrainer/.mplconfig"),
         XDG_CACHE_HOME=str(ROOT/".build/debug-output/focus-launch/cache"))
start=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
with (HERE/"training.log").open("x") as log:
    process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    with (HERE/"started.json").open("x") as f:
        json.dump({"pid":process.pid,"startedAt":started,"command":command,"timeoutSeconds":2100},f,indent=2)
    print(json.dumps({"pid":process.pid,"startedAt":started}),flush=True)
    try: code=process.wait(timeout=2100)
    except subprocess.TimeoutExpired:
        process.terminate()
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
        code=124
result={"pid":process.pid,"startedAt":started,"endedAt":datetime.now(timezone.utc).isoformat(),
        "exitCode":code,"elapsedSeconds":time.monotonic()-start,"command":command}
with (HERE/"execution.json").open("x") as f: json.dump(result,f,indent=2)
print(json.dumps(result),flush=True)
raise SystemExit(code)
