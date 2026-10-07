"""TTR sidecar-v2 to production crops; development-only, no invented frame IDs."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, expanded_box, local, member
from harvest_bundle_validation import validate_bundle
from simulator_focus_manifest import build


def require(condition, reason):
    if not condition:
        raise FocusDataError(reason)


def bundle_identity(root, contract):
    names = ["dataset-index.json", "harvest-receipt.json"]
    names += [row["metadataPath"] for row in contract["usableRows"]]
    return {name: hashlib.sha256(member(root, name).read_bytes()).hexdigest() for name in names}


def pairs_from_bundle(contract, corpus, producer):
    from harvest_focus_pairs import FOCUSABLE
    require(contract.get("unknownClassCount") == 0 and
            contract.get("acceptedRowCount") == len(contract["usableRows"]), "unsupported_or_missing_annotations")
    manifest = build(contract, corpus, producer, None)
    pairs = []
    for row in manifest["pairs"]:
        binding = row.get("observationBinding")
        require(row.get("sidecarVersion") in (2, 3) and isinstance(binding, dict)
                and binding.get("schemaVersion") == row["sidecarVersion"], "v2_brackets_required")
        focused = [e for e in row["elements"] if e["is_focused"]]
        require(len(focused) == 1 and focused[0]["taxonomy_class"] in FOCUSABLE, "unsupported_focus_target")
        target = focused[0]["element_id"]
        frames = {}
        for role, scene in (("unfocused", binding["baselineScene"]), ("focused", binding["focusedScene"])):
            element = next((e for e in scene["elements"] if e["element_id"] == target), None)
            require(element is not None and element["taxonomy_class"] == focused[0]["taxonomy_class"], "pair_taxonomy_conflict")
            frames[role] = {**row[role], "bounds": element["pixel_bounds"],
                            "labelSource": "fixtureCaptureBracket", "observedFocusID": scene.get("focused_element_id")}
        pairs.append({"pair_id": row["pairID"], "recipe_group": row["recipeGroup"],
                      "recipe_seed": int(row["recipeGroup"].split(":")[1]), "split": "development",
                      "original_split": row["split"], "fixture_scene": row["family"], "theme": row["theme"],
                      "element_type": focused[0]["taxonomy_class"], "elementID": target,
                      "labelSource": "fixtureGroundTruth", "sourceKind": "simulatorFixture",
                      "frames": frames, "annotation": row["annotation"], "observationBinding": binding})
    return pairs


def validate_ttr_manifest(document, root):
    require(document.get("sourceKind") == "simulatorFixture" and document.get("purpose") == "development-pilot"
            and "trainingApproval" not in document, "ttr_development_only")
    contract = validate_bundle(root)
    if 'targetCoverage' in document or contract['targetCoverage']['available']:
        require(document.get('targetCoverage') == contract['targetCoverage'], 'changed_target_coverage')
    context = contract.get("sourceDescription") or {}
    environment = context.get("environment") or {}
    require(environment.get("isSimulator") is not False, "conflicting_simulator_source_context")
    require(document.get("bundleIdentity") == bundle_identity(root, contract), "changed_bundle_identity")
    require(document.get("observedSource") == contract.get("sourceDescription"), "changed_source_description")
    expected = pairs_from_bundle(contract, document["corpusID"], document["producerReference"])
    actual = document.get("pairs", [])
    require(len(actual) == len(expected) and all(isinstance(p, dict) for p in actual)
            and [{k: p.get(k) for k in e} for e, p in zip(expected, actual)] == expected, "changed_ttr_membership")
    if document.get("evidenceKind") == "reviewed-fixture":
        review = document.get("visualReview", {})
        require(isinstance(review, dict) and review.get("accepted") is True
                and review.get("bundleIdentitySHA256") == digest(document["bundleIdentity"])
                and review.get("sourceKind") == "simulatorFixture", "missing_ttr_visual_review")
        report = member(ROOT, review.get("report"))
        require(report.stat().st_size > 0 and hashlib.sha256(report.read_bytes()).hexdigest() == review.get("reportSHA256"),
                "changed_visual_review")
    else:
        require(document.get("evidenceKind") == "test-only", "missing_evidence_kind")
    return contract


def frame_boxes(pair, root):
    from focus_dataset_contract import image
    require(pair.get("split") == "development", "ttr_development_only")
    boxes = {}
    for role in ("focused", "unfocused"):
        frame = pair["frames"][role]
        require(frame.get("labelSource") == "fixtureCaptureBracket", "untrusted_ttr_label")
        boxes[role] = expanded_box(frame["bounds"], image(root, frame))
    return boxes


def derive(bundle, output, corpus, producer, *, review=None, test_only=False, dry_run=False):
    from focus_runtime import RUNTIME_PREPROCESSING, identity, rendered_items
    from focus_dataset_contract import validate_manifest
    root, output = local(bundle), local(output)
    require(not output.exists(), "output_collision")
    require(test_only != (review is not None), "choose_test_only_or_visual_review")
    contract = validate_bundle(root)
    result = {"version": "1.5", "sourceKind": "simulatorFixture", "purpose": "development-pilot",
              "evidenceKind": "test-only" if test_only else "reviewed-fixture", "corpusID": corpus,
              "producerReference": producer, "sourceRoot": str(root.relative_to(ROOT)),
              "bundleIdentity": bundle_identity(root, contract), "observedSource": contract.get("sourceDescription"),
              "targetCoverage": contract['targetCoverage'],
              "preprocessing": RUNTIME_PREPROCESSING, "runtimeCrop": identity(),
              "pairs": pairs_from_bundle(contract, corpus, producer)}
    if review is not None:
        result["visualReview"] = review
    validate_ttr_manifest(result, root)
    if dry_run:
        return result
    output.mkdir(parents=True, exist_ok=False)
    images = rendered_items(result)
    for pair in result["pairs"]:
        boxes = frame_boxes(pair, root)
        for role, label in (("focused", 1), ("unfocused", 0)):
            key, raw, _ = next(images)
            require(key == f"{pair['pair_id']}:{label}", "runtime_membership_mismatch")
            name = digest({"pair": pair["pair_id"], "role": role}) + ".png"
            with (output/name).open("xb") as stream:
                stream.write(raw)
            pair[role+"_crop"] = name
            pair[role+"_crop_sha256"] = hashlib.sha256(raw).hexdigest()
            pair[role+"_crop_box"] = boxes[role]
    validate_manifest(result, output)
    with (output/"focus_dataset_manifest.json").open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--corpus-id")
    p.add_argument("--producer-reference")
    p.add_argument("--review-crops", action="store_true")
    p.add_argument("--review-model", type=Path, help="Inspection-only scoring; no admission or accuracy qualification")
    p.add_argument('--review-geometry', choices=('endpoint','pair-union'), default='endpoint')
    p.add_argument('--compare-review-scores', type=Path, help='Compatible cached endpoint diagnostic; requires pair-union scoring')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--review-schema4-subset", action="store_true")
    group.add_argument("--visual-review", type=Path)
    group.add_argument("--test-only", action="store_true")
    args = p.parse_args()
    try:
        require(args.review_geometry=='endpoint' or (args.review_schema4_subset and args.review_model),
                'union_requires_inspection_scoring')
        require(not args.compare_review_scores or (args.review_schema4_subset and args.review_model and
                args.review_geometry=='pair-union'), 'comparison_requires_union_scoring')
        if args.review_schema4_subset:
            from harvest_schema4_review import review, render_review, score_review
            root, output = local(args.bundle), local(args.output)
            require(not output.exists(), 'output_collision')
            result = review(root)
            output.mkdir(parents=True, exist_ok=False)
            with (output/'schema4-review.json').open('x') as stream:
                json.dump(result, stream, indent=2, allow_nan=False)
            if args.review_crops:
                crops=render_review(root,output,result)
                with (output/'review-crops.json').open('x') as stream:
                    json.dump(crops,stream,indent=2,allow_nan=False)
            if args.review_model:
                scores=score_review(root,local(args.review_model),result,args.review_geometry)
                with (output/'review-scores.json').open('x') as stream:
                    json.dump(scores,stream,indent=2,allow_nan=False)
                if args.compare_review_scores:
                    from harvest_schema4_review import compare_geometry, decode, read
                    prior=local(args.compare_review_scores)
                    comparison=compare_geometry(decode(read(prior.parent,prior.name)),scores)
                    with (output/'geometry-comparison.json').open('x') as stream:
                        json.dump(comparison,stream,indent=2,allow_nan=False)
            print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))
            return 0 if result['reviewed'] == result['expected'] else 2
        require(not args.review_crops, 'review_crops_requires_schema4_inspection')
        require(not args.review_model, 'review_model_requires_schema4_inspection')
        require(args.corpus_id and args.producer_reference, 'corpus_and_producer_required')
        result = derive(args.bundle, args.output, args.corpus_id, args.producer_reference,
                        review=json.loads(args.visual_review.read_text()) if args.visual_review else None,
                        test_only=args.test_only)
        print(json.dumps({"pairs": len(result["pairs"]), "version": "1.5", "trainingApproval": False,
                          "targetCoverage": result['targetCoverage']}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
