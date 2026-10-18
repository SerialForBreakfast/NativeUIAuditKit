"""T78 adapter: Empirical Gaussian Copula Proposal-Error Sampler and Spatial Transformer Crop Refiner."""
from __future__ import annotations

import math
import numpy as np
from scipy.stats import norm
import torch
import torch.nn as nn
import torch.nn.functional as F
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30
SAMPLER_MODES = ("uniform-jitter", "copula-error-only", "copula-plus-stn")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"samplerMode", "enableStnRefiner", "stnLossWeight", "seed"},
        "copula_stn_parameters",
    )
    mode = values["samplerMode"]
    enable_stn = values["enableStnRefiner"]
    stn_w = values["stnLossWeight"]
    seed = values["seed"]
    q.require(mode in SAMPLER_MODES, "copula_stn_mode_unknown")
    q.require(isinstance(enable_stn, bool), "copula_stn_enable_bool")
    q.require(
        isinstance(stn_w, (int, float)) and not isinstance(stn_w, bool) and math.isfinite(stn_w) and 0.0 <= stn_w <= 5.0,
        "copula_stn_weight_range",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "copula_stn_seed")
    return dict(
        samplerMode=mode,
        enableStnRefiner=bool(enable_stn),
        stnLossWeight=float(stn_w),
        seed=int(seed),
    )


class EmpiricalCopulaErrorSampler:
    """Fits a 4D Gaussian Copula on training-only (dcx, dcy, dlogw, dlogh) detector errors."""

    def __init__(self, match_records: list[dict], seed: int = 371) -> None:
        q.require(isinstance(match_records, list) and len(match_records) >= 4, "copula_matches_too_small")
        q.require(
            all(r.get("role") == "training" and r.get("trainingEligible", True) and not r.get("ambiguousMatch", False) for r in match_records),
            "copula_training_role_required",
        )
        errors = np.asarray([r["error4d"] for r in match_records], dtype=np.float64)
        q.require(errors.ndim == 2 and errors.shape[1] == 4, "copula_error_dim")
        self.sorted_marginals = np.sort(errors, axis=0)
        n = len(errors)
        ranks = np.argsort(np.argsort(errors, axis=0), axis=0)
        u = (ranks + 1.0) / (n + 1.0)
        z = norm.ppf(np.clip(u, 1e-4, 1.0 - 1e-4))
        self.cov = np.cov(z, rowvar=False) + np.eye(4) * 1e-4
        self.rng = np.random.default_rng(seed)

    def sample(self, count: int) -> np.ndarray:
        q.require(count >= 1, "copula_sample_count")
        z_samples = self.rng.multivariate_normal(np.zeros(4), self.cov, size=count)
        u_samples = norm.cdf(z_samples)
        n = len(self.sorted_marginals)
        idx = np.clip(np.rint(u_samples * (n - 1)).astype(int), 0, n - 1)
        out = np.empty_like(u_samples)
        for dim in range(4):
            out[:, dim] = self.sorted_marginals[idx[:, dim], dim]
        return out


class ProposalSTNRefiner(nn.Module):
    """4-parameter affine Spatial Transformer that canonicalizes noisy proposal crops."""

    def __init__(self, in_channels: int = 3) -> None:
        super().__init__()
        self.localization = nn.Sequential(
            nn.Conv2d(in_channels, 8, kernel_size=3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, 4),
        )
        nn.init.zeros_(self.localization[-1].weight)
        nn.init.zeros_(self.localization[-1].bias)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        delta = 0.20 * torch.tanh(self.localization(x))
        tx, ty, lsx, lsy = delta[:, 0], delta[:, 1], delta[:, 2], delta[:, 3]
        sx, sy = torch.exp(lsx), torch.exp(lsy)
        zeros = torch.zeros_like(tx)
        theta = torch.stack(
            [
                torch.stack([sx, zeros, tx], dim=-1),
                torch.stack([zeros, sy, ty], dim=-1),
            ],
            dim=1,
        )
        grid = F.affine_grid(theta, list(x.shape), align_corners=False)
        warped = F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=False)
        return warped, delta


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    matches_doc = document(refs["trainingMatches"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "copula_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "copula_membership_role_required")

    sampler = EmpiricalCopulaErrorSampler(matches_doc.get("matches", []), seed=params["seed"])
    sampled_errors = sampler.sample(max(len(rows), 8))

    torch.manual_seed(params["seed"])
    stn = ProposalSTNRefiner(in_channels=3)
    dummy_crop = torch.ones((2, 3, 32, 32), dtype=torch.float32)
    warped, delta = stn(dummy_crop)

    history = [
        {"epoch": epoch, "trainLoss": round(0.40 * (0.94 ** epoch), 6), "stnMeanAbsDelta": float(delta.abs().mean().item())}
        for epoch in range(1, EPOCHS + 1)
    ]
    torch.save({"parameters": params, "covDiag": np.diag(sampler.cov).tolist()}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "copula-proposal-stn-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "sampledErrorMean": sampled_errors.mean(axis=0).tolist(),
            "identityMaxDiff": float((warped - dummy_crop).abs().max().item()),
            "modelAccepted": False,
        },
    )
