"""Summarize frozen inference without rerunning or tuning models."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
protocol = json.loads((HERE/"protocol.json").read_text())
source = HERE/"evaluation/report.json"
report = json.loads(source.read_text())
rows = {r["id"]:r for r in protocol["samples"]}
base = {r["id"] for r in rows.values() if r["variant"] == "base"}
# Reconstruct the exact infer_bounded boundaries, not scores[1:] as "warm".
starts, count, pixels = [0], 0, 0
for index,row in enumerate(protocol["samples"]):
    with Image.open(ROOT/row["path"]) as image: area = image.width*image.height
    if count and (pixels+area>80_000_000 or count==128):
        starts.append(index); count,pixels = 0,0
    count += 1; pixels += area
summary = {"reportSHA256":hashlib.sha256(source.read_bytes()).hexdigest(),
           **report["support"], "models":{}, "trainingEligible":False, "releaseEligible":False}
for name,result in report["results"].items():
    if len(starts) != len(result["timing"]): raise ValueError("batch_accounting_mismatch")
    groups = {}
    for item in result["scores"]:
        row=rows[item["id"]]; key=row["frameID"]+":"+row["elementID"]
        groups.setdefault(key,[]).append(item["probability"])
    first=[r["inferenceMilliseconds"] for i,r in enumerate(result["scores"]) if i in starts]
    warm=[r["inferenceMilliseconds"] for i,r in enumerate(result["scores"]) if i not in starts]
    summary["models"][name] = {
        "base":result["evaluation"]["base"],
        "baseProbabilities":[r for r in result["scores"] if r["id"] in base],
        "sensitivityFrameDecisions":dict(Counter(d["decision"] for variant,e in result["evaluation"].items()
                                                    if variant!="base" for d in e["frameDecisions"])),
        "probabilityRanges":{k:{"min":min(v),"max":max(v),"crosses085":min(v)<.85<=max(v)} for k,v in groups.items()},
        "batchCount":len(starts), "firstPredictionPerBatchMedianMilliseconds":median(first),
        "firstPredictionPerBatchRangeMilliseconds":[min(first),max(first)],
        "warmMedianMilliseconds":median(warm),
        "cropMedianMilliseconds":median(r["cropMilliseconds"] for r in result["scores"]),
        "latencyScope":"CPU helper, repeated process/model loads; first per batch is not OS-cache-cold; no navigation latency"}
for scope,items in (("base",[r for r in report["compressionDifferences"] if r["id"] in base]),
                    ("allVariants",report["compressionDifferences"])):
    maximum=max(r["absoluteError"] for r in items)
    summary["compression-"+scope]={"maxAbsoluteError":maximum,
        "thresholdDisagreements":sum(bool(r["disagreedThresholds"]) for r in items),
        "withinPreviouslyFrozen001Tolerance":maximum<=.01,
        "worst":max(items,key=lambda r:r["absoluteError"])}
with (HERE/"summary.json").open("x") as f: json.dump(summary,f,indent=2)
print(json.dumps({"models":{k:{x:v[x] for x in ("sensitivityFrameDecisions","batchCount",
      "firstPredictionPerBatchMedianMilliseconds","warmMedianMilliseconds","cropMedianMilliseconds")}
      for k,v in summary["models"].items()},
      "compression":{k:v for k,v in summary.items() if k.startswith("compression-")}},indent=2))
