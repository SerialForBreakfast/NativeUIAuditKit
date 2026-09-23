"""Compare existing immutable report results without additional inference."""
import hashlib
import json
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from focus_ring_baseline import artifact_digest
from export_focus_ring_coreml import package_size_report

HERE = Path(__file__).resolve().parent
old_path = ROOT / "reports/work/FOCUS-EXPORT-01/parity.json"
new_path = HERE / "parity.json"
old, new = [json.loads(p.read_text()) for p in (old_path, new_path)]
for field in ("referenceSHA256", "protocolSHA256", "checkpointSHA256", "runtime"):
    if old[field] != new[field]: raise ValueError("incompatible_reference:" + field)
first = {r["id"]: r for r in old["coremlSamples"]}
second = {r["id"]: r for r in new["coremlSamples"]}
if first.keys() != second.keys(): raise ValueError("membership_mismatch")
differences = [{"id": key, "fp16": first[key]["probability"], "int8": second[key]["probability"],
    "absoluteError": abs(first[key]["probability"]-second[key]["probability"]),
    "disagreedThresholds": [t for t in (.5,.7,.85) if (first[key]["probability"]>=t) != (second[key]["probability"]>=t)]} for key in first]
run = ROOT / "NativeUITrainer/focus_ring_runs/fdr007-native-incremental"
fp16, int8 = [run / name / "FocusRingDetector.mlpackage" for name in ("export-01", "export-03-int8")]
if artifact_digest(fp16) != "4d43d6f4aedb7d26e820c7c33d79fa4e21b28d64a25a683f03c6219e64ccdf02": raise ValueError("changed_fp16")
sizes = [package_size_report(p) for p in (fp16,int8)]
timing = {}
for name, data in (("fp16",old),("int8",new)):
    timing[name] = {"loadMilliseconds": [r["modelLoadMilliseconds"] for r in data["coremlTiming"]],
        "firstPredictionMilliseconds": [data["coremlSamples"][i]["inferenceMilliseconds"] for i in (0,9)],
        "warmMedianMilliseconds": median(r["inferenceMilliseconds"] for i,r in enumerate(data["coremlSamples"]) if i not in (0,9)),
        "cropMedianMilliseconds": median(r["cropMilliseconds"] for r in data["coremlSamples"])}
result = {"formatVersion": "focus-compression-comparison-v1", "releaseEligible": False,
    "reportHashes": {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (old_path,new_path)},
    "packageHashes": {"fp16":artifact_digest(fp16), "int8":artifact_digest(int8)},
    "sizes": dict(zip(("fp16","int8"),sizes)),
    "reductionPercent": 100*(1-sizes[1]["size_bytes"]/sizes[0]["size_bytes"]),
    "fp16Differences": differences, "maxFP16AbsoluteError": max(r["absoluteError"] for r in differences),
    "fp16ComparisonPassed": all(r["absoluteError"] <= .01 and not r["disagreedThresholds"] for r in differences),
    "torchComparisonPassed": new["comparison"]["passed"], "timing": timing,
    "limitations": new["limitations"] + ["Single sequential host trials; no statistically supported speedup claim."]}
with (HERE / "comparison.json").open("x") as stream: json.dump(result,stream,indent=2)
print(json.dumps({k:v for k,v in result.items() if k != "fp16Differences"},indent=2))
