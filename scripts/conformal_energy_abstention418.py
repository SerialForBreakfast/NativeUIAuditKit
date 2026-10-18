"""T80 adapter: Helmholtz Free-Energy OOD Normalization and Split Conformal Abstention Calibration."""
from __future__ import annotations

import math
from collections import Counter
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"alpha", "temperature", "oodEnergyThreshold"},
        "conformal_parameters",
    )
    alpha = values["alpha"]
    temp = values["temperature"]
    ood_thr = values["oodEnergyThreshold"]
    q.require(
        isinstance(alpha, (int, float)) and not isinstance(alpha, bool) and math.isfinite(alpha) and 0.005 <= alpha <= 0.25,
        "conformal_alpha_range",
    )
    q.require(
        isinstance(temp, (int, float)) and not isinstance(temp, bool) and math.isfinite(temp) and 0.05 <= temp <= 5.0,
        "conformal_temperature_range",
    )
    q.require(
        isinstance(ood_thr, (int, float)) and not isinstance(ood_thr, bool) and math.isfinite(ood_thr) and -5.0 <= ood_thr <= 5.0,
        "conformal_ood_threshold_range",
    )
    return dict(alpha=float(alpha), temperature=float(temp), oodEnergyThreshold=float(ood_thr))


def logit_from_prob(probs: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    p_clip = np.clip(probs, eps, 1.0 - eps)
    return np.log(p_clip / (1.0 - p_clip))


def fit_conformal_quantile(nonconformity_scores: list[float], alpha: float = 0.05) -> float:
    q.require(len(nonconformity_scores) >= 4, "conformal_calibration_too_small")
    n = len(nonconformity_scores)
    level = min(1.0, math.ceil((n + 1) * (1.0 - alpha)) / n)
    return float(np.quantile(np.asarray(nonconformity_scores, dtype=np.float64), level, method="higher"))


def classify_screen_conformal_energy(
    scores: list[float],
    q_hat: float,
    temperature: float = 1.0,
    ood_energy_threshold: float = 0.0,
    null_logit: float = 1.7346,
) -> dict[str, object]:
    """Classifies a screen into verified_no_focus, certified_focus, ambiguous_competition, or suspected_missing_proposal_or_ood."""
    if not scores:
        return {
            "state": "verified_no_focus",
            "selectedIndex": None,
            "predictionSet": [],
            "bgEnergy": -10.0,
            "energyMargin": 0.0,
        }
    probs = np.asarray(scores, dtype=np.float64)
    q.require(np.all(np.isfinite(probs)) and np.all((probs >= 0.0) & (probs <= 1.0)), "conformal_invalid_scores")
    z = logit_from_prob(probs)
    bg_energy = float(np.median(z)) if len(z) > 1 else float(z[0])

    # Subtract positive OOD baseline shift when background median exceeds ood_energy_threshold
    drift_shift = max(0.0, bg_energy - ood_energy_threshold)
    z_centered = z - drift_shift

    scaled = np.concatenate([z_centered / temperature, np.array([null_logit / temperature])])
    scaled -= np.max(scaled)
    exp_s = np.exp(scaled)
    cal_probs = exp_s[:-1] / np.sum(exp_s)
    nonconf = 1.0 - cal_probs
    pred_set = [int(i) for i, nc in enumerate(nonconf) if nc <= q_hat]

    order = np.argsort(-z_centered)
    top_idx = int(order[0])
    top_z = float(z_centered[top_idx])
    rest_z = z_centered[order[1:]] if len(order) > 1 else np.array([null_logit])
    energy_margin = top_z - float(temperature * np.log(np.sum(np.exp(rest_z / temperature))))

    if len(pred_set) == 1 and top_z >= null_logit:
        state = "certified_focus"
        selected = pred_set[0]
    elif len(pred_set) >= 2:
        state = "ambiguous_competition"
        selected = None
    elif bg_energy > ood_energy_threshold:
        state = "suspected_missing_proposal_or_ood"
        selected = None
    else:
        state = "verified_no_focus"
        selected = None

    return {
        "state": state,
        "selectedIndex": selected,
        "predictionSet": pred_set,
        "bgEnergy": round(bg_energy, 5),
        "energyMargin": round(energy_margin, 5),
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    cal_doc = document(refs["calibrationReports"])
    eval_doc = document(refs["evaluationReports"])

    cal_groups = {r["group"] for r in cal_doc.get("rows", [])}
    eval_groups = {r["group"] for r in eval_doc.get("rows", [])}
    q.require(cal_groups and eval_groups and cal_groups.isdisjoint(eval_groups), "conformal_group_leakage")

    cal_nonconf = []
    for row in cal_doc["rows"]:
        scores = np.asarray(row["scores"], dtype=np.float64)
        z = logit_from_prob(scores)
        target_idx = row.get("focusedIndex")
        if target_idx is not None and 0 <= target_idx < len(z):
            scaled = np.concatenate([z / params["temperature"], np.array([1.7346 / params["temperature"]])])
            scaled -= np.max(scaled)
            exp_s = np.exp(scaled)
            p_target = exp_s[target_idx] / np.sum(exp_s)
            cal_nonconf.append(float(1.0 - p_target))
        else:
            cal_nonconf.append(0.10)

    q_hat = fit_conformal_quantile(cal_nonconf, alpha=params["alpha"])
    eval_rows = []
    for row in eval_doc["rows"]:
        res = classify_screen_conformal_energy(
            row["scores"],
            q_hat=q_hat,
            temperature=params["temperature"],
            ood_energy_threshold=params["oodEnergyThreshold"],
        )
        res["id"] = row["id"]
        res["group"] = row["group"]
        eval_rows.append(res)

    state_counts = Counter(r["state"] for r in eval_rows)
    result = {
        "version": "conformal-energy-abstention-v1",
        "parameters": params,
        "conformalQuantile": round(q_hat, 6),
        "stateCounts": dict(state_counts),
        "rows": eval_rows,
        "inputs": refs,
        "modelAccepted": False,
    }
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
