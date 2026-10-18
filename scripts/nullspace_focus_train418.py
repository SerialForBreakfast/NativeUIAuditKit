"""T77 adapter: Null-Space Projected Fine-Tuning (Null-LoRA + LP-FT) for FocusRingClassifier."""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"subspaceEnergy", "lpWarmupEpochs", "seed"},
        "nullspace_parameters",
    )
    energy = values["subspaceEnergy"]
    lp_epochs = values["lpWarmupEpochs"]
    seed = values["seed"]
    q.require(
        isinstance(energy, (int, float)) and not isinstance(energy, bool) and math.isfinite(energy) and 0.50 <= energy <= 1.0,
        "nullspace_energy_range",
    )
    q.require(isinstance(lp_epochs, int) and not isinstance(lp_epochs, bool) and 0 <= lp_epochs <= 15, "nullspace_lp_epochs")
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "nullspace_seed")
    return dict(subspaceEnergy=float(energy), lpWarmupEpochs=int(lp_epochs), seed=int(seed))


class OrthogonalSubspaceProjector:
    """Projects weight updates onto the orthogonal complement of retained anchor activations."""

    def __init__(self, energy_threshold: float = 0.99) -> None:
        q.require(0.50 <= energy_threshold <= 1.0, "nullspace_energy_range")
        self.energy_threshold = float(energy_threshold)
        self.projectors: dict[str, torch.Tensor] = {}

    @torch.no_grad()
    def fit_anchor_matrix(self, name: str, anchor_features: torch.Tensor) -> dict[str, float]:
        q.require(anchor_features.ndim == 2 and anchor_features.shape[0] >= 2, "nullspace_anchor_shape")
        x = anchor_features.float()
        cov = x.T @ x
        u, s, _ = torch.linalg.svd(cov, full_matrices=False)
        total_energy = torch.sum(s).clamp_min(1e-12)
        cum_energy = torch.cumsum(s, dim=0) / total_energy

        if self.energy_threshold >= 1.0:
            k = int((s > 1e-6).sum().item())
        else:
            k = int(torch.searchsorted(cum_energy, self.energy_threshold).item()) + 1
            k = min(k, u.shape[1] - 1)
        u_k = u[:, :k]
        proj = torch.eye(u.shape[0], device=x.device, dtype=torch.float32) - (u_k @ u_k.T)
        self.projectors[name] = proj
        return {
            "totalDim": float(u.shape[0]),
            "retainedRank": float(k),
            "nullRank": float(u.shape[0] - k),
            "capturedEnergy": float(cum_energy[max(k - 1, 0)].item()),
        }

    @torch.no_grad()
    def project_linear_grad(self, name: str, layer: nn.Linear) -> None:
        if name in self.projectors and layer.weight.grad is not None:
            proj = self.projectors[name].to(layer.weight.grad.device, dtype=layer.weight.grad.dtype)
            layer.weight.grad.copy_(layer.weight.grad @ proj)


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    anchors = document(refs["anchorManifest"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "nullspace_config_init_mismatch")
    rows = membership.get("rows", [])
    anchor_rows = anchors.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "nullspace_training_role_required")
    q.require(anchor_rows and all(r.get("role") == "training" for r in anchor_rows), "nullspace_anchor_role_required")

    torch.manual_seed(params["seed"])
    dim = 8
    anchor_x = torch.tensor([r.get("features", [1.0, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]) for r in anchor_rows], dtype=torch.float32)
    train_x = torch.tensor([r.get("features", [0.0, 0.0, 0.0, 1.0, 0.8, 0.4, 0.2, 0.1]) for r in rows], dtype=torch.float32)
    train_y = torch.tensor([float(r.get("focused", 1)) for r in rows], dtype=torch.float32)

    encoder = nn.Linear(dim, dim, bias=False)
    head = nn.Linear(dim, 1)
    projector = OrthogonalSubspaceProjector(energy_threshold=params["subspaceEnergy"])
    subspace_stats = projector.fit_anchor_matrix("encoder", anchor_x)
    initial_anchor_out = encoder(anchor_x).detach().clone()

    opt = torch.optim.SGD(list(encoder.parameters()) + list(head.parameters()), lr=0.05)
    history = []
    for epoch in range(1, EPOCHS + 1):
        opt.zero_grad()
        hidden = encoder(train_x)
        if epoch <= params["lpWarmupEpochs"]:
            hidden = hidden.detach()
        logits = head(hidden).squeeze(-1)
        loss = F.binary_cross_entropy_with_logits(logits, train_y)
        loss.backward()
        if epoch > params["lpWarmupEpochs"]:
            projector.project_linear_grad("encoder", encoder)
        opt.step()
        anchor_drift = float(torch.norm(encoder(anchor_x).detach() - initial_anchor_out).item())
        history.append({"epoch": epoch, "trainLoss": float(loss.detach().item()), "anchorFeatureDriftL2": round(anchor_drift, 6)})

    torch.save({"parameters": params, "subspaceStats": subspace_stats}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "nullspace-focus-train-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "subspaceStats": subspace_stats,
            "finalTrainLoss": history[-1]["trainLoss"],
            "finalAnchorDriftL2": history[-1]["anchorFeatureDriftL2"],
            "modelAccepted": False,
        },
    )
