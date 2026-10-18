"""T75 adapter: Kinematic Phase-Correlation Scroll Registration and Action-Cone Transition Decoding."""
from __future__ import annotations

import math
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
DIRECTIONS = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"scrollPhaseThreshold", "coneHalfAngleDeg"},
        "kinematic_parameters",
    )
    thr = values["scrollPhaseThreshold"]
    angle = values["coneHalfAngleDeg"]
    q.require(
        isinstance(thr, (int, float)) and not isinstance(thr, bool) and math.isfinite(thr) and 2.0 <= thr <= 100.0,
        "kinematic_scroll_threshold",
    )
    q.require(
        isinstance(angle, (int, float)) and not isinstance(angle, bool) and math.isfinite(angle) and 10.0 <= angle <= 85.0,
        "kinematic_cone_angle",
    )
    return dict(scrollPhaseThreshold=float(thr), coneHalfAngleDeg=float(angle))


def estimate_fft_phase_scroll(before_luma: np.ndarray, after_luma: np.ndarray, eps: float = 1e-8) -> dict[str, float]:
    """Estimates 2D viewport translation (dx, dy) between before_luma and after_luma using Hann-windowed FFT phase correlation."""
    q.require(before_luma.ndim == 2 and before_luma.shape == after_luma.shape, "kinematic_luma_shape")
    h, w = before_luma.shape
    win_y = np.hanning(h)[:, None]
    win_x = np.hanning(w)[None, :]
    window = win_y * win_x

    f1 = np.fft.fft2((before_luma.astype(np.float64) - np.mean(before_luma)) * window)
    f2 = np.fft.fft2((after_luma.astype(np.float64) - np.mean(after_luma)) * window)
    cross_power = (f1 * np.conj(f2)) / (np.abs(f1 * np.conj(f2)) + eps)
    corr = np.fft.fftshift(np.abs(np.fft.ifft2(cross_power)))

    peak_y, peak_x = np.unravel_index(int(np.argmax(corr)), corr.shape)
    cy, cx = h // 2, w // 2
    dy = float(cy - peak_y)
    dx = float(cx - peak_x)
    return {"dxScroll": dx, "dyScroll": dy, "peakCorrelation": float(corr[peak_y, peak_x])}


def classify_kinematic_transition(
    action: str,
    before_focus_xy: tuple[float, float],
    after_focus_xy: tuple[float, float],
    scroll_dx_dy: tuple[float, float],
    scroll_threshold_px: float = 8.0,
    cone_half_angle_deg: float = 45.0,
) -> dict[str, object]:
    """Classifies a before/after remote action into focus_moved, viewport_scrolled, boundary_noop, or invalid_direction."""
    action_key = action.lower()
    q.require(action_key in DIRECTIONS, "kinematic_action_unknown")
    ux, uy = DIRECTIONS[action_key]

    bx, by = before_focus_xy
    ax, ay = after_focus_xy
    sdx, sdy = scroll_dx_dy

    # Screen-space displacement and scroll-compensated content-space displacement
    screen_dx, screen_dy = ax - bx, ay - by
    content_dx, content_dy = screen_dx - sdx, screen_dy - sdy

    screen_mag = math.hypot(screen_dx, screen_dy)
    scroll_mag = math.hypot(sdx, sdy)
    content_mag = math.hypot(content_dx, content_dy)

    cos_limit = math.cos(math.radians(cone_half_angle_deg))
    if content_mag < scroll_threshold_px and scroll_mag < scroll_threshold_px:
        return {
            "transitionState": "boundary_noop_or_background_anim",
            "directionConsistent": True,
            "screenStepPx": round(screen_mag, 3),
            "scrollStepPx": round(scroll_mag, 3),
            "contentStepPx": round(content_mag, 3),
        }

    cosine = (content_dx * ux + content_dy * uy) / max(content_mag, 1e-6)
    consistent = cosine >= cos_limit
    if scroll_mag >= scroll_threshold_px and screen_mag < scroll_threshold_px:
        state = "viewport_scrolled_focus_stationary" if consistent else "unexpected_scroll_direction"
    elif consistent:
        state = "focus_moved"
    else:
        state = "invalid_direction_jump"

    return {
        "transitionState": state,
        "directionConsistent": bool(consistent),
        "cosineAlignment": round(cosine, 4),
        "screenStepPx": round(screen_mag, 3),
        "scrollStepPx": round(scroll_mag, 3),
        "contentStepPx": round(content_mag, 3),
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    manifest = document(refs["pairsManifest"])
    pairs = manifest.get("pairs", [])
    q.require(isinstance(pairs, list) and len(pairs) > 0, "kinematic_pairs_empty")

    rows = []
    for item in pairs:
        res = classify_kinematic_transition(
            item["action"],
            tuple(item["beforeFocusXY"]),
            tuple(item["afterFocusXY"]),
            tuple(item.get("scrollDxDy", [0.0, 0.0])),
            scroll_threshold_px=params["scrollPhaseThreshold"],
            cone_half_angle_deg=params["coneHalfAngleDeg"],
        )
        res["id"] = item["id"]
        rows.append(res)

    summary = {
        "version": "kinematic-transition-v1",
        "parameters": params,
        "pairs": len(rows),
        "rows": rows,
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
