"""Prepare retained evidence and real trainer preflight; never authorizes a run."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from focus_mixed_assembly import reference

spec={"version":"focus-development-input-v1",
      "nativeInput":reference(ROOT/"reports/work/OS-FOCUS-04-ASSEMBLY/native-current-input.json"),
      "retainedReview":reference(ROOT/"reports/work/FOCUS-RETAINED-01/audit/review.json"),
      "dispositions":reference(ROOT/"reports/work/FOCUS-RETAINED-01/dispositions.json"),
      "baseline":reference(ROOT/"NativeUITrainer/focus_ring_runs/fdr007-native-incremental/weights/best.pt"),
      "excludedDialogManifest":reference(ROOT/"dataset/focus_ring/direct-dialog-20260922-2147/focus_dataset_manifest.json")}
with (HERE/"input.json").open("x") as f: json.dump(spec,f,indent=2)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",TMPDIR=str(ROOT/".build/debug-output/focus-launch/tmp"))
commands=[("assembly",[sys.executable,"scripts/focus_mixed_assembly.py","--input",str(HERE/"input.json"),"--output",str(HERE/"dataset")],0),
          ("preflight",[sys.executable,"scripts/train_focus_ring_detector.py","--experiment-protocol",str(HERE/"dataset/focus_dataset_manifest.json"),
                        "--experiment-arm","warm-stretch","--name","mixed-appearance-development-proposed","--dry-run"],2),
          ("production-rejection",[sys.executable,"scripts/train_focus_ring_detector.py","--dataset",str(HERE/"dataset"),
                                  "--name","mixed-appearance-development-proposed","--preflight"],2)]
results=[]
for label,command,expected in commands:
    start=time.monotonic()
    with (HERE/(label+".log")).open("x") as f:
        r=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
    row={"step":label,"command":command,"exitCode":r.returncode,"expectedExitCode":expected,"seconds":time.monotonic()-start}
    results.append(row); print(json.dumps(row),flush=True)
    with (HERE/"execution.json").open("w") as f: json.dump(results,f,indent=2)
    if r.returncode!=expected: raise SystemExit(1)
doc=json.loads((HERE/"dataset/focus_dataset_manifest.json").read_text())
approval={"version":"focus-development-approval-v1","approved":False,"protocolSHA256":doc["protocolSHA256"],
          "runName":"mixed-appearance-development-proposed","arm":"warm-stretch", "reviewer":"", "reviewReference":""}
with (HERE/"approval-draft.json").open("x") as f: json.dump(approval,f,indent=2)
print(json.dumps({"counts":doc["counts"],"protocolSHA256":doc["protocolSHA256"],"approval":"not granted"}))
