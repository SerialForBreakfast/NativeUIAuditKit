"""Score HCF pilot methods against verified focus truth on identical membership.

Contract: Research/Plans/HCF337.md. Synthetic inputs make no accuracy claim.
"""
import argparse
import itertools
import json
import math
import random
from pathlib import Path

TRUTH_VERSION = "hcf-pilot-truth-v1"
PREDICTION_VERSION = "hcf-pilot-predictions-v1"
REPORT_VERSION = "hcf-pilot-score-v1"
IOU_THRESHOLD = 0.5
PROFILES = {"default", "high_contrast"}
ROLES = ("development", "reserved")
STATES = {"focused", "no_focus", "uncertain"}
DECISIONS = {"select", "abstain"}
SUCCESS = {"correct", "correct_abstention"}


def require(condition, code):
    if not condition:
        raise ValueError(code)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def check_box(box, width, height):
    require(isinstance(box, dict) and set(box) == {"x", "y", "width", "height"}, "box_fields")
    require(all(finite(v) for v in box.values()), "box_not_finite")
    require(box["width"] > 0 and box["height"] > 0, "box_no_area")
    require(box["x"] >= 0 and box["y"] >= 0 and box["x"] + box["width"] <= width
            and box["y"] + box["height"] <= height, "box_outside_image")
    return box


def iou(a, b):
    w = max(0.0, min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"]))
    h = max(0.0, min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"]))
    inter = w * h
    return inter / (a["width"] * a["height"] + b["width"] * b["height"] - inter)


def load_truth(doc):
    require(isinstance(doc, dict) and doc.get("version") == TRUTH_VERSION, "truth_version")
    frames = doc.get("frames")
    require(isinstance(frames, list) and frames, "truth_frames")
    by_id = {}
    for f in frames:
        require(isinstance(f, dict), "truth_frame")
        fid = f.get("frame_id")
        require(isinstance(fid, str) and fid, "truth_frame_id")
        require(fid not in by_id, "duplicate_truth_frame")
        require(isinstance(f.get("sha256"), str) and len(f["sha256"]) == 64, "truth_sha256")
        require(type(f.get("width")) is int and type(f.get("height")) is int
                and f["width"] > 0 and f["height"] > 0, "truth_dimensions")
        require(f.get("profile") in PROFILES, "truth_profile")
        require(f.get("role") in ROLES, "truth_role")
        for key in ("family", "scene"):
            require(isinstance(f.get(key), str) and f[key], "truth_group")
        focus = f.get("focus")
        require(isinstance(focus, dict) and focus.get("state") in STATES, "truth_focus_state")
        if focus["state"] == "focused":
            check_box(focus.get("box"), f["width"], f["height"])
        else:
            require("box" not in focus, "truth_box_without_focus")
        by_id[fid] = f
    return by_id


def load_method(doc, truth):
    require(isinstance(doc, dict) and doc.get("version") == PREDICTION_VERSION, "prediction_version")
    name = doc.get("method")
    require(isinstance(name, str) and name, "method_name")
    entries = doc.get("frames")
    require(isinstance(entries, list), "prediction_frames")
    by_id = {}
    for e in entries:
        fid = e.get("frame_id") if isinstance(e, dict) else None
        require(isinstance(fid, str) and fid not in by_id, "duplicate_prediction_frame")
        by_id[fid] = e
    require(set(by_id) == set(truth), "membership_mismatch")
    for fid, e in by_id.items():
        frame = truth[fid]
        require(e.get("sha256") == frame["sha256"], "prediction_sha256_mismatch")
        require(e.get("decision") in DECISIONS, "prediction_decision")
        if e["decision"] == "select":
            check_box(e.get("box"), frame["width"], frame["height"])
        else:
            require("box" not in e, "abstain_with_box")
        if "latency_ms" in e:
            require(finite(e["latency_ms"]) and e["latency_ms"] >= 0, "latency_invalid")
    return name, by_id


def outcome(frame, entry):
    state = frame["focus"]["state"]
    if state == "uncertain":
        return "excluded", None
    if state == "no_focus":
        return ("correct_abstention" if entry["decision"] == "abstain" else "wrong_focus"), None
    if entry["decision"] == "abstain":
        return "miss", None
    overlap = iou(entry["box"], frame["focus"]["box"])
    return ("correct" if overlap >= IOU_THRESHOLD else "wrong_focus"), overlap


def representative_frames(truth):
    """Keep 1 frame for each repeated image inside a group; return kept IDs and excluded count."""
    chosen = {}
    for fid in sorted(truth):
        f = truth[fid]
        chosen.setdefault((f["family"], f["scene"], f["sha256"]), fid)
    kept = set(chosen.values())
    return kept, len(truth) - len(kept)


def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def group_interval(rows, seed, resamples):
    """Bootstrap the wrong-focus rate by resampling layout-family/scene groups."""
    groups = {}
    for r in rows:
        wrong, scored = groups.get(r["group"], (0, 0))
        groups[r["group"]] = (wrong + (r["outcome"] == "wrong_focus"), scored + 1)
    keys = sorted(groups)
    if not keys:
        return None
    rng = random.Random(seed)
    estimates = []
    for _ in range(resamples):
        sample = [groups[rng.choice(keys)] for _ in keys]
        estimates.append(sum(w for w, _ in sample) / sum(s for _, s in sample))
    return {"groups": len(keys), "low": percentile(estimates, 0.025),
            "high": percentile(estimates, 0.975), "seed": seed, "resamples": resamples}


def summarize(rows, seed, resamples):
    counts = {k: 0 for k in ("correct", "wrong_focus", "miss", "correct_abstention")}
    for r in rows:
        counts[r["outcome"]] += 1
    scored = len(rows)
    focused = sum(1 for r in rows if r["state"] == "focused")
    no_focus = scored - focused
    selections = sum(1 for r in rows if r["decision"] == "select")
    overlaps = [r["iou"] for r in rows if r["outcome"] == "correct"]
    latencies = [r["latency_ms"] for r in rows]
    complete = scored > 0 and all(v is not None for v in latencies)
    return {
        "scored": scored, "focused": focused, "noFocus": no_focus, "counts": counts,
        "wrongFocusRate": rate(counts["wrong_focus"], scored),
        "missRate": rate(counts["miss"], focused),
        "abstentionRate": rate(counts["miss"] + counts["correct_abstention"], scored),
        "coverage": rate(selections, scored),
        "noFocusSpecificity": rate(counts["correct_abstention"], no_focus),
        "accuracy": rate(counts["correct"] + counts["correct_abstention"], scored),
        "meanCorrectIoU": sum(overlaps) / len(overlaps) if overlaps else None,
        "latencyMs": ({"p50": percentile(latencies, 0.5), "p95": percentile(latencies, 0.95)}
                      if complete else None),
        "wrongFocusGroupInterval": group_interval(rows, seed, resamples),
    }


def score(truth_doc, method_docs, seed=0, resamples=2000):
    truth = load_truth(truth_doc)
    kept, duplicates = representative_frames(truth)
    uncertain = sum(1 for fid in kept if truth[fid]["focus"]["state"] == "uncertain")
    methods = {}
    for doc in method_docs:
        name, entries = load_method(doc, truth)
        require(name not in methods, "duplicate_method")
        rows = []
        for fid in sorted(kept):
            frame = truth[fid]
            result, overlap = outcome(frame, entries[fid])
            if result == "excluded":
                continue
            rows.append({"frame_id": fid, "group": f'{frame["family"]}/{frame["scene"]}',
                         "role": frame["role"], "state": frame["focus"]["state"],
                         "decision": entries[fid]["decision"], "outcome": result, "iou": overlap,
                         "latency_ms": entries[fid].get("latency_ms")})
        methods[name] = rows
    require(methods, "no_methods")
    report = {"version": REPORT_VERSION, "iouThreshold": IOU_THRESHOLD, "truthFrames": len(truth),
              "duplicateFramesExcluded": duplicates, "uncertainExcluded": uncertain,
              "methods": {}, "paired": []}
    for name, rows in methods.items():
        report["methods"][name] = {"all": summarize(rows, seed, resamples)}
        for role in ROLES:
            report["methods"][name][role] = summarize([r for r in rows if r["role"] == role], seed, resamples)
    for a, b in itertools.combinations(sorted(methods), 2):
        win_a = {r["frame_id"] for r in methods[a] if r["outcome"] in SUCCESS}
        win_b = {r["frame_id"] for r in methods[b] if r["outcome"] in SUCCESS}
        report["paired"].append({"methods": [a, b], "onlyFirstCorrect": len(win_a - win_b),
                                 "onlySecondCorrect": len(win_b - win_a), "bothCorrect": len(win_a & win_b)})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("truth", type=Path)
    parser.add_argument("methods", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--resamples", type=int, default=2000)
    args = parser.parse_args()
    require(not args.output.exists(), "output_exists")
    report = score(json.loads(args.truth.read_text()),
                   [json.loads(p.read_text()) for p in args.methods], args.seed, args.resamples)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
