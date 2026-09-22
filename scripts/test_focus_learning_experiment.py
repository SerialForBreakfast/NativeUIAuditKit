import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import focus_learning_experiment as e
from focus_dataset_contract import ROOT, FocusDataError, pixel_digest


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        root = ROOT/".build/debug-output"; root.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        (self.path/"checkpoint.pt").write_bytes(b"unit-test-only")
        self.doc = {"version": "focus-learning-protocol-v1", "configuration": e.CONFIG,
                    "scope": "development-only-same-app-screen-groups", "releaseEligible": False,
                    "runtime": {"test": True}, "warmCheckpoint": {"path": e.rel(self.path/"checkpoint.pt"),
                    "sha256": e.sha(self.path/"checkpoint.pt")}, "samples": []}
        for i in range(8):
            path = self.path/f"{i}.png"
            Image.new("RGB", (256, 256), (20+i*20, 0, 0)).save(path)
            crop = {"path": e.rel(path), "sha256": e.sha(path)}
            crop["pixelSHA256"] = pixel_digest(ROOT, crop)
            screen = "settings/root" if i < 4 else "settings/accessibility"
            self.doc["samples"].append({"id": str(i), "label": i%2, "screenID": screen,
                "group": screen, "split": e.SPLITS[screen], "sourcePixelSHA256": str(i),
                "crops": {"stretch": crop, "aspect-fit": copy.deepcopy(crop)}})
        self.patcher = patch.object(e, "identity", return_value={"test": True})
        self.patcher.start(); self.addCleanup(self.patcher.stop)

    def test_support(self):
        self.assertEqual(e.validate_document(self.doc), {"train": {0: 2, 1: 2}, "validation": {0: 2, 1: 2}})

    def test_incremental_protocol_excludes_challenge_screens(self):
        self.doc["version"] = "focus-learning-protocol-v2"
        self.doc["samples"][0]["screenID"] = "settings/apps"
        e.validate_document(self.doc)
        for screen in ("home/root", "settings/remotes"):
            self.doc["samples"][0]["screenID"] = screen
            with self.assertRaisesRegex(FocusDataError, "changed_frozen_screen_split"):
                e.validate_document(self.doc)
        with self.assertRaisesRegex(FocusDataError, "frozen_screen_groups"):
            e.sources_for([], incremental=True)

    def test_hash_change(self):
        (self.path/"0.png").write_bytes(b"changed")
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)

    def test_checkpoint_hash(self):
        (self.path/"checkpoint.pt").write_bytes(b"changed")
        with self.assertRaisesRegex(FocusDataError, "changed_experiment_input"): e.validate_document(self.doc)

    def test_group_leakage(self):
        self.doc["samples"][4]["group"] = "settings/root"
        with self.assertRaisesRegex(FocusDataError, "group_leakage"): e.validate_document(self.doc)

    def test_pixel_leakage(self):
        self.doc["samples"][4]["crops"] = copy.deepcopy(self.doc["samples"][0]["crops"])
        with self.assertRaisesRegex(FocusDataError, "pixel_leakage"): e.validate_document(self.doc)

    def test_invalid_labels(self):
        self.doc["samples"][0]["label"] = True
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)

    def test_release_claim_rejected(self):
        self.doc["releaseEligible"] = True
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)

    def test_config_and_version(self):
        self.doc["configuration"] = {**e.CONFIG, "epochs": 30}
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)
        self.doc["configuration"] = e.CONFIG; self.doc["version"] = "future"
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)

    def test_unsafe_path(self):
        self.doc["warmCheckpoint"]["path"] = "../elsewhere.pt"
        with self.assertRaises(FocusDataError): e.validate_document(self.doc)

    def test_actual_trainer_missing_protocol_fails_without_launch(self):
        r = subprocess.run([sys.executable, str(ROOT/"scripts/train_focus_ring_detector.py"),
            "--experiment-protocol", str(self.path/"missing.json"), "--experiment-arm", "warm-stretch",
            "--name", "offline-test-only", "--preflight"], capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["launchEligible"])
        self.assertFalse((ROOT/"NativeUITrainer/focus_ring_runs/offline-test-only").exists())

    def test_report_metrics(self):
        from focus_learning_report import metrics
        rows = [{"id": "a", "label": 1, "probability": .8}, {"id": "b", "label": 0, "probability": .2}]
        result = metrics(rows)
        self.assertEqual(result["auroc"], 1)
        self.assertEqual(result["0.5"]["accuracy"], 1)
        self.assertEqual(result["0.85"]["fn"], 1)
        rows[0]["probability"] = float("nan")
        with self.assertRaises(FocusDataError): metrics(rows)

    def test_missing_review_and_collision(self):
        records = [{"screenID": screen, "split": split,
                    "manifest": {"path": e.rel(self.path/"missing.json"), "sha256": "absent"}}
                   for screen, split in e.SPLITS.items()]
        with self.assertRaisesRegex(FocusDataError, "missing_pixels"): e.sources_for(records)
        with self.assertRaisesRegex(FocusDataError, "output_collision"):
            e.prepare(records, self.path, self.path/"checkpoint.pt")

    def test_4k_reporting_batches_respect_pixel_limit(self):
        import focus_learning_report as report
        items = [{"id": str(i), "path": "test-only"} for i in range(18)]
        with patch("PIL.Image.open") as opened, patch.object(report, "invoke") as invoke:
            im = opened.return_value.__enter__.return_value
            im.width, im.height = 3840, 2160
            invoke.side_effect = lambda rows, model: {"results": list(rows)}
            result = report.infer_bounded(items, "fake-model")
        self.assertEqual(result["results"], items)
        self.assertEqual([len(c.args[0]) for c in invoke.call_args_list], [9, 9])

    def source_records(self, include_review_hash):
        doc = {"version": "unsupported-test-only"}
        doc["manifestSHA256"] = e.digest(doc)
        path = self.path/"manifest.json"; path.write_text(json.dumps(doc))
        review = self.path/"review.md"
        review.write_text(doc["manifestSHA256"] if include_review_hash else "No reviewed content hash")
        return [{"screenID": screen, "split": split,
                 "manifest": {"path": e.rel(path), "sha256": e.sha(path)},
                 "review": {"path": e.rel(review), "sha256": e.sha(review)}}
                for screen, split in e.SPLITS.items()]

    def test_unreviewed_source_rejected(self):
        with self.assertRaisesRegex(FocusDataError, "unreviewed_manifest"):
            e.sources_for(self.source_records(False))

    def test_unsupported_source_rejected(self):
        with self.assertRaisesRegex(FocusDataError, "unsupported_native_source"):
            e.sources_for(self.source_records(True))

    def test_challenge_requires_review_and_new_output(self):
        from focus_learning_report import native_challenge
        record = self.source_records(False)[0]
        record["split"] = "challenge"
        path = self.path/"source.json"; path.write_text(json.dumps(record))
        with self.assertRaisesRegex(FocusDataError, "unreviewed_manifest"):
            native_challenge(path, self.path/"checkpoint.pt", self.path/"result.json")
        with self.assertRaisesRegex(FocusDataError, "output_collision"):
            native_challenge(path, self.path/"checkpoint.pt", path)
        record["split"] = "train"; path.write_text(json.dumps(record))
        with self.assertRaisesRegex(FocusDataError, "challenge_partition_required"):
            native_challenge(path, self.path/"checkpoint.pt", self.path/"result.json")

    def test_changed_protocol_rejected_before_launch(self):
        path = self.path/"protocol.json"
        path.write_text(json.dumps({**self.doc, "protocolSHA256": "incorrect"}))
        with self.assertRaisesRegex(FocusDataError, "changed_protocol"):
            e.load_protocol(path, "warm-stretch", "test-only-never-launched")

    def test_challenge_isolation_checks_new_training_membership(self):
        from focus_learning_report import assert_challenge_isolation
        protocol = {"samples": [{"sourcePixelSHA256": "frame", "group": "apps",
                                 "crops": {"stretch": {"pixelSHA256": "crop"}}}]}
        protocol["protocolSHA256"] = e.digest(protocol)
        assert_challenge_isolation([{"pixelSHA256": "other"}], [], "remotes", protocol)
        with self.assertRaisesRegex(FocusDataError, "challenge_pixel_leakage"):
            assert_challenge_isolation([{"pixelSHA256": "crop"}], [], "remotes", protocol)
        with self.assertRaisesRegex(FocusDataError, "challenge_pixel_leakage"):
            assert_challenge_isolation([], [{"frames": {"focused": {"pixelSHA256": "frame"}}}], "remotes", protocol)
        with self.assertRaisesRegex(FocusDataError, "challenge_lineage_leakage"):
            assert_challenge_isolation([], [], "apps", protocol)
        protocol["samples"][0]["group"] = "changed"
        with self.assertRaisesRegex(FocusDataError, "changed_protocol"):
            assert_challenge_isolation([], [], "remotes", protocol)


if __name__ == "__main__": unittest.main()
