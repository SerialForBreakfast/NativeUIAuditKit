"""FDR-008 appearance diagnostics using frozen reviews and production crops."""
import base64
from collections import Counter
import io
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"scripts"))
from focus_visual_comparison import validate_protocol, score, sha
from focus_learning_report import infer_bounded
from focus_mixed_assembly import reference, checked
from focus_dataset_contract import digest, pixel_digest
from focus_runtime import identity
from PIL import Image

training_path=ROOT/"reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json"
training=json.loads(training_path.read_text())
assert training["protocolSHA256"]==digest({k:v for k,v in training.items() if k!="protocolSHA256"})
known={r[k]["pixelSHA256"] for r in training["samples"] for k in ("frame","crop")}
models={"fdr007":training["warmCheckpoint"],
        "fdr008":reference(ROOT/"NativeUITrainer/focus_ring_runs/fdr008-mixed-appearance/weights/best.pt")}
run=json.loads((ROOT/"NativeUITrainer/focus_ring_runs/fdr008-mixed-appearance/experiment-result.json").read_text())
assert models["fdr008"]["sha256"]==run["bestSHA256"] and run["protocolSHA256"]==training["protocolSHA256"]
sources={}; started=time.monotonic()
for surface,folder in (("photos","FOCUS-VISUAL-01"),("home","FOCUS-VISUAL-02")):
    path=ROOT/"reports/work"/folder/"protocol.json"
    protocol=json.loads(path.read_text()); validate_protocol(protocol)
    prior_path=path.parent/"evaluation/report.json"; prior=json.loads(prior_path.read_text())
    assert prior["protocolSHA256"]==protocol["protocolSHA256"] and prior["models"]==protocol["models"]
    shipped=prior["results"]["shipped"]
    assert score(protocol["samples"],shipped["scores"])==shipped["evaluation"]
    for r in {r["path"]:r for r in protocol["samples"]}.values():
        assert pixel_digest(ROOT,{"path":r["path"],"sha256":r["sha256"]}) not in known
    sources[surface]={"protocol":reference(path),"referenceReport":reference(prior_path),
                      "document":protocol,"shipped":shipped}
frozen={"version":"focus-visual-checkpoint-comparison-v1","sources":{k:{x:v[x] for x in ("protocol","referenceReport")} for k,v in sources.items()},
        "models":models,"trainingProtocol":reference(training_path),"runtime":identity(),
        "thresholds":[.5,.70,.85],"trainingEligible":False,"releaseEligible":False}
frozen["protocolSHA256"]=digest(frozen)
with (HERE/"protocol.json").open("x") as f: json.dump(frozen,f,indent=2)

os.environ["TORCH_HOME"]=str(ROOT/"NativeUITrainer/.torch")
import numpy as np
import torch
from focus_ring_backbone import mobilenetv4_conv_small
classifiers={}
for name,ref in models.items():
    model=mobilenetv4_conv_small(pretrained=False,num_classes=1)
    model.load_state_dict(torch.load(checked(ref),map_location="cpu",weights_only=True)["state_dict"],strict=True)
    model.eval(); classifiers[name]=model
results={}
for surface,source in sources.items():
    rows=source["document"]["samples"]
    items=[{"id":r["id"],"path":str(ROOT/r["path"]),"sha256":r["sha256"],"bounds":r["bounds"]} for r in rows]
    rendered=infer_bounded(items,None)["results"]
    assert [r["id"] for r in rendered]==[r["id"] for r in rows]
    tensors=[]
    for r in rendered:
        raw=base64.b64decode(r["png"],validate=True)
        with Image.open(io.BytesIO(raw)) as im:
            assert im.size==(256,256)
            # Match focus_dataset_contract.pixel_digest's decoded-RGB convention.
            import hashlib
            assert hashlib.sha256(str(im.size).encode()+b"\0"+im.convert("RGB").tobytes()).hexdigest() not in known
            tensors.append(torch.from_numpy(np.array(im.convert("RGB"),copy=True)).permute(2,0,1).float().div(255))
    result={"shipped":{"backend":"CoreML CPU retained reference","evaluation":source["shipped"]["evaluation"]}}
    for name,model in classifiers.items():
        predictions=[]; start=time.monotonic()
        with torch.inference_mode():
            for offset in range(0,len(rows),32):
                probabilities=torch.sigmoid(model(torch.stack(tensors[offset:offset+32]))).view(-1).tolist()
                predictions.extend({"id":r["id"],"probability":p} for r,p in zip(rows[offset:offset+32],probabilities,strict=True))
        result[name]={"backend":"Torch CPU","seconds":time.monotonic()-start,
                      "scores":predictions,"evaluation":score(rows,predictions)}
    results[surface]=result
    with (HERE/(surface+".json")).open("x") as f: json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps({"surface":surface,"base":{k:dict(Counter(d["decision"] for d in v["evaluation"]["base"]["frameDecisions"])) for k,v in result.items()}}),flush=True)
for source in sources.values():
    validate_protocol(source["document"]); checked(source["protocol"]); checked(source["referenceReport"])
for ref in models.values(): checked(ref)
assert identity()==frozen["runtime"]; checked(frozen["trainingProtocol"])
report={"version":"focus-visual-checkpoint-report-v1","protocolSHA256":frozen["protocolSHA256"],
        "results":results,"seconds":time.monotonic()-started,"trainingEligible":False,"releaseEligible":False,
        "limitations":["Manual visual-only labels, not callback-ground-truth training data",
                        "Known development failures, not untouched evaluation; unknown journey relation stays unknown",
                        "Exact pixel separation is not semantic independence",
                        "Reviewer boxes; no localization, navigation, CoreML export parity or physical qualification"]}
with (HERE/"report.json").open("x") as f: json.dump(report,f,indent=2,allow_nan=False)
