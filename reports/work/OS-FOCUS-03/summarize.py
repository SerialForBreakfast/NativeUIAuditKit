"""Bind completed training and frozen challenge evidence; no inference or writes to models."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root/"scripts"))
from focus_learning_report import metrics

here = Path(__file__).resolve().parent
load = lambda path: json.loads(path.read_text())
before, after = load(here/"challenge-before.json"), load(here/"challenge-after.json")
run_path = root/"NativeUITrainer/focus_ring_runs/fdr007-native-incremental/experiment-result.json"
run = load(run_path)
assert before["source"] == after["source"] and before["runtime"] == after["runtime"]
assert before["shipped"]["sha256"] == after["shipped"]["sha256"]
assert run["status"] == "completed" and not run["releaseEligible"]
assert run["bestSHA256"] == after["candidate"]["sha256"]
assert run["protocolSHA256"] in after["isolationProtocols"]
assert [r["id"] for r in before["candidate"]["predictions"]] == [r["id"] for r in after["candidate"]["predictions"]]
selected = min(run["history"], key=lambda h: (h["validation"]["loss"], -h["epoch"]))
report = {"version": "native-focus-incremental-summary-v1", "releaseEligible": False,
    "pairCounts": {"train": 40, "validation": 9, "challenge": 6, "homeAdmitted": 0},
    "protocolSHA256": run["protocolSHA256"], "candidateSHA256": run["bestSHA256"],
    "selectedEpoch": selected["epoch"], "validationLoss": run["selected"]["loss"],
    "validation": metrics(run["selected"]["predictions"]),
    "challenge": {"shipped": before["shipped"]["metrics"], "previous": before["candidate"]["metrics"],
                  "incremental": after["candidate"]["metrics"]},
    "training": load(here/"fdr007-launch02-execution.json"),
    "trainingComputeSeconds": run["elapsedSeconds"],
    "evidence": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [run_path, here/"challenge-before.json", here/"challenge-after.json", here/"corpus-01/protocol.json"]},
    "conclusion": "Native Settings performance retained; no measured challenge gain over FDR-006. No additional training justified by this saturated stratum.",
    "limitations": ["One runtime/style/app, correlated pairs", "Validation used for checkpoint selection",
        "No retained fixture test, CoreML export parity, model-driven navigation or physical qualification"]}
with (here/"summary.json").open("x") as stream: json.dump(report, stream, indent=2)
print(json.dumps(report, indent=2))
