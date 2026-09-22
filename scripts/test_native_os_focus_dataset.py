import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import native_os_focus_dataset as subject
from focus_dataset_contract import ROOT, FocusDataError


class NativeIntakeTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".build/debug-output"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entries = []
        for i in range(2):
            Image.new("RGB", (200, 100), (i*100, 0, 0)).save(self.root/f"{i}.png")
            nodes = [{"identifier": "", "label": str(j), "kind": 75,
                      "bounds": [5, 5+j*20, 80, 15], "focused": i == j} for j in range(2)]
            obs = {"timestamp": i*10, "nodes": nodes, "focus": nodes[i], "viewportPoints": [0, 0, 100, 50]}
            after = copy.deepcopy(obs); after["timestamp"] += 1
            frame = {"version": "native-os-focus-observation-v1", "sourceKind": "tvos_simulator_os",
                     "name": str(i), "action": "activate-settings" if i == 0 else "down",
                     "before": obs, "after": after, "captureStartedAt": i*10+.2,
                     "captureEndedAt": i*10+.5, "pixelDimensions": [200, 100],
                     "pngSHA256": hashlib.sha256((self.root/f"{i}.png").read_bytes()).hexdigest()}
            (self.root/f"{i}.json").write_text(json.dumps(frame))
            for ext in ("png", "json"):
                self.entries.append({"exportedFileName": f"{i}.{ext}", "deviceId": "exact", "isAssociatedWithFailure": False})
        (self.root/"end.txt").write_text("inputs=1; completed=true; settingsForeground=true")
        self.entries.append({"exportedFileName": "end.txt", "deviceId": "exact", "isAssociatedWithFailure": False})
        self.save_entries()

    def save_entries(self):
        (self.root/"manifest.json").write_text(json.dumps([{"attachments": self.entries}]))

    def mutate(self, fn):
        path = self.root/"0.json"
        value = json.loads(path.read_text()); fn(value)
        path.write_text(json.dumps(value))

    def test_deterministic_pairs_and_measured_scale(self):
        frames, counts = subject.read_journey(self.root, "exact")
        pairs, gaps = subject.pair_frames(frames, "layout-a")
        self.assertEqual(pairs, subject.pair_frames(frames, "layout-a")[0])
        self.assertEqual(counts["inputs"], 1)
        self.assertEqual(counts["transitions"][0]["direction"], "down")
        self.assertFalse(counts["exhaustiveCoverage"])
        self.assertEqual(len(pairs), 2); self.assertEqual(gaps, [])
        self.assertEqual(pairs[0]["frames"]["focused"]["bounds"], [10, 10, 160, 30])
        self.assertTrue(all(p["split"] == "development" for p in pairs))

    def test_wrong_target_and_failed_trial(self):
        with self.assertRaisesRegex(FocusDataError, "wrong_target"):
            subject.read_journey(self.root, "other")
        self.entries[0]["isAssociatedWithFailure"] = True; self.save_entries()
        with self.assertRaises(FocusDataError): subject.read_journey(self.root, "exact")

    def test_version_two_requires_screen_and_verified_return(self):
        self.mutate(lambda f: f.update(version="native-os-focus-observation-v2"))
        with self.assertRaisesRegex(FocusDataError, "missing_screen_identity"):
            subject.read_journey(self.root, "exact")
        for i in range(2):
            path = self.root/f"{i}.json"
            f = json.loads(path.read_text())
            f.update(version="native-os-focus-observation-v2", screenID="settings/general")
            if i == 0: f["action"] = "enter-general"
            path.write_text(json.dumps(f))
        with self.assertRaisesRegex(FocusDataError, "unverified_submenu_return"):
            subject.read_journey(self.root, "exact", "settings/general")
        (self.root/"end.txt").write_text("inputs=1; completed=true; settingsForeground=true; returnedRoot=true; screenID=settings/general")
        self.assertEqual(len(subject.read_journey(self.root, "exact", "settings/general")[0]), 2)

    def test_partial_completion(self):
        (self.root/"end.txt").write_text("inputs=1; completed=false; settingsForeground=true")
        with self.assertRaisesRegex(FocusDataError, "incomplete"):
            subject.read_journey(self.root, "exact")

    def test_home_entrypoint_and_forbidden_action(self):
        for i in range(2):
            path = self.root/f"{i}.json"
            f = json.loads(path.read_text())
            f.update(version="native-os-focus-observation-v2", screenID="home/root",
                     action="setup-home" if i == 0 else "left")
            path.write_text(json.dumps(f))
        (self.root/"end.txt").write_text("inputs=1; completed=true; homeForeground=true; screenID=home/root; stop=budget-frontier;")
        frames, counts = subject.read_journey(self.root, "exact", "home/root")
        self.assertEqual(counts["inputs"], 1)
        self.assertEqual(len(subject.pair_frames(frames, "home-challenge")[0]), 2)
        path = self.root/"1.json"
        f = json.loads(path.read_text()); f["action"] = "select"
        path.write_text(json.dumps(f))
        with self.assertRaisesRegex(FocusDataError, "unexpected_action"):
            subject.read_journey(self.root, "exact", "home/root")

    def test_home_does_not_accept_settings_terminal(self):
        with self.assertRaisesRegex(FocusDataError, "incomplete_journey"):
            subject.read_journey(self.root, "exact", "home/root")

    def test_home_unknown_text_cannot_hide_conflicting_completion(self):
        (self.root/"end.txt").write_text("inputs=1; completed=true; homeForeground=true; screenID=home/root;")
        (self.root/"extra.txt").write_text("completed=false")
        self.entries.append({"exportedFileName": "extra.txt", "deviceId": "exact", "isAssociatedWithFailure": False})
        self.save_entries()
        with self.assertRaisesRegex(FocusDataError, "incomplete_journey"):
            subject.read_journey(self.root, "exact", "home/root")

    def test_home_identity_uses_label_not_repeated_cell_identifier(self):
        a = {"identifier": "AppCell", "label": "Settings", "kind": 1}
        b = {**a, "label": "Fixture"}
        self.assertNotEqual(subject.node_key(a), subject.node_key(b))
        with self.assertRaisesRegex(FocusDataError, "missing_native_identity"):
            subject.node_key({**a, "label": ""})

    def test_hash_and_missing_image(self):
        (self.root/"0.png").write_bytes(b"corrupt")
        with self.assertRaises(FocusDataError): subject.read_journey(self.root, "exact")

    def test_unsupported_version(self):
        self.mutate(lambda f: f.update(version="future"))
        with self.assertRaisesRegex(FocusDataError, "unsupported"):
            subject.read_journey(self.root, "exact")

    def test_stale_observation(self):
        self.mutate(lambda f: f.update(captureEndedAt=90))
        with self.assertRaisesRegex(FocusDataError, "stale"):
            subject.read_journey(self.root, "exact")

    def test_changed_focus(self):
        self.mutate(lambda f: f["after"]["focus"].update(label="different"))
        with self.assertRaisesRegex(FocusDataError, "unstable"):
            subject.read_journey(self.root, "exact")

    def test_prediction_source_rejected(self):
        self.mutate(lambda f: f.update(sourceKind="modelPrediction"))
        with self.assertRaises(FocusDataError): subject.read_journey(self.root, "exact")

    def test_traversal_and_duplicate_attachments(self):
        self.entries[0]["exportedFileName"] = "../escape.png"; self.save_entries()
        with self.assertRaises(FocusDataError): subject.read_journey(self.root, "exact")

    def test_real_entrypoint_preserves_no_training_approval(self):
        import base64
        import io
        stream = io.BytesIO(); Image.new("RGB", (256, 256)).save(stream, format="PNG")
        def runtime(items, model=None):
            return {"results": [{"id": item["id"], "png": base64.b64encode(stream.getvalue()).decode()} for item in items]}
        with patch.object(subject, "identity", return_value={"test": True}), patch.object(subject, "invoke", side_effect=runtime):
            doc = subject.build(self.root, "exact", "same-layout", self.root/"out")
            self.assertFalse(doc["trainingEligible"])
            self.assertEqual(doc["visualReview"], "pending")
            self.assertEqual(len(doc["pairs"]), 2)
            with self.assertRaisesRegex(FocusDataError, "collision"):
                subject.build(self.root, "exact", "same-layout", self.root/"out")

    def test_identical_pixels_with_different_truth_rejected(self):
        original = (self.root/"0.png").read_bytes()
        (self.root/"1.png").write_bytes(original)
        path = self.root/"1.json"
        frame = json.loads(path.read_text()); frame["pngSHA256"] = hashlib.sha256(original).hexdigest()
        path.write_text(json.dumps(frame))
        with self.assertRaisesRegex(FocusDataError, "contradictory"):
            subject.read_journey(self.root, "exact")

    def test_clipped_pair_is_gap_not_clamped(self):
        frames, _ = subject.read_journey(self.root, "exact")
        frames[0]["frame"]["before"]["nodes"][0]["bounds"] = [-1, 0, 80, 15]
        pairs, gaps = subject.pair_frames(frames, "layout")
        self.assertEqual(len(pairs), 1)
        self.assertEqual(gaps[0]["elementID"], "75:0")

    def test_model_entrypoint_uses_separate_crop_and_score_contracts(self):
        import base64
        import io
        stream = io.BytesIO(); Image.new("RGB", (256, 256)).save(stream, format="PNG")
        def runtime(items, model=None):
            return {"results": [{"id": item["id"], **({"probability": .9} if model else
                {"png": base64.b64encode(stream.getvalue()).decode()})} for item in items]}
        with patch.object(subject, "identity", return_value={"test": True}), \
             patch.object(subject, "artifact_digest", return_value="f"*64), \
             patch.object(subject, "invoke", side_effect=runtime):
            doc = subject.build(self.root, "exact", "layout", self.root/"scored", Path("unused"))
            self.assertEqual(doc["developmentConfusionAt085"], {"TP": 2, "FN": 0, "FP": 2, "TN": 0})

    def test_duplicate_identity_is_not_bound_by_position(self):
        frames, _ = subject.read_journey(self.root, "exact")
        frames[0]["frame"]["before"]["nodes"].append(copy.deepcopy(frames[0]["frame"]["before"]["nodes"][0]))
        pairs, gaps = subject.pair_frames(frames, "layout")
        self.assertEqual(len(pairs), 1)
        self.assertEqual(gaps[0]["elementID"], "75:0")


if __name__ == "__main__": unittest.main()
