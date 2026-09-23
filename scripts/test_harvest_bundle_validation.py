#!/usr/bin/env python3
"""Deterministic H1 contract tests for the offline harvest bundle validator."""
from __future__ import annotations

import hashlib
import json
import shutil
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from harvest_bundle_validation import HarvestValidationError, validate_bundle
from harvest_focus_pairs import extract_fixture_bundle
from simulator_focus_manifest import SimulatorManifestError, build

ROOT = Path(__file__).resolve().parent.parent


def png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0\x7f\x7f\x7f")) + chunk(b"IEND", b"")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class H1Tests(unittest.TestCase):
    def setUp(self) -> None:
        (ROOT / ".build/debug-output").mkdir(parents=True, exist_ok=True)
        self.d = Path(tempfile.mkdtemp(dir=ROOT / ".build/debug-output", prefix="h1_"))
        self.write_bundle()

    def tearDown(self) -> None:
        if self.d.exists():
            shutil.rmtree(self.d)

    def row(self, identifier: str = "synth-0", split: str = "training", focused: str = "f.png", metadata: str = "m.json") -> dict:
        return {"id": identifier, "path": focused, "sha256": sha((self.d / focused).read_bytes()), "expectedFocus": "e", "box": [0, 0, 1, 1], "metadata": {"unfocusedPath": "u.png", "focusedPath": focused, "metadataPath": metadata}, "split": split}

    def write_bundle(self) -> None:
        image = png()
        meta = {"id": "synth-0", "unfocused_png": "u.png", "focused_png": "f.png", "focused_element_id": "e", "is_settled": True, "recipe": {"recipe_hash": "recipe-a", "seed": 7, "archetype": "grid_matrix", "theme": "high_contrast"}, "elements": [{"element_id": "e", "taxonomy_class": "collectionItem", "is_focused": True, "normalized_bounds": [0, 0, 1, 1], "pixel_bounds": [0, 0, 1, 1]}]}
        for name, body in {"u.png": image, "f.png": image, "m.json": json.dumps(meta).encode()}.items():
            (self.d / name).write_bytes(body)
        row = self.row()
        for split in ("training", "calibration", "held-out"):
            (self.d / f"{split}.json").write_text(json.dumps([row] if split == "training" else []))
        (self.d / "manifest.json").write_text(json.dumps([row]))
        (self.d / "harvest-receipt.json").write_text(json.dumps({"schemaVersion": 1, "outcome": "completed", "acceptedRowCount": 1, "rejections": [], "failure": None}))
        self.reindex()

    def reindex(self, source_description: dict | None = None) -> None:
        excluded = {"dataset-index.json", "harvest-receipt.json"}
        artifacts = []
        for path in sorted(self.d.iterdir()):
            if path.name not in excluded and path.is_file() and not path.is_symlink():
                body = path.read_bytes()
                artifacts.append({"path": path.name, "sha256": sha(body), "byteCount": len(body)})
        index = {"datasetLayoutVersion": 1, "telemetryContract": "harvest-canonical-v1; source-version-unverified", "producer": "TVTestRig", "producerBuild": "fixture-build-unverified", "provenance": "unverified-pixel-telemetry-binding", "normalizedCoordinates": "xyxy-top-left-unit", "pixelCoordinates": "xywh-top-left-pixels", "artifacts": artifacts}
        if source_description is not None:
            index["sourceDescription"] = source_description
        (self.d / "dataset-index.json").write_text(json.dumps(index))

    def replace_metadata(self, change) -> None:
        metadata = json.loads((self.d / "m.json").read_text())
        change(metadata)
        (self.d / "m.json").write_text(json.dumps(metadata))
        self.reindex()

    def test_positive_preserves_source_and_is_unverified(self) -> None:
        before = {path.name: sha(path.read_bytes()) for path in self.d.iterdir() if path.is_file()}
        result = validate_bundle(self.d)
        after = {path.name: sha(path.read_bytes()) for path in self.d.iterdir() if path.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["integrity"], "pass")
        self.assertFalse(result["eligibleForTraining"])
        self.assertEqual(result["producer"], "TVTestRig")
        self.assertIsNone(result["identityEvidence"])
        self.assertEqual(len(result["usableRows"]), 1)

    def test_reported_source_description_is_preserved_but_not_trusted(self) -> None:
        source = {"requestedDeviceID": "office-stable-id-redacted", "captureMethod": "fixture-batch", "collectedAt": "2026-09-19T20:34:07Z", "environment": {"os": "tvOS"}, "fixture": {"scene": "actionDialog"}, "assurance": "reported-source; not-attested"}
        self.reindex(source)
        result = validate_bundle(self.d)
        self.assertEqual(result["sourceDescription"], source)
        self.assertEqual(result["usableRows"][0]["sourceDescription"], source)
        self.assertIsNone(result["identityEvidence"])
        self.assertFalse(result["eligibleForTraining"])
        source["assurance"] = "attested"
        self.reindex(source)
        with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
            validate_bundle(self.d)

    def test_versions_receipt_and_altered_artifact_fail_closed(self) -> None:
        index = json.loads((self.d / "dataset-index.json").read_text())
        index["datasetLayoutVersion"] = 2
        (self.d / "dataset-index.json").write_text(json.dumps(index))
        with self.assertRaisesRegex(HarvestValidationError, "unsupported_version"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        receipt = json.loads((self.d / "harvest-receipt.json").read_text())
        receipt["outcome"] = "aborted"
        (self.d / "harvest-receipt.json").write_text(json.dumps(receipt))
        with self.assertRaisesRegex(HarvestValidationError, "incomplete_run"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        (self.d / "f.png").write_bytes(b"changed")
        with self.assertRaisesRegex(HarvestValidationError, "integrity_failed"):
            validate_bundle(self.d)

    def test_swift_date_is_preserved_without_admission(self) -> None:
        for date in (811804819.582654, 0, -1, "2026-09-22T21:20:19Z"):
            with self.subTest(date=date):
                source = {"captureMethod": "simctl-explicit-uuid", "collectedAt": date,
                          "assurance": "reported-source; not-attested"}
                self.reindex(source)
                result = validate_bundle(self.d)
                self.assertEqual(result["sourceDescription"], source)
                self.assertFalse(result["eligibleForTraining"])
                self.assertIsNone(result["identityEvidence"])

    def test_invalid_dates_fail_closed(self) -> None:
        for date in (None, True, False, [], {}, "", float("nan"), float("inf"), -float("inf")):
            with self.subTest(date=date):
                self.reindex({"captureMethod": "simctl-explicit-uuid", "collectedAt": date,
                              "assurance": "reported-source; not-attested"})
                with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
                    validate_bundle(self.d)

    def test_numeric_date_does_not_supply_missing_resolved_theme(self) -> None:
        self.replace_metadata(lambda meta: meta["recipe"].pop("theme"))
        self.reindex({"captureMethod": "simctl-explicit-uuid", "collectedAt": 811804819.582654,
                      "assurance": "reported-source; not-attested"})
        result = validate_bundle(self.d)
        self.assertEqual(result["integrity"], "pass")
        with self.assertRaisesRegex(SimulatorManifestError, "unsupported_theme"):
            build(result, "inspection-only", "producer-reference", None)

    def test_partial_symlink_missing_and_duplicate_artifacts_fail_closed(self) -> None:
        partial = self.d.parent / ".x.partial-1"
        self.d.rename(partial); self.d = partial
        with self.assertRaisesRegex(HarvestValidationError, "incomplete_run"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        (self.d / "m.json").unlink()
        with self.assertRaisesRegex(HarvestValidationError, "unsafe_or_invalid_manifest"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        (self.d / "u.png").unlink(); (self.d / "u.png").symlink_to("f.png")
        with self.assertRaisesRegex(HarvestValidationError, "unsafe_or_invalid_manifest"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        index = json.loads((self.d / "dataset-index.json").read_text())
        index["artifacts"].append(index["artifacts"][0])
        (self.d / "dataset-index.json").write_text(json.dumps(index))
        with self.assertRaisesRegex(HarvestValidationError, "unsafe_or_invalid_manifest"):
            validate_bundle(self.d)

    def test_malformed_image_stale_focus_split_conflict_and_bounds_fail_closed(self) -> None:
        (self.d / "f.png").write_bytes(b"not a png"); self.reindex()
        with self.assertRaisesRegex(HarvestValidationError, "invalid_image"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        self.replace_metadata(lambda metadata: metadata.update(focused_element_id="not-e"))
        with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        (self.d / "training.json").write_text("[]"); self.reindex()
        with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
            validate_bundle(self.d)
        self.tearDown(); self.setUp()
        self.replace_metadata(lambda metadata: metadata["elements"][0].update(normalized_bounds=[0, 0, 2, 1]))
        with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
            validate_bundle(self.d)

    def test_unknown_and_empty_usable_annotations_remain_ineligible(self) -> None:
        self.replace_metadata(lambda metadata: metadata["elements"][0].update(taxonomy_class="not-a-known-class"))
        result = validate_bundle(self.d)
        self.assertEqual(result["unknownClassCount"], 1)
        self.assertEqual(result["usableRows"], [])
        self.assertFalse(result["eligibleForTraining"])

    def test_cross_split_shared_baseline_fails_closed(self) -> None:
        (self.d / "f2.png").write_bytes((self.d / "f.png").read_bytes())
        metadata = json.loads((self.d / "m.json").read_text()); metadata["id"] = "synth-1"; metadata["focused_png"] = "f2.png"
        (self.d / "m2.json").write_text(json.dumps(metadata))
        first = self.row()
        second = self.row("synth-1", "held-out", "f2.png", "m2.json")
        (self.d / "manifest.json").write_text(json.dumps([first, second]))
        (self.d / "training.json").write_text(json.dumps([first]))
        (self.d / "calibration.json").write_text("[]")
        (self.d / "held-out.json").write_text(json.dumps([second]))
        (self.d / "harvest-receipt.json").write_text(json.dumps({"schemaVersion": 1, "outcome": "completed", "acceptedRowCount": 2, "rejections": [], "failure": None}))
        self.reindex()
        with self.assertRaisesRegex(HarvestValidationError, "invalid_metadata"):
            validate_bundle(self.d)

    def test_simulator_manifest_retains_originals_and_does_not_open_gates(self) -> None:
        manifest = build(validate_bundle(self.d), "pilot-v1", "c6ec816", {"udid": "recorded-not-trusted"})
        pair = manifest["pairs"][0]
        self.assertEqual(pair["originalFamily"], "grid_matrix")
        self.assertEqual(pair["family"], "gridMatrix")
        self.assertEqual(pair["originalTheme"], "high_contrast")
        self.assertEqual(pair["theme"], "highContrast")
        self.assertFalse(manifest["eligibility"]["generalTrainingApproval"])
        self.assertEqual(manifest["eligibility"]["physicalQualification"], "not-established")
        bad = validate_bundle(self.d)
        bad["usableRows"][0]["recipe"]["archetype"] = "unsupported"
        with self.assertRaisesRegex(SimulatorManifestError, "unsupported_family"):
            build(bad, "pilot-v1", "c6ec816", None)

    def test_fixture_extraction_uses_frame_truth_and_writes_paired_crops(self) -> None:
        output = self.d / "focus-pairs"
        with self.assertRaisesRegex(SimulatorManifestError, "missing_observed_pair_evidence"):
            extract_fixture_bundle(self.d, output, "pilot-v1", "c6ec816", 0.16, False)
        proof = {"version": "focus-pair-evidence-v1", "evidenceKind": "test-only", "sourceKind": "simulatorFixture", "producerReference": "c6ec816", "pairs": [{"pairID": "synth-0", "elementID": "e", "frames": {
            role: {"path": path, "sha256": sha((self.d / path).read_bytes()), "bounds": [0, 0, 1, 1], "frameID": role, "focusFrameID": role, "labelSource": "fixtureCallback", "observedFocusID": "e" if role == "focused" else None}
            for role, path in (("focused", "f.png"), ("unfocused", "u.png"))}}]}
        result = extract_fixture_bundle(self.d, output, "pilot-v1", "c6ec816", 0.16, False, proof)
        self.assertEqual(result["pairs"], 1)
        manifest = json.loads((output / "focus_dataset_manifest.json").read_text())
        pair = manifest["pairs"][0]
        self.assertEqual(pair["labelSource"], "fixtureGroundTruth")
        self.assertEqual(pair["fixture_scene"], "gridMatrix")
        self.assertEqual(pair["theme"], "highContrast")
        self.assertTrue((output / pair["focused_crop"]).is_file())
        self.assertTrue((output / pair["unfocused_crop"]).is_file())


if __name__ == "__main__":
    unittest.main()
