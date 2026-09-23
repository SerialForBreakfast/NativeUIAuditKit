"""Reviewed retained-recipe experiment adapter; no capture or model execution."""
import base64
import io
import json
import re
from collections import Counter

from PIL import Image
import focus_mixed_assembly as assembly
from focus_dataset_contract import ROOT, FocusDataError, digest, local, image, text
from focus_runtime import identity, invoke, RUNTIME_PREPROCESSING
from direct_tvos_resume import audit_chain
from direct_focus_manifest import pairs_from_capture

VERSION = "focus-development-experiment-v1"
INPUT_VERSION = "focus-development-input-v1"
CONFIG = {"epochs":30,"batch":64,"lr":0.0003,"seed":42,"maxSeconds":1800,
          "model":"mobilenetv4_conv_small","augmentation":"none","inputSize":256,
          "initialization":"warm-weights-fresh-optimizer","testDuringTraining":False,
          "selection":"minimum-native-validation-bce-earliest-tie"}
NATIVE_SPLITS = {"settings/root":"train","settings/general":"train",
                 "settings/apps":"train","settings/accessibility":"validation"}


def require(condition, message):
    if not condition:
        raise FocusDataError(message)


def sealed(ref, version, field):
    path = assembly.checked(ref)
    doc = assembly.object_json(path)
    require(doc.get("version") == version, "unsupported_development_input")
    require(doc.get(field) == digest({k:v for k,v in doc.items() if k != field}), "changed_development_input")
    return doc


def retained_rows(review_ref, disposition_ref):
    review = sealed(review_ref, "focus-retained-review-v1", "reviewSHA256")
    decisions = sealed(disposition_ref, "focus-retained-dispositions-v1", "dispositionsSHA256")
    require(decisions.get("reviewSHA256") == review["reviewSHA256"]
            and decisions.get("reviewFileSHA256") == review_ref["sha256"]
            and decisions.get("trainingEligible") is False, "unbound_dispositions")
    require(review.get("trainingEligible") is False and review.get("runtime") == identity()
            and review.get("preprocessing") == RUNTIME_PREPROCESSING, "changed_crop_runtime")
    sources = [assembly.checked({k:s[k] for k in ("path","sha256")}) for s in review["sources"]]
    entries, _, count = audit_chain(sources)
    require(all(e["doc"].get("evidenceKind") == "fixture-native-capture" for e in entries), "test_only_evidence")
    saved = {p["pairID"]:p for p in review["pairs"]}
    selected = {p["pairID"]:p for p in decisions["pairs"]}
    require(len(saved) == len(review["pairs"]) == count and len(selected) == len(decisions["pairs"])
            and set(saved) == set(selected), "retained_membership_mismatch")
    rows, seen, index, reconstructed = [], {}, 0, set()
    for entry in entries:
        root = entry["path"].parent
        for recipe in entry["doc"]["recipes"]:
            for pair in sorted(pairs_from_capture({"recipes":[recipe]}), key=lambda p:(p["elementID"],p["pair_id"])):
                pid = pair["pair_id"]
                require(pid in saved and pid not in reconstructed, "retained_membership_mismatch")
                reconstructed.add(pid)
                p, decision = saved[pid], selected[pid]
                metadata = {"catalogIndex":index,"family":pair["fixture_scene"],"theme":pair["theme"],
                            "seed":pair["recipe_seed"]}
                require(all(p.get(k)==v and decision.get(k)==v for k,v in metadata.items()), "changed_retained_metadata")
                require(p.get("labelSource")=="fixtureNativeInterval" and p.get("elementID")==pair["elementID"]
                        and p.get("control")==pair["element_type"] and p.get("partition")=="development"
                        and p.get("sourceReceiptSHA256")==entry["sha256"], "changed_retained_label")
                items, frame_records, crop_records, edges = [], {}, {}, []
                for role in ("focused","unfocused"):
                    frame = pair["frames"][role]; stored = p[role]
                    size = image(root,frame); x,y,w,h = frame["bounds"]
                    if x<=0 or y<=0 or x+w>=size[0] or y+h>=size[1]: edges.append(role+":viewport-edge")
                    actual = assembly.record(root,frame)
                    require(stored["path"]==actual["path"] and stored["sha256"]==actual["sha256"]
                            and stored["framePixelSHA256"]==actual["pixelSHA256"]
                            and stored["bounds"]==frame["bounds"] and stored["dimensions"]==list(size)
                            and stored["intervalSHA256"]==digest(frame["interval"]), "changed_retained_geometry_or_label")
                    crop = {"path":stored["cropPath"],"sha256":stored["cropSHA256"]}
                    image(ROOT,crop,(256,256)); crop = assembly.record(ROOT,crop)
                    require(crop["pixelSHA256"]==stored["cropPixelSHA256"], "changed_crop_pixels")
                    frame_records[role], crop_records[role] = actual,crop
                    items.append({"id":pid+role,"path":str(ROOT/actual["path"]),"sha256":actual["sha256"],"bounds":frame["bounds"]})
                rendered = invoke(items)["results"]
                require([r["id"] for r in rendered]==[i["id"] for i in items], "runtime_membership_mismatch")
                for role,result in zip(("focused","unfocused"),rendered,strict=True):
                    with Image.open(io.BytesIO(base64.b64decode(result["png"],validate=True))) as expected, Image.open(ROOT/crop_records[role]["path"]) as actual:
                        require(expected.size==(256,256) and expected.convert("RGB").tobytes()==actual.convert("RGB").tobytes(), "crop_pixel_mismatch")
                require(p["edgeFlags"]==edges and decision["edgeFlags"]==edges, "changed_edge_flags")
                if p["family"] == "focusMaze":
                    require(decision["disposition"]=="excluded-first-experiment", "unreviewed_maze")
                    continue
                require(decision.get("visualReview")=="both-production-crops-reviewed" and not edges, "visual_review_required")
                key = tuple(crop_records[r]["pixelSHA256"] for r in ("focused","unfocused"))
                if key in seen:
                    require(decision["disposition"]=="duplicate-pair" and decision.get("representative")==seen[key], "duplicate_disposition_mismatch")
                    continue
                seen[key] = pid
                require(decision["disposition"]=="reviewed-development-candidate", "unreviewed_pair")
                for role,label in (("focused",1),("unfocused",0)):
                    rows.append({"id":digest(["retained-fixture",pid,role]),"sourceID":"retained-fixture",
                        "pairID":pid,"label":label,"sourceKind":"tvos_native_generator",
                        "manifestVersion":"focus-retained-review-v1","labelSource":"fixtureNativeInterval",
                        "frameLabelSource":pair["frames"][role]["labelSource"],
                        "split":"train","relatedGroup":"retained-fixture-development",
                        "intrinsicGroup":"retained-fixture-development","recipeSeed":p["seed"],
                        "scene":p["family"],"style":p["theme"],"control":p["control"],
                        "runtime":review["runtime"],"elementID":p["elementID"],"bounds":p[role]["bounds"],
                        "frame":frame_records[role],"crop":crop_records[role],"priorUse":"development",
                        "sourceBlockers":["development_only_source_contract"]})
            index += 1
    require(reconstructed==set(saved), "retained_membership_mismatch")
    require(decisions["counts"]==dict(Counter(p["disposition"] for p in decisions["pairs"])), "disposition_count_mismatch")
    require(review["runtime"]==identity(), "changed_crop_runtime")
    # Recheck source chain after rendering; no publishing or capture operation occurs.
    audit_chain(sources)
    return rows


def assemble(spec):
    require(spec.get("version")==INPUT_VERSION, "unsupported_development_input")
    native_spec = assembly.object_json(assembly.checked(spec["nativeInput"]))
    require(native_spec["baseline"]==spec["baseline"], "changed_baseline")
    for e in native_spec["sources"]:
        require(assembly.object_json(assembly.checked(e["manifest"])).get("version")=="native-os-focus-dataset-v1", "native_only_input_required")
    native = assembly.assemble(native_spec)
    for row in native["samples"]:
        require(row["scene"] in NATIVE_SPLITS and row["split"]==NATIVE_SPLITS[row["scene"]]
                and row["priorUse"]=="development"
                and set(row["sourceBlockers"]) <= {"source_training_review_required"}, "native_role_or_review_conflict")
    require({r["scene"] for r in native["samples"]}==set(NATIVE_SPLITS), "missing_native_screen_group")
    # Bind the excluded historical smoke, without admitting it as another source.
    excluded = assembly.object_json(assembly.checked(spec["excludedDialogManifest"]))
    require(excluded.get("version")=="1.4" and excluded.get("sourceKind")=="tvos_native_generator",
            "invalid_excluded_dialog")
    rows = sorted(native["samples"]+retained_rows(spec["retainedReview"],spec["dispositions"]),key=lambda r:r["id"])
    assembly.isolation(rows)
    require(any(r["split"]=="validation" for r in rows) and any(r["split"]=="train" for r in rows), "missing_experiment_partition")
    doc = {"version":VERSION,"scope":"development-only-mixed-appearance","inputs":spec,
           "samples":rows,"sampling":assembly.sampling(rows),"configuration":CONFIG,
           "preprocessing":RUNTIME_PREPROCESSING,"warmCheckpoint":spec["baseline"],
           "trainingEligible":False,"releaseEligible":False,"independentFixtureValidation":False,
           "counts":{s:sum(r["split"]==s for r in rows)//2 for s in ("train","validation")},
           "limitations":["Native validation measures retention, not Fixture generalization",
                           "Partial pilot remains partial; experimental roles do not alter source admission",
                           "Home/Photos/Remotes excluded; prior dialog smoke excluded as overlapping development lineage"]}
    doc["protocolSHA256"] = digest(doc)
    return doc


def load(path):
    path = local(path)
    doc = sealed(assembly.reference(path), VERSION, "protocolSHA256")
    require(assemble(doc["inputs"])==doc, "changed_experiment_membership")
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    doc = load(path)
    require(arm=="warm-stretch", "unsupported_development_arm")
    require(isinstance(run_name,str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}",run_name), "explicit_safe_run_name_required")
    out = ROOT/"NativeUITrainer/focus_ring_runs"/run_name
    require(not any(p.is_symlink() for p in (out,*out.parents)) and not out.exists(), "output_collision")
    blockers = []; approval_ref = None
    try:
        require(approval_path is not None, "missing_experiment_approval")
        approval_ref = assembly.reference(local(approval_path))
        approval = assembly.object_json(assembly.checked(approval_ref))
        require(approval.get("version")=="focus-development-approval-v1" and approval.get("approved") is True
                and approval.get("protocolSHA256")==doc["protocolSHA256"] and approval.get("runName")==run_name
                and approval.get("arm")==arm, "missing_or_stale_experiment_approval")
        text(approval.get("reviewer")); text(approval.get("reviewReference"))
    except (OSError,ValueError,KeyError,TypeError) as error:
        blockers.append(str(error))
    rows = [{"id":r["id"],"path":assembly.checked({k:r["crop"][k] for k in ("path","sha256")}),
             "label":float(r["label"]),"split":r["split"],"samplingWeight":doc["sampling"]["weights"].get(r["id"],1.)}
            for r in doc["samples"]]
    return {"formatVersion":"focus-development-preflight-v1","configurationValid":True,
            "launchEligible":not blockers,"blockers":blockers,"executionAuthorized":False,
            "releaseEligible":False,"configuration":CONFIG,"protocolSHA256":doc["protocolSHA256"],
            "protocolFile":assembly.reference(path),"approval":approval_ref,"arm":arm,
            "counts":doc["counts"],"sampling":doc["sampling"],"warmCheckpoint":doc["warmCheckpoint"],
            "independentFixtureValidation":False,"output":str(out.relative_to(ROOT))},rows
