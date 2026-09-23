"""Dependency-free declared-version checks for NUA annotation sidecars.

This is intentionally a narrow local guard for schema selection and the image
metadata invariants used by fixture normalization; it does not fabricate fields
or silently select a different schema version.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {
    "1.0": ROOT / "Research" / "schemas" / "annotation.schema.json",
    "1.1": ROOT / "Research" / "schemas" / "annotation.schema.v1.1.json",
    "1.2": ROOT / "Research" / "schemas" / "annotation.schema.v1.2.json",
}
TOP_LEVEL_REQUIRED = {"schemaVersion", "imageSHA256", "image", "generatorProfile", "elements"}
IMAGE_REQUIRED = {
    "fileName", "pixelWidth", "pixelHeight", "scale", "platform", "osVersion", "deviceName",
    "interfaceIdiom", "orientation", "colorScheme", "dynamicTypeSize", "locale", "layoutDirection",
    "safeAreaInsets", "reduceTransparency", "increaseContrast", "boldText", "buttonShapes",
    "onOffLabels", "smartInvert",
}


class AnnotationSchemaError(ValueError):
    pass


def schema_for_declared_version(sidecar: dict[str, Any]) -> Path:
    version = sidecar.get("schemaVersion")
    if not isinstance(version, str) or not version:
        raise AnnotationSchemaError("sidecar is missing schemaVersion")
    try:
        return SCHEMAS[version]
    except KeyError as exc:
        raise AnnotationSchemaError(f"unsupported schemaVersion: {version}") from exc


def validate_sidecar_structure(sidecar: dict[str, Any]) -> Path:
    schema = schema_for_declared_version(sidecar)
    missing = TOP_LEVEL_REQUIRED - set(sidecar)
    if missing:
        raise AnnotationSchemaError(f"sidecar is missing required top-level fields: {sorted(missing)}")
    if not isinstance(sidecar["elements"], list) or not isinstance(sidecar["generatorProfile"], dict):
        raise AnnotationSchemaError("sidecar elements/generatorProfile have invalid types")
    image = sidecar["image"]
    if not isinstance(image, dict):
        raise AnnotationSchemaError("sidecar image must be an object")
    missing_image = IMAGE_REQUIRED - set(image)
    if missing_image:
        raise AnnotationSchemaError(f"sidecar image is missing required fields: {sorted(missing_image)}")
    scale = image["scale"]
    permitted = {2, 3} if sidecar["schemaVersion"] == "1.0" else {1, 2, 3}
    if isinstance(scale, bool) or not isinstance(scale, int) or scale not in permitted:
        raise AnnotationSchemaError(f"schema {sidecar['schemaVersion']} does not permit image.scale={scale!r}")
    return schema


def load_and_validate(path: Path) -> dict[str, Any]:
    try:
        sidecar = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AnnotationSchemaError(f"invalid sidecar JSON: {exc}") from exc
    if not isinstance(sidecar, dict):
        raise AnnotationSchemaError("sidecar root must be an object")
    validate_sidecar_structure(sidecar)
    return sidecar
