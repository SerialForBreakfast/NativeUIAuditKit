#!/usr/bin/env python3
"""Offline contract tests for prediction-artifact-v1.

All temporary bytes live under .build/debug-output/; no model is loaded and no
inference is attempted.
"""

from __future__ import annotations

import json
import shutil
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from prediction_artifact import (
    PredictionArtifactError,
    build_artifact,
    ensure_new_output,
    load_request,
    make_result,
    write_artifact,
)


ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = ROOT / ".build" / "debug-output"


def png_bytes(width: int, height: int) -> bytes:
    """Create a deterministic, real RGB PNG without third-party image writers."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + b"\x7f\x7f\x7f" * width for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


class PredictionArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        WORK_ROOT.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix="prediction_artifact_", dir=WORK_ROOT))
        (self.work / "images").mkdir()
        (self.work / "labels").mkdir()
        (self.work / "images" / "rectangular.png").write_bytes(png_bytes(320, 180))
        (self.work / "labels" / "rectangular.txt").write_text("")
        (self.work / "checkpoint.pt").write_bytes(b"test checkpoint bytes")
        (self.work / "category-map.json").write_text(json.dumps({"version": "1.0", "categories": [{"id": 0, "name": "label"}]}))

    def tearDown(self) -> None:
        shutil.rmtree(self.work)

    def write_manifest(self, images: list[dict]) -> Path:
        path = self.work / "request.json"
        path.write_text(json.dumps({"formatVersion": "prediction-input-manifest-v1", "corpusID": "toy-v1", "images": images}))
        return path

    def valid_entry(self, image_id: str = "fixtures/rectangular.png") -> dict:
        return {"imageID": image_id, "imagePath": "images/rectangular.png", "labelPath": "labels/rectangular.txt"}

    def test_rectangular_empty_result_is_complete_and_uses_original_dimensions(self) -> None:
        request = load_request(self.write_manifest([self.valid_entry()]), class_count=1)
        result = make_result(request.images[0], class_count=1, detections=[])
        artifact = build_artifact(
            request, self.work / "checkpoint.pt", self.work / "category-map.json", "1.0", {"imgsz": 640}, [result]
        )
        self.assertEqual(result["status"], "empty")
        self.assertEqual((result["width"], result["height"]), (320, 180))
        self.assertTrue(artifact["completeness"]["complete"])
        self.assertEqual(artifact["completeness"]["resultCount"], 1)

    def test_failed_result_is_explicit_and_complete(self) -> None:
        request = load_request(self.write_manifest([self.valid_entry()]), class_count=1)
        result = make_result(request.images[0], 1, failure={"code": "inference_failed", "message": "synthetic failure"})
        artifact = build_artifact(
            request, self.work / "checkpoint.pt", self.work / "category-map.json", "1.0", {"imgsz": 640}, [result]
        )
        self.assertEqual(result["status"], "failed")
        self.assertTrue(artifact["completeness"]["complete"])

    def test_invalid_detection_id_score_and_bounds_are_rejected(self) -> None:
        request = load_request(self.write_manifest([self.valid_entry()]), class_count=1)
        image = request.images[0]
        for detection in (
            {"classID": 1, "score": 0.5, "xyxyPixels": [0, 0, 10, 10]},
            {"classID": 0, "score": 1.1, "xyxyPixels": [0, 0, 10, 10]},
            {"classID": 0, "score": 0.5, "xyxyPixels": [10, 0, 10, 10]},
        ):
            with self.assertRaises(PredictionArtifactError):
                make_result(image, 1, detections=[detection])

    def test_corrupt_image_fails_readiness_before_inference(self) -> None:
        (self.work / "images" / "broken.png").write_bytes(b"not a png")
        with self.assertRaisesRegex(PredictionArtifactError, "cannot be decoded"):
            load_request(
                self.write_manifest([{"imageID": "fixtures/broken.png", "imagePath": "images/broken.png", "labelPath": "labels/rectangular.txt"}]),
                class_count=1,
            )

    def test_duplicate_ids_and_dangling_symlink_fail_readiness(self) -> None:
        with self.assertRaisesRegex(PredictionArtifactError, "duplicate imageID"):
            load_request(self.write_manifest([self.valid_entry(), self.valid_entry()]), class_count=1)
        dangling = self.work / "images" / "dangling.png"
        dangling.symlink_to("missing.png")
        with self.assertRaisesRegex(PredictionArtifactError, "dangling symlink"):
            load_request(
                self.write_manifest([{"imageID": "fixtures/dangling.png", "imagePath": "images/dangling.png", "labelPath": "labels/rectangular.txt"}]),
                class_count=1,
            )

    def test_incomplete_result_set_and_output_collision_are_rejected(self) -> None:
        (self.work / "images" / "second.png").write_bytes(png_bytes(320, 180))
        (self.work / "labels" / "second.txt").write_text("")
        second = {"imageID": "fixtures/second.png", "imagePath": "images/second.png", "labelPath": "labels/second.txt"}
        request = load_request(self.write_manifest([self.valid_entry(), second]), class_count=1)
        with self.assertRaisesRegex(PredictionArtifactError, "exactly one record"):
            build_artifact(
                request, self.work / "checkpoint.pt", self.work / "category-map.json", "1.0", {"imgsz": 640},
                [make_result(request.images[0], 1, detections=[])],
            )
        output = self.work / "result.json"
        write_artifact(output, {"fixture": True})
        with self.assertRaisesRegex(PredictionArtifactError, "already exists"):
            ensure_new_output(output, ROOT)


if __name__ == "__main__":
    unittest.main()
