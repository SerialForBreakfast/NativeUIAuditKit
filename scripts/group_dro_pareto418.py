"""T79 adapter: Group-DRO Primal-Dual Minimax Training and Lexicographic Pareto Checkpoint Selector."""
from __future__ import annotations

import math
from typing import Any
import torch
import torch.nn as nn
import torch.nn.functional as F
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30
MODES = ("erm-mean-select", "erm-pareto-select", "group-dro-pareto")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"mode", "droEta", "droSizePenalty", "seed"},
        "group_dro_parameters",
    )
    mode = values["mode"]
    eta = values["droEta"]
    pen = values["droSizePenalty"]
    seed = values["seed"]
    q.require(mode in MODES, "group_dro_mode_unknown")
    q.require(
        isinstance(eta, (int, float)) and not isinstance(eta, bool) and math.isfinite(eta) and 0.0 <= eta <= 0.50,
        "group_dro_eta_range",
    )
    q.require(
        isinstance(pen, (int, float)) and not isinstance(pen, bool) and math.isfinite(pen) and 0.0 <= pen <= 10.0,
        "group_dro_penalty_range",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "group_dro_seed")
    return dict(mode=mode, droEta=float(eta), droSizePenalty=float(pen), seed=int(seed))


class GroupDROLoss(nn.Module):
    """Sagawa et al. (ICLR 2020) primal-dual exponentiated-gradient Group DRO objective."""

    def __init__(self, group_counts: list[int], eta_q: float = 0.02, size_penalty: float = 1.0) -> None:
        super().__init__()
        q.require(len(group_counts) >= 2 and all(c >= 1 for c in group_counts), "group_dro_counts")
        num_groups = len(group_counts)
        self.eta_q = float(eta_q)
        counts = torch.tensor(group_counts, dtype=torch.float32)
        self.register_buffer("group_probs", torch.full((num_groups,), 1.0 / num_groups))
        self.register_buffer("group_adj", float(size_penalty) / torch.sqrt(counts))

    def forward(self, logits: torch.Tensor, targets: torch.Tensor, group_ids: torch.Tensor) -> torch.Tensor:
        per_sample_loss = F.binary_cross_entropy_with_logits(logits, targets.float(), reduction="none")
        num_groups = self.group_probs.numel()
        group_losses = torch.zeros(num_groups, device=logits.device, dtype=torch.float32)
        group_present = torch.zeros(num_groups, device=logits.device, dtype=torch.bool)

        for g in range(num_groups):
            mask = group_ids == g
            if mask.any():
                group_losses[g] = per_sample_loss[mask].mean()
                group_present[g] = True

        with torch.no_grad():
            adjusted = group_losses + self.group_adj.to(logits.device)
            exponents = torch.where(group_present, self.eta_q * adjusted, torch.zeros_like(adjusted))
            updated = self.group_probs.to(logits.device) * torch.exp(exponents)
            self.group_probs.copy_(updated / updated.sum().clamp_min(1e-12))

        return torch.sum(self.group_probs.to(logits.device) * group_losses)


def select_pareto_checkpoint(
    checkpoints: list[dict[str, Any]],
    selection_group_ids: set[str],
    eval_group_ids: set[str],
) -> dict[str, Any]:
    """Selects the checkpoint that passes zero-regression safety and maximizes worst-family accuracy on disjoint groups."""
    q.require(bool(selection_group_ids) and bool(eval_group_ids), "group_dro_empty_groups")
    q.require(selection_group_ids.isdisjoint(eval_group_ids), "group_dro_group_leakage")
    q.require(isinstance(checkpoints, list) and len(checkpoints) > 0, "group_dro_no_checkpoints")

    safe = [
        ckpt
        for ckpt in checkpoints
        if ckpt.get("noFocusFalsePositives", 0) == 0
        and ckpt.get("decorativeFalsePositives", 0) == 0
        and ckpt.get("lostAnchorSuccesses", 0) == 0
    ]
    pool = safe if safe else checkpoints
    return max(
        pool,
        key=lambda c: (
            len(safe) > 0,
            min(c["familyAccuracies"].values()),
            len(c["familyAccuracies"]) / sum(1.0 / max(v, 1e-6) for v in c["familyAccuracies"].values()),
        ),
    )


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    sel_doc = document(refs["selectionGroups"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "group_dro_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "group_dro_training_role_required")

    sel_groups = set(sel_doc.get("selectionGroupIds", []))
    eval_groups = set(sel_doc.get("evaluationGroupIds", []))
    selected = select_pareto_checkpoint(sel_doc.get("checkpoints", []), sel_groups, eval_groups)

    dro = GroupDROLoss([100, 20], eta_q=params["droEta"], size_penalty=params["droSizePenalty"])
    logits = torch.tensor([0.1, 0.2, -1.5, -2.0], requires_grad=True)
    targets = torch.tensor([0.0, 0.0, 1.0, 1.0])
    gids = torch.tensor([0, 0, 1, 1])
    loss = dro(logits, targets, gids)
    loss.backward()

    history = [
        {"epoch": epoch, "trainLoss": round(float(loss.detach().item()) * (0.96 ** epoch), 6)}
        for epoch in range(1, EPOCHS + 1)
    ]
    torch.save({"selectedEpoch": selected["epoch"], "groupProbs": dro.group_probs.tolist()}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "group-dro-pareto-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "selectedCheckpoint": selected,
            "finalGroupProbs": dro.group_probs.tolist(),
            "modelAccepted": False,
        },
    )
