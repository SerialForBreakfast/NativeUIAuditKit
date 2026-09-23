"""Post-run fixed-membership diagnostic comparison; never selects or trains weights."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from focus_dataset_contract import digest, image, pixel_digest
from focus_mixed_assembly import checked, reference
from focus_learning_report import metrics
from focus_learning_experiment import reviewed_native
from focus_runtime import identity

protocol=json.loads((ROOT/"reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json").read_text())
assert protocol["protocolSHA256"]==digest({k:v for k,v in protocol.items() if k!="protocolSHA256"})
run_dir=ROOT/"NativeUITrainer/focus_ring_runs/fdr008-mixed-appearance"
run=json.loads((run_dir/"experiment-result.json").read_text())
assert run["status"]=="completed" and run["protocolSHA256"]==protocol["protocolSHA256"] and len(run["history"])==30
rows=[]
for r in protocol["samples"]:
    ref={k:r["crop"][k] for k in ("path","sha256")}; checked(ref); image(ROOT,ref,(256,256))
    assert pixel_digest(ROOT,ref)==r["crop"]["pixelSHA256"]
    rows.append({"id":r["id"],"label":r["label"],"path":ref["path"],"sha256":ref["sha256"],
                 "split":r["split"],"sourceKind":r["sourceKind"],"theme":r["style"],"control":r["control"]})

# Reuse the previously qualified native challenge and FDR-007/shipped scores only
# after source/hash/runtime/lineage checks. It never influences checkpoint choice.
prior_path=ROOT/"reports/work/OS-FOCUS-03/challenge-after.json"
prior=json.loads(prior_path.read_text()); doc,source,pairs=reviewed_native(prior["source"])
assert prior["candidate"]["sha256"]==protocol["warmCheckpoint"]["sha256"]
assert prior["runtime"]==doc["runtime"]==identity()
known={r[k]["pixelSHA256"] for r in protocol["samples"] for k in ("crop","frame")}
assert doc["lineage"] not in {r["intrinsicGroup"] for r in protocol["samples"]}
assert all(f["pixelSHA256"] not in known for p in pairs for f in p["frames"].values())
for r in prior["candidate"]["predictions"]:
    path=Path(r["crop"]); path=path if path.is_absolute() else ROOT/path
    ref={"path":str(path.relative_to(ROOT)),"sha256":r["cropSHA256"]}
    checked(ref); image(ROOT,ref,(256,256))
    pixels=pixel_digest(ROOT,ref); assert pixels==r["pixelSHA256"] and pixels not in known
    rows.append({"id":r["id"],"label":r["label"],"path":ref["path"],"sha256":ref["sha256"],
                 "split":"challenge","sourceKind":"tvos_simulator_os","theme":"unknown","control":"settings/remotes"})
assert len({r["id"] for r in rows})==len(rows)
os.environ["TORCH_HOME"]=str(ROOT/"NativeUITrainer/.torch")
import numpy as np
import torch
from PIL import Image
from focus_ring_backbone import mobilenetv4_conv_small

def predict(ref):
    model=mobilenetv4_conv_small(pretrained=False,num_classes=1)
    model.load_state_dict(torch.load(checked(ref),map_location="cpu",weights_only=True)["state_dict"],strict=True)
    model.eval(); predictions=[]; start=time.monotonic()
    with torch.inference_mode():
        for offset in range(0,len(rows),32):
            batch=rows[offset:offset+32]; tensors=[]
            for r in batch:
                with Image.open(checked({k:r[k] for k in ("path","sha256")})) as im:
                    tensors.append(torch.from_numpy(np.array(im.convert("RGB"),copy=True)).permute(2,0,1).float().div(255))
            probabilities=torch.sigmoid(model(torch.stack(tensors))).view(-1).tolist()
            predictions.extend({**r,"probability":p} for r,p in zip(batch,probabilities,strict=True))
    checked(ref)
    groups={}
    for r in predictions:
        for group in (r["split"]+":"+r["sourceKind"],r["split"]+":"+r["sourceKind"]+":"+r["theme"]+":"+r["control"]):
            groups.setdefault(group,[]).append(r)
    return {"checkpoint":ref,"backend":"torch-cpu","seconds":time.monotonic()-start,
            "metrics":{k:metrics(v) for k,v in groups.items()},"predictions":predictions}

best=reference(run_dir/"weights/best.pt"); assert best["sha256"]==run["bestSHA256"]
before=predict(protocol["warmCheckpoint"]); after=predict(best)
assert [r["id"] for r in before["predictions"]]==[r["id"] for r in after["predictions"]]
selected=min(run["history"],key=lambda r:(r["validation"]["loss"],r["epoch"]))
result={"version":"focus-mixed-development-result-v1","protocolSHA256":run["protocolSHA256"],
        "selectedEpoch":selected["epoch"],"validationBCE":run["selected"]["loss"],
        "initialValidation":metrics(run["initial"]["predictions"]),"selectedValidation":metrics(run["selected"]["predictions"]),
        "before":before,"after":after,"priorChallenge":reference(prior_path),
        "shippedChallenge":prior["shipped"]["metrics"],"execution":json.loads((HERE/"execution.json").read_text()),
        "releaseEligible":False,"limitations":["Fixture scores are on training members, not independent evaluation",
            "Native validation selects checkpoints; challenge is reused development evidence",
            "Torch CPU diagnostic comparison is not CoreML export parity or physical-device qualification"]}
with (HERE/"comparison.json").open("x") as f: json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps({"selectedEpoch":result["selectedEpoch"],"validationBCE":result["validationBCE"],
                  "before":{k:v for k,v in before["metrics"].items() if k.count(":")==1},
                  "after":{k:v for k,v in after["metrics"].items() if k.count(":")==1}},indent=2))
