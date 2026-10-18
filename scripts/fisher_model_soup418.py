"""T86 adapter: Fisher-Weighted Model Soups and BatchNorm Recalibration (FisherSoup, PM08)."""
from __future__ import annotations

import torch
import torch.nn as nn
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
MODES = ("single-checkpoint", "uniform-soup-bn", "fisher-soup-bn")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"mergeMode", "recalibrateBn"},
        "fisher_soup_parameters",
    )
    mode = values["mergeMode"]
    recal = values["recalibrateBn"]
    q.require(mode in MODES, "fisher_soup_mode_unknown")
    q.require(isinstance(recal, bool), "fisher_soup_recalibrate_bool")
    return dict(mergeMode=mode, recalibrateBn=bool(recal))


@torch.no_grad()
def merge_checkpoints_fisher(
    state_dicts: list[dict[str, torch.Tensor]],
    fishers: list[dict[str, torch.Tensor]],
    lambdas: list[float],
    mode: str = "fisher-soup-bn",
) -> dict[str, torch.Tensor]:
    """Merges compatible state_dicts coordinate-wise weighted by lambda_m * F_k^(m) or uniform soup weights."""
    q.require(mode in MODES, "fisher_soup_mode_unknown")
    q.require(
        len(state_dicts) == len(fishers) == len(lambdas) and len(state_dicts) >= 2,
        "fisher_soup_length_mismatch",
    )
    keys0 = set(state_dicts[0].keys())
    for sd in state_dicts[1:]:
        q.require(set(sd.keys()) == keys0, "fisher_soup_incompatible_keys")
        for k in keys0:
            q.require(sd[k].shape == state_dicts[0][k].shape, f"fisher_soup_shape_mismatch:{k}")

    if mode == "single-checkpoint":
        return {k: v.clone() for k, v in state_dicts[0].items()}

    merged: dict[str, torch.Tensor] = {}
    for key in state_dicts[0]:
        t0 = state_dicts[0][key]
        if not t0.is_floating_point():
            merged[key] = t0.clone()
            continue
        if mode == "fisher-soup-bn" and key in fishers[0]:
            num = torch.zeros_like(t0, dtype=torch.float32)
            den = torch.zeros_like(t0, dtype=torch.float32)
            for sd, fi, lam in zip(state_dicts, fishers, lambdas):
                weight = float(lam) * fi[key].to(t0.device, dtype=torch.float32).clamp_min(1e-12)
                num += weight * sd[key].to(t0.device, dtype=torch.float32)
                den += weight
            merged[key] = (num / den.clamp_min(1e-12)).to(dtype=t0.dtype)
        else:
            total_lam = max(sum(float(l) for l in lambdas), 1e-12)
            acc = sum(float(lam) * sd[key].to(dtype=torch.float32) for sd, lam in zip(state_dicts, lambdas)) / total_lam
            merged[key] = acc.to(dtype=t0.dtype)
    return merged


@torch.no_grad()
def recalibrate_batchnorm_tensors(
    training_batches: list[torch.Tensor],
    bn_module: nn.BatchNorm1d,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Recomputes exact cumulative BatchNorm running_mean and running_var on training-only batches."""
    q.require(len(training_batches) >= 1, "fisher_soup_bn_empty")
    bn_module.reset_running_stats()
    bn_module.momentum = None
    bn_module.train()
    for batch in training_batches:
        bn_module(batch)
    bn_module.eval()
    return bn_module.running_mean.clone(), bn_module.running_var.clone()


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    ckpts_doc = document(refs["checkpoints"])
    train_doc = document(refs["trainingManifests"])

    q.require(
        train_doc.get("role") == "training" and train_doc.get("trainingEligible", True),
        "fisher_soup_role_violation",
    )
    models = ckpts_doc.get("models", [])
    q.require(len(models) >= 2, "fisher_soup_need_two_models")
    inits = {m.get("initialization") for m in models}
    q.require(len(inits) == 1, "fisher_soup_initialization_mismatch")

    state_dicts = [{"w": torch.tensor(m["weights"], dtype=torch.float32)} for m in models]
    fishers = [{"w": torch.tensor(m["fisher"], dtype=torch.float32)} for m in models]
    lambdas = [float(m.get("lambda", 1.0)) for m in models]

    merged = merge_checkpoints_fisher(state_dicts, fishers, lambdas, mode=params["mergeMode"])
    bn = nn.BatchNorm1d(merged["w"].numel())
    if params["recalibrateBn"]:
        train_x = [torch.tensor(train_doc["features"], dtype=torch.float32)]
        rmean, rvar = recalibrate_batchnorm_tensors(train_x, bn)
    else:
        rmean, rvar = bn.running_mean, bn.running_var

    result = {
        "version": "fisher-model-soup-v1",
        "parameters": params,
        "mergedWeights": [round(float(v), 6) for v in merged["w"].tolist()],
        "bnRunningMean": [round(float(v), 6) for v in rmean.tolist()],
        "bnRunningVar": [round(float(v), 6) for v in rvar.tolist()],
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
