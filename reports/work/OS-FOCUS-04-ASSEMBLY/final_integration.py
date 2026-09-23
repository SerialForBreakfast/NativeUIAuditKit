"""Final real entrypoint verification; preserve earlier iteration outputs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from focus_mixed_assembly import reference
out=HERE/"final"; out.mkdir(exist_ok=False)
commands=[]
def run(label,args,expected=0):
    command=[sys.executable,*map(str,args)]; start=time.monotonic()
    with (out/(label+".log")).open("x") as f:
        r=subprocess.run(command,cwd=ROOT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},
                         stdout=f,stderr=subprocess.STDOUT,timeout=300)
    commands.append({"label":label,"command":command,"exitCode":r.returncode,"expectedExitCode":expected,"seconds":time.monotonic()-start})
    print(json.dumps(commands[-1]),flush=True)
    if r.returncode!=expected: raise ValueError("unexpected_exit_"+label)
try:
    run("native",[ROOT/"scripts/focus_mixed_assembly.py","--input",HERE/"native-current-input.json","--output",out/"native"])
    spec=json.loads((HERE/"mixed-current-input.json").read_text())
    spec["previous"]=reference(out/"native/focus_dataset_manifest.json")
    with (out/"input.json").open("x") as f: json.dump(spec,f,indent=2)
    run("mixed",[ROOT/"scripts/focus_mixed_assembly.py","--input",out/"input.json","--output",out/"mixed"])
    run("preflight",[ROOT/"scripts/train_focus_ring_detector.py","--dataset",out/"mixed",
                     "--name","mixed-readiness-not-a-run","--preflight"],2)
    report=json.loads((out/"preflight.log").read_text())
    if report.get("counts")!={"train":40,"validation":9,"test":0,"development":2}: raise ValueError("unexpected_support")
    if set(report["blockers"])!={"missing_required_partition","missing_corpus_approval","source_training_review_required","underfilled_quota"}:
        raise ValueError("unexpected_preflight_blocker")
    if (ROOT/report["output"]).exists(): raise ValueError("preflight_created_run")
    assembly=json.loads((out/"mixed/focus_dataset_manifest.json").read_text())
    if len(assembly["delta"]["addedSamples"])!=4 or assembly["delta"]["addedSources"]!=["direct-dialog"]:
        raise ValueError("unexpected_delta")
    summary={"assemblySHA256":assembly["assemblySHA256"],"counts":report["counts"],"blockers":report["blockers"],
             "diagnosticOnlyBlockers":report["diagnosticOnlyBlockers"],"retainedSamples":98,"addedSamples":4,
             "trainingSampleCount":len(report["sampling"]["weights"]),"strata":report["sampling"]["strata"],
             "configurationValid":report["configurationValid"],"launchEligible":report["launchEligible"],
             "baseline":report["baseline"],"executionAuthorized":False}
    with (out/"summary.json").open("x") as f: json.dump(summary,f,indent=2)
finally:
    with (out/"execution.json").open("x") as f: json.dump(commands,f,indent=2)
