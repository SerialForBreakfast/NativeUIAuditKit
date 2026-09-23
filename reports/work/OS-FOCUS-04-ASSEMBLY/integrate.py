"""Real retained-data CLI assembly, additive upgrade and blocked trainer preflight."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from focus_mixed_assembly import reference

manifest=HERE/"root-runtime-crops/manifest.json"
source=json.loads(manifest.read_text())
old=json.loads((HERE/"settings-root-review.json").read_text())
review={**old,"manifestSHA256":reference(manifest)["sha256"],
        "reviewReference":str((HERE/"root-review.md").relative_to(ROOT)),
        "priorReview":reference(HERE/"root-review.md"),
        "pairs":{p["pair_id"]:{"partition":"train","relatedGroup":source["lineage"]} for p in source["pairs"]}}
reviewpath=HERE/"settings-root-current-review.json"
with reviewpath.open("x") as f: json.dump(review,f,indent=2)
entry={"id":"settings-root","manifest":reference(manifest),"review":reference(reviewpath)}
spec=json.loads((HERE/"native-input.json").read_text())
spec["sources"]=[entry if r["id"]=="settings-root" else r for r in spec["sources"]]
inputpath=HERE/"native-current-input.json"
with inputpath.open("x") as f: json.dump(spec,f,indent=2)
commands=[]
def run(label,args,expected=0):
    start=time.monotonic(); cmd=[sys.executable,*map(str,args)]
    with (HERE/(label+".log")).open("x") as log:
        r=subprocess.run(cmd,cwd=ROOT,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},
                         stdout=log,stderr=subprocess.STDOUT,timeout=300)
    commands.append({"label":label,"command":cmd,"exitCode":r.returncode,"expectedExitCode":expected,"seconds":time.monotonic()-start})
    print(json.dumps(commands[-1]),flush=True)
    if r.returncode!=expected: raise RuntimeError("unexpected_exit: "+label)
try:
    run("native-assembly",[ROOT/"scripts/focus_mixed_assembly.py","--input",inputpath,"--output",HERE/"native-v1"])
    mixed=json.loads((HERE/"mixed-input-template.json").read_text())
    mixed["sources"]=[entry if r["id"]=="settings-root" else r for r in mixed["sources"]]
    mixed["previous"]=reference(HERE/"native-v1/focus_dataset_manifest.json")
    mixedpath=HERE/"mixed-current-input.json"
    with mixedpath.open("x") as f: json.dump(mixed,f,indent=2)
    run("mixed-assembly",[ROOT/"scripts/focus_mixed_assembly.py","--input",mixedpath,"--output",HERE/"mixed-v2"])
    run("trainer-preflight",[ROOT/"scripts/train_focus_ring_detector.py","--dataset",HERE/"mixed-v2",
                             "--name","mixed-readiness-not-a-run","--preflight"],expected=2)
finally:
    with (HERE/"integration-execution.json").open("x") as f: json.dump(commands,f,indent=2)
