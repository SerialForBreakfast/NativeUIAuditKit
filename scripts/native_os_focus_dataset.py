"""Admit completed native XCTest focus journeys for development, never training approval."""
import argparse
import base64
import hashlib
import io
import json
import math
from pathlib import Path

from focus_dataset_contract import FocusDataError, digest, local, member, image, pixel_digest, expanded_box
from focus_runtime import invoke, identity, RUNTIME_PREPROCESSING
from focus_ring_baseline import artifact_digest


def node_key(node):
    key = node.get("identifier") or node.get("label")
    if key == "AppCell":
        label = node.get("label")
        if not isinstance(label, str) or not label.strip():
            raise FocusDataError("missing_native_identity")
        key += ":" + label # HeadBoard repeats AppCell; duplicate labels still reject.
    if not isinstance(key, str) or not key.strip():
        raise FocusDataError("missing_native_identity")
    return str(node["kind"]) + ":" + key


def read_journey(attachments, target, screen="settings/root"):
    attachments = local(attachments)
    exported = json.loads(member(attachments, "manifest.json").read_text())
    if not isinstance(exported, list) or len(exported) != 1:
        raise FocusDataError("one_test_required")
    entries = exported[0]["attachments"]
    if not entries or len(entries) > 200:
        raise FocusDataError("invalid_attachment_count")
    records, pngs, terminal, names = [], {}, [], set()
    for entry in entries:
        if entry.get("deviceId") != target or entry.get("isAssociatedWithFailure") is not False:
            raise FocusDataError("failed_or_wrong_target")
        path = member(attachments, entry["exportedFileName"])
        if path.name in names:
            raise FocusDataError("duplicate_attachment")
        names.add(path.name)
        if path.suffix == ".png" and str(entry.get("suggestedHumanReadableName", "")).startswith("entry-review"):
            image(attachments, {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        elif path.suffix == ".png":
            pngs[hashlib.sha256(path.read_bytes()).hexdigest()] = path.name
        elif path.suffix == ".json":
            records.append((path.name, json.loads(path.read_text())))
        elif path.suffix == ".txt":
            if screen == "home/root" and str(entry.get("suggestedHumanReadableName", "")).startswith("home-setup-context"):
                continue  # Diagnostic tree, retained in sourceHashes; never completion evidence.
            terminal.append(path.read_text())
        else:
            raise FocusDataError("unexpected_attachment")
    foreground = "homeForeground=true" if screen == "home/root" else "settingsForeground=true"
    if screen not in {"home/root", "settings/root", "settings/general", "settings/accessibility", "settings/apps", "settings/remotes"}:
        raise FocusDataError("unsupported_screen")
    if len(terminal) != 1 or "completed=true" not in terminal[0] or foreground not in terminal[0]:
        raise FocusDataError("incomplete_journey")
    if screen == "home/root" and "screenID=home/root;" not in terminal[0]:
        raise FocusDataError("wrong_screen")
    if screen.startswith("settings/") and screen != "settings/root" and ("returnedRoot=true" not in terminal[0] or "screenID="+screen not in terminal[0]):
        raise FocusDataError("unverified_submenu_return")
    records.sort(key=lambda row: row[1]["name"])
    if not records or len(records) > 41:
        raise FocusDataError("invalid_frame_count")
    if f"inputs={len(records)-1};" not in terminal[0]:
        raise FocusDataError("input_accounting")
    unique, seen_pixels, seen_names = [], {}, set()
    transitions, previous_focus, previous_action = [], None, None
    for index, (sidecar, frame) in enumerate(records):
        if frame.get("version") not in {"native-os-focus-observation-v1", "native-os-focus-observation-v2"} or frame.get("sourceKind") != "tvos_simulator_os":
            raise FocusDataError("unsupported_observation")
        if frame["version"] == "native-os-focus-observation-v2" and "screenID" not in frame:
            raise FocusDataError("missing_screen_identity")
        if frame.get("screenID", "settings/root") != screen:
            raise FocusDataError("wrong_screen")
        if frame["name"] in seen_names:
            raise FocusDataError("duplicate_frame")
        seen_names.add(frame["name"])
        setup_action = {"home/root": "setup-home", "settings/root": "activate-settings", "settings/general": "enter-general", "settings/accessibility": "enter-accessibility", "settings/apps": "enter-apps", "settings/remotes": "enter-remotes and devices"}[screen]
        directions = {"up", "down", "left", "right"} if screen == "home/root" else {"up", "down"}
        if frame["action"] not in ({setup_action} if index == 0 else directions):
            raise FocusDataError("unexpected_action")
        before, after = frame["before"], frame["after"]
        if before["nodes"] != after["nodes"] or before["focus"] != after["focus"] or before["viewportPoints"] != after["viewportPoints"]:
            raise FocusDataError("unstable_capture")
        times = [before["timestamp"], frame["captureStartedAt"], frame["captureEndedAt"], after["timestamp"]]
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in times) or times != sorted(times) or times[-1]-times[0] > 5:
            raise FocusDataError("stale_capture")
        focused = [n for n in before["nodes"] if n.get("focused") is True]
        if focused != [before["focus"]]:
            raise FocusDataError("ambiguous_focus")
        node_key(focused[0])
        current_focus = node_key(focused[0])
        if previous_focus is not None:
            transitions.append({"source": previous_focus, "direction": frame["action"],
                                "destination": current_focus, "observation": frame["name"],
                                "boundary": previous_focus == current_focus,
                                "directionPair": [previous_action, frame["action"]] if previous_action else None})
        previous_focus = current_focus
        previous_action = frame["action"] if index else None
        sha = frame["pngSHA256"]
        if sha not in pngs:
            raise FocusDataError("missing_pixels")
        raw = {"path": pngs[sha], "sha256": sha}
        size = image(attachments, raw, frame["pixelDimensions"])
        view = before["viewportPoints"]
        if len(view) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) for v in view) or min(view[2:]) <= 0:
            raise FocusDataError("invalid_viewport")
        sx, sy = size[0]/view[2], size[1]/view[3]
        if abs(sx-sy) > 1e-6:
            raise FocusDataError("nonuniform_scale")
        pixels = pixel_digest(attachments, raw)
        # AX can omit decorative chevrons on a return visit while pixels are
        # identical. Preserve the first full observation; require identical
        # focus identity/geometry, not an identical decorative subtree.
        binding = digest([before["focus"], before["viewportPoints"]])
        if pixels in seen_pixels:
            if seen_pixels[pixels] != binding:
                raise FocusDataError("contradictory_identical_pixels")
            continue
        seen_pixels[pixels] = binding
        unique.append({"frame": frame, "sidecar": sidecar, "raw": raw, "pixelSHA256": pixels, "scale": sx})
    if set(pngs) != {r[1]["pngSHA256"] for r in records}:
        raise FocusDataError("unindexed_pixels")
    visited = sorted({node_key(f["frame"]["before"]["focus"]) for f in unique})
    tested = {(e["source"], e["direction"]) for e in transitions}
    return unique, {"observations": len(records), "inputs": len(records)-1,
                    "uniqueFrames": len(unique), "terminal": terminal[0],
                    "transitions": transitions, "visitedIdentities": visited,
                    "unexploredDirections": [{"source": key, "direction": direction}
                        for key in visited for direction in ("left", "right", "up", "down")
                        if (key, direction) not in tested], "exhaustiveCoverage": False}


def pair_frames(frames, lineage):
    """One focused/unfocused example per identity; nearest eligible negative, deterministic."""
    keys = sorted({node_key(f["frame"]["before"]["focus"]) for f in frames})
    pairs, gaps = [], []
    for key in keys:
        roles = {True: [], False: []}
        for f in frames:
            nodes = [n for n in f["frame"]["before"]["nodes"] if (n.get("identifier") or n.get("label")) and node_key(n) == key]
            if len(nodes) != 1:
                continue  # Do not bind duplicate labels by position.
            node = nodes[0]
            x, y, w, h = node["bounds"]
            vx, vy, _, _ = f["frame"]["before"]["viewportPoints"]
            s = f["scale"]
            bounds = [(x-vx)*s, (y-vy)*s, w*s, h*s]
            try:
                expanded_box(bounds, f["frame"]["pixelDimensions"])
            except FocusDataError:
                continue  # Clipped/offscreen controls are not silently clamped labels.
            roles[node["focused"]].append({**f["raw"], "bounds": bounds,
                "sidecar": f["sidecar"], "pixelSHA256": f["pixelSHA256"],
                "observationName": f["frame"]["name"], "labelSource": "nativeAX-capture-interval"})
        if not roles[True] or not roles[False]:
            gaps.append({"elementID": key, "reason": "no_unambiguous_unclipped_pair"})
            continue
        positive = roles[True][0]
        negative = next((n for n in roles[False] if n["pixelSHA256"] != positive["pixelSHA256"]), None)
        if negative is None:
            gaps.append({"elementID": key, "reason": "contradictory_identical_pixels"})
            continue
        pairs.append({"pair_id": digest([lineage, key, positive, negative]), "elementID": key,
                      "split": "development", "lineage": lineage,
                      "frames": {"focused": positive, "unfocused": negative}})
    if not pairs:
        raise FocusDataError("no_pairs")
    return pairs, gaps


def build(attachments, target, lineage, output, model=None, screen="settings/root"):
    attachments, output = local(attachments), local(output)
    if output.exists():
        raise FocusDataError("output_collision")
    if not lineage.strip() or target == "booted":
        raise FocusDataError("explicit_identity_required")
    frames, accounting = read_journey(attachments, target, screen)
    pairs, gaps = pair_frames(frames, lineage)
    runtime = identity()
    model_hash = artifact_digest(model) if model else None
    source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in attachments.iterdir() if p.is_file()}
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    pending = []
    for pair in pairs:
        for role, label in (("focused", 1), ("unfocused", 0)):
            f = pair["frames"][role]
            key = pair["pair_id"] + ":" + role
            pending.append((pair, role, label, f, {"id": key, "path": str(member(attachments, f["path"])),
                             "sha256": f["sha256"], "bounds": f["bounds"]}))
    # Two frames remain within the helper's 80-million-pixel bound even at
    # the input validator's 40-million-pixel maximum. Reuse a model per batch.
    for start in range(0, len(pending), 2):
        batch = pending[start:start+2]
        items = [item[4] for item in batch]
        reply = invoke(items)
        inference = invoke(items, model) if model else None
        if inference and [r["id"] for r in inference["results"]] != [i["id"] for i in items]:
            raise FocusDataError("runtime_membership_mismatch")
        probabilities = {r["id"]: r["probability"] for r in inference["results"]} if inference else {}
        if len(reply["results"]) != len(batch):
            raise FocusDataError("runtime_membership_mismatch")
        for (pair, role, label, f, item), row in zip(batch, reply["results"], strict=True):
            key = item["id"]
            if row["id"] != key:
                raise FocusDataError("runtime_membership_mismatch")
            if model:
                row["probability"] = probabilities[key]
            crop = base64.b64decode(row["png"], validate=True)
            from PIL import Image
            with Image.open(io.BytesIO(crop), formats=["PNG"]) as decoded:
                decoded.load()
                if decoded.size != (256, 256):
                    raise FocusDataError("runtime_crop_size")
            if model and (type(row.get("probability")) not in (int, float)
                          or not math.isfinite(row["probability"]) or not 0 <= row["probability"] <= 1):
                raise FocusDataError("invalid_runtime_probability")
            filename = pair["pair_id"] + "-" + role + ".png"
            with (output/filename).open("xb") as stream:
                stream.write(crop)
            f["crop"] = filename
            f["cropSHA256"] = hashlib.sha256(crop).hexdigest()
            rows.append({"id": key, "label": label, "probability": row.get("probability"),
                         "timing": {k:v for k,v in (inference or reply).items() if k != "results"}})
    if runtime != identity() or model and model_hash != artifact_digest(model):
        raise FocusDataError("runtime_or_model_changed")
    if source_hashes != {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in attachments.iterdir() if p.is_file()}:
        raise FocusDataError("source_changed")
    report = {"version": "native-os-focus-dataset-v1", "sourceKind": "tvos_simulator_os",
              "target": target, "screenID": screen, "lineage": lineage, "partition": "development",
              "trainingEligible": False, "visualReview": "pending", "completion": "completed",
              "sourceRoot": str(attachments.relative_to(Path(__file__).resolve().parents[1])),
              "sourceHashes": source_hashes, "accounting": accounting, "gaps": gaps,
              "preprocessing": RUNTIME_PREPROCESSING, "runtime": runtime,
              "modelSHA256": model_hash, "pairs": pairs, "scores": rows,
              "binding": "Native AX brackets screenshot interval; not atomic framebuffer attestation",
              "integration": "Native boxes injected; not detector proposals or model-driven navigation"}
    if model:
        report["developmentConfusionAt085"] = {
            "TP": sum(r["label"] == 1 and r["probability"] >= .85 for r in rows),
            "FN": sum(r["label"] == 1 and r["probability"] < .85 for r in rows),
            "FP": sum(r["label"] == 0 and r["probability"] >= .85 for r in rows),
            "TN": sum(r["label"] == 0 and r["probability"] < .85 for r in rows)}
    report["manifestSHA256"] = digest(report)
    with (output/"manifest.json").open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attachments", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--lineage", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--screen", choices=["home/root", "settings/root", "settings/general", "settings/accessibility", "settings/apps", "settings/remotes"], default="settings/root")
    args = parser.parse_args()
    try:
        result = build(args.attachments, args.target, args.lineage, args.output, local(args.model) if args.model else None, args.screen)
        print(json.dumps({"pairs": len(result["pairs"]), "trainingEligible": False,
                          "accounting": result["accounting"], "confusion": result.get("developmentConfusionAt085")}))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
