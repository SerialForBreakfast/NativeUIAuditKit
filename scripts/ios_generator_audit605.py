"""Audit the two source-verified UIKit recipes and their matched iOS consumer scans."""
import argparse
from collections import Counter
from pathlib import Path

import research_queue as q
from ios_annotation_contract478 import review
from qpacket_import604 import _iou_edge

# Only the audited recipes support this interpretation. UISwitch supplies iOS toggle evidence.
SOURCE_HASHES = {
    "NativeUIDatasetGenerator/Templates/UIKitControlsViewController.swift": "4d2d79bf673cd4a893e15c4b83fb65bf44359ef9ca9fa23d7851fa7c2ff7548c",
    "NativeUIDatasetGenerator/Templates/UIKitToggleFormViewController.swift": "764e42612e5adc2fe04e5525b0cda0a510048791f1678ff272f6e1a215e1bd60",
    "NativeUIDatasetGenerator/Sources/SeededRNG.swift": "a54219960b3bb894347464ee5cb073cb821b00866ab8c5d3c0886e727bf6b7cc",
}
ROLES = {"navigationBar": "bar", "primaryButton": "button", "secondaryButton": "button",
         "toggle": "toggle", "secureField": "textField", "activityIndicator": "indicator",
         "progressView": "indicator", "pageControl": "pageControl",
         "segmentedControl": "segmentedControl", "label": "excluded_static_text",
         "slider": "unsupported_slider"}
SHIPPED = {"navigationBar", "primaryButton", "alert", "textField", "toggle"}


def xywh(rect):
    return [rect[k] for k in ("x", "y", "width", "height")]


def score(elements, predictions):
    """Greedy one-to-one, descending confidence. Preserve strict legacy class names."""
    remaining = {e["id"]: e for e in elements if e["elementType"] in SHIPPED}
    counts = Counter()
    misses = []
    for pred in sorted(predictions, key=lambda d: -d["confidence"]):
        cls = pred["elementType"]
        q.require(cls in SHIPPED and pred["confidenceSource"] == "pixelModel", "unexpected_prediction")
        matches = [(_iou_edge(xywh(pred["boundingBoxPixels"]), xywh(gt["boundsPixels"]))[0], ident)
                   for ident, gt in remaining.items() if gt["elementType"] == cls]
        iou, ident = max(matches, default=(0, None))
        if iou >= 0.5:
            counts[(cls, "matched")] += 1
            del remaining[ident]
        else:
            counts[(cls, "unmatchedPrediction")] += 1
    for ident, gt in remaining.items():
        counts[(gt["elementType"], "missed")] += 1
        misses.append(ident)
    return counts, misses


def audit(manifest_path, scan_path):
    manifest = q.load(manifest_path)
    build = manifest["build"]
    receipt_path = q.ROOT / build["path"]
    q.require(q.digest(receipt_path) == build["sha256"], "generator_build_pin")
    sources = q.load(receipt_path)["sources"]
    q.require(all(sources.get(k) == v for k, v in SOURCE_HASHES.items()), "unaudited_generator_source")
    contract = review(manifest_path, manifest_path.with_name("benchmark_summary.json"))
    q.require(contract["annotationContractPassed"], "source_inventory_failed")
    batch = q.load(scan_path)
    scans = {Path(r["input"]).stem: r for r in batch["results"]}
    rows = manifest["rows"]
    q.require(len(scans) == len(batch["results"]) == len(rows) and
              set(scans) == {r["id"] for r in rows}, "incomplete_scan")
    counts, roles, failures, frames, models = Counter(), Counter(), [], [], set()
    role_support, role_hits = Counter(), Counter()
    for row in rows:
        ident = row["id"]
        side = q.load(manifest_path.parent / row["sidecar"]["path"])
        items = [e for e in side["elements"] if not e["excluded"]]
        roles.update(ROLES[e["elementType"]] for e in items)
        r = scans[ident]
        if r["status"] != "success":
            failures.append(ident)
            continue
        q.require(r["configuration"]["platform"] == "iOS" and r["configuration"]["minConfidence"] == 0.5
                  and not r["configuration"]["ocr"] and r["inputSHA256"] == side["imageSHA256"]
                  == row["image"]["sha256"], "scan_binding")
        model = r["runtime"]["detector"]
        q.require(model["modelID"] == "nativeui-ios-v2.0", "unexpected_model")
        models.add(model["treeSHA256"])
        partial, misses = score(items, r["runtime"]["result"]["elements"])
        counts.update(partial)
        # Compare role coverage on the same boxes. Report unsupported model heads explicitly.
        role_labels = {e["id"]: ROLES[e["elementType"]] for e in items
                       if ROLES[e["elementType"]] not in ("excluded_static_text", "unsupported_slider")}
        role_support.update(role_labels.values())
        available = dict(role_labels)
        for pred in sorted(r["runtime"]["result"]["elements"], key=lambda d: -d["confidence"]):
            role = ROLES.get(pred["elementType"], "dialog" if pred["elementType"] == "alert" else None)
            candidates = [(_iou_edge(xywh(pred["boundingBoxPixels"]), xywh(e["boundsPixels"]))[0], e["id"])
                          for e in items if available.get(e["id"]) == role]
            overlap, matched = max(candidates, default=(0, None))
            if overlap >= 0.5:
                role_hits[role] += 1
                del available[matched]
        frames.append(dict(id=ident, group=row["group"], misses=misses))
    q.require(len(models) == 1, "mixed_or_missing_model")
    return dict(images=len(rows), groups=len({r["group"] for r in rows}), failures=failures,
                roleCounts=dict(roles), roleRecall={r: [role_hits[r], n] for r, n in role_support.items()},
                consumerCounts={c:{s:counts[c,s] for s in
                ("matched","missed","unmatchedPrediction")} for c in sorted(SHIPPED)},
                frames=frames, modelSHA256=next(iter(models)), manifestSHA256=q.digest(manifest_path),
                scanSHA256=q.digest(scan_path), trainingAdmitted=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "scan", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    q.save(args.output, audit(args.manifest, args.scan))
