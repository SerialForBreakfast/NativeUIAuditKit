"""Direct Fixture/simctl development acquisition; no TVTestRig coordinator dependency."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from focus_dataset_contract import ROOT, FocusDataError, digest, expanded_box, image, local, member
from simulator_focus_manifest import FAMILY_MAP, THEME_MAP
from direct_tvos_targets import expected_targets, SOURCE_HASHES

BUNDLE = "com.showblender.TVTestRigFixture"
COUNTS = {"action_dialog": 2, "grid_matrix": 4, "media_shelf": 4,
          "settings_list": 4, "hero_carousel": 4, "focus_maze": 4, "kitchen_sink": 41}
SOURCE = "tvos_native_generator"


def require(ok, reason):
    if not ok:
        raise FocusDataError(reason)


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def new_output(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink_output")
    path = local(path)
    require(not path.exists(), "output_collision")
    return path


def catalog(smoke=False):
    recipes = [{"schema_version": 1, "archetype": family, "element_count": count,
                "theme": theme, "density": "regular", "seed": seed, "step_index": 0}
               for family, count in COUNTS.items()
               for theme in ("light", "dark", "high_contrast") for seed in (7, 19)]
    if smoke:
        recipes = [r for r in recipes if r["archetype"] == "action_dialog"
                   and r["theme"] == "high_contrast" and r["seed"] == 7]
    result = {"version": "direct-tvos-catalog-v1", "purpose": "development-pilot", "recipes": recipes}
    result["sha256"] = digest(result)
    return result


def validate_catalog(value):
    unsigned = {k: v for k, v in value.items() if k != "sha256"}
    require(value.get("sha256") == digest(unsigned), "changed_catalog")
    require(value in (catalog(), catalog(True)), "unsupported_catalog")


def run(args, timeout=10):
    reply = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    require(reply.returncode == 0, "command_failed: " + reply.stderr[-600:])
    return reply.stdout


def endpoint_parts(endpoint):
    p = urlparse(endpoint)
    require(p.scheme == "http" and p.hostname == "127.0.0.1" and p.port
            and p.path in ("", "/") and not p.username and not p.password
            and not p.query and not p.fragment, "unsupported_endpoint")
    return p


def bind_target(target, endpoint):
    require(str(uuid.UUID(target)).upper() == target, "explicit_uuid_required")
    port = endpoint_parts(endpoint).port
    inventory = json.loads(run(["xcrun", "simctl", "list", "devices", "available", "-j"]))
    matches = [(runtime, d) for runtime, devices in inventory["devices"].items()
               for d in devices if d["udid"] == target]
    require(len(matches) == 1 and "tvOS" in matches[0][0]
            and matches[0][1]["state"] == "Booted", "target_not_ready")
    bundle = Path(run(["xcrun", "simctl", "get_app_container", target, BUNDLE, "app"]).strip())
    require(f"/Devices/{target}/" in str(bundle), "wrong_installed_target")
    pids = set(run(["lsof", "-t", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"]).split())
    require(len(pids) == 1, "ambiguous_endpoint")
    pid = next(iter(pids))
    command = run(["ps", "-p", pid, "-o", "command="]).strip()
    require(command.split(" -", 1)[0] == str(bundle / "TVTestRigFixture"), "wrong_endpoint_target")
    binaries = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (bundle / "TVTestRigFixture", bundle / "TVTestRigFixture.debug.dylib") if p.is_file()}
    require("TVTestRigFixture" in binaries, "missing_fixture_binary")
    return {"simulatorUDID": target, "runtime": matches[0][0], "deviceProfile": matches[0][1]["name"],
            "endpoint": endpoint, "pid": int(pid), "binaries": binaries,
            "xcode": run(["xcodebuild", "-version"]).strip()}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise FocusDataError("endpoint_redirect")


class Fixture:
    def __init__(self, endpoint):
        endpoint_parts(endpoint)
        self.endpoint = endpoint.rstrip("/")
        self.deadline = None
        self.last_snapshot = None
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def budget(self, maximum):
        seconds = maximum if self.deadline is None else min(maximum, self.deadline - time.monotonic())
        require(seconds > 0, "recipe_timeout")
        return seconds

    def request(self, path, body=None):
        req = Request(self.endpoint + path, data=None if body is None else json.dumps(body).encode(),
                      headers={"Content-Type": "application/json"})
        with self.opener.open(req, timeout=self.budget(5)) as reply:
            raw = reply.read(2 * 1024 * 1024 + 1)
        require(len(raw) <= 2 * 1024 * 1024, "oversize_telemetry")
        return json.loads(raw)

    def snapshot(self):
        start = time.time()
        device = self.request("/device")
        scene = self.request("/scene")
        self.last_snapshot = {"startedAt": start, "finishedAt": time.time(), "device": device, "scene": scene}
        return self.last_snapshot

    def settle(self, expected, recipe):
        until = time.monotonic() + self.budget(10)
        previous_deadline = self.deadline
        self.deadline = until
        last = None
        last_reason = "no_observation"
        try:
            while time.monotonic() < until:
                last = self.snapshot()
                try:
                    scene_signature(last, expected, recipe)
                    return last
                except FocusDataError as error:
                    last_reason = str(error)
                    time.sleep(min(.1, max(0, until - time.monotonic())))
        finally:
            self.deadline = previous_deadline
        raise FocusDataError("settle_timeout: " + last_reason + ": " + json.dumps(last, separators=(",", ":"))[-1500:])


def scene_signature(snapshot, expected, recipe):
    scene, device = snapshot["scene"], snapshot["device"]
    require(device.get("fixture_instance_id") and device.get("fixture_run_id"), "missing_instance")
    require(scene.get("schema_version") == 1 and device.get("schema_version") == 1, "unsupported_telemetry")
    actual_recipe = scene.get("recipe", {})
    require(all(actual_recipe.get(k) == v for k, v in recipe.items()), "wrong_recipe")
    obs, diag = scene.get("focus_observation", {}), scene.get("observation_diagnostics", {})
    require(scene.get("is_settled") is True and not scene.get("harvest_challenge_active")
            and obs.get("verified") is True and obs.get("source") == "uikit_focus_system"
            and obs.get("geometrySource") == "uikit_window_converted_bounds", "unverified_native_state")
    require(obs.get("observedID") == expected and scene.get("focused_element_id") == expected
            and diag.get("nativeFocusResolved") is True and diag.get("reason") == "ready"
            and diag.get("missingIDs") == [], "wrong_focus_or_geometry")
    age, stable = diag.get("sampleAgeMilliseconds"), diag.get("stableMilliseconds")
    require(type(age) in (int, float) and math.isfinite(age) and 0 <= age < 1000
            and type(stable) in (int, float) and math.isfinite(stable) and stable >= 150,
            "stale_or_unsettled")
    stamp = scene.get("timestamp")
    require(type(stamp) in (int, float) and math.isfinite(stamp)
            and abs(snapshot["finishedAt"] - stamp) <= 5, "stale_scene")
    require(type(obs.get("generation")) is int and obs["generation"] >= 0 and
            obs["generation"] == diag.get("generation") == diag.get("sampledGeneration"), "generation_mismatch")
    elements = scene.get("elements", [])
    ids = [e["element_id"] for e in elements]
    require(len(ids) == len(set(ids)) and elements, "invalid_elements")
    focused = [e["element_id"] for e in elements if e.get("is_focused") is True]
    require(focused == ([] if expected is None else [expected]), "conflicting_focus_labels")
    planned = obs.get("plannedFocusIDs")
    require(isinstance(planned, list) and planned and len(set(planned)) == len(planned)
            and set(planned) <= set(ids), "missing_focus_targets")
    require(planned == expected_targets(recipe), "incomplete_planned_targets")
    size = (scene.get("scene_width"), scene.get("scene_height"))
    for e in elements:
        expanded_box(e.get("pixel_bounds"), size)
        x, y, w, h = e["pixel_bounds"]
        normal = [x/size[0], y/size[1], (x+w)/size[0], (y+h)/size[1]]
        require(len(e.get("normalized_bounds", [])) == 4 and
                all(abs(a-b) < 1e-6 for a, b in zip(normal, e["normalized_bounds"])),
                "coordinate_conflict: " + e["element_id"])
    return {"instance": device["fixture_instance_id"], "run": device["fixture_run_id"],
            "recipe": actual_recipe, "generation": obs["generation"], "observed": expected,
            "size": size, "elements": elements, "planned": planned}


def validate_interval(record, recipe, root):
    expected = record.get("observedFocusID")
    require(record.get("binding") == "native-observation-bracket-v1", "unknown_binding")
    a, b = record["before"], record["after"]
    require(scene_signature(a, expected, recipe) == scene_signature(b, expected, recipe), "capture_state_changed")
    start, end = record["captureStartedAt"], record["captureFinishedAt"]
    require(a["finishedAt"] <= start <= end <= b["startedAt"]
            and 0 <= b["finishedAt"] - a["startedAt"] <= 20, "invalid_capture_interval")
    size = image(root, record)
    require(size == (a["scene"]["scene_width"], a["scene"]["scene_height"]), "screenshot_geometry_mismatch")
    return size


def capture_frame(fixture, target, output, name, expected, recipe):
    if hasattr(fixture, "binding"):
        require(bind_target(target, fixture.endpoint) == fixture.binding, "endpoint_binding_changed")
    before = fixture.settle(expected, recipe)
    if hasattr(fixture, "initial_device"):
        require(all(before["device"].get(k) == fixture.initial_device[k]
                    for k in ("fixture_instance_id", "fixture_run_id")), "instance_changed")
    start = time.time()
    run(["xcrun", "simctl", "io", target, "screenshot", "--type=png", str(output / name)], fixture.budget(15))
    end = time.time()
    after = fixture.snapshot()
    if hasattr(fixture, "binding"):
        require(bind_target(target, fixture.endpoint) == fixture.binding, "endpoint_binding_changed")
    record = {"path": name, "sha256": hashlib.sha256((output/name).read_bytes()).hexdigest(),
              "binding": "native-observation-bracket-v1", "observedFocusID": expected,
              "captureStartedAt": start, "captureFinishedAt": end, "before": before, "after": after}
    write_json(output / (name + ".json"), record)
    validate_interval(record, recipe, output)
    return record


def validate_capture(doc, root):
    if doc.get("version") == "direct-tvos-capture-set-v1":
        from direct_tvos_resume import validate_set
        return validate_set(doc, root)
    return _audit_capture(doc, root, failed_prefix=False)


def _audit_capture(doc, root, *, failed_prefix, segment=False):
    """Shared evidence checks; failed-prefix audit cannot admit a dataset."""
    require(doc.get("version") == ("direct-tvos-segment-v1" if segment else "direct-tvos-capture-v1") and doc.get("sourceKind") == SOURCE,
            "unsupported_direct_capture")
    require(doc.get("state") == ("failed" if failed_prefix else "completed"), "incomplete_capture")
    require(doc.get("evidenceKind") in {"test-only", "fixture-native-capture"}, "missing_capture_evidence_kind")
    validate_catalog(doc["catalog"])
    expected_recipes = doc["catalog"]["recipes"]
    if segment:
        bounds = doc.get("recipeRange", [])
        require(len(bounds) == 2 and all(type(i) is int for i in bounds)
                and 0 <= bounds[0] < bounds[1] <= len(expected_recipes), "invalid_segment_range")
        expected_recipes = expected_recipes[bounds[0]:bounds[1]]
    if failed_prefix:
        require(len(doc["recipes"]) < len(expected_recipes), "no_remaining_recipes")
        expected_recipes = expected_recipes[:len(doc["recipes"])]
    require([x["recipe"] for x in doc["recipes"]] == expected_recipes, "incomplete_recipe_membership")
    total = 0
    initial = doc.get("initialDevice", {})
    instance = (initial.get("fixture_instance_id"), initial.get("fixture_run_id"))
    require(all(isinstance(x, str) and x for x in instance), "missing_initial_identity")
    target = doc.get("target", {})
    require(doc.get("targetPlanSourceHashes") == SOURCE_HASHES, "unknown_target_plan")
    if doc["evidenceKind"] != "test-only":
        require(str(uuid.UUID(target.get("simulatorUDID", ""))).upper() == target["simulatorUDID"], "invalid_target")
        endpoint_parts(target.get("endpoint", ""))
        require("tvOS" in target.get("runtime", "") and target.get("deviceProfile")
                and type(target.get("pid")) is int and target["pid"] > 0
                and target.get("binaries", {}).get("TVTestRigFixture") and target.get("xcode"), "missing_runtime_identity")
        hashes = [doc.get("runnerSHA256"), *target["binaries"].values()]
        require(all(isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h)
                    for h in hashes), "invalid_build_hash")
    paths = set()
    for result in doc["recipes"]:
        frames, recipe = result["frames"], result["recipe"]
        require(frames and frames[0].get("observedFocusID") is None, "missing_reference")
        planned = frames[0]["before"]["scene"]["focus_observation"]["plannedFocusIDs"]
        require(result.get("expectedTargets") == planned == expected_targets(recipe), "changed_expected_targets")
        require([f.get("observedFocusID") for f in frames[1:]] == planned, "incomplete_focus_sweep")
        reference_classes = {e["element_id"]: e["taxonomy_class"] for e in frames[0]["before"]["scene"]["elements"]}
        for f in frames:
            require(f["path"] not in paths, "duplicate_capture_path")
            paths.add(f["path"])
            validate_interval(f, recipe, root)
            signature = scene_signature(f["before"], f["observedFocusID"], recipe)
            current = (signature["instance"], signature["run"])
            require(current == instance, "instance_changed")
            require({e["element_id"]: e["taxonomy_class"] for e in signature["elements"]} == reference_classes,
                    "sweep_taxonomy_changed")
            require(json.loads(member(root, f["path"] + ".json").read_text()) == f, "changed_frame_sidecar")
        total += len(planned)
    require(doc.get("acceptedPairs") == total and doc.get("postflight", {}).get("responsive") is True, "count_or_health_mismatch")
    final = doc["postflight"].get("device", {})
    require((final.get("fixture_instance_id"), final.get("fixture_run_id")) == instance, "postflight_instance_changed")
    return total


def resume_plan(receipt):
    """Inspect only: do not relabel partial data or construct an executable catalog."""
    receipt = Path(receipt).absolute()
    require(not any(p.is_symlink() for p in (receipt, *receipt.parents)), "symlink_input")
    receipt = local(receipt)
    raw = receipt.read_bytes()
    doc = json.loads(raw)
    pairs = _audit_capture(doc, receipt.parent, failed_prefix=True)
    require(receipt.read_bytes() == raw, "receipt_changed_during_audit")
    done = len(doc["recipes"])
    remaining = [{"catalogIndex": i, "recipe": recipe, "expectedTargets": expected_targets(recipe)}
                 for i, recipe in enumerate(doc["catalog"]["recipes"]) if i >= done]
    return {"version": "direct-tvos-resume-plan-v1", "purpose": "planning-only",
            "executionAllowed": False, "trainingEligible": False,
            "sourceReceipt": str(receipt.relative_to(ROOT)),
            "sourceReceiptSHA256": hashlib.sha256(raw).hexdigest(),
            "sourceEvidenceKind": doc["evidenceKind"], "catalogSHA256": doc["catalog"]["sha256"],
            "sourceTarget": doc["target"], "sourceRunnerSHA256": doc.get("runnerSHA256"),
            "verifiedPrefixRecipes": done, "verifiedPrefixPairs": pairs,
            "remainingRecipes": remaining,
            "remainingPairs": sum(len(r["expectedTargets"]) for r in remaining),
            "admittedPairs": 0, "postflight": doc["postflight"],
            "resumeRequirements": ["changed producer evidence for retained failure",
                "fresh exact-target readiness and authority", "reviewed multi-run lineage/merge contract",
                "full original catalog accounting and visual review before admission"]}


def execute(plan, target, endpoint, output, *, continuation=None):
    validate_catalog(plan)
    output = new_output(output)
    binding = bind_target(target, endpoint)  # No mutation before exact endpoint ownership.
    start, stop = 0, len(plan["recipes"])
    if continuation is not None:
        require(continuation["binding"] == binding, "resume_binding_changed")
        start, stop = continuation["recipeRange"]
        require(type(start) is int and type(stop) is int and 0 <= start < stop <= len(plan["recipes"]),
                "invalid_segment_range")
    fixture = Fixture(endpoint)
    fixture.binding = binding
    initial = fixture.request("/device")
    require(initial.get("schema_version") == 1 and all(isinstance(initial.get(k), str) and initial[k]
                for k in ("fixture_instance_id", "fixture_run_id")), "invalid_initial_device")
    fixture.initial_device = initial
    output.mkdir(parents=True)
    doc = {"version": "direct-tvos-capture-v1", "sourceKind": SOURCE, "catalog": plan,
           "target": binding, "initialDevice": initial, "state": "partial", "recipes": [], "acceptedPairs": 0,
           "evidenceKind": "fixture-native-capture",
           "targetPlanSourceHashes": SOURCE_HASHES,
           "runnerSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if continuation is not None:
        doc.update(version="direct-tvos-segment-v1", recipeRange=[start, stop],
                   predecessorSHA256=continuation["predecessorSHA256"],
                   continuationRunnerSHA256=continuation["continuationRunnerSHA256"],
                   repairReview=continuation.get("repairReview"))
    write_json(output / "started.json", doc)
    try:
        for index, recipe in enumerate(plan["recipes"]):
            if not start <= index < stop:
                continue
            fixture.deadline = time.monotonic() + 120
            require(bind_target(target, endpoint) == binding, "endpoint_binding_changed")
            device = fixture.request("/device")
            require(all(device[k] == initial[k] for k in ("fixture_instance_id", "fixture_run_id")), "instance_changed")
            fixture.request("/recipe", recipe)
            fixture.request("/focus/set", {"element_id": None, "settle_time_ms": 150})
            frames = [capture_frame(fixture, target, output, f"{index:03d}-reference.png", None, recipe)]
            planned = expected_targets(recipe)
            result = {"recipe": recipe, "expectedTargets": planned, "frames": frames}
            doc["recipes"].append(result)
            for n, element in enumerate(planned):
                fixture.request("/focus/set", {"element_id": element, "settle_time_ms": 150})
                frames.append(capture_frame(fixture, target, output, f"{index:03d}-{n:03d}.png", element, recipe))
                doc["acceptedPairs"] += 1
            write_json(output / f"recipe-{index:03d}.json", result)
            print(json.dumps({"recipe": index+1, "of": len(plan["recipes"]), "pairs": len(planned)}), flush=True)
        fixture.deadline = None
        final = fixture.request("/device")
        require(all(final[k] == initial[k] for k in ("fixture_instance_id", "fixture_run_id")), "postflight_instance_changed")
        doc.update(state="completed", postflight={"responsive": True, "device": final, "scene": fixture.request("/scene")})
        _audit_capture(doc, output, failed_prefix=False, segment=continuation is not None)
        write_json(output / ("segment.json" if continuation is not None else "direct-capture.json"), doc)
    except Exception as error:
        fixture.deadline = None
        doc.update(state="failed", error=str(error), lastObservation=fixture.last_snapshot)
        try: doc["postflight"] = {"responsive": True, "device": fixture.request("/device"), "scene": fixture.request("/scene")}
        except Exception as health: doc["postflight"] = {"responsive": False, "error": str(health)}
        write_json(output / "failed.json", doc)
        raise
    return doc


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan", action="store_true"); modes.add_argument("--execute", action="store_true")
    modes.add_argument("--validate", type=Path)
    modes.add_argument("--resume-plan", type=Path, help="Read-only failed-prefix audit; never resumes capture")
    p.add_argument("--smoke", action="store_true"); p.add_argument("--catalog", type=Path)
    p.add_argument("--target"); p.add_argument("--endpoint"); p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        if args.plan:
            require(args.output is not None, "output_required")
            output = new_output(args.output); output.parent.mkdir(parents=True, exist_ok=True)
            write_json(output, catalog(args.smoke))
        elif args.resume_plan:
            require(args.output is not None, "output_required")
            output = new_output(args.output)
            result = resume_plan(args.resume_plan)
            output.parent.mkdir(parents=True, exist_ok=True)
            write_json(output, result)
            print(json.dumps({"verifiedPrefixPairs": result["verifiedPrefixPairs"],
                              "remainingPairs": result["remainingPairs"], "executionAllowed": False}))
        elif args.validate:
            doc = json.loads(args.validate.read_text()); print(json.dumps({"pairs": validate_capture(doc, args.validate.parent)}))
        else:
            require(all((args.catalog, args.target, args.endpoint, args.output)), "explicit_execution_inputs_required")
            execute(json.loads(args.catalog.read_text()), args.target, args.endpoint, args.output)
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
