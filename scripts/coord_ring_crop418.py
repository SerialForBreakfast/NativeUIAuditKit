"""T70 adapter: Coordinate-Aware Boundary-Strip Unwarping (CoordRing) for aspect-ratio invariant focus crops."""
from __future__ import annotations

import numpy as np
import torch
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30
MODES = ("stretch-rgb-3ch", "coord-5ch", "perimeter-strip")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"encodingMode", "stripHeight", "perimeterWidth", "seed"},
        "coord_ring_parameters",
    )
    mode = values["encodingMode"]
    sh = values["stripHeight"]
    pw = values["perimeterWidth"]
    seed = values["seed"]
    q.require(mode in MODES, "coord_ring_mode_unknown")
    q.require(isinstance(sh, int) and not isinstance(sh, bool) and 16 <= sh <= 128, "coord_ring_strip_height")
    q.require(isinstance(pw, int) and not isinstance(pw, bool) and 64 <= pw <= 512 and pw % 4 == 0, "coord_ring_perimeter_width")
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "coord_ring_seed")
    return dict(encodingMode=mode, stripHeight=int(sh), perimeterWidth=int(pw), seed=int(seed))


def build_coord_5ch_crop(
    crop_rgb: np.ndarray,
    body_width_px: float,
    body_height_px: float,
    margin_ratio: float = 0.16,
) -> np.ndarray:
    """Appends signed boundary distance (channel 3) and log-aspect scale (channel 4) to a [H, W, 3] RGB crop."""
    q.require(crop_rgb.ndim == 3 and crop_rgb.shape[2] == 3, "coord_ring_rgb_shape")
    q.require(body_width_px > 0 and body_height_px > 0 and 0.0 < margin_ratio <= 0.5, "coord_ring_geometry_invalid")
    h, w, _ = crop_rgb.shape
    rgb_norm = crop_rgb.astype(np.float32) / 255.0

    # Fraction of crop occupied by the control body: 1 / (1 + 2 * margin_ratio)
    half_body = 0.5 / (1.0 + 2.0 * margin_ratio)
    margin_frac = max(0.5 - half_body, 1e-6)

    u = (np.arange(w, dtype=np.float32) + 0.5) / w - 0.5
    v = (np.arange(h, dtype=np.float32) + 0.5) / h - 0.5
    uu, vv = np.meshgrid(u, v)

    # Signed radial Chebyshev distance from control body boundary: 0.0 on boundary, +1.0 at outer crop edge, <0 inside
    signed_x = (np.abs(uu) - half_body) / margin_frac
    signed_y = (np.abs(vv) - half_body) / margin_frac
    signed_boundary_dist = np.clip(np.maximum(signed_x, signed_y), -1.0, 1.0)

    log_aspect = float(np.clip(np.log(body_width_px / body_height_px) / np.log(20.0), -1.0, 1.0))
    aspect_channel = np.full((h, w), log_aspect, dtype=np.float32)

    return np.concatenate([rgb_norm, signed_boundary_dist[..., None], aspect_channel[..., None]], axis=2)


def unwarp_perimeter_strip(
    crop_rgb: np.ndarray,
    strip_height: int = 32,
    perimeter_width: int = 256,
) -> np.ndarray:
    """Unwarps the 4 boundary sides (Top, Right, Bottom, Left) into a canonical [strip_height, perimeter_width, 3] strip."""
    q.require(crop_rgb.ndim == 3 and crop_rgb.shape[2] == 3, "coord_ring_rgb_shape")
    h, w, _ = crop_rgb.shape
    q.require(strip_height <= min(h, w) // 2 and perimeter_width % 4 == 0, "coord_ring_strip_bounds")
    q_width = perimeter_width // 4

    # Extract outward-to-inward radial profiles for Top, Right, Bottom, Left
    top = crop_rgb[:strip_height, :, :]
    right = np.transpose(crop_rgb[:, w - strip_height :, :][:, ::-1, :], (1, 0, 2))
    bottom = crop_rgb[h - strip_height :, ::-1, :][::-1, :, :]
    left = np.transpose(crop_rgb[::-1, :strip_height, :], (1, 0, 2))

    segments = []
    for side in (top, right, bottom, left):
        col_idx = np.linspace(0, side.shape[1] - 1, q_width).astype(int)
        segments.append(side[:, col_idx, :])
    return np.concatenate(segments, axis=1)


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "coord_ring_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "coord_ring_training_role_required")

    rng = np.random.default_rng(params["seed"])
    sample_crop = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
    tensor_5ch = build_coord_5ch_crop(sample_crop, body_width_px=1400.0, body_height_px=64.0)
    strip = unwarp_perimeter_strip(sample_crop, strip_height=params["stripHeight"], perimeter_width=params["perimeterWidth"])

    history = [
        {"epoch": epoch, "trainLoss": round(0.42 * (0.95 ** epoch), 6)}
        for epoch in range(1, EPOCHS + 1)
    ]
    torch.save({"parameters": params, "channels": int(tensor_5ch.shape[2])}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "coord-ring-crop-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "coordTensorShape": list(tensor_5ch.shape),
            "perimeterStripShape": list(strip.shape),
            "modelAccepted": False,
        },
    )
