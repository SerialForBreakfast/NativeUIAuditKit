"""T69 adapter: Within-screen Set-Contrastive (SupCon + ListMLE dustbin) focus ranking."""
from __future__ import annotations

import math
import torch
import torch.nn.functional as F
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"supconWeight", "listmleWeight", "temperature", "seed"},
        "set_rank_parameters",
    )
    sw = values["supconWeight"]
    lw = values["listmleWeight"]
    temp = values["temperature"]
    seed = values["seed"]
    for name, val in (("supconWeight", sw), ("listmleWeight", lw)):
        q.require(
            isinstance(val, (int, float)) and not isinstance(val, bool) and math.isfinite(val) and 0.0 <= val <= 2.0,
            f"set_rank_{name}",
        )
    q.require(
        isinstance(temp, (int, float)) and not isinstance(temp, bool) and math.isfinite(temp) and 0.01 <= temp <= 5.0,
        "set_rank_temperature",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "set_rank_seed")
    return dict(supconWeight=float(sw), listmleWeight=float(lw), temperature=float(temp), seed=int(seed))


def supervised_contrastive_loss(
    embeddings: torch.Tensor,
    labels: torch.Tensor,
    temperature: float = 0.07,
    eps: float = 1e-7,
) -> torch.Tensor:
    """Khosla et al. (NeurIPS 2020) Supervised Contrastive Loss on L2-normalized embeddings [B, D]."""
    z = F.normalize(embeddings, p=2, dim=-1)
    n = z.shape[0]
    if n <= 1:
        return z.sum() * 0.0
    sim = (z @ z.T) / max(float(temperature), eps)
    eye = torch.eye(n, device=z.device, dtype=torch.bool)
    sim = sim - sim.masked_fill(eye, -1e9).max(dim=1, keepdim=True).values.detach()

    exp_sim = torch.exp(sim).masked_fill(eye, 0.0)
    log_prob = sim - torch.log(exp_sim.sum(dim=1, keepdim=True).clamp_min(eps))

    pos_mask = (labels[:, None] == labels[None, :]) & (~eye)
    pos_counts = pos_mask.sum(dim=1)
    valid = pos_counts > 0
    if not valid.any():
        return z.sum() * 0.0
    mean_log_pos = (log_prob * pos_mask.float()).sum(dim=1)[valid] / pos_counts[valid].float()
    return (-mean_log_pos.mean()).clamp_min(0.0)


def screen_listmle_dustbin_loss(
    screen_logits: torch.Tensor,
    screen_labels: torch.Tensor,
    dustbin_logit: torch.Tensor,
) -> torch.Tensor:
    """Plackett-Luce / ListMLE set ranking loss with a learnable dustbin for no-focus screens."""
    q.require(screen_logits.ndim == 1 and screen_logits.shape == screen_labels.shape, "set_rank_screen_shape")
    pos_count = int((screen_labels > 0.5).sum().item())
    q.require(pos_count <= 1, "set_rank_conflicting_focus")
    augmented = torch.cat([screen_logits, dustbin_logit.view(1)], dim=0)
    target_idx = int(torch.argmax(screen_labels).item()) if pos_count == 1 else int(screen_logits.numel())
    return F.cross_entropy(augmented.unsqueeze(0), torch.tensor([target_idx], device=screen_logits.device))


def validate_screen_groups(screen_groups: list[dict]) -> None:
    """Enforces PAPER417-PAIRS rules: single scene per group, <=1 focused target, no cross-scene mixing."""
    q.require(isinstance(screen_groups, list) and len(screen_groups) > 0, "set_rank_empty_groups")
    for sg in screen_groups:
        rows = sg.get("candidates", [])
        q.require(len(rows) >= 2, "set_rank_singleton_screen")
        scenes = {r.get("sceneId") for r in rows}
        q.require(len(scenes) == 1, "set_rank_cross_scene_pair")
        focused = sum(int(r.get("focused", 0)) == 1 for r in rows)
        q.require(focused <= 1, "set_rank_multiple_focused_targets")


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    screens_doc = document(refs["screenGroups"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "set_rank_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "set_rank_training_role_required")
    screen_groups = screens_doc.get("screens", [])
    validate_screen_groups(screen_groups)

    torch.manual_seed(params["seed"])
    dustbin = torch.nn.Parameter(torch.tensor(1.7346))
    proj = torch.nn.Linear(8, 8)
    head = torch.nn.Linear(8, 1)
    opt = torch.optim.Adam(list(proj.parameters()) + list(head.parameters()) + [dustbin], lr=0.02)

    history = []
    for epoch in range(1, EPOCHS + 1):
        opt.zero_grad()
        all_embeds = []
        all_labels = []
        rank_losses = []
        for sg in screen_groups:
            cands = sg["candidates"]
            feats = torch.tensor([c.get("features", [float(c.get("focused", 0))] * 8) for c in cands], dtype=torch.float32)
            lbls = torch.tensor([float(c.get("focused", 0)) for c in cands], dtype=torch.float32)
            emb = proj(feats)
            logits = head(emb).squeeze(-1)
            all_embeds.append(emb)
            all_labels.append(lbls)
            rank_losses.append(screen_listmle_dustbin_loss(logits, lbls, dustbin))

        cat_embeds = torch.cat(all_embeds, dim=0)
        cat_labels = torch.cat(all_labels, dim=0)
        bce = F.binary_cross_entropy_with_logits(head(cat_embeds).squeeze(-1), cat_labels)
        supcon = supervised_contrastive_loss(cat_embeds, cat_labels, temperature=params["temperature"])
        listmle = torch.stack(rank_losses).mean()
        total = bce + params["supconWeight"] * supcon + params["listmleWeight"] * listmle
        total.backward()
        opt.step()
        history.append({
            "epoch": epoch,
            "trainLoss": float(total.detach().item()),
            "bceLoss": float(bce.detach().item()),
            "supconLoss": float(supcon.detach().item()),
            "listmleLoss": float(listmle.detach().item()),
            "dustbinLogit": float(dustbin.detach().item()),
        })

    torch.save({"dustbin": float(dustbin.detach().item()), "parameters": params}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "set-contrastive-focus-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "screenCount": len(screen_groups),
            "finalTrainLoss": history[-1]["trainLoss"],
            "finalDustbinLogit": history[-1]["dustbinLogit"],
            "modelAccepted": False,
        },
    )
