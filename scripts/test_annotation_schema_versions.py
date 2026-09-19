#!/usr/bin/env python3
"""Structural parity and declared-version tests for annotation schemas."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from annotation_schema_validation import AnnotationSchemaError, schema_for_declared_version, validate_sidecar_structure


ROOT = Path(__file__).resolve().parent.parent


def valid_sidecar(version: str, scale: int) -> dict:
    return {
        "schemaVersion": version, "imageSHA256": "0" * 64, "generatorProfile": {}, "elements": [],
        "image": {
            "fileName": "fixture.png", "pixelWidth": 1, "pixelHeight": 1, "scale": scale,
            "platform": "tvOS", "osVersion": "unknown", "deviceName": "fixture", "interfaceIdiom": "tv",
            "orientation": "landscape", "colorScheme": "dark", "dynamicTypeSize": "large", "locale": "en_US",
            "layoutDirection": "ltr", "safeAreaInsets": {}, "reduceTransparency": False,
            "increaseContrast": False, "boldText": False, "buttonShapes": False, "onOffLabels": False,
            "smartInvert": False,
        },
    }


class AnnotationSchemaVersionTests(unittest.TestCase):
    def test_structural_parity_has_only_approved_validation_deltas(self) -> None:
        v10 = json.loads((ROOT / "Research/schemas/annotation.schema.json").read_text())
        v11 = json.loads((ROOT / "Research/schemas/annotation.schema.v1.1.json").read_text())
        self.assertEqual(v10["$schema"], v11["$schema"])
        self.assertEqual(v10["required"], v11["required"])
        self.assertEqual(v10["properties"].keys(), v11["properties"].keys())
        self.assertEqual(v10["definitions"], v11["definitions"])
        self.assertEqual(v10["properties"]["image"], {**v11["properties"]["image"], "properties": {**v11["properties"]["image"]["properties"], "scale": v10["properties"]["image"]["properties"]["scale"]}})

    def test_missing_and_unsupported_versions_have_no_fallback(self) -> None:
        with self.assertRaisesRegex(AnnotationSchemaError, "missing schemaVersion"):
            schema_for_declared_version({})
        with self.assertRaisesRegex(AnnotationSchemaError, "unsupported schemaVersion"):
            schema_for_declared_version({"schemaVersion": "9.9"})

    def test_incomplete_sidecar_and_v10_scale_one_fail(self) -> None:
        broken = valid_sidecar("1.1", 1)
        del broken["image"]["deviceName"]
        with self.assertRaisesRegex(AnnotationSchemaError, "missing required fields"):
            validate_sidecar_structure(broken)
        with self.assertRaisesRegex(AnnotationSchemaError, "does not permit"):
            validate_sidecar_structure(valid_sidecar("1.0", 1))

    def test_v11_accepts_all_valid_scales(self) -> None:
        for scale in (1, 2, 3):
            self.assertEqual(validate_sidecar_structure(valid_sidecar("1.1", scale)).name, "annotation.schema.v1.1.json")


if __name__ == "__main__":
    unittest.main()
