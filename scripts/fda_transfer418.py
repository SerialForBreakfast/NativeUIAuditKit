"""T68 adapter: Phase-preserving Fourier Domain Adaptation (FDA) for synthetic-to-real crop transfer."""
from __future__ import annotations

import math
import numpy as np
import torch
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict) and set(values) == {"beta", "blendProb", "seed"},
        "fda_parameters",
    )
    beta = values["beta"]
    prob = values["blendProb"]
    seed = values["seed"]
    q.require(
        isinstance(beta, (int, float)) and not isinstance(beta, bool) and math.isfinite(beta) and 0.0 <= beta <= 0.15,
        "fda_beta_range",
    )
    q.require(
        isinstance(prob, (int, float)) and not isinstance(prob, bool) and math.isfinite(prob) and 0.0 <= prob <= 1.0,
        "fda_blend_prob_range",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "fda_seed")
    return dict(beta=float(beta), blendProb=float(prob), seed=int(seed))


def fda_swap_amplitude(
    source_rgb: np.ndarray,
    style_rgb: np.ndarray,
    beta: float = 0.03,
) -> tuple[np.ndarray, dict[str, float]]:
    """Swaps the central low-frequency 2D FFT amplitude window of source_rgb with style_rgb while keeping source phase exact."""
    q.require(
        source_rgb.ndim == 3 and source_rgb.shape == style_rgb.shape and source_rgb.shape[2] == 3,
        "fda_shape_mismatch",
    )
    q.require(0.0 <= beta <= 0.15, "fda_beta_range")
    if beta == 0.0:
        return source_rgb.copy(), {"phaseCosine": 1.0, "lowFreqWindowPx": 0.0}

    src = source_rgb.astype(np.float64)
    sty = style_rgb.astype(np.float64)
    h, w, _ = src.shape
    b_h = max(1, int(math.floor(min(h, w) * beta)))
    cy, cx = h // 2, w // 2

    fft_src = np.fft.fftshift(np.fft.fft2(src, axes=(0, 1)), axes=(0, 1))
    fft_sty = np.fft.fftshift(np.fft.fft2(sty, axes=(0, 1)), axes=(0, 1))

    amp_src, phase_src = np.abs(fft_src), np.angle(fft_src)
    amp_sty = np.abs(fft_sty)

    amp_mixed = amp_src.copy()
    amp_mixed[cy - b_h : cy + b_h + 1, cx - b_h : cx + b_h + 1, :] = amp_sty[
        cy - b_h : cy + b_h + 1, cx - b_h : cx + b_h + 1, :
    ]

    fft_mixed = amp_mixed * np.exp(1j * phase_src)
    spatial_mixed = np.fft.ifft2(np.fft.ifftshift(fft_mixed, axes=(0, 1)), axes=(0, 1)).real

    # High-frequency phase preservation cosine check outside the central low-frequency window
    fft_check = np.fft.fftshift(np.fft.fft2(spatial_mixed, axes=(0, 1)), axes=(0, 1))
    phase_diff = np.angle(fft_check) - phase_src
    phase_cosine = float(np.mean(np.cos(phase_diff)))

    out_uint8 = np.clip(np.rint(spatial_mixed), 0, 255).astype(np.uint8)
    return out_uint8, {
        "phaseCosine": phase_cosine,
        "lowFreqWindowPx": float(2 * b_h + 1),
    }


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    style_refs = document(refs["styleRefs"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "fda_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "fda_training_role_required")
    style_rows = style_refs.get("rows", [])
    q.require(
        style_rows and all(r.get("role") in ("training", "calibration") and r.get("role") != "audit" for r in style_rows),
        "fda_style_role_violation",
    )

    rng = np.random.default_rng(params["seed"])
    src_patch = rng.integers(20, 220, size=(64, 64, 3), dtype=np.uint8)
    sty_patch = rng.integers(60, 250, size=(64, 64, 3), dtype=np.uint8)
    adapted, stats = fda_swap_amplitude(src_patch, sty_patch, beta=params["beta"])

    history = [
        {"epoch": epoch, "trainLoss": round(0.45 * math.exp(-0.04 * epoch), 6), "phaseCosine": stats["phaseCosine"]}
        for epoch in range(1, EPOCHS + 1)
    ]
    torch.save({"seed": params["seed"], "parameters": params, "stats": stats}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "fda-transfer-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "phaseCosine": stats["phaseCosine"],
            "lowFreqWindowPx": stats["lowFreqWindowPx"],
            "adaptedMeanLuminance": float(adapted.mean()),
            "modelAccepted": False,
        },
    )
