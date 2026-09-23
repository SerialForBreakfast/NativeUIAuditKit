"""Summarize retained inference; never tune thresholds or rerun models."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median

HERE=Path(__file__).resolve().parent
protocol=json.loads((HERE/"protocol.json").read_text())
source=HERE/"evaluation/report.json"
report=json.loads(source.read_text())
rows={r["id"]:r for r in protocol["samples"]}
base={r["id"] for r in rows.values() if r["variant"]=="base"}
summary={"reportSHA256":hashlib.sha256(source.read_bytes()).hexdigest(),
    "reviewedFrames":2,"reviewedBoxes":4,"correlatedVariantsPerBox":7,"models":{},
    "trainingEligible":False,"releaseEligible":False}
for name,result in report["results"].items():
    groups={}
    for item in result["scores"]:
        row=rows[item["id"]]; key=row["frameID"]+":"+row["elementID"]
        groups.setdefault(key,[]).append(item["probability"])
    summary["models"][name]={"base":result["evaluation"]["base"],
        "baseProbabilities":[r for r in result["scores"] if r["id"] in base],
        "sensitivityFrameDecisions":dict(Counter(d["decision"] for name,e in result["evaluation"].items() if name!="base" for d in e["frameDecisions"])),
        "probabilityRanges":{k:{"min":min(v),"max":max(v),"crosses085":min(v)<.85<=max(v)} for k,v in groups.items()},
        "modelLoads":result["timing"],
        "firstPredictionMilliseconds":result["scores"][0]["inferenceMilliseconds"],
        "warmMedianMilliseconds":median(r["inferenceMilliseconds"] for r in result["scores"][1:]),
        "cropMedianMilliseconds":median(r["cropMilliseconds"] for r in result["scores"])}
for scope,items in (("base",[r for r in report["compressionDifferences"] if r["id"] in base]),("allVariants",report["compressionDifferences"])):
    maximum=max(r["absoluteError"] for r in items)
    summary["compression-"+scope]={"maxAbsoluteError":maximum,
        "thresholdDisagreements":sum(bool(r["disagreedThresholds"]) for r in items),
        "withinPreviouslyFrozen001Tolerance":maximum<=.01,
        "worst":max(items,key=lambda r:r["absoluteError"])}
with (HERE/"summary.json").open("x") as stream: json.dump(summary,stream,indent=2)
print(json.dumps(summary,indent=2))
