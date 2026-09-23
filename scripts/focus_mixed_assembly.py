"""Immutable native/fixture FocusRing assembly. No capture, model imports or training."""
import argparse
import base64
from collections import Counter
import hashlib
import io
import json
from pathlib import Path

from focus_dataset_contract import (ROOT, FocusDataError, digest, local, member, image,
                                    pixel_digest, text, validate_manifest)
from focus_runtime import identity, invoke, RUNTIME_PREPROCESSING

VERSION = "focus-mixed-assembly-v1"
PARTITIONS = {"train", "validation", "test", "development"}


def object_json(path):
    doc=json.loads(path.read_text())
    if not isinstance(doc,dict): raise FocusDataError("object_required")
    return doc


def reference(path):
    path = local(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def checked(ref):
    path = member(ROOT, ref["path"])
    if reference(path) != ref:
        raise FocusDataError("changed_assembly_input")
    return path


def sealed(path):
    doc = object_json(local(path))
    content = dict(doc); expected = content.pop("assemblySHA256", None)
    if doc.get("version") != VERSION or digest(content) != expected:
        raise FocusDataError("changed_or_unsupported_assembly")
    return doc


def record(root, raw):
    image(root, raw)
    return {**reference(member(root, raw["path"])), "pixelSHA256": pixel_digest(root, raw)}


def native_pairs(doc, manifest):
    from native_os_focus_dataset import read_journey, pair_frames
    content = dict(doc); expected = content.pop("manifestSHA256", None)
    if (digest(content) != expected or doc.get("completion") != "completed"
            or doc.get("sourceKind") != "tvos_simulator_os" or doc.get("partition") != "development"
            or doc.get("preprocessing") != RUNTIME_PREPROCESSING or doc.get("runtime") != identity()):
        raise FocusDataError("unsupported_or_changed_native_manifest")
    source = local(ROOT/doc["sourceRoot"])
    # read_journey uses manifest.json too; its inventory must be hash-bound.
    if not isinstance(doc.get("sourceHashes"), dict) or "manifest.json" not in doc["sourceHashes"]:
        raise FocusDataError("missing_native_source_inventory")
    for name, sha in doc["sourceHashes"].items():
        checked({"path":str(member(source,name).relative_to(ROOT)), "sha256":sha})
    if {p.name for p in source.iterdir() if p.is_file()} != set(doc["sourceHashes"]):
        raise FocusDataError("changed_native_source_inventory")
    screen = doc.get("screenID", "settings/root")
    frames, _ = read_journey(source, doc["target"], screen)
    pairs, _ = pair_frames(frames, doc["lineage"])
    derived = {p["pair_id"]:p for p in doc["pairs"]}
    if len(derived) != len(doc["pairs"]) or set(derived) != {p["pair_id"] for p in pairs}:
        raise FocusDataError("changed_native_membership")
    result = []
    for pair in pairs:
        saved = derived[pair["pair_id"]]
        for key in ("elementID", "split", "lineage"):
            if saved.get(key) != pair[key]: raise FocusDataError("changed_native_lineage_or_label")
        crops = {}
        items=[{"id":pair["pair_id"]+role,"path":str(member(source,pair["frames"][role]["path"])),
                "sha256":pair["frames"][role]["sha256"],"bounds":pair["frames"][role]["bounds"]}
               for role in ("focused","unfocused")]
        # Two inputs stay inside the helper's 80MP cap even at the source 40MP limit.
        results=invoke(items)["results"]
        if [r["id"] for r in results]!=[i["id"] for i in items]: raise FocusDataError("runtime_membership_mismatch")
        rendered_by_id={r["id"]:r for r in results}
        for role in ("focused", "unfocused"):
            frame, stored = pair["frames"][role], saved["frames"][role]
            if {k:v for k,v in stored.items() if k not in {"crop","cropSHA256"}} != frame:
                raise FocusDataError("changed_native_geometry_or_label")
            crop = {"path":stored["crop"], "sha256":stored["cropSHA256"]}
            image(manifest.parent, crop, (256,256))
            from PIL import Image
            png=rendered_by_id[pair["pair_id"]+role]["png"]
            with Image.open(io.BytesIO(base64.b64decode(png,validate=True))) as rendered, Image.open(member(manifest.parent,crop["path"])) as actual:
                if rendered.size!=(256,256) or rendered.convert("RGB").tobytes()!=actual.convert("RGB").tobytes():
                    raise FocusDataError("crop_pixel_mismatch")
            crops[role] = record(manifest.parent,crop)
        result.append({"pair":pair, "crops":crops, "source":source,
                       "scene":screen, "style":"unknown", "control":pair["elementID"].split(":",1)[0],
                       "labelSource":"nativeAX-capture-interval", "intrinsicGroup":doc["lineage"],
                       "runtime":doc["runtime"], "originPartition":"development"})
    return result


def source_rows(entry):
    sid = text(entry.get("id"))
    path, review_path = checked(entry["manifest"]), checked(entry["review"])
    doc, review = object_json(path), object_json(review_path)
    if (review.get("version")!="focus-source-review-v1" or review.get("manifestSHA256")!=entry["manifest"]["sha256"]
            or review.get("priorUse") not in {"development", "untouched", "test-only"}
            or type(review.get("relationshipsKnown")) is not bool
            or type(review.get("trainingApproved")) is not bool):
        raise FocusDataError("invalid_source_review")
    text(review.get("reviewer")); text(review.get("reviewReference"))
    if "priorReview" in review: checked(review["priorReview"])
    if "supersedesReview" in review: checked(review["supersedesReview"])
    version = doc.get("version")
    blockers = []
    if version == "native-os-focus-dataset-v1":
        pairs = native_pairs(doc,path)
        if review["priorUse"] == "untouched": raise FocusDataError("native_development_not_untouched")
    elif version in {"1.2","1.3","1.4","1.5"}:
        validate_manifest(doc,path.parent)  # Source-specific adapters retain their own admission contracts.
        root = local(ROOT/doc["sourceRoot"])
        pairs = [{"pair":p, "source":root, "scene":p["fixture_scene"], "style":p["theme"],
                  "control":p["element_type"], "labelSource":"fixtureGroundTruth",
                  "intrinsicGroup":p["recipe_group"], "runtime":doc.get("runtimeCrop"),
                  "originPartition":{"val":"validation"}.get(p["split"],p["split"]),
                  "crops":{role:record(path.parent,{"path":p[role+"_crop"],"sha256":p[role+"_crop_sha256"]})
                           for role in ("focused","unfocused")}} for p in doc["pairs"]]
        if version=="1.2": blockers.append("runtime_crop_parity_required")
        if version in {"1.4","1.5"}: blockers.append("development_only_source_contract")
        if doc["evidenceKind"]!="reviewed-fixture": blockers.append("test_only_evidence")
    else:
        raise FocusDataError("unsupported_assembly_source")
    if not review["relationshipsKnown"]: blockers.append("unknown_source_relationships")
    if not review["trainingApproved"]: blockers.append("source_training_review_required")
    if review["priorUse"]=="test-only": blockers.append("test_only_evidence")
    assignments = review.get("pairs")
    if not isinstance(assignments,dict) or set(assignments)!={p["pair"]["pair_id"] for p in pairs}:
        raise FocusDataError("review_membership_mismatch")
    rows = []
    for item in pairs:
        pair = item["pair"]; pid = pair["pair_id"]; assignment = assignments[pid]
        split = assignment.get("partition"); group = text(assignment.get("relatedGroup"))
        if split not in PARTITIONS: raise FocusDataError("invalid_partition")
        if version != "native-os-focus-dataset-v1" and split != item["originPartition"]:
            raise FocusDataError("fixture_partition_drift")
        if split=="test" and review["priorUse"]!="untouched": raise FocusDataError("evaluation_reuse")
        if version in {"1.4","1.5"} and split!="development": raise FocusDataError("development_only_source_contract")
        for role,label in (("focused",1),("unfocused",0)):
            raw = pair["frames"][role]
            rows.append({"id":digest([sid,pid,role]), "sourceID":sid, "pairID":pid, "label":label,
                "sourceKind":doc["sourceKind"], "manifestVersion":version, "labelSource":item["labelSource"],
                "frameLabelSource":raw["labelSource"],
                "split":split, "relatedGroup":group, "intrinsicGroup":item["intrinsicGroup"],
                "scene":item["scene"], "style":item["style"], "control":item["control"],
                "runtime":item["runtime"], "elementID":pair["elementID"], "bounds":raw["bounds"],
                "frame":record(item["source"],raw), "crop":item["crops"][role],
                "priorUse":review["priorUse"], "sourceBlockers":sorted(set(blockers)),
                "recipeSeed":pair.get("recipe_seed")})
    return rows


def isolation(rows):
    seen, owners, labels, pairs, crop_pairs = set(), {}, {}, set(), set()
    for r in rows:
        if r["id"] in seen: raise FocusDataError("duplicate_sample")
        seen.add(r["id"])
        crop = r["crop"]["pixelSHA256"]
        if crop in labels and labels[crop]!=r["label"]: raise FocusDataError("contradictory_crop_labels")
        labels[crop] = r["label"]
        keys=[("group",r["relatedGroup"]),("intrinsic",r["sourceKind"],r["intrinsicGroup"]),
              ("pixels",crop),("pixels",r["frame"]["pixelSHA256"])]
        if r["recipeSeed"] is not None: keys.append(("recipeSeed",r["recipeSeed"]))
        for key in keys:
            if key in owners and owners[key]!=r["split"]: raise FocusDataError("cross_source_split_leakage")
            owners[key]=r["split"]
    by_pair={}
    for r in rows: by_pair.setdefault((r["sourceID"],r["pairID"]),[]).append(r)
    for members in by_pair.values():
        if sorted(r["label"] for r in members)!=[0,1]: raise FocusDataError("incomplete_pair")
        key=tuple((r["frame"]["pixelSHA256"],tuple(r["bounds"])) for r in sorted(members,key=lambda r:r["label"]))
        crop_key=tuple(r["crop"]["pixelSHA256"] for r in sorted(members,key=lambda r:r["label"]))
        if key in pairs or crop_key in crop_pairs: raise FocusDataError("duplicate_pair_content")
        pairs.add(key)
        crop_pairs.add(crop_key)


def stratum(r):
    return (r["sourceKind"],r["scene"],r["style"],r["control"])


def sampling(rows):
    train=[r for r in rows if r["split"]=="train"]
    counts=Counter(stratum(r) for r in train)
    return {"policy":"equal-source-scene-style-control-v1", "basis":"training-only",
            "weights":{r["id"]:len(train)/(len(counts)*counts[stratum(r)]) for r in train},
            "strata":[{"key":list(k),"samples":n} for k,n in sorted(counts.items())]}


def assemble(spec):
    if isinstance(spec,dict) and spec.get("version")=="focus-development-input-v1":
        from focus_development_experiment import assemble as development_assemble
        return development_assemble(spec)
    if not isinstance(spec,dict) or spec.get("version")!="focus-assembly-input-v1": raise FocusDataError("unsupported_assembly_input")
    entries=spec.get("sources")
    if not isinstance(entries,list) or not entries: raise FocusDataError("empty_sources")
    if len({e["id"] for e in entries})!=len(entries): raise FocusDataError("duplicate_source")
    entries=sorted(entries,key=lambda e:e["id"])
    checked(spec["baseline"])  # Existing local checkpoint or reference artifact; no deserialization.
    rows=sorted([r for e in entries for r in source_rows(e)],key=lambda r:r["id"])
    isolation(rows)
    previous=spec.get("previous")
    delta={"addedSources":[e["id"] for e in entries],"addedSamples":[r["id"] for r in rows],
           "removedSamples":[],"updatedReviews":[]}
    if previous:
        old=sealed(checked(previous))
        current={e["id"]:e for e in entries}; members={r["id"]:r for r in rows}
        for entry in old["inputs"]["sources"]:
            new=current.get(entry["id"])
            if new is None or new["manifest"]!=entry["manifest"]: raise FocusDataError("retention_or_partition_drift")
            if new!=entry:
                review=object_json(checked(new["review"]))
                if review.get("supersedesReview")!=entry["review"]: raise FocusDataError("retention_or_partition_drift")
                delta["updatedReviews"].append(entry["id"])
        immutable=lambda r:{k:v for k,v in r.items() if k!="sourceBlockers"}
        if any(r["id"] not in members or immutable(members[r["id"]])!=immutable(r) for r in old["samples"]):
            raise FocusDataError("retention_or_partition_drift")
        delta["addedSources"]=sorted(set(current)-{e["id"] for e in old["inputs"]["sources"]})
        delta["addedSamples"]=sorted(set(members)-{r["id"] for r in old["samples"]})
    coverage=Counter((r["split"],*stratum(r),r["label"]) for r in rows)
    doc={"version":VERSION,"inputs":{**spec,"sources":entries},"samples":rows,"sampling":sampling(rows),
         "coverage":[{"partition":k[0],"sourceKind":k[1],"scene":k[2],"style":k[3],"control":k[4],"label":k[5],"samples":v}
                     for k,v in sorted(coverage.items())],"delta":delta,
         "trainingEligible":False,"releaseEligible":False,
         "limitations":["Approval and full fixture quotas checked separately in trainer preflight",
                         "Native AX and fixture callbacks are distinct evidence; interval binding is not atomic attestation",
                         "Unknown styles remain unknown; no style inferred from filenames"]}
    doc["assemblySHA256"]=digest(doc)
    return doc


def load(path):
    doc=sealed(path)
    if assemble(doc["inputs"])!=doc: raise FocusDataError("changed_assembly_membership")
    return doc


def load_samples(dataset,split):
    doc=sealed(local(dataset)/"focus_dataset_manifest.json")
    result=[]
    for r in doc["samples"]:
        if r["split"]!=split: continue
        path=checked({k:r["crop"][k] for k in ("path","sha256")})
        result.append({"id":r["id"],"path":path,"label":float(r["label"]),"pair_id":r["pairID"],
                       "theme":r["style"],"element_type":r["control"],"sourceKind":r["sourceKind"],
                       "samplingWeight":doc["sampling"]["weights"].get(r["id"],1.)})
    return result


def readiness(doc, dataset):
    """Keep fixture milestone gates separate from auxiliary native support."""
    from focus_ring_readiness import validate, ReadinessError
    rows=doc["samples"]
    blockers=sorted({b for r in rows for b in r["sourceBlockers"]
                     if r["split"]!="development" or b=="unknown_source_relationships"})
    if any(not any(r["split"]==s for r in rows) for s in ("train","validation","test")):
        blockers.append("missing_required_partition")
    fixtures=[]
    for entry in doc["inputs"]["sources"]:
        manifest=checked(entry["manifest"]); source=json.loads(manifest.read_text())
        if source.get("version")!="1.3": continue
        for pair in source["pairs"]:
            if pair["split"]=="development": continue
            evidence=dict(pair["frames"]["unfocused"])
            evidence["path"]=str(member(ROOT/source["sourceRoot"],evidence["path"]).relative_to(ROOT))
            fixtures.append({"pairID":entry["id"]+":"+pair["pair_id"],"focused":pair["focused_crop"],
                "unfocused":pair["unfocused_crop"],"seed":str(pair["recipe_seed"]),
                "recipeGroup":pair["recipe_group"],"split":pair["split"],"scene":pair["fixture_scene"],
                "theme":pair["theme"],"class":pair["element_type"],"labelSource":"fixtureGroundTruth",
                "validatedUnfocusedEvidence":evidence})
    quota={}
    try: quota=validate(fixtures,evidence_root=ROOT)
    except ReadinessError as error: blockers.append(str(error))
    try:
        approval=json.loads(member(dataset,"training_approval.json").read_text())
        if (approval.get("version")!="focus-assembly-approval-v1" or approval.get("approved") is not True
                or approval.get("assemblySHA256")!=doc["assemblySHA256"]):
            raise FocusDataError("missing_corpus_approval")
        text(approval.get("reviewer")); text(approval.get("reviewReference"))
    except (OSError,ValueError,KeyError,TypeError): blockers.append("missing_corpus_approval")
    return {"blockers":sorted(set(blockers)),"fixtureQuota":quota,
            "diagnosticOnlyBlockers":sorted({b for r in rows if r["split"]=="development" for b in r["sourceBlockers"]}),
            "counts":{s:sum(r["split"]==s for r in rows)//2 for s in sorted(PARTITIONS)}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        raw=a.output.absolute()
        if any(x.is_symlink() for x in [raw,*raw.parents]): raise FocusDataError("symlink_output")
        out=local(raw)
        if out.exists(): raise FocusDataError("output_collision")
        doc=assemble(json.loads(local(a.input).read_text()))
        out.mkdir(parents=True,exist_ok=False)
        with (out/"focus_dataset_manifest.json").open("x") as f: json.dump(doc,f,indent=2,allow_nan=False)
        key="assemblySHA256" if "assemblySHA256" in doc else "protocolSHA256"
        print(json.dumps({key:doc[key],"samples":len(doc["samples"]),"trainingEligible":False}))
    except (OSError,ValueError,KeyError,TypeError) as error: p.exit(2,str(error)+"\n")


if __name__=="__main__": main()
