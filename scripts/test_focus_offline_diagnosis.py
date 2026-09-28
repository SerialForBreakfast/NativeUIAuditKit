"""Offline tests use isolated generated fixtures, never historical reports or models."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import focus_offline_diagnosis as d


class DiagnosisTests(unittest.TestCase):
    def setUp(self):
        base = d.ROOT / ".build/debug-output"
        base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="offline-diag-test-", dir=base))
        self.addCleanup(shutil.rmtree, self.root)
        self.frame = self.make_image("frame.png", (400, 300), "gray")
        self.crop = self.make_image("crop.png", (256, 256), "white")
        common = {"group": "cinema_rows", "role": "appearance-validation", "pairID": "p", "theme": "dark",
                  "family": "cinema_rows", "hard": False, "control": "button", "elementID": "a",
                  "stratum": "fixture-detail-action", "bounds": [20, 20, 100, 60],
                  "path": self.frame["path"], "sha256": self.frame["sha256"], "framePixelSHA256": self.frame["pixelSHA256"],
                  "crop": self.crop}
        self.rows = [{**common, "id": f"pair-{label}", "kind": "pair", "label": label} for label in (1, 0)]
        self.rows += [{**common, "id": f"comp-{label}", "kind": "competition", "label": label,
                       "elementID": "a" if label else "b", "frameID": "cinema_rows:p", "candidateCount": 2,
                       "candidateComplete": True} for label in (1, 0)]

    def make_image(self, name, size, color):
        path = self.root / name
        Image.new("RGB", size, color).save(path)
        result = d.ref(path)
        result["pixelSHA256"] = d.pixel_digest(d.ROOT, result)
        return result

    def result(self, scores=(.9, .1, .9, .1)):
        predictions = [{"id": r["id"], "probability": p} for r, p in zip(self.rows, scores)]
        return {**d.score(self.rows, predictions), "predictions": predictions, "state": "complete", "backend": "fixture"}

    def fixture(self):
        proposal = self.root / "proposal.json"
        d.write(proposal, {"samples": []})
        candidate = {"version": "focus-appearance-experiment-v1", "inputs": {"proposal": d.ref(proposal)},
                     "samples": [{"id": f"candidate-{label}", "sourceID": "source", "pairID": "p", "label": label,
                                  "use": "train-candidate", "scene": "grid", "style": "dark", "control": "button",
                                  "labelSource": "fixture", "frame": self.frame, "crop": self.crop} for label in (0, 1)],
                     "counts": {"train-candidate": 2}, "sampling": {}, "selection": {}, "configuration": {},
                     "readinessBlockers": ["independence"], "trainingEligible": False}
        metadata = self.root / "metadata.json"
        d.write(metadata, {})
        protocol = {"version": d.PROTOCOL_VERSION, "threshold": .85, "variants": ["base"],
                    "preprocessing": d.RUNTIME_PREPROCESSING, "samples": self.rows, "finalChallengeScored": False,
                    "trainingEligible": False, "independentEvaluationEligible": False, "implementation": [],
                    "crops": d.ref(metadata), "review": d.ref(metadata)}
        protocol["seal"] = d.digest(protocol)
        protocol_path, candidate_path = self.root / "protocol.json", self.root / "candidate.json"
        d.write(protocol_path, protocol)
        d.write(candidate_path, candidate)
        results = {name: {**self.result(), "protocolSHA256": protocol["seal"]} for name in d.MODELS}
        comparison = {"version": d.PROTOCOL_VERSION, "protocol": d.ref(protocol_path), "results": results, "finalChallengeScored": False}
        for name, result in results.items():
            d.write(self.root / (name + ".json"), result)
        comparison_path = self.root / "comparison.json"
        d.write(comparison_path, comparison)
        return protocol_path, comparison_path, candidate_path

    def test_reproduces_and_distinguishes_populations(self):
        result = d.analyze(self.rows, self.result())
        self.assertEqual(result["reproduced"]["frameCounts"], {"unique-correct": 1})
        self.assertEqual(result["reproduced"]["metrics"]["pair"]["groups"]["overall"]["tp"], 1)
        self.assertAlmostEqual(result["paired"][0]["difference"], .8)
        self.assertEqual(result["strictTopRank"], 1)

    def test_ties_are_not_unique_ranks(self):
        result = d.analyze(self.rows, self.result((.9, .9, .9, .9)))
        self.assertEqual((result["ranks"][0]["rankBest"], result["ranks"][0]["rankWorst"]), (1, 2))
        self.assertEqual(result["ranks"][0]["margin"], 0)
        self.assertEqual(result["reproduced"]["frameCounts"], {"multiple-focus": 1})

    def test_all_frame_decisions(self):
        for scores, expected in [((.1, .1), "no-focus"), ((.1, .9), "wrong-focus"),
                                 ((.9, .1), "unique-correct"), ((.9, .9), "multiple-focus")]:
            with self.subTest(expected=expected):
                result = d.analyze(self.rows, self.result((.9, .1, *scores)))
                self.assertEqual(result["ranks"][0]["decision"], expected)

    def test_missing_duplicate_reordered_invalid_predictions(self):
        for mutate in [lambda p: p.pop(), lambda p: p.append(p[0]), lambda p: p.reverse(),
                       *[lambda p, value=value: p[0].update(probability=value) for value in [True, None, -1, 1.1, float("nan"), float("inf")]]]:
            result = self.result()
            mutate(result["predictions"])
            with self.assertRaises((ValueError, TypeError)):
                d.analyze(self.rows, result)

    def test_incomplete_or_conflicting_membership(self):
        for mutate in [lambda r: r.pop(), lambda r: r[2].update(candidateComplete=False),
                       lambda r: r[2].update(candidateCount=3), lambda r: r[2].update(frameID="wrong"),
                       lambda r: r[1].update(elementID="other"), lambda r: r[2].update(bounds=[0, 0, 1, 1]),
                       lambda r: r[3].update(path="different.png"), lambda r: r.pop(1)]:
            rows = copy.deepcopy(self.rows)
            mutate(rows)
            with self.assertRaises(ValueError):
                d.validate_membership(rows)

    def test_unknown_and_empty_strata(self):
        for row in self.rows:
            row["stratum"] = "unknown"
        result = d.analyze(self.rows, self.result())
        self.assertEqual(result["distributions"]["pair"]["stratum:photos-buttons"]["1"]["status"], "unavailable")
        self.assertIsNone(d.distribution([])["median"])
        self.assertEqual(result["distributions"]["pair"]["stratum:unknown"]["1"]["n"], 1)

    def test_published_counts_and_state_must_match(self):
        for key, value in [("accounted", 0), ("frameCounts", {}), ("state", "failed")]:
            result = self.result()
            result[key] = value
            with self.assertRaises(ValueError):
                d.analyze(self.rows, result)

    def test_final_challenge_rejected_even_if_role_forged(self):
        for role in ("appearance-validation", "final-challenge"):
            rows = copy.deepcopy(self.rows)
            for row in rows:
                row.update(group="memory_mosaic", role=role)
            with self.assertRaises(ValueError):
                d.validate_membership(rows)

    def test_protocol_drift(self):
        paths = self.fixture()
        protocol = d.read(paths[0])
        for key, value in [("threshold", .5), ("version", "future"), ("variants", ["margin-sweep"]),
                           ("finalChallengeScored", True)]:
            changed = copy.deepcopy(protocol)
            changed[key] = value
            changed["seal"] = d.digest({k: v for k, v in changed.items() if k != "seal"})
            with self.assertRaises(ValueError):
                d.validate_protocol(changed)

    def test_end_to_end_cli_determinism_and_preservation(self):
        paths = self.fixture()
        before = {str(p): d.ref(p) for p in self.root.iterdir()}
        index = self.root / "index.json"
        cli = d.ROOT / "scripts/focus_offline_diagnosis.py"
        command = [sys.executable, "-B", str(cli), "freeze", "--protocol", str(paths[0]),
                   "--comparison", str(paths[1]), "--candidate", str(paths[2]), "--output", str(index)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        for folder in ("out1", "out2"):
            process = subprocess.run([sys.executable, "-B", str(cli), "report", "--index", str(index),
                                      "--output", str(self.root / folder)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        for p in (self.root / "out1").rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(), (self.root / "out2" / p.relative_to(self.root / "out1")).read_bytes())
        for path, record in before.items():
            self.assertEqual(d.ref(Path(path)), record)

    def test_changed_missing_corrupt_images_block_without_reduction(self):
        paths = self.fixture()
        index = self.root / "index.json"
        d.freeze(*paths, index)
        (self.root / "frame.png").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "blocked_inputs"):
            d.report(index, self.root / "blocked")
        accounting = d.read(self.root / "blocked/accounting.json")
        self.assertEqual(len(accounting["images"]), 2)
        self.assertEqual(sum(r["state"] == "blocked" for r in accounting["images"]), 1)
        self.assertFalse((self.root / "blocked/diagnosis.json").exists())
        (self.root / "frame.png").unlink()
        with self.assertRaisesRegex(ValueError, "blocked_inputs"):
            d.report(index, self.root / "missing")

    def test_candidate_protected_and_incomplete_rejected(self):
        paths = self.fixture()
        for mutation in ("protected", "missing", "duplicate"):
            candidate = d.read(paths[2])
            if mutation == "protected":
                candidate["samples"][0]["use"] = "final-challenge"
            elif mutation == "missing":
                candidate["samples"].pop()
            else:
                candidate["samples"].append(candidate["samples"][0])
            with self.assertRaises(ValueError):
                d.candidate_pairs(candidate)

    def test_valid_hash_corrupt_pixels_and_invalid_bounds(self):
        corrupt = self.root / "corrupt.png"
        corrupt.write_bytes(b"not an image")
        with self.assertRaisesRegex(ValueError, "corrupt_image"):
            d.image(d.ROOT, d.ref(corrupt))
        paths = self.fixture()
        protocol = d.read(paths[0])
        for row in protocol["samples"]:
            row["bounds"] = [-1, 0, 10, 10]
        protocol["seal"] = d.digest({k: v for k, v in protocol.items() if k != "seal"})
        d.write(paths[0], protocol)
        comparison = d.read(paths[1])
        comparison["protocol"] = d.ref(paths[0])
        d.write(paths[1], comparison)
        index = self.root / "index.json"
        d.freeze(*paths, index)
        with self.assertRaisesRegex(ValueError, "out_of_frame_bounds"):
            d.report(index, self.root / "invalid-bounds")

    def test_inventory_cannot_add_protected_or_unbound_images(self):
        paths = self.fixture()
        index = self.root / "index.json"
        doc = d.freeze(*paths, index)
        doc["images"].append({"path": "protected-challenge.png", "sha256": "0"*64})
        doc["seal"] = d.digest({k: v for k, v in doc.items() if k != "seal"})
        d.write(index, doc)
        with patch.object(d, "image", side_effect=AssertionError("must reject before pixel access")):
            with self.assertRaisesRegex(ValueError, "inventory_membership"):
                d.report(index, self.root / "protected")

    def test_changed_hash_and_missing_artifact(self):
        paths = self.fixture()
        index = self.root / "index.json"
        d.freeze(*paths, index)
        (self.root / "metadata.json").write_text('{"changed": true}')
        with self.assertRaisesRegex(ValueError, "blocked_inputs"):
            d.report(index, self.root / "metadata-changed")
        (self.root / "shipped.json").unlink()
        with self.assertRaises(OSError):
            d.freeze(*paths, self.root / "missing-index.json")

    def test_no_execution_calls(self):
        # Runtime functions are never part of freeze/report; retained model identity is metadata.
        paths = self.fixture()
        with patch("focus_runtime.invoke", side_effect=AssertionError("inference forbidden")), \
             patch("focus_surface_evaluation.run", side_effect=AssertionError("inference forbidden")):
            index = self.root / "index.json"
            d.freeze(*paths, index)
            d.report(index, self.root / "output")
        self.assertNotIn("torch", sys.modules)
        self.assertNotIn("coremltools", sys.modules)


if __name__ == "__main__":
    unittest.main()
