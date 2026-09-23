#!/usr/bin/env python3
"""Exercises the exported YOLO layout through preflight and review contracts."""
from __future__ import annotations
import hashlib, json, shutil, struct, subprocess, sys, tempfile, unittest, zlib
from pathlib import Path

from corpus_assembly import assemble
from reference_comparison import compare
from regression_selector import build

ROOT = Path(__file__).resolve().parent.parent

def png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0\x00\x00\x00")) + chunk(b"IEND", b"")

class IntegratedOfflineToolchainTests(unittest.TestCase):
    def setUp(self) -> None:
        debug = ROOT / ".build/debug-output"
        debug.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(dir=debug, prefix="integrated_toolchain_"))
        self.source = self.work / "source"
        for split, name, family in (("train", "train", "TrainFamily"), ("train", "holdout", "CardDetail"), ("validation", "validation", "ValidationFamily")):
            directory = self.source / split
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"{name}.png").write_bytes(png())
            sidecar = {"image": {"pixelWidth": 1, "pixelHeight": 1}, "generatorProfile": {"templateFamily": family}, "elements": [{"elementType": "primaryButton", "boundsVisionNormalized": {"x": 0, "y": 0, "width": 1, "height": 1}}]}
            (directory / f"{name}.json").write_text(json.dumps(sidecar))
        self.exported = self.work / "exported"

    def tearDown(self) -> None:
        shutil.rmtree(self.work)

    def test_export_assembly_preflight_selector_and_comparison(self) -> None:
        outside = subprocess.run([sys.executable, str(ROOT / "scripts/export_coco.py"), "--dataset", str(self.source), "--output", "/outside-nativeui-toolchain-output"], capture_output=True, text=True)
        self.assertNotEqual(outside.returncode, 0)
        self.assertIn("inside the project", outside.stderr)
        export = subprocess.run([sys.executable, str(ROOT / "scripts/export_coco.py"), "--dataset", str(self.source), "--output", str(self.exported)], capture_output=True, text=True)
        self.assertEqual(export.returncode, 0, export.stderr)
        for split in ("train", "val", "test"):
            self.assertTrue((self.exported / split / "images").is_dir())
            self.assertTrue((self.exported / split / "labels").is_dir())
        weights = self.work / "run009-best.pt"; weights.write_bytes(b"test-only")
        preflight = subprocess.run([sys.executable, str(ROOT / "scripts/train_ios_model.py"), "--validate-only", "--dataset", str(self.exported), "--initial-weights", str(weights), "--output-dir", str(self.work / "runs")], capture_output=True, text=True)
        self.assertEqual(preflight.returncode, 0, preflight.stdout + preflight.stderr)
        self.assertIn('"configurationValid": true', preflight.stdout)
        image = self.exported / "test/images/holdout.png"; label = self.exported / "test/labels/holdout.txt"
        member = {"id": "holdout", "image": str(image), "label": str(label), "sourceSplit": "test", "platform": "iOS", "family": "CardDetail", "width": 1, "height": 1, "classes": [7]}
        suite = build([member], [], 250)
        self.assertEqual([row["id"] for row in suite["members"]], ["holdout"])
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        corpus = assemble([{"id": "train", "split": "training", "contentSHA256": "train-content", "family": "TrainFamily", "source": "synthetic", "classes": [7]}, {"id": "holdout", "split": "held-out", "contentSHA256": digest, "family": "CardDetail", "source": "synthetic", "classes": [7]}])
        self.assertEqual(corpus["trainingClassCounts"], {7: 1})
        artifact = {"formatVersion": "prediction-artifact-v1", "corpus": {"contentSHA256": digest}, "categoryMap": {"sha256": "map"}, "settingsSHA256": "settings", "completeness": {"complete": True, "requestedImageIDs": ["holdout"]}, "results": [{"imageID": "holdout", "imageSHA256": digest, "labelSHA256": hashlib.sha256(label.read_bytes()).hexdigest(), "status": "empty"}], "metrics": {"map50": 0.0}}
        self.assertEqual(compare(artifact, artifact)["sampleCount"], 1)
        incomplete_metrics = dict(artifact, metrics={"toggleAP": None})
        unavailable = compare(artifact, incomplete_metrics)
        self.assertEqual(unavailable["metricAvailability"], "unavailable")
        self.assertEqual(unavailable["deltas"], {})
        self.assertEqual(unavailable["unavailableMetrics"], {"map50": ["right"], "toggleAP": ["left", "right"]})
        collision = subprocess.run([sys.executable, str(ROOT / "scripts/export_coco.py"), "--dataset", str(self.source), "--output", str(self.exported)], capture_output=True, text=True)
        self.assertNotEqual(collision.returncode, 0)
        self.assertIn("refusing collision", collision.stderr)

if __name__ == "__main__":
    unittest.main()
