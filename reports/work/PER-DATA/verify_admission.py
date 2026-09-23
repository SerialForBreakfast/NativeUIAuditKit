"""Adversarial checks on the real reviewed manifest, without modifying pixels."""
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from perception_benchmark import BenchmarkError, validate_manifest, verify_evidence

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "manifest.json").read_text())
results = []
for name, error, mutate, verify in [
    ("changed_bytes", "image_hash_mismatch", lambda d: d["cases"][0].update(imageSHA256="0"*64), True),
    ("unknown_chevron_relation", "ambiguous_chevron_relation", lambda d: d["cases"][0]["labels"].update(chevrons=[{"id":"bad", "visibility":"visible", "box":[1,1,4,4], "rowID":"unknown"}]), False),
    ("test_partition_upgrade", "native_review_not_development_eligible", lambda d: d["cases"][0].update(partition="test"), False),
    ("privacy_upgrade", "native_review_not_development_eligible", lambda d: d["cases"][0].update(privacyReview="pending"), False),
    ("prediction_as_truth", "unreviewed_or_prediction_labels", lambda d: d["cases"][0]["labels"].update(origin="modelPrediction"), False),
]:
    changed = deepcopy(manifest); mutate(changed)
    try:
        cases = validate_manifest(changed)
        if verify: verify_evidence(cases)
    except BenchmarkError as caught:
        if str(caught) != error: raise
        results.append({"case":name,"rejected":True,"reason":str(caught)})
    else: raise AssertionError("unexpected_admission:"+name)
with (HERE / "adversarial.json").open("x") as stream: json.dump(results,stream,indent=2)
print(json.dumps(results))
