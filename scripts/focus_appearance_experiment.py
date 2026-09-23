"""Appearance development adapter. Preflight never imports a model or grants execution."""
import json
import math
import re
from collections import Counter, defaultdict

import focus_mixed_assembly as a
import focus_development_experiment as legacy
import focus_appearance_proposal as proposal
from focus_dataset_contract import ROOT, FocusDataError, digest, local, pixel_digest, text

INPUT_VERSION = "focus-appearance-input-v1"
VERSION = "focus-appearance-experiment-v1"
SELECTION = "minimum-equal-source-validation-bce-retention-floor-earliest-tie"
CONFIG = {**legacy.CONFIG, "selection": SELECTION}
STRATA = {"dense-dark-media", "bright-unfocused-artwork", "gray-blank-placeholders",
          "dock-neighbor-focus", "photos-buttons"}
FIXTURE_KINDS = {"tvos_native_generator", "simulatorFixture"}


def require(ok, reason):
    if not ok:
        raise FocusDataError(reason)


def sealed(ref, version, field):
    doc = a.object_json(a.checked(ref))
    require(doc.get("version") == version, "unsupported_appearance_contract")
    require(doc.get(field) == digest({k:v for k,v in doc.items() if k != field}), "changed_appearance_contract")
    return doc


def reconstruct(spec):
    saved = sealed(spec["proposal"], "focus-appearance-proposal-v1", "proposalSHA256")
    refs = saved["inputs"]
    require(len(refs) >= 3, "missing_proposal_inputs")
    for ref in refs:
        a.checked(ref)
    # Reconstruct native/retained labels and production crops, not just a new seal.
    legacy.load(a.checked(refs[0]))
    rebuilt = proposal.audit(*(a.checked(ref) for ref in refs[:3]))
    stable = lambda d: {k:v for k,v in d.items() if k not in {"seconds", "proposalSHA256"}}
    require(stable(saved) == stable(rebuilt), "changed_proposal_membership_or_weights")
    protected = sealed(spec["protected"], "appearance-protected-evidence-audit-v1", "auditSHA256")
    require(protected.get("proposal") == spec["proposal"], "unbound_protected_evidence")
    for ref in protected["remotesInputs"]:
        a.checked(ref)
    manifest = a.checked(protected["remotesInputs"][1])
    expected = []
    native = a.object_json(manifest)
    for item in a.native_pairs(native, manifest):
        p = item["pair"]
        for role,label in (("focused",1),("unfocused",0)):
            expected.append({"id":"protected-remotes:"+p["pair_id"]+":"+role,"sourceID":"remotes",
                "pairID":p["pair_id"],"sourceKind":native["sourceKind"],"split":"challenge",
                "relatedGroup":native["lineage"],"intrinsicGroup":native["lineage"],"recipeSeed":None,
                "frame":a.record(item["source"],p["frames"][role]),"crop":item["crops"][role],
                "label":label,"proposedRole":"known-retention-challenge"})
    require(expected == protected["remotesSamples"], "changed_protected_membership")
    visual = set()
    for source in protected["visualDiagnostics"]:
        doc = a.object_json(a.checked(source["protocol"]))
        require(doc.get("protocolSHA256") == digest({k:v for k,v in doc.items() if k != "protocolSHA256"}), "changed_visual_protocol")
        expected_frames = {(r["path"],r["sha256"]) for r in doc["samples"]}
        require(expected_frames == {(r["path"],r["sha256"]) for r in source["frames"]}, "changed_visual_inventory")
        for r in source["frames"]:
            a.checked({k:r[k] for k in ("path","sha256")})
            require(pixel_digest(ROOT,r) == r["pixelSHA256"], "changed_visual_pixels")
            visual.add(r["pixelSHA256"])
    return saved, expected, visual


def logical(row):
    require(row["sourceKind"] in FIXTURE_KINDS | {"tvos_simulator_os"}, "unsupported_sampling_source")
    return "fixture" if row["sourceKind"] in FIXTURE_KINDS else "native"


def join_rows(rows):
    # Seed groups cannot evade isolation by changing capture adapters.
    return proposal.components([{**r,"sourceKind":logical(r)} for r in rows])


def weights(rows):
    candidates = [{**r,"sourceKind":logical(r),"proposedRole":"train-candidate"}
                  for r in rows if r["split"] == "train"]
    require({r["sourceKind"] for r in candidates} == {"native","fixture"}, "missing_sampling_source")
    result = proposal.balanced_weights(candidates)
    return {"policy":"equal-native-fixture-stratum-label-v1", "basis":"training-only",
            "weights":result["probabilities"],"sourceMass":result["sourceMass"],
            "effectiveSampleSize":result["effectiveSampleSize"]}


def check_pairs(rows):
    pairs = defaultdict(list)
    for r in rows:
        require(type(r["label"]) is int and r["label"] in (0,1), "invalid_label")
        pairs[r["sourceID"],r["pairID"]].append(r)
    contents = set()
    for members in pairs.values():
        require(sorted(r["label"] for r in members) == [0,1], "incomplete_pair")
        key = tuple(r["crop"]["pixelSHA256"] for r in sorted(members,key=lambda r:r["label"]))
        require(key not in contents, "duplicate_pair_disposition_required")
        contents.add(key)


def selection_check(selection, rows, warm):
    require(isinstance(selection,dict) and selection.get("policy") == SELECTION
            and selection.get("threshold") == .85, "unresolved_checkpoint_selection")
    floor = selection.get("nativeRetentionFloor")
    require(type(floor) in (int,float) and math.isfinite(floor) and 0 <= floor <= 1, "invalid_retention_floor")
    reference = a.object_json(a.checked(selection["reference"]))
    native = [r for r in rows if r["use"] == "retention-validation"]
    require(reference.get("version") == "appearance-retention-reference-v1"
            and reference.get("model") == warm and reference.get("threshold") == .85
            and reference.get("membershipSHA256") == digest(native), "unbound_retention_reference")
    text(reference.get("reviewer")); text(reference.get("reviewReference"))
    predictions = reference.get("predictions",[])
    require(len(predictions) == len(native) and {p["id"] for p in predictions} == {r["id"] for r in native}, "retention_prediction_membership")
    labels = {r["id"]:r["label"] for r in native}
    for p in predictions:
        require(type(p["probability"]) in (int,float) and math.isfinite(p["probability"])
                and 0 <= p["probability"] <= 1 and p["label"] == labels[p["id"]], "invalid_retention_prediction")
    accuracy = sum((p["probability"] >= .85) == bool(p["label"]) for p in predictions)/len(native)
    require(floor == accuracy, "retention_floor_differs_from_frozen_reference")


def assemble(spec):
    require(isinstance(spec,dict) and spec.get("version") == INPUT_VERSION, "unsupported_appearance_input")
    saved, protected, visual = reconstruct(spec)
    warm = saved["initializationProposal"]; a.checked(warm)
    rows = []
    for source in saved["samples"]:
        use = {"train-candidate":"train", "retention-validation":"validation"}.get(source["proposedRole"])
        require(use is not None, "invalid_proposal_role")
        rows.append({**source,"originSplit":source["split"],"split":use,"use":source["proposedRole"]})
    for entry in spec.get("additions",[]):
        for source in a.source_rows(entry):
            require(source["manifestVersion"] in {"1.4","1.5"} and source["split"] == "development"
                    and source["priorUse"] == "development" and source["sourceKind"] in FIXTURE_KINDS
                    and set(source["sourceBlockers"]) <= {"development_only_source_contract","source_training_review_required"}, "invalid_development_addition")
            rows.append({**source,"originSplit":source["split"],"split":"train","use":"train-candidate"})
    for entry in spec.get("evaluation",[]):
        role = entry["role"]
        require(role in {"appearance-validation","final-challenge"} and entry["stratum"] in STRATA, "invalid_evaluation_role_or_stratum")
        review = a.object_json(a.checked(entry["source"]["review"]))
        family = text(review.get("independentFamily"))
        reservation = a.object_json(a.checked(entry["reservation"]))
        require(reservation.get("version") == "appearance-evaluation-reservation-v2"
                and reservation.get("role") == role and reservation.get("stratum") == entry["stratum"]
                and reservation.get("family") == family and reservation.get("previouslyUsed") is False,
                "invalid_evaluation_reservation")
        text(reservation.get("reviewer")); text(reservation.get("reviewReference"))
        source_rows = a.source_rows(entry["source"])
        require(reservation.get("source") == entry["source"]
                and reservation.get("membershipSHA256") == digest(sorted(source_rows,key=lambda r:r["id"])),
                "unbound_evaluation_reservation")
        for source in source_rows:
            require(source["priorUse"] == "untouched"
                    and set(source["sourceBlockers"]) <= {"source_training_review_required"}
                    and source["split"] == ("validation" if role == "appearance-validation" else "test"), "reused_or_ineligible_evaluation")
            require(not any(source[k]["pixelSHA256"] in visual for k in ("frame","crop")), "known_visual_evaluation_reuse")
            rows.append({**source,"originSplit":source["split"],"use":role,"evaluationStratum":entry["stratum"],
                         "independentFamily":family})
    rows.sort(key=lambda r:r["id"])
    check_pairs(rows+protected)
    # Retain source review lineage AND the broader family reservation in the graph.
    audit_rows = rows+protected
    lineage = join_rows(audit_rows)
    require(not any(g["crossPartitionConflict"] for g in lineage["components"]), "cross_partition_lineage_conflict")
    blockers = []
    for role in ("appearance-validation","final-challenge"):
        for stratum in sorted(STRATA):
            group_ids = set()
            for g in lineage["components"]:
                members = [r for r in rows if r["id"] in g["samples"] and r["use"] == role and r.get("evaluationStratum") == stratum]
                if {r["label"] for r in members} == {0,1}: group_ids.add(g["id"])
            if len(group_ids) < 2: blockers.append("insufficient_independent_"+role+":"+stratum)
    selection = spec.get("selection")
    try: selection_check(selection,rows,warm)
    except (OSError,ValueError,KeyError,TypeError) as error: blockers.append(str(error))
    doc = {"version":VERSION,"inputs":spec,"scope":"development-only-balanced-appearance",
           "samples":rows,"sampling":weights(rows),"lineage":lineage,"configuration":CONFIG,
           "selection":selection,"warmCheckpoint":warm,"readinessBlockers":sorted(set(blockers)),
           "trainingEligible":False,"releaseEligible":False,"modelGatePassed":"not_assessed",
           "counts":dict(Counter(r["use"] for r in rows)),
           "partialDuplicateCrops":{k:v for k,v in _duplicates(rows).items() if len(v)>1}}
    doc["protocolSHA256"] = digest(doc)
    return doc


def _duplicates(rows):
    result = defaultdict(list)
    for r in rows: result[r["crop"]["pixelSHA256"]].append(r["id"])
    return dict(result)


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = sealed(a.reference(path),VERSION,"protocolSHA256")
    require(assemble(doc["inputs"]) == doc, "changed_appearance_membership_or_weights")
    require(arm == "warm-stretch", "unsupported_appearance_arm")
    require(isinstance(run_name,str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}",run_name), "explicit_safe_run_name_required")
    out = ROOT/"NativeUITrainer/focus_ring_runs"/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), "output_collision")
    blockers = list(doc["readinessBlockers"]); approval_ref = None
    try:
        require(approval_path is not None,"missing_experiment_approval")
        approval_ref = a.reference(local(approval_path)); approval = a.object_json(a.checked(approval_ref))
        require(approval.get("version") == "focus-appearance-approval-v1" and approval.get("approved") is True
                and approval.get("protocolSHA256") == doc["protocolSHA256"] and approval.get("runName") == run_name
                and approval.get("arm") == arm, "missing_or_stale_experiment_approval")
        text(approval.get("reviewer")); text(approval.get("reviewReference"))
    except (OSError,ValueError,KeyError,TypeError) as error: blockers.append(str(error))
    # Challenge membership is audited above but is never exposed to training loaders.
    rows = [{"id":r["id"],"path":a.checked({k:r["crop"][k] for k in ("path","sha256")}),
             "label":float(r["label"]),"split":r["split"],"use":r["use"],"sourceKind":r["sourceKind"],
             "samplingWeight":doc["sampling"]["weights"].get(r["id"],0.)}
            for r in doc["samples"] if r["use"] != "final-challenge"]
    return {"formatVersion":"focus-appearance-preflight-v1","configurationValid":True,
            "launchEligible":not blockers,"blockers":blockers,"executionAuthorized":False,"releaseEligible":False,
            **{k:doc[k] for k in ("configuration","selection","protocolSHA256","sampling","warmCheckpoint","counts")},
            "protocolFile":a.reference(path),"approval":approval_ref,"arm":arm,"output":str(out.relative_to(ROOT))}, rows


def selection_metrics(predictions, rows, selection):
    """Pure scoring used by the existing trainer; no model dependency."""
    require(len(predictions) == len(rows) and [p["id"] for p in predictions] == [r["id"] for r in rows], "validation_membership_mismatch")
    losses = defaultdict(list); retention = []
    for p,r in zip(predictions,rows):
        probability = p["probability"]
        require(math.isfinite(probability) and 0 <= probability <= 1 and p["label"] == r["label"], "invalid_validation_prediction")
        group = "native" if r["use"] == "retention-validation" else "appearance"
        probability = max(1e-12,min(1-1e-12,probability))
        losses[group].append(-math.log(probability if r["label"] else 1-probability))
        if group == "native": retention.append((p["probability"] >= selection["threshold"]) == bool(r["label"]))
    require(set(losses) == {"native","appearance"}, "missing_selection_partition")
    accuracy = sum(retention)/len(retention)
    return {"selectionLoss":sum(sum(v)/len(v) for v in losses.values())/2,
            "nativeRetentionAccuracy":accuracy,"checkpointEligible":accuracy >= selection["nativeRetentionFloor"]}
