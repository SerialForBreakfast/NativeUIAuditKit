#!/usr/bin/env python3
"""Side-effect-free candidate configuration and corpus readiness validation."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

class PreflightError(ValueError): pass

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(dataset: Path, initial_weights: Path | None, resume: Path | None, output: Path, taxonomy: Path) -> dict:
    if initial_weights and resume: raise PreflightError("initial_weights_and_resume_conflict")
    if output.exists(): raise PreflightError("output_collision")
    if not taxonomy.is_file(): raise PreflightError("missing_taxonomy")
    if not dataset.is_dir() or not (dataset / "dataset.yaml").is_file(): raise PreflightError("missing_dataset_config")
    required = ("train", "val", "test")
    counts = {}
    for split in required:
        images = dataset / "images" / split
        labels = dataset / "labels" / split
        if not images.is_dir() or not labels.is_dir(): raise PreflightError("missing_split")
        pngs = sorted(images.glob("*.png"))
        if not pngs: raise PreflightError("ineligible_corpus")
        if any(not (labels / (p.stem + ".txt")).is_file() for p in pngs): raise PreflightError("missing_label")
        if any(not p.is_file() for p in pngs): raise PreflightError("missing_pixel")
        counts[split] = len(pngs)
    selected = resume or initial_weights
    if selected is None or not selected.is_file() or selected.suffix != ".pt": raise PreflightError("stale_or_missing_weights")
    return {"configurationValid": True, "launchEligible": False, "reason": "P5-A validates configuration only; P5-B binds eligible real corpora.", "mode": "resume" if resume else "fresh", "dataset": str(dataset), "datasetYamlSHA256": sha(dataset / "dataset.yaml"), "taxonomySHA256": sha(taxonomy), "weightsSHA256": sha(selected), "splitCounts": counts, "epochs": 150, "scheduler": "cosine", "seed": 42, "output": str(output)}
