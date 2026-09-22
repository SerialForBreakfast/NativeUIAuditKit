#!/usr/bin/env python3
"""Offline PER-05 benchmark. Uses production Swift measurements, never truth as input."""
import argparse
import hashlib
import json
import math
import platform
import subprocess
import time
from collections import Counter, deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {"static", "crossfade", "focus-animation", "scroll", "background-carousel"}


class Invalid(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Invalid(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def host_description():
    # Avoid platform.platform()'s subprocess-based CPU lookup in timeout handling.
    return f"{platform.system()} {platform.release()} {platform.machine()}"


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and 0 < len(value) <= 256


def read_json(path):
    require(path.stat().st_size <= 8_388_608, "oversized_json")
    def pairs(items):
        d = {}
        for k, v in items:
            require(k not in d, "duplicate_json_key")
            d[k] = v
        return d
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def validate_policy(p):
    require(p.get("version") == "transition-policy-v1" and text(p.get("reference")), "policy_version_or_reference")
    require(p.get("frozenOn") in ("development", "validation", "test-only"), "test_fitted_policy")
    for k in ("distanceThreshold", "stableMs", "maxGapMs", "maxAgeMs", "timeoutMs", "toolTimeoutSeconds"):
        require(number(p.get(k)) and p[k] > 0, "invalid_policy_" + k)
    require(type(p.get("minimumFrames")) is int and 2 <= p["minimumFrames"] <= 8, "history_bound")
    require(type(p.get("noiseThreshold")) is int and 0 <= p["noiseThreshold"] <= 255, "noise_threshold")
    require(p["stableMs"] < p["timeoutMs"] <= 60_000 and p["toolTimeoutSeconds"] <= 120, "timeout_bound")


def validate(doc, root, policy):
    validate_policy(policy)
    require(doc.get("version") == "transition-sequences-v1" and text(doc.get("corpusID")), "manifest_version")
    sequences = doc.get("sequences")
    require(isinstance(sequences, list) and 1 <= len(sequences) <= 64, "sequence_count")
    ids, groups, pixels = set(), {}, {}
    for s in sequences:
        require(text(s.get("id")) and s["id"] not in ids, "sequence_id"); ids.add(s["id"])
        for k in ("group", "sourceReference", "reviewReference"):
            require(text(s.get(k)), "missing_" + k)
        require(s.get("partition") in ("development", "validation", "test"), "partition")
        require(s.get("sourceKind") in ("test-only", "simulator", "physical"), "source")
        require(s.get("scenario") in SCENARIOS and s.get("regionOrigin") == "caller-configured", "scenario_or_regions_origin")
        require(s.get("labelOrigin") in ("synthetic-generator", "reviewed-human", "fixture-callback"), "prediction_truth")
        require(s.get("focusSource") in ("test-only", "independent-observation"), "focus_source")
        if s["sourceKind"] != "test-only":
            require(s["focusSource"] != "test-only" and s["labelOrigin"] != "synthetic-generator" and policy["frozenOn"] != "test-only", "false_real_evidence")
        require(groups.setdefault(s["group"], s["partition"]) == s["partition"], "group_leakage")
        require(number(s.get("startMs")) and s["startMs"] >= 0, "start_time")
        frames = s.get("frames")
        require(isinstance(frames, list) and 1 <= len(frames) <= 64, "frame_bound")
        regions = s.get("foregroundRegions")
        require(isinstance(regions, list) and 1 <= len(regions) <= 8, "region_count")
        for b in regions:
            require(isinstance(b, list) and len(b) == 4 and all(number(x) for x in b) and min(b[:2]) >= 0 and min(b[2:]) > 0, "region_box")
        frame_ids, last_arrival, size = set(), -1, None
        for f in frames:
            require(text(f.get("id")) and f["id"] not in frame_ids and text(f.get("observationID")), "frame_identity"); frame_ids.add(f["id"])
            require(all(number(f.get(k)) and f[k] >= 0 for k in ("capturedMs", "observedMs")), "timestamp")
            require(f["observedMs"] > last_arrival and f["observedMs"] >= s["startMs"], "arrival_order"); last_arrival = f["observedMs"]
            require(f.get("truth") in ("ready", "unstable", "unknown") and f.get("focus") in ("present", "none", "unknown"), "state_label")
            require(type(f.get("missing", False)) is bool, "missing_type")
            if f.get("missing"):
                require(not any(k in f for k in ("path", "sha256", "width", "height")), "missing_with_pixels")
                continue
            require(isinstance(f.get("path"), str) and not Path(f["path"]).is_absolute() and ".." not in Path(f["path"]).parts, "image_path")
            path = root / f["path"]
            require(path.resolve().is_relative_to(root.resolve()) and path.resolve() == path.absolute(), "image_escape")
            require(path.is_file() and 0 < path.stat().st_size <= 32*1024*1024, "missing_or_large_image")
            require(file_hash(path) == f.get("sha256"), "image_hash")
            with Image.open(path) as im:
                require(im.format == "PNG" and im.width * im.height <= 16_000_000, "image_format_or_size")
                require(type(f.get("width")) is int and type(f.get("height")) is int and im.size == (f["width"], f["height"]), "image_dimensions")
                im.load()
                pixel_hash = hashlib.sha256(str(im.size).encode() + im.convert("RGB").tobytes()).hexdigest()
                require(pixels.setdefault(pixel_hash, s["partition"]) == s["partition"], "pixel_leakage")
                require(size is None or size == im.size, "unregistered_dimensions"); size = im.size
            require(all(b[0]+b[2] <= size[0] and b[1]+b[3] <= size[1] for b in regions), "region_outside")
    return sequences


def overlap(a, b):
    return min(a[0]+a[2], b[0]+b[2]) > max(a[0], b[0]) and min(a[1]+a[3], b[1]+b[3]) > max(a[1], b[1])


def pair_id(a, b):
    return digest([a["id"], b["id"]])


def measure(sequence, root, policy, helper):
    pairs = []
    frames = sequence["frames"]
    for i, current in enumerate(frames):
        if current.get("missing"):
            continue
        for previous in frames[:i]:
            if previous.get("missing"):
                continue
            pairs.append({"id": pair_id(previous, current), **{
                k: {"path": str((root / f["path"]).absolute()), "sha256": f["sha256"]}
                for k, f in (("previous", previous), ("current", current))}})
    if not pairs:
        return {}, {"host": host_description(), "processMilliseconds": None, "pairMilliseconds": []}
    start = time.perf_counter()
    result = subprocess.run([str(helper)], input=json.dumps({"version": 1, "root": str(root.absolute()), "noiseThreshold": policy["noiseThreshold"], "pairs": pairs}), text=True, capture_output=True, timeout=policy["toolTimeoutSeconds"])
    require(result.returncode == 0, "primitive_execution_failed:" + result.stderr[-600:])
    reply = json.loads(result.stdout)
    require(reply.get("version") == 1 and isinstance(reply.get("results"), list), "primitive_protocol")
    rows = reply["results"]
    require(len(rows) == len(pairs) and [r["id"] for r in rows] == [p["id"] for p in pairs], "primitive_membership")
    for r in rows:
        require(number(r.get("distance")) and r["distance"] >= 0 and number(r.get("milliseconds")) and r["milliseconds"] >= 0, "primitive_nonfinite")
        require(isinstance(r.get("regions"), list) and all(isinstance(b, list) and len(b)==4 and all(number(v) for v in b) and min(b[:2]) >= 0 and min(b[2:]) > 0 for b in r["regions"]), "primitive_regions")
    return {r["id"]: r for r in rows}, {"host": reply["host"], "processMilliseconds": (time.perf_counter()-start)*1000, "pairMilliseconds": [r["milliseconds"] for r in rows]}


def predict(sequence, measurements, p, mode):
    """Causal bounded-memory policy. Never reads truth or later frames."""
    history = deque()
    seen = set()  # bounded by the admitted 64-frame episode
    last_capture = None
    decisions = []
    for f in sequence["frames"]:
        evidence = []
        state, reason = "unknown", "missing"
        if f["observedMs"] - sequence["startMs"] >= p["timeoutMs"]:
            state, reason = "timeout", "deadline"
        elif f.get("missing"):
            pass
        elif f["observationID"] in seen:
            reason = "repeated_observation"
        elif not 0 <= f["observedMs"]-f["capturedMs"] <= p["maxAgeMs"]:
            reason = "stale_or_future"
        elif last_capture is not None and f["capturedMs"] <= last_capture:
            reason = "capture_order"
        elif f["focus"] != "present":
            reason = "focus_" + f["focus"]
        else:
            gap = bool(history) and f["capturedMs"]-history[-1]["capturedMs"] > p["maxGapMs"]
            if gap:
                history.clear()
            history.append(f)
            if len(history) > p["minimumFrames"]:
                del history[1]  # retain the stable-run anchor, not just recent frames
            state, reason = "wait", "cadence_gap" if gap else "insufficient_history"
            if len(history) >= 2:
                rows = [measurements.get(pair_id(old, f)) for old in list(history)[:-1]]
                if any(r is None for r in rows):
                    state, reason = "unknown", "missing_measurement"
                else:
                    evidence = [{"previousObservationID": old["observationID"], "distance": r["distance"], "regions": r["regions"]}
                                for old, r in zip(list(history)[:-1], rows)]
                    stable = all(r["distance"] <= p["distanceThreshold"] for r in rows) if mode == "full-frame" else not any(overlap(box, roi) for r in rows for box in r["regions"] for roi in sequence["foregroundRegions"])
                    if not stable:
                        state, reason = "wait", "visual_change"
                        history.clear(); history.append(f)
                    elif len(history) == p["minimumFrames"] and f["capturedMs"]-history[0]["capturedMs"] >= p["stableMs"]:
                        state, reason = "ready", "stable_window"
        if state in ("unknown", "timeout"):
            history.clear()
        decisions.append({"id": f["id"], "observationID": f["observationID"], "capturedMs": f["capturedMs"], "observedMs": f["observedMs"], "state": state, "reason": reason, "support": [x["observationID"] for x in history], "primitiveEvidence": evidence})
        seen.add(f["observationID"])
        if not f.get("missing") and f["capturedMs"] <= f["observedMs"]:
            last_capture = max(last_capture if last_capture is not None else -1, f["capturedMs"])
    return decisions


def score(sequence, decisions):
    counts = Counter(); delays = []; interval = None; detected = False
    for f, d in zip(sequence["frames"], decisions):
        truth, state = f["truth"], d["state"]
        counts["frames"] += 1; counts[truth+"Support"] += 1; counts[state+"Decisions"] += 1
        counts["reason:"+d["reason"]] += 1
        if truth == "unstable" and state == "ready": counts["prematureReady"] += 1
        if truth == "ready" and state in ("wait", "timeout"): counts["falseWaits"] += 1
        if truth == "unknown" and state == "ready": counts["unscoredReady"] += 1
        if truth == "ready":
            if interval is None: interval = f["capturedMs"]; detected = False
            if not detected and state == "ready":
                delays.append(max(0, f["observedMs"]-interval)); detected = True
        elif interval is not None:
            if not detected: delays.append(None)
            interval = None
    if interval is not None and not detected: delays.append(None)
    return {"counts": dict(counts), "readyIntervalDelayMs": delays,
            "timedOut": any(d["state"]=="timeout" for d in decisions),
            "noReady": not any(d["state"]=="ready" for d in decisions)}


def summarize(results):
    c = Counter(); delays = []
    for r in results:
        c.update(r["counts"]); delays += r["readyIntervalDelayMs"]
    def rate(key, denominator): return c[key]/c[denominator] if c[denominator] else None
    return {"sequences": len(results), "counts": dict(c), "prematureReadyRate": rate("prematureReady", "unstableSupport"),
            "falseWaitRate": rate("falseWaits", "readySupport"), "abstentionRate": rate("unknownDecisions", "frames"),
            "timedOutSequences": sum(r["timedOut"] for r in results), "noReadySequences": sum(r["noReady"] for r in results),
            "readyIntervalDelayMs": delays, "undetectedReadyIntervals": delays.count(None)}


def percentiles(values):
    values = sorted(values)
    return {"n": len(values), **{k: values[min(len(values)-1, math.ceil(q*len(values))-1)] if values else None for k,q in (("p50",.5),("p95",.95))}}


def evaluate(doc, root, policy, helper, measurement_fn=measure):
    sequences = validate(doc, root, policy)
    results = []; timings = []; failures = []
    for s in sequences:
        try:
            measurements, timing = measurement_fn(s, root, policy, helper); timings.append(timing)
        except (Invalid, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
            failures.append({"sequence": s["id"], "reason": str(exc)[:800]})
            continue
        policies = {}
        for mode in ("full-frame", "foreground-roi"):
            decisions = predict(s, measurements, policy, mode)
            policies[mode] = {"decisions": decisions, "metrics": score(s, decisions)}
        results.append({"id": s["id"], "sourceKind": s["sourceKind"], "scenario": s["scenario"], "partition": s["partition"], "group": s["group"], "policies": policies})
    summary = {}
    for mode in ("full-frame", "foreground-roi"):
        slices = {"overall": summarize([r["policies"][mode]["metrics"] for r in results])}
        for key, values in (("sourceKind", ("test-only", "simulator", "physical")), ("scenario", SCENARIOS), ("partition", ("development", "validation", "test"))):
            for value in sorted(values):
                slices[key+":"+value] = summarize([r["policies"][mode]["metrics"] for r in results if r[key]==value])
        summary[mode] = slices
    sources = ["scripts/transition_benchmark.py", "scripts/generate_transition_fixture.py", "Tools/TransitionTool/main.swift", "Sources/NativeUIAuditKit/Perception/FrameSimilarity.swift", "Sources/NativeUIAuditKit/Perception/ChangeRegionLocalizer.swift"]
    return {"version": "transition-report-v1", "status": "partial" if failures else "complete", "corpusSHA256": digest(doc), "policySHA256": digest(policy),
            "helperSHA256": file_hash(helper), "sourceHashes": {p: file_hash(ROOT/p) for p in sources}, "policy": policy,
            "accounting": {"expectedSequences":len(sequences), "evaluatedSequences":len(results), "failedSequences":len(failures)},
            "results": results, "summary": summary, "failures": failures,
            "latency": {"scope":"offline process including image decode and primitive measurements; not TTR navigation", "hosts":sorted({t["host"] for t in timings}),
                        "machineArchitecture": platform.machine(), "pythonHost": host_description(),
                        "processColdMs": percentiles([t["processMilliseconds"] for t in timings if t["processMilliseconds"] is not None]),
                        "firstPairMs":percentiles([t["pairMilliseconds"][0] for t in timings if t["pairMilliseconds"]]),
                        "subsequentPairMs":percentiles([v for t in timings for v in t["pairMilliseconds"][1:]])},
            "outcomes": {"dataEligible":False,"liveIntegrationQualified":False,"modelGatePassed":None},
            "recommendation":"No temporal training: validate independent held-out complete journeys and reviewed numeric gates first. ROI stability does not establish focus correctness, overlay safety or action authority."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True); parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--helper", type=Path, default=ROOT/".build/debug/TransitionTool")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        output = args.output.absolute()
        require(output.resolve().is_relative_to(ROOT) and output.parent.is_dir() and not output.exists() and not output.is_symlink(), "output_collision_or_boundary")
        manifest = args.manifest.absolute(); require(manifest.resolve().is_relative_to(ROOT), "manifest_boundary")
        helper = args.helper.resolve(); require(helper.is_relative_to(ROOT) and helper.is_file(), "helper_missing_or_boundary")
        report = evaluate(read_json(manifest), manifest.parent, read_json(args.policy), helper)
        with output.open("x") as stream: json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        print(json.dumps({"status":report["status"],"output":str(output),"accounting":report["accounting"]}))
        return 1 if report["failures"] else 0
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error":str(exc)})); return 2


if __name__ == "__main__":
    raise SystemExit(main())
