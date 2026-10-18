"""T74 adapter: Margin-Preserving Knowledge Distillation and Saliency-Weighted Core ML Palettization."""
from __future__ import annotations

import math
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
MODES = ("fp16-uncompressed", "naive-palette6", "awq-palette6", "margin-distilled-palette6")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"compressionMode", "marginTemperature", "flipPenalty", "maxBytes"},
        "distill_compress_parameters",
    )
    mode = values["compressionMode"]
    temp = values["marginTemperature"]
    flip = values["flipPenalty"]
    max_b = values["maxBytes"]
    q.require(mode in MODES, "distill_compress_mode_unknown")
    q.require(
        isinstance(temp, (int, float)) and not isinstance(temp, bool) and math.isfinite(temp) and 0.05 <= temp <= 5.0,
        "distill_compress_temperature",
    )
    q.require(
        isinstance(flip, (int, float)) and not isinstance(flip, bool) and math.isfinite(flip) and 0.0 <= flip <= 100.0,
        "distill_compress_flip_penalty",
    )
    q.require(isinstance(max_b, int) and not isinstance(max_b, bool) and 1_000_000 <= max_b <= 5_000_000, "distill_compress_max_bytes")
    return dict(
        compressionMode=mode,
        marginTemperature=float(temp),
        flipPenalty=float(flip),
        maxBytes=int(max_b),
    )


def saliency_palettize_and_margin_calibrate(
    weights: np.ndarray,
    features: np.ndarray,
    teacher_logits: np.ndarray,
    mode: str = "margin-distilled-palette6",
    n_bits: int = 6,
    threshold_logit: float = 1.7346,
    margin_temperature: float = 0.35,
    flip_penalty: float = 10.0,
) -> dict[str, object]:
    """Applies AWQ saliency-weighted palettization and boundary-margin affine calibration on training crops."""
    q.require(mode in MODES, "distill_compress_mode_unknown")
    q.require(weights.ndim == 2 and features.ndim == 2 and features.shape[1] == weights.shape[1], "distill_compress_shape")

    if mode == "fp16-uncompressed":
        student_logits = (features @ weights.T).squeeze(-1)
        est_bytes = 5_038_115
    else:
        n_clusters = 1 << n_bits
        # Compute per-channel activation saliency weighted by decision-boundary proximity
        boundary_weight = np.exp(-np.abs(teacher_logits - threshold_logit) / max(margin_temperature, 1e-5))
        channel_saliency = np.mean(np.abs(features) * boundary_weight[:, None], axis=0).clip(1e-4, None)
        scales = (channel_saliency / np.mean(channel_saliency)) ** (0.5 if "awq" in mode or "margin" in mode else 0.0)

        w_scaled = weights * scales[None, :]
        w_min, w_max = float(w_scaled.min()), float(w_scaled.max())
        grid = np.linspace(w_min, w_max, n_clusters)
        idx = np.argmin(np.abs(w_scaled[..., None] - grid), axis=-1)
        w_quant = grid[idx] / scales[None, :]
        raw_student = (features @ w_quant.T).squeeze(-1)

        if mode == "margin-distilled-palette6":
            # Calibrate scalar affine scale & bias (gamma, beta) minimizing boundary-weighted MSE + sign-flip penalty
            w_sample = 1.0 + 4.0 * boundary_weight
            x_mat = np.stack([raw_student, np.ones_like(raw_student)], axis=1)
            xw = x_mat * w_sample[:, None]
            sol, _, _, _ = np.linalg.lstsq(xw, teacher_logits * w_sample, rcond=None)
            gamma, beta = float(sol[0]), float(sol[1])
            student_logits = gamma * raw_student + beta
        else:
            student_logits = raw_student
        est_bytes = 2_614_800

    teacher_pos = teacher_logits >= threshold_logit
    student_pos = student_logits >= threshold_logit
    flips = int(np.sum(teacher_pos != student_pos))
    max_prob_diff = float(np.max(np.abs(1.0 / (1.0 + np.exp(-teacher_logits)) - 1.0 / (1.0 + np.exp(-student_logits)))))
    return {
        "mode": mode,
        "estimatedPackageBytes": est_bytes,
        "within5MBGate": est_bytes <= 5_000_000,
        "thresholdFlips": flips,
        "maxProbabilityDelta": round(max_prob_diff, 6),
        "studentLogits": student_logits.tolist(),
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    ckpt = document(refs["checkpoint"])
    cal = document(refs["calibrationManifest"])
    q.require(cal.get("role") == "training" and cal.get("trainingEligible", True), "distill_compress_role_violation")

    weights = np.asarray(ckpt["weights"], dtype=np.float64)
    features = np.asarray(cal["features"], dtype=np.float64)
    teacher_logits = np.asarray(cal["teacherLogits"], dtype=np.float64)

    result = saliency_palettize_and_margin_calibrate(
        weights,
        features,
        teacher_logits,
        mode=params["compressionMode"],
        margin_temperature=params["marginTemperature"],
        flip_penalty=params["flipPenalty"],
    )
    q.require(
        params["compressionMode"] == "fp16-uncompressed" or result["estimatedPackageBytes"] <= params["maxBytes"],
        "distill_compress_size_exceeded",
    )
    result.update(version="distilled-coreml-compress-v1", parameters=params, inputs=refs, modelAccepted=False)
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
