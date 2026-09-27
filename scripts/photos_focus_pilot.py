"""Offline TTR Photos evidence import and human review. Never captures or scores models."""
import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw

from focus_dataset_contract import ROOT, FocusDataError, digest, image, local, member, pixel_digest, text
from focus_runtime import identity, bounded_batches, invoke, RUNTIME_PREPROCESSING

INDEX = "photos-focus-capture-index-v1"
INTAKE = "photos-focus-intake-v1"
REVIEW = "photos-focus-review-v1"
DIAGNOSTIC = "photos-focus-diagnostic-v1"
FLAGS = dict(partition="development", trainingEligible=False,
             independentEvaluationEligible=False, modelGatePassed="not_assessed")


def require(ok, reason):
    if not ok:
        raise FocusDataError(reason)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value), "invalid_id")
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    path = local(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def checked(root, record, limit=32 * 1024 * 1024):
    path = member(root, record["path"])
    require(path.stat().st_size <= limit, "file_size_limit")
    require(sha(path) == record["sha256"], "changed_hash")
    return path


def read(path):
    path = local(path)
    require(path.stat().st_size <= 2 * 1024 * 1024, "json_size_limit")
    def unique(items):
        out = {}
        for k, v in items:
            require(k not in out, "duplicate_json_key")
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: require(False, "nonfinite_json"))


def fresh(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink_output")
    path = local(path)
    require(any(path.is_relative_to(ROOT / prefix) for prefix in
                ("dataset/tvos_captures", "dataset/focus_ring", "reports/work", ".build")), "diagnostic_output_required")
    require(not path.exists(), "output_collision")
    return path


def write(path, doc, *, sealed=False):
    if sealed:
        doc["seal"] = digest(doc)
    with path.open("x") as stream:
        json.dump(doc, stream, indent=2, allow_nan=False)


def sealed(path, version):
    doc = read(path)
    require(doc.get("version") == version and
            doc.get("seal") == digest({k: v for k, v in doc.items() if k != "seal"}), "changed_or_unsupported_manifest")
    require(all(doc.get(k) == v for k, v in FLAGS.items()), "diagnostic_only")
    return doc


def raw_id(value):
    # Swift UUID-backed wrapper uses rawValue; string RawRepresentable may be scalar.
    return text(value["rawValue"] if isinstance(value, dict) and set(value) == {"rawValue"} else value)


def envelope(doc, kind, commands):
    require(isinstance(doc, dict) and type(doc.get("schemaVersion")) is int and doc.get("schemaVersion") == 1 and doc.get("success") is True
            and doc.get("error") is None and doc.get("command") in commands, "failed_or_unsupported_ttr_envelope")
    require(set(doc["data"]) == {kind} and set(doc["data"][kind]) == {"_0"}, "unsupported_ttr_payload")
    return doc["data"][kind]["_0"]


def session(doc, spec):
    status = envelope(doc, "status", {"status", "session status"})
    require(raw_id(status["selectedDeviceID"]) == spec["targetID"] and
            raw_id(status["sessionID"]) == spec["sessionID"], "wrong_session_or_target")
    require(status["connectionStatus"] == "connected" and status["commandActive"] is False
            and status["queuedCommandCount"] == 0, "session_not_idle_connected")


def observation(doc, spec, image_path):
    obs = envelope(doc, "observation", {"observe capture"})
    require(obs["sourceDeviceID"] == spec["sourceDeviceID"], "wrong_source_device")
    require(obs["mimeType"] == "image/png" and obs["orientation"] == "up"
            and obs["outputWritten"] is True, "unsupported_image_export")
    freshness = obs["freshness"]
    require(freshness["status"] == "current" and freshness["confidence"] in {"exact", "estimated"}
            and type(freshness["estimatedAgeMilliseconds"]) is int
            and 0 <= freshness["estimatedAgeMilliseconds"] <= 1000, "stale_observation")
    timestamp = obs["capturedAt"]
    require(type(timestamp["wallClock"]) in (int, float) and math.isfinite(timestamp["wallClock"])
            and type(timestamp["monotonic"]["nanoseconds"]) is int
            and timestamp["monotonic"]["nanoseconds"] >= 0, "invalid_timestamp")
    dimensions = obs["dimensions"]
    require(all(type(dimensions[k]) is int and dimensions[k] > 0 for k in ("width", "height")), "invalid_dimensions")
    image(image_path.parent, {"path": image_path.name, "sha256": sha(image_path)},
          [dimensions["width"], dimensions["height"]])
    require(not obs.get("imageBase64") or base64.b64decode(obs["imageBase64"], validate=True) == image_path.read_bytes(),
            "inline_image_mismatch")
    generation = obs.get("connectionGeneration")
    require(generation is None or type(generation) is int and generation >= 0, "invalid_generation")
    raw_id(obs["id"]); raw_id(obs["providerID"])
    return obs


def preview(source, destination, title, controls=()):
    with Image.open(source) as im:
        canvas = im.convert("RGB")
        draw = ImageDraw.Draw(canvas)
        for c in controls:
            x, y, w, h = c["bounds"]
            color = "lime" if c["state"] == "focused" else "orange"
            draw.rectangle((x, y, x+w, y+h), outline=color, width=3)
            draw.text((x, max(0, y-14)), c["id"], fill=color)
        canvas.thumbnail((1200, 675))
        sheet = Image.new("RGB", (canvas.width, canvas.height+36), "white")
        sheet.paste(canvas, (0, 36)); ImageDraw.Draw(sheet).text((8, 10), title, fill="black")
        sheet.save(destination)


def import_capture(input_path, output):
    input_path, output = local(input_path), fresh(output)
    original_index = ref(input_path)
    spec = read(input_path)
    require(isinstance(spec, dict) and spec.get("version") == INDEX, "unsupported_capture_index")
    for key in ("targetID", "sourceDeviceID", "sessionID", "operator", "sourceBindingReference"):
        text(spec.get(key))
    frames = spec["frames"]
    require(isinstance(frames, list) and 0 < len(frames) <= 60, "frame_limit")
    require(len({identifier(r["id"]) for r in frames}) == len(frames), "duplicate_frame_id")
    require(len({identifier(r["screenID"]) for r in frames}) <= 3, "screen_limit")
    root = input_path.parent
    status_path = checked(root, spec["sessionEvidence"], 2 * 1024 * 1024)
    session(read(status_path), spec)
    output.parent.mkdir(parents=True, exist_ok=True)
    estimated_bytes = input_path.stat().st_size + status_path.stat().st_size
    for entry in frames:
        for key in ("image", "observation", "nativeEvidence"):
            if key not in entry: continue
            try:
                limit = (32 if key == "image" else 2) * 1024 * 1024
                size = member(root, entry[key]["path"]).stat().st_size
                if size <= limit: estimated_bytes += size
            except (ValueError, OSError, KeyError, TypeError):
                pass  # Preserve per-frame failure accounting below.
    require(shutil.disk_usage(output.parent).free > estimated_bytes + 2_000_000_000, "storage_reserve")
    output.mkdir(); (output/"raw").mkdir(); (output/"raw/frames").mkdir(); (output/"sheets").mkdir()
    shutil.copyfile(input_path, output/"raw/index.json")
    shutil.copyfile(status_path, output/"raw/session.json")
    records = []; seen = {}; times = []; generations = set()
    for number, entry in enumerate(frames, 1):
        row = {"id": entry["id"], "number": number, "screenID": entry["screenID"], "sources": entry,
               "state": "blocked", "reason": None}
        try:
            image_path = checked(root, entry["image"])
            obs_path = checked(root, entry["observation"], 2 * 1024 * 1024)
            # Retain bounded, hash-valid evidence even if semantic/PNG checks fail.
            frame_root = output/"raw/frames"/entry["id"]
            frame_root.mkdir()
            saved_image = frame_root/"frame.png"
            saved_obs = frame_root/"observation.json"
            shutil.copyfile(image_path, saved_image); shutil.copyfile(obs_path, saved_obs)
            require(sha(saved_image) == entry["image"]["sha256"] and
                    sha(saved_obs) == entry["observation"]["sha256"], "source_changed_during_copy")
            row.update(image=ref(saved_image), observation=ref(saved_obs))
            if entry.get("nativeEvidence"):
                native = checked(root, entry["nativeEvidence"], 2 * 1024 * 1024)
                saved = frame_root/"native.json"
                shutil.copyfile(native, saved)
                require(sha(saved) == entry["nativeEvidence"]["sha256"], "native_changed_during_copy")
                row["nativeEvidence"] = ref(saved)
            obs = observation(read(saved_obs), spec, saved_image)
            oid = raw_id(obs["id"])
            require(oid not in seen, "duplicate_observation_id")
            seen[oid] = entry["id"]
            row.update(metadata=obs, pixelSHA256=pixel_digest(ROOT, row["image"]), state="imported")
            times.append(obs["capturedAt"]["monotonic"]["nanoseconds"])
            if obs.get("connectionGeneration") is not None: generations.add(obs["connectionGeneration"])
            with Image.open(saved_image) as im:
                if max(high for low, high in im.convert("RGB").getextrema()) == 0:
                    row.update(state="blocked", reason="black_capture")
            preview(saved_image, output/"sheets"/f"{number:02d}.png", f"{number:02d} {entry['id']} / {entry['screenID']} UNREVIEWED")
            checked(root, entry["image"]); checked(root, entry["observation"], 2 * 1024 * 1024)
        except (ValueError, OSError, KeyError, TypeError) as error:
            row.update(state="blocked", reason=str(error))
        records.append(row)
    if (times and (times != sorted(times) or max(times)-min(times) > 45*60*1_000_000_000)) or len(generations) > 1:
        for row in records:
            if row["state"] == "imported": row.update(state="blocked", reason="session_time_or_generation_changed")
    require(sha(input_path) == sha(output/"raw/index.json") == original_index["sha256"] and
            sha(status_path) == sha(output/"raw/session.json") == spec["sessionEvidence"]["sha256"], "source_changed_during_import")
    doc = {"version": INTAKE, **FLAGS, "source": ref(output/"raw/index.json"),
           "sessionEvidence": ref(output/"raw/session.json"), "sessionBinding": "operator-declared-context-not-atomic",
           "targetID": spec["targetID"], "sessionID": spec["sessionID"], "frames": records,
           "counts": dict(Counter(r["state"] for r in records))}
    write(output/"intake.json", doc, sealed=True)
    review = {"version": REVIEW, "intake": ref(output/"intake.json"), "frames": [
        {"id": r["id"], "imageSHA256": r.get("image", {}).get("sha256"), "confirmed": False,
         "reviewer": None, "reviewedAt": None, "reviewReference": None, "photosConfirmed": False,
         "settled": False, "contentApproved": False, "nativeAssessment": "not-reviewed" if r.get("nativeEvidence") else "unavailable",
         "controls": []} for r in records], "pairs": []}
    write(output/"review-template.json", review)
    return doc


def box(value, size):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value), "invalid_bounds")
    x, y, w, h = value
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= size[0] and y+h <= size[1], "invalid_bounds")


def reviewed_frame(row, review):
    require(row["state"] == "imported", "frame_intake_blocked")
    path = checked(ROOT, row["image"]); checked(ROOT, row["observation"], 2*1024*1024)
    require(review.get("imageSHA256") == row["image"]["sha256"], "review_image_changed")
    require(review.get("confirmed") is True, "unconfirmed_review")
    text(review.get("reviewer")); text(review.get("reviewReference"))
    when = datetime.fromisoformat(text(review.get("reviewedAt")).replace("Z", "+00:00"))
    require(when.utcoffset() is not None, "review_timezone_required")
    require(all(review.get(k) is True for k in ("photosConfirmed", "settled", "contentApproved")), "context_or_content_unconfirmed")
    if row.get("nativeEvidence"):
        checked(ROOT, row["nativeEvidence"], 2*1024*1024)
        require(review.get("nativeAssessment") == "consistent", "native_unresolved_or_conflicting")
    else:
        require(review.get("nativeAssessment") == "unavailable", "fabricated_native_review")
    controls = review["controls"]
    require(isinstance(controls, list) and 0 < len(controls) <= 100, "missing_controls")
    require(len({identifier(c["id"]) for c in controls}) == len(controls), "duplicate_control_id")
    size = image(ROOT, row["image"])
    for c in controls:
        box(c["bounds"], size)
        require(c["state"] in {"focused", "unfocused", "unknown"}, "invalid_focus_state")
    require(sum(c["state"] == "focused" for c in controls) <= 1, "multiple_reviewed_focus")
    return path


def review_capture(intake_path, review_path, output):
    intake_path, review_path, output = local(intake_path), local(review_path), fresh(output)
    doc = sealed(intake_path, INTAKE); review = read(review_path)
    checked(ROOT, doc["source"]); checked(ROOT, doc["sessionEvidence"])
    require(review.get("version") == REVIEW and review.get("intake") == ref(intake_path), "changed_review_intake")
    rows = {r["id"]: r for r in doc["frames"]}
    annotations = review["frames"]
    require(isinstance(annotations, list) and len(annotations) == len(rows) and
            {a["id"] for a in annotations} == set(rows), "review_frame_membership")
    attempts = review["pairs"]
    require(isinstance(attempts, list) and len(attempts) <= 20, "pair_limit")
    require(len({identifier(p["id"]) for p in attempts}) == len(attempts), "duplicate_pair_id")
    review_ref = ref(review_path); intake_ref = ref(intake_path)
    output.mkdir(parents=True); (output/"sheets").mkdir(); (output/"crops").mkdir()
    shutil.copyfile(review_path, output/"review.json")
    valid = {}; frame_states = []
    for a in annotations:
        row = rows[a["id"]]
        try:
            path = reviewed_frame(row, a)
            preview(path, output/"sheets"/f"{row['number']:02d}.png", f"{row['number']:02d} {row['id']} HUMAN REVIEW", a["controls"])
            valid[a["id"]] = a
            state = {"id": a["id"], "state": "reviewed"}
        except (ValueError, OSError, KeyError, TypeError) as error:
            state = {"id": a["id"], "state": "blocked", "reason": str(error)}
        frame_states.append(state)
    pairs = []
    for attempt in attempts:
        result = {"id": attempt["id"], "request": attempt, "state": "blocked"}
        try:
            element = identifier(attempt["elementID"])
            f, u = attempt["focusedFrame"], attempt["unfocusedFrame"]
            require(f in valid and u in valid and f != u, "missing_or_unreviewed_pair_frame")
            require(rows[f]["screenID"] == rows[u]["screenID"], "cross_screen_pair")
            bound = {}
            for label, fid in (("focused", f), ("unfocused", u)):
                controls = valid[fid]["controls"]
                matches = [c for c in controls if c["id"] == element]
                require(len(matches) == 1 and matches[0]["state"] == label, "missing_or_conflicting_pair_label")
                require(sum(c["state"] == "focused" for c in controls) == 1, "unresolved_frame_focus")
                bound[label] = {"frameID": fid, "image": rows[fid]["image"], "bounds": matches[0]["bounds"],
                                "labelSource": "human-reviewed-visual", "review": valid[fid]}
            require(rows[f]["pixelSHA256"] != rows[u]["pixelSHA256"], "identical_focus_pair_pixels")
            result.update(state="crop-pending", frames=bound, elementID=element, screenID=rows[f]["screenID"])
        except (ValueError, OSError, KeyError, TypeError) as error:
            result["reason"] = str(error)
        pairs.append(result)
    pending = [p for p in pairs if p["state"] == "crop-pending"]
    runtime = None; runtime_failure = None
    if pending:
        try: runtime = identity()
        except (ValueError, OSError) as error: runtime_failure = str(error)
    items = [{"id": p["id"]+":"+label, "path": str(checked(ROOT, f["image"])),
              "sha256": f["image"]["sha256"], "bounds": f["bounds"]}
             for p in pending for label, f in p["frames"].items()]
    crops = {}; failures = {}
    for batch in bounded_batches(items):
        try:
            require(runtime_failure is None, runtime_failure)
            results = invoke(batch)["results"]  # crop mode: no model argument, ever
            require([r["id"] for r in results] == [r["id"] for r in batch], "crop_membership")
            for r in results:
                png = base64.b64decode(r["png"], validate=True)
                with Image.open(io.BytesIO(png), formats=["PNG"]) as im:
                    im.load(); require(im.size == (256, 256), "crop_dimensions")
                path = output/"crops"/(r["id"].replace(":", "-")+".png")
                with path.open("xb") as stream: stream.write(png)
                crops[r["id"]] = {**ref(path), "pixelSHA256": pixel_digest(ROOT, ref(path))}
        except (ValueError, OSError, KeyError, TypeError) as error:
            failures.update({i["id"]: str(error) for i in batch})
    for p in pending:
        ids = [p["id"]+":"+label for label in p["frames"]]
        if any(k in failures or k not in crops for k in ids):
            p.update(state="blocked", reason="crop_failed:"+next((failures[k] for k in ids if k in failures), "missing"))
        else:
            for label, f in p["frames"].items(): f["crop"] = crops[p["id"]+":"+label]
            p["state"] = "accepted-diagnostic"
    # A pixel-identical control crop cannot truthfully have both focus labels.
    pixel_uses = defaultdict(list)
    for p in pending:
        for label, f in p["frames"].items():
            if "crop" in f: pixel_uses[f["crop"]["pixelSHA256"]].append((p, label))
    contradictions = []
    for pixel, uses in pixel_uses.items():
        if len({label for _, label in uses}) > 1:
            contradictions.append(pixel)
            for p, _ in uses: p.update(state="blocked", reason="contradictory_crop_pixels")
    duplicate_pairs = []; seen = {}
    for p in pending:
        if p["state"] != "accepted-diagnostic": continue
        key = tuple(p["frames"][k]["crop"]["pixelSHA256"] for k in ("focused", "unfocused"))
        if key in seen:
            p.update(state="duplicate", reason="duplicate_pair_pixels", duplicateOf=seen[key]); duplicate_pairs.append(p["id"])
        else:
            seen[key] = p["id"]
            sheet = Image.new("RGB", (512, 288), "white")
            for x, label in ((0, "focused"), (256, "unfocused")):
                with Image.open(checked(ROOT, p["frames"][label]["crop"])) as im: sheet.paste(im.convert("RGB"), (x, 32))
                ImageDraw.Draw(sheet).text((x+4, 8), p["id"]+" "+label, fill="black")
            sheet.save(output/"sheets"/(p["id"]+"-pair.png"))
    if runtime is not None and runtime != identity():
        for pair in pairs:
            if pair["state"] in {"accepted-diagnostic", "duplicate"}:
                pair.update(state="blocked", reason="crop_runtime_changed")
    require(review_ref == ref(review_path) and intake_ref == ref(intake_path), "inputs_changed_during_review")
    for row in rows.values():
        for key in ("image", "observation", "nativeEvidence"):
            if key in row: checked(ROOT, row[key])
    groups = defaultdict(list)
    for r in rows.values():
        if r.get("pixelSHA256"): groups[r["pixelSHA256"]].append(r["id"])
    result = {"version": DIAGNOSTIC, **FLAGS, "intake": intake_ref, "review": ref(output/"review.json"),
              "labelSource": "human-reviewed-visual", "runtime": runtime, "preprocessing": RUNTIME_PREPROCESSING,
              "frames": frame_states, "pairs": pairs, "frameCounts": dict(Counter(r["state"] for r in frame_states)),
              "pairCounts": dict(Counter(p["state"] for p in pairs)), "frameFiles": sum("image" in r for r in rows.values()),
              "distinctFramePixels": len(groups), "duplicateFrames": [ids for ids in groups.values() if len(ids) > 1],
              "duplicatePairs": duplicate_pairs, "contradictoryCropPixels": contradictions,
              "nativeQualification": "not_assessed", "candidateSetCompleteness": "not_assessed"}
    write(output/"diagnostic.json", result, sealed=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("import"); p.add_argument("--input", type=Path, required=True)
    p = commands.add_parser("review"); p.add_argument("--intake", type=Path, required=True); p.add_argument("--review", type=Path, required=True)
    for p in commands.choices.values(): p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (import_capture(args.input, args.output) if args.command == "import" else
                  review_capture(args.intake, args.review, args.output))
        print(json.dumps({k: result[k] for k in ("version", "counts", "frameCounts", "pairCounts", "trainingEligible") if k in result}))
        return 2 if any(r["state"] == "blocked" for r in result.get("frames", [])+result.get("pairs", [])) else 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"state": "failed", "reason": str(error), "trainingEligible": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
