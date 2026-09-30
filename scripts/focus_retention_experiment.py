"""Explicit retention-only development policy; full appearance gates stay unmet."""
from collections import Counter
import importlib.metadata
import math
import platform
import re
import sys

import focus_appearance_experiment as appearance
import focus_mixed_assembly as a
import focus_training_extension as extension
from focus_dataset_contract import ROOT, digest, local, text

VERSION = "focus-retention-experiment-v1"
INPUT_VERSION = "focus-retention-input-v1"
POLICY = "minimum-retention-bce-floor-earliest-tie"
FORMAT = "focus-retention-preflight-v1"
require = appearance.require


def runtime_identity():
    """Pin runtime and executable code without importing a model framework."""
    from focus_runtime import identity
    sources = ("train_focus_ring_detector.py", "focus_ring_backbone.py",
               "focus_retention_experiment.py", "focus_training_extension.py",
               "focus_learning_experiment.py", "focus_appearance_experiment.py",
               "focus_mixed_assembly.py", "focus_dataset_contract.py", "focus_runtime.py")
    return {"python": platform.python_version(), "environment": sys.prefix,
            "executable": sys.executable,
            "hostOS": platform.mac_ver()[0], "architecture": platform.machine(),
            "packages": {p: importlib.metadata.version(p) for p in ("torch", "numpy", "Pillow")},
            "code": [a.reference(ROOT/"scripts"/p) for p in sources], "crop": identity()}


def assemble(spec):
    require(isinstance(spec, dict) and spec.get("version") == INPUT_VERSION, "unsupported_retention_input")
    source = appearance.sealed(spec["extension"], extension.VERSION, "protocolSHA256")
    rows = source["samples"]
    require(rows and all((r["split"], r["use"]) in
            {("train", "train-candidate"), ("validation", "retention-validation")} for r in rows),
            "retention_only_membership_required")
    require({r["use"] for r in rows} == {"train-candidate", "retention-validation"}, "missing_retention_partition")
    require(source["counts"] == dict(Counter(r["use"] for r in rows)), "changed_retention_counts")
    appearance.check_pairs(rows)
    appearance.selection_check(source["selection"], rows, source["warmCheckpoint"])
    require(source["selection"]["nativeRetentionFloor"] == 1, "approved_perfect_retention_floor_required")
    expected = {f"insufficient_independent_{role}:{stratum}"
                for role in ("appearance-validation", "final-challenge") for stratum in appearance.STRATA}
    require(set(source["readinessBlockers"]) == expected, "unexpected_full_protocol_blockers")
    require(source["configuration"] == appearance.CONFIG and source["sampling"] == appearance.weights(rows),
            "changed_retention_configuration_or_sampling")
    a.checked(source["warmCheckpoint"])
    doc = {"version": VERSION, "inputs": spec, "runtime": runtime_identity(),
           "scope": "one-retention-selected-development-run", "samples": rows,
           "configuration": {**source["configuration"], "selection": POLICY},
           "selection": {**source["selection"], "policy": POLICY},
           "sampling": source["sampling"], "counts": source["counts"], "warmCheckpoint": source["warmCheckpoint"],
           "unmetQualificationBlockers": source["readinessBlockers"],
           "releaseEligible": False, "modelGatePassed": "not_assessed"}
    doc["protocolSHA256"] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = appearance.sealed(a.reference(path), VERSION, "protocolSHA256")
    require(doc == assemble(doc["inputs"]), "changed_retention_protocol_or_runtime")
    source = appearance.sealed(doc["inputs"]["extension"], extension.VERSION, "protocolSHA256")
    require(source == extension.assemble(source["inputs"]), "changed_retention_extension")
    require(arm == "warm-stretch", "unsupported_retention_arm")
    require(isinstance(run_name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_name), "explicit_safe_run_name_required")
    out = ROOT/"NativeUITrainer/focus_ring_runs"/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out, *out.parents)), "output_collision")
    approval_ref, blockers = None, []
    try:
        require(approval_path is not None, "missing_experiment_approval")
        approval_ref = a.reference(local(approval_path))
        approval = a.object_json(a.checked(approval_ref))
        require(approval.get("version") == "focus-retention-approval-v1" and approval.get("approved") is True
                and approval.get("protocolSHA256") == doc["protocolSHA256"]
                and approval.get("runName") == run_name and approval.get("arm") == arm,
                "missing_or_stale_retention_approval")
        text(approval.get("reviewer")); text(approval.get("reviewReference"))
    except (OSError, ValueError, KeyError, TypeError) as error:
        blockers.append(str(error))
    rows = [{"id": r["id"], "path": a.checked({k:r["crop"][k] for k in ("path", "sha256")}),
             "label": float(r["label"]), "split": r["split"], "use": r["use"], "sourceKind": r["sourceKind"],
             "samplingWeight": doc["sampling"]["weights"].get(r["id"], 0.)} for r in doc["samples"]]
    require(runtime_identity() == doc["runtime"], "changed_retention_runtime")
    return {"formatVersion": FORMAT, "configurationValid": True, "launchEligible": not blockers,
            "blockers": blockers, "executionAuthorized": False, "releaseEligible": False,
            **{k:doc[k] for k in ("runtime", "configuration", "selection", "sampling", "counts",
                                 "warmCheckpoint", "protocolSHA256", "unmetQualificationBlockers")},
            "protocolFile": a.reference(path), "approval": approval_ref, "arm": arm,
            "output": str(out.relative_to(ROOT))}, rows


def selection_metrics(predictions, rows, selection):
    require(selection.get("policy") == POLICY and selection.get("threshold") == .85
            and selection.get("nativeRetentionFloor") == 1, "invalid_retention_selection")
    require(rows and len({r["id"] for r in rows}) == len(rows)
            and all(r["use"] == "retention-validation" and r["split"] == "validation" for r in rows)
            and {r["label"] for r in rows} == {0, 1}, "invalid_retention_membership")
    require(len(predictions) == len(rows) and [p["id"] for p in predictions] == [r["id"] for r in rows],
            "validation_membership_mismatch")
    losses, correct = [], 0
    for p, r in zip(predictions, rows):
        probability = p["probability"]
        require(type(probability) in (int, float) and math.isfinite(probability) and 0 <= probability <= 1
                and p["label"] == r["label"], "invalid_validation_prediction")
        correct += (probability >= .85) == bool(r["label"])
        clipped = max(1e-12, min(1-1e-12, probability))
        losses.append(-math.log(clipped if r["label"] else 1-clipped))
    return {"selectionLoss": sum(losses)/len(losses), "nativeRetentionAccuracy": correct/len(rows),
            "retentionCorrect": correct, "retentionCount": len(rows), "checkpointEligible": correct == len(rows)}
