"""Read-only integrated evidence checks, with one new local check report."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from focus_ring_baseline import artifact_digest
from perception_benchmark import validate_manifest, verify_evidence

here = Path(__file__).resolve().parent
per = ROOT / "reports/work/PER-DATA"
sources = [ROOT / "scripts" / name for name in ("compress_focus_ring_coreml.py",
    "test_focus_compression.py", "perception_benchmark.py", "test_perception_native_review.py")]
sources += list(here.glob("*.py")) + list(per.glob("*.py"))
for path in sources: compile(path.read_text(), str(path), "exec")
for path in list(here.glob("*.json")) + list(per.glob("*.json")): json.loads(path.read_text())
manifest = json.loads((per / "manifest.json").read_text())
verified = verify_evidence(validate_manifest(manifest))
dispositions = json.loads((per / "dispositions.json").read_text())
for item in dispositions["members"]:
    if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
        raise ValueError("source_image_changed")
comparison = json.loads((here / "comparison.json").read_text())
run = ROOT / "NativeUITrainer/focus_ring_runs/fdr007-native-incremental"
for name, folder in (("fp16","export-01"),("int8","export-03-int8")):
    if artifact_digest(run / folder / "FocusRingDetector.mlpackage") != comparison["packageHashes"][name]:
        raise ValueError("source_model_changed")
report = {"status":"passed", "sourceImagesUnchanged":len(dispositions["members"]),
    "perceptionVerification":verified, "fp16AndInt8Unchanged":True,
    "sourceHashes":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    "coordination":"not_applicable", "modelGate":"not_assessed"}
with (here / "final-checks.json").open("x") as stream: json.dump(report,stream,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!="sourceHashes"}))
