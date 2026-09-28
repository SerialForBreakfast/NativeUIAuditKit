"""Admit reviewed Fixture training additions without relaxing model/evaluation gates."""
from collections import Counter, defaultdict
import json
import re

import focus_appearance_experiment as appearance
import focus_mixed_assembly as a
from focus_dataset_contract import ROOT, digest, local, text

INPUT_VERSION = "focus-training-extension-input-v1"
VERSION = "focus-training-extension-v1"
require = appearance.require


def pair_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["sourceID"], row["pairID"]].append(row)
    for members in groups.values():
        require(sorted(r["label"] for r in members) == [0, 1], "incomplete_pair")
    return groups


def extend(base, additions, protected, reserved_pixels=()):
    """Pure deterministic admission; preserved base members always take precedence."""
    rows = list(base["samples"])
    require(len({r["id"] for r in rows + additions}) == len(rows + additions), "duplicate_sample")
    seen = {}
    for key, members in pair_groups(rows).items():
        seen[tuple(r["crop"]["pixelSHA256"] for r in sorted(members, key=lambda r:r["label"]))] = key
    excluded_pixels = set(reserved_pixels) | {r[k]["pixelSHA256"] for r in rows + protected
                       if r["split"] != "train" for k in ("frame", "crop")}
    labels = {r["crop"]["pixelSHA256"]: r["label"] for r in rows + protected}
    dispositions = []
    for key, members in sorted(pair_groups(additions).items()):
        for r in members:
            require(r["manifestVersion"] == "1.5" and r["sourceKind"] == "simulatorFixture"
                    and r["split"] == "development" and r["priorUse"] == "development"
                    and set(r["sourceBlockers"]) == {"development_only_source_contract"},
                    "unapproved_or_incompatible_training_source")
        pixels = tuple(r["crop"]["pixelSHA256"] for r in sorted(members, key=lambda r:r["label"]))
        decision = {"sourceID": key[0], "pairID": key[1]}
        if any(r[k]["pixelSHA256"] in excluded_pixels for r in members for k in ("frame", "crop")):
            decision["disposition"] = "excluded-evaluation-overlap"
        elif any(r["crop"]["pixelSHA256"] in labels and labels[r["crop"]["pixelSHA256"]] != r["label"] for r in members) or pixels[0] == pixels[1]:
            decision["disposition"] = "excluded-contradictory-crop-labels"
        elif pixels in seen:
            decision.update(disposition="duplicate-pair", representative=list(seen[pixels]))
        else:
            decision["disposition"] = "admitted-training-pair"
            seen[pixels] = key
            for r in members:
                labels[r["crop"]["pixelSHA256"]] = r["label"]
                rows.append({**r, "originSplit": r["split"], "split": "train", "use": "train-candidate"})
        dispositions.append(decision)
    rows.sort(key=lambda r:r["id"])
    appearance.check_pairs(rows + protected)
    lineage = appearance.join_rows(rows + protected)
    require(not any(g["crossPartitionConflict"] for g in lineage["components"]), "cross_partition_lineage_conflict")
    require(any(d["disposition"] == "admitted-training-pair" for d in dispositions), "no_new_training_pairs")
    return rows, dispositions, lineage


def assemble(spec):
    require(isinstance(spec, dict) and spec.get("version") == INPUT_VERSION, "unsupported_training_extension")
    base = appearance.sealed(spec["base"], appearance.VERSION, "protocolSHA256")
    require(appearance.assemble(base["inputs"]) == base, "changed_base_candidate")
    sources = spec.get("additions")
    require(isinstance(sources, list) and sources and len({e["id"] for e in sources}) == len(sources), "invalid_addition_sources")
    additions = [r for entry in sources for r in a.source_rows(entry)]
    protected = appearance.sealed(base["inputs"]["protected"], "appearance-protected-evidence-audit-v1", "auditSHA256")["remotesSamples"]
    # Metadata-only comparison; never open or score protected challenge images.
    reserved = appearance.sealed(spec["reservedPixels"], "surface-crops-v1", "seal")
    reserved_pixels = {p for r in reserved["samples"] for p in (r["framePixelSHA256"], r["crop"]["pixelSHA256"])}
    rows, dispositions, lineage = extend(base, additions, protected, reserved_pixels)
    doc = {"version": VERSION, "inputs": spec, "scope": "reviewed-simulator-training-additions",
           "samples": rows, "dispositions": dispositions, "lineage": lineage,
           "sampling": appearance.weights(rows), "counts": dict(Counter(r["use"] for r in rows)),
           "admissionCounts": dict(Counter(d["disposition"] for d in dispositions)),
           "configuration": base["configuration"], "selection": base["selection"],
           "warmCheckpoint": base["warmCheckpoint"], "readinessBlockers": base["readinessBlockers"],
           "trainingEligible": False, "releaseEligible": False, "modelGatePassed": "not_assessed"}
    doc["protocolSHA256"] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = appearance.sealed(a.reference(path), VERSION, "protocolSHA256")
    require(assemble(doc["inputs"]) == doc, "changed_training_extension")
    require(arm == "warm-stretch", "unsupported_extension_arm")
    require(isinstance(run_name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_name), "explicit_safe_run_name_required")
    out = ROOT / "NativeUITrainer/focus_ring_runs" / run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out, *out.parents)), "output_collision")
    blockers = list(doc["readinessBlockers"])
    approval_ref = None
    try:
        require(approval_path is not None, "missing_experiment_approval")
        approval_ref = a.reference(local(approval_path))
        approval = a.object_json(a.checked(approval_ref))
        require(approval.get("version") == "focus-training-extension-approval-v1"
                and approval.get("approved") is True and approval.get("protocolSHA256") == doc["protocolSHA256"]
                and approval.get("arm") == arm and approval.get("runName") == run_name, "missing_or_stale_experiment_approval")
        text(approval.get("reviewer")); text(approval.get("reviewReference"))
    except (OSError, ValueError, KeyError, TypeError) as error:
        blockers.append(str(error))
    rows = [{"id":r["id"], "path":a.checked({k:r["crop"][k] for k in ("path","sha256")}),
             "label":float(r["label"]), "split":r["split"], "use":r["use"], "sourceKind":r["sourceKind"],
             "samplingWeight":doc["sampling"]["weights"].get(r["id"], 0.)}
            for r in doc["samples"] if r["use"] != "final-challenge"]
    return {"formatVersion":"focus-appearance-preflight-v1", "protocolVersion": VERSION,
            "configurationValid":True, "launchEligible":not blockers, "blockers":blockers,
            "executionAuthorized":False, "releaseEligible":False,
            **{k:doc[k] for k in ("configuration","selection","protocolSHA256","sampling","warmCheckpoint","counts","admissionCounts")},
            "protocolFile":a.reference(path), "approval":approval_ref, "arm":arm,
            "output":str(out.relative_to(ROOT))}, rows
