#!/usr/bin/env python3
"""Side-effect-free candidate configuration and corpus readiness validation."""
from __future__ import annotations
import hashlib, json
import struct
import zlib
from pathlib import Path

class PreflightError(ValueError): pass

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _png_dimensions(path: Path) -> tuple[int, int]:
    try:
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError
        offset, width, height, bit_depth, color_type, interlace = 8, 0, 0, 0, 0, 0
        idat, seen_ihdr, seen_iend = bytearray(), False, False
        while offset < len(data):
            if offset + 12 > len(data):
                raise ValueError
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            end = offset + 12 + length
            if end > len(data):
                raise ValueError
            payload = data[offset + 8:offset + 8 + length]
            expected_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
            if zlib.crc32(kind + payload) & 0xffffffff != expected_crc:
                raise ValueError
            if kind == b"IHDR":
                if seen_ihdr or length != 13:
                    raise ValueError
                width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", payload)
                seen_ihdr = True
            elif kind == b"IDAT":
                idat.extend(payload)
            elif kind == b"IEND":
                if length != 0 or end != len(data):
                    raise ValueError
                seen_iend = True
                break
            offset = end
        channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
        if not seen_ihdr or not seen_iend or width <= 0 or height <= 0 or not idat:
            raise ValueError
        if channels is None or bit_depth not in (1, 2, 4, 8, 16) or interlace != 0:
            raise PreflightError("unsupported_pixel_format")
        row_bytes = (width * channels * bit_depth + 7) // 8
        pixels = zlib.decompress(bytes(idat))
        if len(pixels) != height * (row_bytes + 1):
            raise ValueError
    except PreflightError:
        raise
    except (OSError, struct.error, ValueError, zlib.error) as error:
        raise PreflightError("corrupt_pixel") from error
    return width, height

def _split_paths(dataset: Path, split: str) -> tuple[Path, Path]:
    canonical = (dataset / "images" / split, dataset / "labels" / split)
    exported = (dataset / split / "images", dataset / split / "labels")
    if canonical[0].is_dir() or canonical[1].is_dir():
        return canonical
    if exported[0].is_dir() or exported[1].is_dir():
        return exported
    return canonical

def validate(dataset: Path, initial_weights: Path | None, resume: Path | None, output: Path, taxonomy: Path) -> dict:
    if initial_weights and resume: raise PreflightError("initial_weights_and_resume_conflict")
    if output.exists(): raise PreflightError("output_collision")
    if not taxonomy.is_file(): raise PreflightError("missing_taxonomy")
    if not dataset.is_dir() or not (dataset / "dataset.yaml").is_file(): raise PreflightError("missing_dataset_config")
    required = ("train", "val", "test")
    counts = {}
    for split in required:
        images, labels = _split_paths(dataset, split)
        if not images.is_dir() or not labels.is_dir(): raise PreflightError("missing_split")
        pngs = sorted(images.glob("*.png"))
        if not pngs: raise PreflightError("ineligible_corpus")
        if any(not (labels / (p.stem + ".txt")).is_file() for p in pngs): raise PreflightError("missing_label")
        for png in pngs:
            if not png.is_file(): raise PreflightError("missing_pixel")
            _png_dimensions(png)
        counts[split] = len(pngs)
    selected = resume or initial_weights
    if selected is None or not selected.is_file() or selected.suffix != ".pt": raise PreflightError("stale_or_missing_weights")
    return {"configurationValid": True, "launchEligible": False, "reason": "P5-A validates configuration only; P5-B binds eligible real corpora.", "mode": "resume" if resume else "fresh", "dataset": str(dataset), "datasetYamlSHA256": sha(dataset / "dataset.yaml"), "taxonomySHA256": sha(taxonomy), "weightsSHA256": sha(selected), "splitCounts": counts, "epochs": 150, "scheduler": "cosine", "seed": 42, "output": str(output)}
