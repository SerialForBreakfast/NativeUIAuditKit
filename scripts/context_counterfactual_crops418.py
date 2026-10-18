"""T83 adapter: Scale-Preserving Concentric Zone Counterfactual Crop Attribution (ContextSwap, B405-198)."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
MODES = ("original-crop", "ctx-harmonic-neutral", "ctx-transplant", "interior-neutral")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"interventionMode", "haloOuterPx", "bodyInnerInsetPx"},
        "context_crop_parameters",
    )
    mode = values["interventionMode"]
    halo_px = values["haloOuterPx"]
    body_px = values["bodyInnerInsetPx"]
    q.require(mode in MODES, "context_crop_mode_unknown")
    q.require(isinstance(halo_px, int) and not isinstance(halo_px, bool) and 8 <= halo_px <= 48, "context_crop_halo_px")
    q.require(isinstance(body_px, int) and not isinstance(body_px, bool) and halo_px + 4 <= body_px <= 96, "context_crop_body_px")
    return dict(interventionMode=mode, haloOuterPx=int(halo_px), bodyInnerInsetPx=int(body_px))


def apply_concentric_intervention(
    crop_rgb: np.ndarray,
    mode: str,
    halo_outer_px: int = 23,
    body_inner_inset_px: int = 41,
    donor_rgb: np.ndarray | None = None,
) -> np.ndarray:
    """Applies a scale-preserving intervention to Z_ctx or Z_in while keeping Z_halo bit-identical."""
    q.require(crop_rgb.ndim == 3 and crop_rgb.shape[2] == 3 and crop_rgb.dtype == np.uint8, "context_crop_rgb_shape")
    h, w, _ = crop_rgb.shape
    q.require(h == w and h >= 64 and 0 < halo_outer_px < body_inner_inset_px < h // 2, "context_crop_bounds")
    q.require(mode in MODES, "context_crop_mode_unknown")

    out = crop_rgb.copy()
    h0, h1 = halo_outer_px, h - halo_outer_px
    b0, b1 = body_inner_inset_px, h - body_inner_inset_px

    if mode == "original-crop":
        return out
    if mode == "ctx-harmonic-neutral":
        clamped = out.astype(np.float32)
        clamped[:h0, h0:h1] = clamped[h0 : h0 + 1, h0:h1]
        clamped[h1:, h0:h1] = clamped[h1 - 1 : h1, h0:h1]
        clamped[:, :h0] = clamped[:, h0 : h0 + 1]
        clamped[:, h1:] = clamped[:, h1 - 1 : h1]
        smoothed = gaussian_filter(clamped, sigma=(4.0, 4.0, 0.0))
        out[:] = np.clip(np.rint(smoothed), 0, 255).astype(np.uint8)
        out[h0:h1, h0:h1] = crop_rgb[h0:h1, h0:h1]
        return out
    if mode == "ctx-transplant":
        q.require(donor_rgb is not None and donor_rgb.shape == crop_rgb.shape and donor_rgb.dtype == np.uint8, "context_crop_donor_invalid")
        out[:] = donor_rgb
        out[h0:h1, h0:h1] = crop_rgb[h0:h1, h0:h1]
        return out
    if mode == "interior-neutral":
        mean_color = np.rint(crop_rgb[b0:b1, b0:b1].mean(axis=(0, 1))).astype(np.uint8)
        out[b0:b1, b0:b1] = mean_color
        return out
    raise ValueError(f"Unsupported mode: {mode}")


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    manifest = document(refs["cropsManifest"])
    rows = manifest.get("rows", [])
    q.require(rows and all(r.get("role") == "development" and not r.get("trainingEligible", False) for r in rows), "context_crop_role_violation")

    h0 = params["haloOuterPx"]
    b0 = params["bodyInnerInsetPx"]
    results = []
    for row in rows:
        size = int(row.get("size", 256))
        h1, b1 = size - h0, size - b0
        crop = np.full((size, size, 3), int(row.get("interiorLuma", 80)), dtype=np.uint8)
        crop[:h0, :] = int(row.get("contextLuma", 220))
        crop[h1:, :] = int(row.get("contextLuma", 220))
        crop[:, :h0] = int(row.get("contextLuma", 220))
        crop[:, h1:] = int(row.get("contextLuma", 220))
        crop[h0:h1, h0:h1] = int(row.get("haloLuma", 240))
        crop[b0:b1, b0:b1] = int(row.get("interiorLuma", 80))

        donor = np.full_like(crop, int(row.get("donorLuma", 40)))
        transformed = apply_concentric_intervention(
            crop,
            mode=params["interventionMode"],
            halo_outer_px=h0,
            body_inner_inset_px=b0,
            donor_rgb=donor,
        )
        # Verify halo zone is 100% bit-identical
        halo_preserved = bool(
            np.array_equal(transformed[h0:b0, h0:h1], crop[h0:b0, h0:h1])
            and np.array_equal(transformed[b1:h1, h0:h1], crop[b1:h1, h0:h1])
        )
        q.require(halo_preserved, "context_crop_halo_corrupted")
        results.append({
            "id": row["id"],
            "haloPreserved": halo_preserved,
            "outerContextMean": round(float(transformed[:h0, :].mean()), 3),
            "interiorMean": round(float(transformed[b0:b1, b0:b1].mean()), 3),
        })

    summary = {
        "version": "context-counterfactual-crops-v1",
        "parameters": params,
        "rows": results,
        "inputs": refs,
        "modelAccepted": False,
    }
    q.save(OUT / "benchmark_summary.json", summary)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
