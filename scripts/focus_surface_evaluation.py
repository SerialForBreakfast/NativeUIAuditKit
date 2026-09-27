"""Fixed-threshold native-surface diagnostics; challenge scoring is never permitted."""
import argparse
import base64
from collections import Counter, defaultdict
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys
import time

from focus_dataset_contract import ROOT, digest, pixel_digest
from focus_mixed_assembly import checked, reference
from focus_ring_baseline import evaluate, model_contract
from focus_runtime import RUNTIME_PREPROCESSING, identity, bounded_batches, invoke
from focus_surface_intake import ROLES, fresh, require, write

STRATA = {"dense_dark_media": "dense-dark-media", "bright_unfocused_artwork": "bright-unfocused-artwork",
          "gray_blank_placeholder": "gray-blank-placeholders", "dock_neighbor": "dock-neighbor-focus",
          "detail_action": "fixture-detail-action"}
VERSION = "focus-surface-validation-v1"


def runtime():
    return {"crop": identity(), "python": platform.python_version(), "executable": sys.executable,
            "packages": {k: importlib.metadata.version(k) for k in ("torch", "numpy", "Pillow")},
            "torchDevice": "cpu", "torchThreads": 2, "torchBatchSize": 32, "coremlComputeUnits": "cpuOnly"}


def group_samples(group):
    rows = []
    for pair in group["pairs"]:
        common = {"group": group["group"], "role": group["role"], "pairID": pair["pair_id"],
                  "theme": pair["theme"], "family": group["group"], "hard": False}
        for role, label in (("focused", 1), ("unfocused", 0)):
            frame = pair["frames"][role]
            rows.append({**common, "id": f"{group['group']}:{pair['pair_id']}:pair:{label}",
                         "kind": "pair", "label": label, "control": pair["element_type"],
                         "elementID": pair["elementID"], "stratum": stratum(pair["elementID"]),
                         "path": str(Path(group["sourceRoot"]) / frame["path"]),
                         "sha256": frame["sha256"], "bounds": frame["bounds"]})
        if group["role"] != "appearance-validation":
            continue
        scene = pair["observationBinding"]["focusedScene"]
        elements = scene["elements"]
        ids = {e["element_id"] for e in elements}
        complete = (len(ids) == len(elements) == scene["recipe"]["element_count"] and
                    ids == set(scene["focus_observation"]["plannedFocusIDs"]))
        require(complete and sum(e["is_focused"] for e in elements) == 1, "incomplete_candidate_set")
        frame = pair["frames"]["focused"]
        for element in elements:
            rows.append({**common, "id": f"{group['group']}:{pair['pair_id']}:competition:{element['element_id']}",
                         "kind": "competition", "frameID": f"{group['group']}:{pair['pair_id']}",
                         "candidateCount": len(elements), "candidateComplete": True,
                         "elementID": element["element_id"], "label": int(element["is_focused"]),
                         "control": element["taxonomy_class"], "stratum": stratum(element["element_id"]),
                         "path": str(Path(group["sourceRoot"]) / frame["path"]),
                         "sha256": frame["sha256"], "bounds": element["pixel_bounds"]})
    return rows


def stratum(element):
    parts = element.split(".")
    require(len(parts) == 4 and parts[2] in STRATA, "unknown_surface_stratum")
    return STRATA[parts[2]]


def item(row):
    return {"id": row["id"], "path": str(ROOT / row["path"]), "sha256": row["sha256"], "bounds": row["bounds"]}


def validate_rows(rows):
    require(bool(rows) and len({r["id"] for r in rows}) == len(rows), "empty_or_duplicate_membership")
    for row in rows:
        require(ROLES.get(row["group"]) == row["role"] == "appearance-validation", "final_challenge_scoring_forbidden")
        require(type(row["label"]) is int and row["label"] in (0, 1), "invalid_label")
        require(row["kind"] in {"pair", "competition"}, "invalid_sample_kind")
    frames = defaultdict(list)
    for row in rows:
        if row["kind"] == "competition": frames[row["frameID"]].append(row)
    for members in frames.values():
        require(all(r["candidateComplete"] is True and r["candidateCount"] == len(members) for r in members)
                and len({r["elementID"] for r in members}) == len(members)
                and sum(r["label"] for r in members) == 1, "incomplete_candidate_set")


def prepare(intake_path, output, crops):
    from PIL import Image, ImageDraw
    output, crops = fresh(output), fresh(crops)
    intake = json.loads(intake_path.read_text())
    require(intake["counts"] == {"accepted-diagnostic-only": intake["expectedRows"]}, "incomplete_intake")
    groups = [json.loads(checked(ref).read_text()) for ref in intake["groups"]]
    samples = [r for g in groups for r in group_samples(g)]
    require(len({r["id"] for r in samples}) == len(samples), "duplicate_sample")
    output.mkdir(parents=True); crops.mkdir(parents=True)
    inventory = []
    for group in groups:
        root = ROOT / group["sourceRoot"]
        for name, expected in group["inventory"].items():
            ref = reference(root / name)
            require(ref["sha256"] == expected, "changed_source_inventory")
            inventory.append(ref)
    by_id = {r["id"]: r for r in samples}
    frame_pixels = {}
    for index, batch in enumerate(bounded_batches([item(r) for r in samples])):
        reply = invoke(batch)  # crop only, including challenge QA; never a model
        for result in reply["results"]:
            row = by_id[result["id"]]
            path = crops / (digest(row["id"]) + ".png")
            with path.open("xb") as stream: stream.write(base64.b64decode(result["png"], validate=True))
            with Image.open(path) as im:
                require(im.size == (256, 256), "wrong_crop_dimensions")
            row["crop"] = reference(path)
            row["crop"]["pixelSHA256"] = pixel_digest(ROOT, row["crop"])
            if row["path"] not in frame_pixels:
                frame_pixels[row["path"]] = pixel_digest(ROOT, row)
            row["framePixelSHA256"] = frame_pixels[row["path"]]
        if index % 10 == 0: print(json.dumps({"cropBatch": index, "completed": sum('crop' in r for r in samples)}), flush=True)
    # Visual intake sheets contain pairs only, never predictions or score-selected cases.
    for group in groups:
        pairs = [r for r in samples if r["group"] == group["group"] and r["kind"] == "pair"]
        sheet = Image.new("RGB", (8 * 160, math.ceil(len(pairs) / 8) * 120), "#303030")
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(pairs):
            with Image.open(ROOT / row["crop"]["path"]) as im:
                im.thumbnail((150, 90)); x, y = (i % 8) * 160, (i // 8) * 120
                sheet.paste(im, (x, y)); draw.text((x, y + 91), f"{row['pairID']} label={row['label']}", fill="white")
        sheet.save(output / (group["group"] + "-pairs.png"))
    doc = {"version": "surface-crops-v1", "intake": reference(intake_path), "groups": intake["groups"],
           "inventory": inventory, "samples": samples, "runtime": runtime(),
           "preprocessing": RUNTIME_PREPROCESSING, "finalChallengeScored": False}
    doc["seal"] = digest(doc); write(output / "crops.json", doc)
    return doc


def seal_check(doc, key="seal"):
    require(doc.get(key) == digest({k: v for k, v in doc.items() if k != key}), "changed_protocol")


def freeze(crops_path, review, output):
    output = fresh(output)
    doc = json.loads(crops_path.read_text()); seal_check(doc)
    reviewed = json.loads(review.read_text())
    require(reviewed.get("crops") == reference(crops_path) and reviewed.get("accepted") is True
            and reviewed.get("independentEvaluationEligible") is False, "missing_or_changed_intake_review")
    rows = [r for r in doc["samples"] if r["role"] == "appearance-validation"]
    validate_rows(rows)
    models = {name: reference(ROOT / "NativeUITrainer/focus_ring_runs" / folder / "weights/best.pt")
              for name, folder in (("fdr007", "fdr007-native-incremental"), ("fdr008", "fdr008-mixed-appearance"))}
    shipped = ROOT / "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
    protocol = {"version": VERSION, "crops": reference(crops_path), "review": reference(review),
                "samples": rows, "models": models, "shipped": {"path": str(shipped.relative_to(ROOT)), **model_contract(shipped)},
                "runtime": runtime(), "threshold": .85, "variants": ["base"],
                "preprocessing": RUNTIME_PREPROCESSING, "finalChallengeScored": False,
                "independentEvaluationEligible": False, "trainingEligible": False,
                "implementation": [reference(ROOT / "scripts" / name) for name in
                    ("focus_surface_evaluation.py", "focus_surface_intake.py", "harvest_sidecar_v2.py",
                     "focus_runtime.py", "focus_ring_baseline.py", "focus_ring_backbone.py")]}
    protocol["seal"] = digest(protocol)
    validate(protocol); output.parent.mkdir(parents=True, exist_ok=True); write(output, protocol)
    return protocol


def validate(doc):
    seal_check(doc)
    require(doc.get("version") == VERSION and doc.get("threshold") == .85
            and doc.get("variants") == ["base"] and doc.get("preprocessing") == RUNTIME_PREPROCESSING
            and doc.get("finalChallengeScored") is False and doc.get("trainingEligible") is False
            and doc.get("independentEvaluationEligible") is False, "unsupported_protocol")
    validate_rows(doc["samples"])
    crops = json.loads(checked(doc["crops"]).read_text()); seal_check(crops)
    require(doc["samples"] == [r for r in crops["samples"] if r["role"] == "appearance-validation"], "changed_membership")
    review = json.loads(checked(doc["review"]).read_text())
    require(review.get("accepted") is True and review.get("crops") == doc["crops"], "changed_review")
    require(runtime() == doc["runtime"] == crops["runtime"], "changed_runtime")
    require(set(doc["models"]) == {"fdr007", "fdr008"}, "model_roles")
    for ref in [*doc["implementation"], *doc["models"].values(), *crops["inventory"], *crops["groups"]]: checked(ref)
    checked(crops["intake"])
    for row in crops["samples"]:
        checked({k: row[k] for k in ("path", "sha256")})
        checked({k: row["crop"][k] for k in ("path", "sha256")})
    require(model_contract(ROOT / doc["shipped"]["path"]) ==
            {k: v for k, v in doc["shipped"].items() if k != "path"}, "changed_model")


def score(rows, predictions):
    validate_rows(rows)
    require([r["id"] for r in rows] == [p.get("id") for p in predictions], "prediction_membership_mismatch")
    values = {}
    for prediction in predictions:
        p = prediction.get("probability")
        require(type(p) in (int, float) and math.isfinite(p) and 0 <= p <= 1, "invalid_probability")
        values[prediction["id"]] = p
    reports = {}
    for kind in ("pair", "competition"):
        subset = [r for r in rows if r["kind"] == kind]
        if not subset: continue
        base = evaluate(subset, {r["id"]: values[r["id"]] for r in subset}, require_hard=False)
        base["threshold"] = {"value": .85, "purpose": "fixed-validation-comparison; no tuning"}
        for key in sorted(set(STRATA.values()) | {"photos-buttons"}):
            selected = [r for r in subset if r["stratum"] == key]
            if not selected:
                base["groups"]["stratum:" + key] = {"n": 0, "status": "unavailable", "recall": None, "fpr": None}
            else:
                result = evaluate(selected, {r["id"]: values[r["id"]] for r in selected}, require_hard=False)["groups"]["overall"]
                if not any(r["label"] for r in selected): result["recall"] = None
                base["groups"]["stratum:" + key] = result
        reports[kind] = base
    frames = defaultdict(list)
    for row in rows:
        if row["kind"] == "competition": frames[row["frameID"]].append(row)
    decisions = []
    for frame, members in frames.items():
        positive = [r for r in members if values[r["id"]] >= .85]
        status = ("multiple-focus" if len(positive) > 1 else "no-focus" if not positive
                  else "unique-correct" if positive[0]["label"] else "wrong-focus")
        decisions.append({"frameID": frame, "group": members[0]["group"], "decision": status,
                          "selected": [r["elementID"] for r in positive]})
    return {"metrics": reports, "frameDecisions": decisions,
            "frameCounts": dict(Counter(r["decision"] for r in decisions)), "accounted": len(rows)}


def run(protocol_path, output):
    import numpy as np
    import torch
    from PIL import Image
    from focus_ring_backbone import mobilenetv4_conv_small
    output = fresh(output); doc = json.loads(protocol_path.read_text()); validate(doc)
    output.mkdir(parents=True); rows = doc["samples"]; torch.set_num_threads(2)
    outcomes = {}
    for name in ("shipped", "fdr007", "fdr008"):
        predictions, timings = [], []
        started = time.monotonic()
        try:
            if name == "shipped":
                for batch in bounded_batches([item(r) for r in rows]):
                    reply = invoke(batch, ROOT / doc["shipped"]["path"])
                    predictions.extend({k: r[k] for k in ("id", "probability", "inferenceMilliseconds")} for r in reply["results"])
                    timings.append({k: v for k, v in reply.items() if k != "results"})
            else:
                model = mobilenetv4_conv_small(pretrained=False, num_classes=1)
                model.load_state_dict(torch.load(checked(doc["models"][name]), map_location="cpu", weights_only=True)["state_dict"], strict=True)
                model.eval(); load_seconds = time.monotonic() - started
                timings.append({"modelLoadSeconds": load_seconds})
                with torch.inference_mode():
                    for offset in range(0, len(rows), 32):
                        members = rows[offset:offset + 32]; tensors = []
                        for row in members:
                            with Image.open(ROOT / row["crop"]["path"]) as im:
                                tensors.append(torch.from_numpy(np.array(im.convert("RGB"), copy=True)).permute(2, 0, 1).float().div(255))
                        batch = torch.stack(tensors); tick = time.monotonic()
                        values = torch.sigmoid(model(batch)).view(-1).tolist()
                        timings.append({"samples": len(members), "inferenceMilliseconds": (time.monotonic() - tick) * 1000})
                        predictions.extend({"id": r["id"], "probability": p} for r, p in zip(members, values, strict=True))
            result = {"state": "complete", **score(rows, predictions)}
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
            result = {"state": "failed", "error": str(error), "accounted": len(rows),
                      "unscored": [r["id"] for r in rows[len(predictions):]], "scored": len(predictions)}
        result.update(predictions=predictions, timing=timings, seconds=time.monotonic() - started,
                      protocolSHA256=doc["seal"], backend="CoreML CPU" if name == "shipped" else "PyTorch CPU,2 threads")
        write(output / (name + ".json"), result); outcomes[name] = result
        print(json.dumps({"model": name, "state": result["state"], "frameCounts": result.get("frameCounts")}), flush=True)
    validate(doc)
    report = {"version": VERSION, "protocol": reference(protocol_path), "results": outcomes,
              "finalChallengeScored": False, "independentEvaluationEligible": False, "modelGatePassed": "not_assessed"}
    write(output / "comparison.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "freeze", "run"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--crops", type=Path)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare": prepare(args.input, args.output, args.crops)
        elif args.command == "freeze": freeze(args.input, args.review, args.output)
        else:
            report = run(args.input, args.output)
            require(all(r["state"] == "complete" for r in report["results"].values()), "incomplete_model_comparison")
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
