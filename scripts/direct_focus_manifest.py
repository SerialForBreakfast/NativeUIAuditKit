"""Direct native capture adapter; runtime crops only, development membership only."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from direct_tvos_capture import SOURCE, require, new_output, validate_capture, validate_interval, write_json
from focus_dataset_contract import ROOT, FocusDataError, digest, expanded_box, local, member
from simulator_focus_manifest import FAMILY_MAP, THEME_MAP


def pairs_from_capture(doc):
    pairs = []
    for result in doc["recipes"]:
        recipe = result["recipe"]
        for focused in result["frames"][1:]:
            element = focused["observedFocusID"]
            frames = {}
            kind = None
            for role, raw in (("unfocused", result["frames"][0]), ("focused", focused)):
                annotations = raw["before"]["scene"]["elements"]
                annotation = next(e for e in annotations if e["element_id"] == element)
                kind = annotation["taxonomy_class"]
                frames[role] = {"path": raw["path"], "sha256": raw["sha256"],
                                "bounds": annotation["pixel_bounds"], "observedFocusID": raw["observedFocusID"],
                                "labelSource": "fixtureNativeInterval", "interval": raw}
            pid = digest({"recipe": recipe, "element": element})
            pairs.append({"pair_id": pid, "recipe_group": f"seed:{recipe['seed']}", "recipe_seed": recipe["seed"],
                          "split": "development", "fixture_scene": FAMILY_MAP[recipe["archetype"]],
                          "theme": THEME_MAP[recipe["theme"]], "element_type": kind, "elementID": element,
                          "sourceKind": SOURCE, "labelSource": "fixtureGroundTruth", "frames": frames,
                          "recipe": recipe})
    return pairs


def validate_direct_manifest(document, root):
    require(document.get("sourceKind") == SOURCE and document.get("purpose") == "development-pilot"
            and "trainingApproval" not in document, "direct_development_only")
    receipt = json.loads(member(root, "direct-capture.json").read_text())
    require(document.get("captureSHA256") == digest(receipt), "changed_capture_receipt")
    validate_capture(receipt, root)
    if receipt["evidenceKind"] == "test-only":
        require(document.get("evidenceKind") == "test-only", "false_reviewed_provenance")
    else:
        review = document.get("visualReview", {})
        require(document.get("evidenceKind") == "reviewed-fixture" and review.get("captureSHA256") == digest(receipt)
                and review.get("accepted") is True and review.get("report"), "missing_visual_review")
        report = member(ROOT, review["report"])
        require(report.stat().st_size > 0 and hashlib.sha256(report.read_bytes()).hexdigest() == review.get("reportSHA256"),
                "changed_visual_review")
    expected = pairs_from_capture(receipt)
    actual = [{k: p.get(k) for k in e} for e, p in zip(expected, document.get("pairs", []))]
    require(len(document.get("pairs", [])) == len(expected) and actual == expected, "changed_direct_membership")


def validate_direct_frames(pair, root):
    boxes = {}
    require(pair.get("split") == "development", "direct_development_only")
    for role, expected in (("focused", pair["elementID"]), ("unfocused", None)):
        frame = pair["frames"][role]
        require(frame.get("labelSource") == "fixtureNativeInterval" and frame.get("observedFocusID") == expected,
                "untrusted_direct_label")
        record = frame["interval"]
        require(record.get("observedFocusID") == expected and all(frame[k] == record[k] for k in ("path", "sha256")),
                "unbound_interval")
        size = validate_interval(record, pair["recipe"], root)
        annotations = record["before"]["scene"]["elements"]
        annotation = next((e for e in annotations if e["element_id"] == pair["elementID"]), None)
        require(annotation is not None and annotation["pixel_bounds"] == frame["bounds"], "unbound_geometry")
        boxes[role] = expanded_box(frame["bounds"], size)
    return boxes


def derive(capture, output, review=None):
    from focus_runtime import RUNTIME_PREPROCESSING, identity, rendered_items
    from focus_dataset_contract import validate_manifest
    root = local(capture.parent)
    doc = json.loads(capture.read_text()); validate_capture(doc, root)
    output = new_output(output)
    result = {"version": "1.4", "sourceKind": SOURCE, "purpose": "development-pilot",
              "evidenceKind": "test-only" if doc["evidenceKind"] == "test-only" else "reviewed-fixture", "corpusID": output.name,
              "producerReference": digest(doc["target"]), "captureSHA256": digest(doc),
              "sourceRoot": str(root.relative_to(ROOT)), "preprocessing": RUNTIME_PREPROCESSING,
              "runtimeCrop": identity(), "pairs": pairs_from_capture(doc)}
    if review is not None: result["visualReview"] = review
    validate_direct_manifest(result, root)
    output.mkdir(parents=True)
    images = rendered_items(result)
    for pair in result["pairs"]:
        boxes = validate_direct_frames(pair, root)
        for role, label in (("focused", 1), ("unfocused", 0)):
            key, raw, _ = next(images)
            require(key == f"{pair['pair_id']}:{label}", "runtime_membership_mismatch")
            name = pair["pair_id"] + f"-{role}.png"
            with (output/name).open("xb") as stream: stream.write(raw)
            pair[role+"_crop"] = name
            pair[role+"_crop_sha256"] = hashlib.sha256(raw).hexdigest()
            pair[role+"_crop_box"] = boxes[role]
    validate_manifest(result, output)
    write_json(output / "focus_dataset_manifest.json", result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", required=True, type=Path); p.add_argument("--output", required=True, type=Path)
    p.add_argument("--visual-review", type=Path, help="Explicit reviewed geometry/focus report bound to capture hash")
    args = p.parse_args()
    try:
        result = derive(args.capture, args.output, json.loads(args.visual_review.read_text()) if args.visual_review else None)
        print(json.dumps({"pairs": len(result["pairs"]), "version": result["version"], "trainingApproval": False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
