import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import direct_tvos_capture as d
from direct_focus_manifest import pairs_from_capture, validate_direct_frames, validate_direct_manifest
from focus_dataset_contract import ROOT, FocusDataError, digest


class DirectTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".build/debug-output/direct-tvos-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = d.catalog(True); self.recipe = self.plan["recipes"][0]

    def frame(self, name, target):
        Image.new("RGB", (100, 100), "red" if target else "blue").save(self.root/name)
        now = time.time()
        def snap(start):
            return {"startedAt": start, "finishedAt": start+.01,
                    "device": {"schema_version": 1, "fixture_instance_id": "instance", "fixture_run_id": "run"},
                    "scene": {"schema_version": 1, "recipe": self.recipe, "timestamp": start,
                              "is_settled": True, "focused_element_id": target, "scene_width": 100, "scene_height": 100,
                              "focus_observation": {"verified": True, "source": "uikit_focus_system",
                                                    "geometrySource": "uikit_window_converted_bounds", "observedID": target,
                                                    "generation": 1, "plannedFocusIDs": ["dialog_btn_0", "dialog_btn_1"]},
                              "observation_diagnostics": {"nativeFocusResolved": True, "reason": "ready", "missingIDs": [],
                                                          "sampleAgeMilliseconds": 1, "stableMilliseconds": 200,
                                                          "generation": 1, "sampledGeneration": 1},
                              "elements": [{"element_id": e, "taxonomy_class": "primaryButton", "is_focused": e == target,
                                            "pixel_bounds": [10, 10, 20, 20], "normalized_bounds": [.1,.1,.3,.3]} for e in ("dialog_btn_0", "dialog_btn_1")]}}
        value = {"path": name, "sha256": hashlib.sha256((self.root/name).read_bytes()).hexdigest(),
                 "binding": "native-observation-bracket-v1", "observedFocusID": target,
                 "captureStartedAt": now+.02, "captureFinishedAt": now+.03,
                 "before": snap(now), "after": snap(now+.04)}
        d.write_json(self.root/(name+".json"), value)
        return value

    def document(self):
        return {"version": "direct-tvos-capture-v1", "sourceKind": d.SOURCE, "state": "completed",
                "evidenceKind": "test-only", "target": {"source": "test-only"},
                "catalog": self.plan, "acceptedPairs": 2, "targetPlanSourceHashes": d.SOURCE_HASHES,
                "initialDevice": {"fixture_instance_id": "instance", "fixture_run_id": "run"}, "postflight": {"responsive": True,
                    "device": {"fixture_instance_id": "instance", "fixture_run_id": "run"}},
                "recipes": [{"recipe": self.recipe, "expectedTargets": d.expected_targets(self.recipe), "frames": [self.frame("ref.png", None),
                                                               self.frame("a.png", "dialog_btn_0"), self.frame("b.png", "dialog_btn_1")]}]}

    def test_valid_accounting_and_interval(self):
        doc = self.document(); self.assertEqual(d.validate_capture(doc, self.root), 2)
        pair = pairs_from_capture(doc)[0]
        self.assertEqual(validate_direct_frames(pair, self.root)["focused"], [6.8,6.8,33.2,33.2])
        self.assertNotIn("frameID", pair["frames"]["focused"])

    def test_stale_mismatch_geometry_and_prediction_labels(self):
        frame = self.frame("x.png", "dialog_btn_0")
        changes = [("is_settled", False), ("focused_element_id", "dialog_btn_1"), ("timestamp", 0)]
        for key, value in changes:
            bad = copy.deepcopy(frame); bad["after"]["scene"][key] = value
            with self.assertRaises(FocusDataError): d.validate_interval(bad, self.recipe, self.root)
        for field, value in (("source", "prediction"), ("verified", False), ("generation", 9)):
            bad = copy.deepcopy(frame); bad["after"]["scene"]["focus_observation"][field] = value
            with self.assertRaises(FocusDataError): d.validate_interval(bad, self.recipe, self.root)
        bad = copy.deepcopy(frame); bad["after"]["device"]["fixture_instance_id"] = "other"
        with self.assertRaises(FocusDataError): d.validate_interval(bad, self.recipe, self.root)

    def test_bytes_missing_corrupt_hash(self):
        frame = self.frame("x.png", "dialog_btn_0")
        (self.root/"x.png").write_bytes(b"corrupt")
        with self.assertRaises(FocusDataError): d.validate_interval(frame, self.recipe, self.root)
        frame["sha256"] = hashlib.sha256(b"corrupt").hexdigest()
        with self.assertRaises(FocusDataError): d.validate_interval(frame, self.recipe, self.root)
        frame["path"] = "absent.png"
        with self.assertRaises(FocusDataError): d.validate_interval(frame, self.recipe, self.root)

    def test_partial_version_membership(self):
        doc = self.document()
        for key, value in (("state", "partial"), ("version", "future"), ("acceptedPairs", 1)):
            bad = copy.deepcopy(doc); bad[key] = value
            with self.assertRaises(FocusDataError): d.validate_capture(bad, self.root)
        doc["recipes"][0]["frames"].pop()
        with self.assertRaises(FocusDataError): d.validate_capture(doc, self.root)

    def test_manifest_split_and_binding(self):
        doc = self.document(); d.write_json(self.root/"direct-capture.json", doc)
        manifest = {"sourceKind": d.SOURCE, "purpose": "development-pilot", "evidenceKind": "test-only", "captureSHA256": digest(doc), "pairs": pairs_from_capture(doc)}
        validate_direct_manifest(manifest, self.root)
        manifest["pairs"][0]["split"] = "test"
        with self.assertRaises(FocusDataError): validate_direct_manifest(manifest, self.root)

    def test_real_runtime_adapter_and_baseline_entrypoints(self):
        from focus_dataset_contract import validate_manifest
        from focus_training_preflight import preflight
        doc = self.document(); raw = self.root/"direct-capture.json"; d.write_json(raw, doc)
        crops = self.root/"crops"
        command = [sys.executable, str(ROOT/"scripts/direct_focus_manifest.py"), "--capture", str(raw), "--output", str(crops)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((crops/"focus_dataset_manifest.json").read_text())
        self.assertEqual(len(validate_manifest(manifest, crops)), 2)
        self.assertFalse(preflight(crops, "direct-test-only")["launchEligible"])
        model = ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
        baseline = [sys.executable, str(ROOT/"scripts/focus_ring_baseline.py"), "--manifest", str(crops/"focus_dataset_manifest.json"), "--model", str(model)]
        protocol = self.root/"protocol.json"
        result = subprocess.run(baseline+["--prepare", "--output", str(protocol)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.root/"baseline.json"
        result = subprocess.run(baseline+["--infer", "--protocol", str(protocol), "--output", str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(report.read_text())["evidenceKind"], "test-only")
        from focus_corpus_overlap import audit, record_owner
        audit_result = audit([crops/"focus_dataset_manifest.json", crops/"focus_dataset_manifest.json"])
        self.assertTrue(audit_result["samePartitionOverlaps"])
        owners, overlaps = {}, set()
        record_owner(owners, ("seed", "7"), "development", "direct", overlaps)
        with self.assertRaisesRegex(FocusDataError, "cross_corpus_split_leakage"):
            record_owner(owners, ("seed", "7"), "test", "ttr", overlaps)
        crop = crops/manifest["pairs"][0]["focused_crop"]
        Image.new("RGB", (256,256), "green").save(crop)
        manifest["pairs"][0]["focused_crop_sha256"] = hashlib.sha256(crop.read_bytes()).hexdigest()
        with self.assertRaisesRegex(FocusDataError, "crop_pixel_mismatch"): validate_manifest(manifest, crops)

    def test_real_execution_failure_is_retained_without_retry(self):
        class FailedFixture:
            deadline = None
            last_snapshot = {"testOnly": True}
            calls = []
            def __init__(self, endpoint): pass
            def request(self, path, body=None):
                self.calls.append(path)
                if path == "/recipe": raise FocusDataError("injected_producer_failure")
                return {"schema_version": 1, "fixture_instance_id": "instance", "fixture_run_id": "run"}
        output = self.root/"failed"
        with patch.object(d, "bind_target", return_value={"testOnly": True}), patch.object(d, "Fixture", FailedFixture):
            with self.assertRaisesRegex(FocusDataError, "injected_producer_failure"):
                d.execute(self.plan, "test-only", "http://127.0.0.1:8080", output)
        self.assertEqual(FailedFixture.calls.count("/recipe"), 1)
        self.assertEqual(json.loads((output/"failed.json").read_text())["state"], "failed")
        self.assertFalse((output/"direct-capture.json").exists())

    def test_frozen_target_counts_and_omission(self):
        counts = {}
        for recipe in d.catalog()["recipes"]:
            targets = d.expected_targets(recipe)
            self.assertEqual(len(targets), len(set(targets)))
            counts.setdefault(recipe["archetype"], set()).add(len(targets))
        self.assertEqual(counts["hero_carousel"], {2})
        self.assertEqual(counts["focus_maze"], {8})
        self.assertEqual(counts["kitchen_sink"], {18})
        self.assertEqual(sum(len(d.expected_targets(r)) for r in d.catalog()["recipes"]), 246)
        frame = self.frame("omitted.png", None)
        for side in ("before", "after"):
            frame[side]["scene"]["focus_observation"]["plannedFocusIDs"].pop()
        with self.assertRaisesRegex(FocusDataError, "incomplete_planned_targets"):
            d.validate_interval(frame, self.recipe, self.root)

    def test_initial_binding_and_target_plan(self):
        doc = self.document()
        for key, value in (("initialDevice", {}), ("targetPlanSourceHashes", {})):
            bad = copy.deepcopy(doc); bad[key] = value
            with self.assertRaises(FocusDataError): d.validate_capture(bad, self.root)
        doc["recipes"][0]["expectedTargets"].pop()
        with self.assertRaisesRegex(FocusDataError, "changed_expected_targets"):
            d.validate_capture(doc, self.root)

    def test_sweep_taxonomy_change_rejected(self):
        doc = self.document()
        frame = doc["recipes"][0]["frames"][1]
        for side in ("before", "after"):
            frame[side]["scene"]["elements"][0]["taxonomy_class"] = "cancelAction"
        (self.root/(frame["path"]+".json")).write_text(json.dumps(frame))
        with self.assertRaisesRegex(FocusDataError, "sweep_taxonomy_changed"):
            d.validate_capture(doc, self.root)

    def test_settle_deadline_restored(self):
        fixture = d.Fixture("http://127.0.0.1:8080")
        original_deadline = time.monotonic()+120
        fixture.deadline = original_deadline
        snapshot = self.frame("settle.png", None)["before"]
        def observe():
            self.assertLessEqual(fixture.deadline-time.monotonic(), 10)
            return snapshot
        with patch.object(fixture, "snapshot", side_effect=observe):
            fixture.settle(None, self.recipe)
        self.assertEqual(fixture.deadline, original_deadline)

    def test_successful_execute_entrypoint_and_collision(self):
        owner = self
        class OfflineFixture:
            deadline = None
            last_snapshot = None
            def __init__(self, endpoint): self.endpoint = endpoint
            def request(self, path, body=None):
                return {"schema_version": 1, "fixture_instance_id": "instance", "fixture_run_id": "run"}
        binding = {"simulatorUDID": "9026ECA9-77DB-4AE6-8FE6-BB239E9571FA", "endpoint": "http://127.0.0.1:8080",
                   "runtime": "tvOS-test-only", "deviceProfile": "test-only", "pid": 1,
                   "binaries": {"TVTestRigFixture": "0"*64}, "xcode": "test-only"}
        def frame(fixture, target, output, name, expected, recipe):
            original = owner.root
            try:
                owner.root = output
                return owner.frame(name, expected)
            finally: owner.root = original
        plan = self.root/"catalog.json"; d.write_json(plan, self.plan)
        out = self.root/"completed"
        args = ["direct_tvos_capture.py", "--execute", "--catalog", str(plan), "--target", binding["simulatorUDID"],
                "--endpoint", binding["endpoint"], "--output", str(out)]
        with patch.object(d, "bind_target", return_value=binding), patch.object(d, "Fixture", OfflineFixture), \
                patch.object(d, "capture_frame", side_effect=frame), patch.object(sys, "argv", args):
            self.assertEqual(d.main(), 0)
            self.assertEqual(d.main(), 2)
        doc = json.loads((out/"direct-capture.json").read_text())
        self.assertEqual(d.validate_capture(doc, out), 2)
        self.assertFalse((out/"failed.json").exists())
        # Test doubles are isolated temporary artifacts, never supplied as real evidence.

    def test_visual_review_and_false_trust(self):
        doc = self.document(); d.write_json(self.root/"direct-capture.json", doc)
        manifest = {"sourceKind": d.SOURCE, "purpose": "development-pilot", "evidenceKind": "reviewed-fixture",
                    "captureSHA256": digest(doc), "pairs": pairs_from_capture(doc)}
        with self.assertRaisesRegex(FocusDataError, "false_reviewed_provenance"): validate_direct_manifest(manifest, self.root)

    def test_review_report_bytes_are_required(self):
        doc = self.document()
        doc.update(evidenceKind="fixture-native-capture", runnerSHA256="0"*64,
                   target={"simulatorUDID": "9026ECA9-77DB-4AE6-8FE6-BB239E9571FA", "endpoint": "http://127.0.0.1:8080",
                           "runtime": "tvOS-test", "deviceProfile": "test", "pid": 1,
                           "binaries": {"TVTestRigFixture": "0"*64}, "xcode": "test-only"})
        d.write_json(self.root/"direct-capture.json", doc)
        report = self.root/"review.json"; d.write_json(report, {"testOnly": True})
        review = {"accepted": True, "captureSHA256": digest(doc), "report": str(report.relative_to(ROOT)),
                  "reportSHA256": hashlib.sha256(report.read_bytes()).hexdigest()}
        manifest = {"sourceKind": d.SOURCE, "purpose": "development-pilot", "evidenceKind": "reviewed-fixture",
                    "captureSHA256": digest(doc), "pairs": pairs_from_capture(doc), "visualReview": review}
        validate_direct_manifest(manifest, self.root)
        review["reportSHA256"] = "0"*64
        with self.assertRaisesRegex(FocusDataError, "changed_visual_review"): validate_direct_manifest(manifest, self.root)
        review["report"] = "../outside.json"
        with self.assertRaisesRegex(FocusDataError, "unsafe_member"): validate_direct_manifest(manifest, self.root)

    def test_plan_cli_and_collisions(self):
        path = self.root/"plan.json"
        args = [sys.executable, str(ROOT/"scripts/direct_tvos_capture.py"), "--plan", "--output", str(path)]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        value = json.loads(path.read_text()); d.validate_catalog(value)
        self.assertEqual(len(value["recipes"]), 42)
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)
        value["recipes"][0]["seed"] = 99
        with self.assertRaises(FocusDataError): d.validate_catalog(value)

    def test_wrong_target_and_endpoint_before_mutation(self):
        for target in ("booted", "not-a-uuid"):
            with self.assertRaises(ValueError): d.bind_target(target, "http://127.0.0.1:8080")
        for url in ("http://example.com", "http://127.0.0.1:8080/path", "http://user@127.0.0.1:8080"):
            with self.assertRaises(FocusDataError): d.endpoint_parts(url)
        target = "9026ECA9-77DB-4AE6-8FE6-BB239E9571FA"
        inv = json.dumps({"devices": {"tvOS": [{"udid": target, "state": "Booted", "name": "test"}]}})
        bundle = f"/Devices/{target}/Fixture.app"
        with patch.object(d, "run", side_effect=[inv, bundle, "1\n2\n"]):
            with self.assertRaisesRegex(FocusDataError, "ambiguous_endpoint"): d.bind_target(target, "http://127.0.0.1:8080")
        with patch.object(d, "run", side_effect=[inv, bundle, "1", "/wrong/process"]):
            with self.assertRaisesRegex(FocusDataError, "wrong_endpoint_target"): d.bind_target(target, "http://127.0.0.1:8080")


if __name__ == "__main__": unittest.main()
