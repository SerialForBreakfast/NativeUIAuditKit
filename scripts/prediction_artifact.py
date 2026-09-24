"""Strict manifest preflight and JSON serialization for prediction-artifact-v1.

This module deliberately has no Ultralytics import.  It is shared by the
evaluator's explicit prediction-export mode and its offline unit tests.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


FORMAT_VERSION = "prediction-artifact-v1"
INPUT_FORMAT_VERSION = "prediction-input-manifest-v1"
EVALUATOR_VERSION = "eval_phase6a-prediction-export-v1"


class PredictionArtifactError(ValueError):
    """A request or artifact violates the versioned prediction contract."""


@dataclass(frozen=True)
class ResolvedImage:
    image_id: str
    image_path: Path
    label_path: Path
    width: int
    height: int
    image_sha256: str
    label_sha256: str


@dataclass(frozen=True)
class PredictionRequest:
    corpus_id: str
    manifest_path: Path
    manifest_sha256: str
    content_sha256: str
    images: tuple[ResolvedImage, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _relative_member(root: Path, raw: Any, field: str, image_id: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise PredictionArtifactError(f"{image_id}: {field} must be a non-empty relative path")
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise PredictionArtifactError(f"{image_id}: {field} must remain relative to the manifest")
    path = (root / candidate).resolve(strict=False)
    if not path.exists():
        raise PredictionArtifactError(f"{image_id}: {field} is missing or has a dangling symlink target")
    if not path.is_file():
        raise PredictionArtifactError(f"{image_id}: {field} must resolve to a regular file")
    return path


def _decode_image(path: Path, image_id: str) -> tuple[int, int]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except Exception as exc:  # Pillow exceptions differ by version/decoder.
        raise PredictionArtifactError(f"{image_id}: image cannot be decoded ({exc})") from exc
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise PredictionArtifactError(f"{image_id}: decoded image dimensions must be positive")
    return width, height


def _validate_label(path: Path, image_id: str, class_count: int) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise PredictionArtifactError(f"{image_id}: label file is not UTF-8") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise PredictionArtifactError(f"{image_id}: label line {line_number} must contain class cx cy width height")
        try:
            class_value = float(fields[0])
            class_id = int(class_value)
            coordinates = [float(value) for value in fields[1:]]
        except ValueError as exc:
            raise PredictionArtifactError(f"{image_id}: label line {line_number} has non-numeric values") from exc
        if class_value != class_id or not 0 <= class_id < class_count:
            raise PredictionArtifactError(f"{image_id}: label line {line_number} has invalid class ID")
        if not all(math.isfinite(value) for value in coordinates):
            raise PredictionArtifactError(f"{image_id}: label line {line_number} has non-finite coordinates")
        cx, cy, width, height = coordinates
        if width <= 0 or height <= 0 or cx < -1e-5 or cy < -1e-5 or cx > 1 + 1e-5 or cy > 1 + 1e-5:
            raise PredictionArtifactError(f"{image_id}: label line {line_number} has invalid normalized bounds")
        if cx - width / 2 < -1e-5 or cx + width / 2 > 1 + 1e-5 or cy - height / 2 < -1e-5 or cy + height / 2 > 1 + 1e-5:
            raise PredictionArtifactError(f"{image_id}: label line {line_number} extends outside normalized image bounds")


def load_request(manifest_path: Path, class_count: int) -> PredictionRequest:
    """Resolve and validate every requested member before model construction."""
    manifest = manifest_path.resolve(strict=False)
    if not manifest.exists() or not manifest.is_file():
        raise PredictionArtifactError("input manifest does not exist")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PredictionArtifactError(f"input manifest is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("formatVersion") != INPUT_FORMAT_VERSION:
        raise PredictionArtifactError(f"input manifest formatVersion must be {INPUT_FORMAT_VERSION!r}")
    corpus_id = payload.get("corpusID")
    images = payload.get("images")
    if not isinstance(corpus_id, str) or not corpus_id or not isinstance(images, list) or not images:
        raise PredictionArtifactError("input manifest requires non-empty corpusID and images")

    root = manifest.parent
    resolved: list[ResolvedImage] = []
    seen_ids: set[str] = set()
    for entry in images:
        if not isinstance(entry, dict):
            raise PredictionArtifactError("input manifest images must be objects")
        image_id = entry.get("imageID")
        if not isinstance(image_id, str) or not image_id or Path(image_id).is_absolute() or ".." in Path(image_id).parts:
            raise PredictionArtifactError("imageID must be a non-empty corpus-relative identifier")
        if image_id in seen_ids:
            raise PredictionArtifactError(f"duplicate imageID: {image_id}")
        seen_ids.add(image_id)
        image_path = _relative_member(root, entry.get("imagePath"), "imagePath", image_id)
        label_path = _relative_member(root, entry.get("labelPath"), "labelPath", image_id)
        width, height = _decode_image(image_path, image_id)
        _validate_label(label_path, image_id, class_count)
        resolved.append(
            ResolvedImage(
                image_id=image_id,
                image_path=image_path,
                label_path=label_path,
                width=width,
                height=height,
                image_sha256=sha256_file(image_path),
                label_sha256=sha256_file(label_path),
            )
        )
    content = [
        {"imageID": item.image_id, "imageSHA256": item.image_sha256, "labelSHA256": item.label_sha256}
        for item in resolved
    ]
    return PredictionRequest(
        corpus_id=corpus_id,
        manifest_path=manifest,
        manifest_sha256=sha256_file(manifest),
        content_sha256=canonical_sha256(content),
        images=tuple(resolved),
    )


def normalize_detections(
    detections: Iterable[dict[str, Any]], image: ResolvedImage, class_count: int
) -> list[dict[str, Any]]:
    """Validate detections without clipping or silently repairing model output."""
    normalized: list[dict[str, Any]] = []
    for index, detection in enumerate(detections):
        if not isinstance(detection, dict):
            raise PredictionArtifactError(f"{image.image_id}: detection {index} is not an object")
        class_id = detection.get("classID")
        score = detection.get("score")
        xyxy = detection.get("xyxyPixels")
        if isinstance(class_id, bool) or not isinstance(class_id, int) or not 0 <= class_id < class_count:
            raise PredictionArtifactError(f"{image.image_id}: detection {index} has invalid class ID")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(float(score)) or not 0 <= float(score) <= 1:
            raise PredictionArtifactError(f"{image.image_id}: detection {index} has invalid score")
        if not isinstance(xyxy, (list, tuple)) or len(xyxy) != 4:
            raise PredictionArtifactError(f"{image.image_id}: detection {index} must have four xyxy pixel values")
        try:
            x1, y1, x2, y2 = [float(value) for value in xyxy]
        except (TypeError, ValueError) as exc:
            raise PredictionArtifactError(f"{image.image_id}: detection {index} has non-numeric coordinates") from exc
        if not all(math.isfinite(value) for value in (x1, y1, x2, y2)):
            raise PredictionArtifactError(f"{image.image_id}: detection {index} has non-finite coordinates")
        if not (0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height):
            raise PredictionArtifactError(f"{image.image_id}: detection {index} lies outside original image bounds")
        normalized.append({"classID": class_id, "score": float(score), "xyxyPixels": [x1, y1, x2, y2]})
    return normalized


def make_result(
    image: ResolvedImage,
    class_count: int,
    detections: Iterable[dict[str, Any]] | None = None,
    failure: dict[str, str] | None = None,
) -> dict[str, Any]:
    if failure is not None:
        if detections is not None:
            raise PredictionArtifactError(f"{image.image_id}: failed result cannot include detections")
        code = failure.get("code")
        message = failure.get("message")
        if not isinstance(code, str) or not code or not isinstance(message, str) or not message:
            raise PredictionArtifactError(f"{image.image_id}: failure requires code and message")
        return {
            "imageID": image.image_id,
            "width": image.width,
            "height": image.height,
            "imageSHA256": image.image_sha256,
            "labelSHA256": image.label_sha256,
            "status": "failed",
            "failure": {"code": code, "message": message},
            "detections": [],
        }
    normalized = normalize_detections(detections or [], image, class_count)
    return {
        "imageID": image.image_id,
        "width": image.width,
        "height": image.height,
        "imageSHA256": image.image_sha256,
        "labelSHA256": image.label_sha256,
        "status": "ok" if normalized else "empty",
        "detections": normalized,
    }


def build_artifact(
    request: PredictionRequest,
    checkpoint: Path,
    category_map: Path,
    category_map_version: str,
    settings: dict[str, Any],
    results: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    checkpoint = checkpoint.resolve(strict=False)
    category_map = category_map.resolve(strict=False)
    if not checkpoint.is_file():
        raise PredictionArtifactError("explicit checkpoint does not exist")
    if not category_map.is_file():
        raise PredictionArtifactError("category map does not exist")
    result_list = list(results)
    requested_ids = [image.image_id for image in request.images]
    result_ids = [entry.get("imageID") for entry in result_list]
    duplicates = sorted({entry for entry in result_ids if result_ids.count(entry) > 1})
    missing = [image_id for image_id in requested_ids if image_id not in result_ids]
    unexpected = [image_id for image_id in result_ids if image_id not in requested_ids]
    if duplicates or missing or unexpected or len(result_list) != len(requested_ids):
        raise PredictionArtifactError("result records must contain exactly one record for every requested image")
    return {
        "formatVersion": FORMAT_VERSION,
        "evaluatorVersion": EVALUATOR_VERSION,
        "corpus": {
            "corpusID": request.corpus_id,
            "inputManifestSHA256": request.manifest_sha256,
            "contentSHA256": request.content_sha256,
        },
        "model": {"checkpointFileName": checkpoint.name, "checkpointSHA256": sha256_file(checkpoint)},
        "categoryMap": {"version": category_map_version, "sha256": sha256_file(category_map)},
        "settings": settings,
        "settingsSHA256": canonical_sha256(settings),
        "completeness": {
            "requestedCount": len(requested_ids),
            "resultCount": len(result_ids),
            "requestedImageIDs": requested_ids,
            "missingImageIDs": missing,
            "duplicateImageIDs": duplicates,
            "unexpectedImageIDs": unexpected,
            "complete": not (duplicates or missing or unexpected) and len(result_list) == len(requested_ids),
        },
        "results": result_list,
    }


def ensure_new_output(output: Path, project_root: Path) -> Path:
    resolved = output.resolve(strict=False)
    root = project_root.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PredictionArtifactError("prediction output must stay inside the project") from exc
    if resolved.exists():
        raise PredictionArtifactError("prediction output already exists; refusing collision or stale reuse")
    return resolved


def write_artifact(output: Path, payload: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
