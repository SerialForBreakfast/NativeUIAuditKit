"""Configuration/data preflight shared with the real trainer. Never imports torch."""
import json
import math
import re
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, local, validate_manifest
from focus_ring_readiness import ReadinessError, validate


def preflight(dataset, name, epochs=30, batch=64, lr=3e-4, model="mobilenetv4_conv_small"):
    config_errors, blockers = [], []
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        config_errors.append("explicit_safe_run_name_required")
    if epochs != 30 or batch != 64 or not math.isfinite(lr) or lr != 3e-4 or model != "mobilenetv4_conv_small":
        config_errors.append("not_established_30_epoch_configuration")
    out = ROOT / "NativeUITrainer/focus_ring_runs" / (name or "UNASSIGNED")
    try:
        local(out)
    except FocusDataError:
        config_errors.append("outside_project_output")
    if out.exists() or out.is_symlink():
        config_errors.append("output_collision")
    rows, document = [], {}
    try:
        dataset = local(dataset)
        document = json.loads((dataset / "focus_dataset_manifest.json").read_text())
        rows = validate_manifest(document, dataset)
        if document.get("version") != "1.3":
            blockers.append("runtime_crop_parity_required")
        counts = {s: sum(r["split"] == s for r in rows) for s in ("train", "validation", "test")}
        if any(n == 0 for n in counts.values()):
            blockers.append("missing_required_partition")
        validate(rows, evidence_root=ROOT / document["sourceRoot"])
        if document["evidenceKind"] != "reviewed-fixture":
            blockers.append("test_only_evidence")
        approval = document.get("trainingApproval", {})
        # Explicit maintainer review, bound to immutable membership, not extraction success.
        if not isinstance(approval, dict) or approval.get("membershipSHA256") != digest(document["pairs"]) or not approval.get("reviewReference") or approval.get("approved") is not True:
            blockers.append("missing_corpus_approval")
    except (OSError, ValueError, FocusDataError, ReadinessError) as error:
        blockers.append(str(error))
    return {"formatVersion": "focus-training-preflight-v1", "configurationValid": not config_errors,
            "launchEligible": not config_errors and not blockers, "configurationErrors": config_errors,
            "blockers": blockers, "manifestSHA256": digest(document) if isinstance(document, dict) else None,
            "output": str(out.relative_to(ROOT)), "counts": {s: sum(r["split"] == s for r in rows) for s in ("train", "validation", "test", "development")},
            "configuration": {"epochs": epochs, "batch": batch, "lr": lr, "model": model,
                              "initialization": "fresh-random", "seed": 42, "inputSize": 256,
                              "augmentation": "horizontal-flip-0.5", "testDuringTraining": False},
            "executionAuthorized": False}
