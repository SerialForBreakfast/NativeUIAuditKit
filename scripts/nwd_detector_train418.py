"""T67 adapter: Normalized Wasserstein Distance (NWD) + CIoU loss for tiny UI control detection."""
from __future__ import annotations

import math
import torch
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"nwdWeight", "nwdConstant", "smallAreaMax", "seed"},
        "nwd_parameters",
    )
    w = values["nwdWeight"]
    c = values["nwdConstant"]
    area_max = values["smallAreaMax"]
    seed = values["seed"]
    q.require(
        isinstance(w, (int, float)) and not isinstance(w, bool) and math.isfinite(w) and 0.0 <= w <= 1.0,
        "nwd_weight_range",
    )
    q.require(
        isinstance(c, (int, float)) and not isinstance(c, bool) and math.isfinite(c) and c > 0.0,
        "nwd_constant_positive",
    )
    q.require(
        isinstance(area_max, (int, float)) and not isinstance(area_max, bool) and 0.0 < area_max <= 0.25,
        "nwd_small_area_range",
    )
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "nwd_seed")
    return dict(nwdWeight=float(w), nwdConstant=float(c), smallAreaMax=float(area_max), seed=int(seed))


def box_iou_ciou_xywh(pred_xywh: torch.Tensor, target_xywh: torch.Tensor, eps: float = 1e-7) -> tuple[torch.Tensor, torch.Tensor]:
    """Computes standard 2D IoU and Complete IoU (CIoU) for [N, 4] (cx, cy, w, h) boxes."""
    px, py, pw, ph = pred_xywh.unbind(dim=-1)
    tx, ty, tw, th = target_xywh.unbind(dim=-1)
    pw = pw.clamp_min(eps)
    ph = ph.clamp_min(eps)
    tw = tw.clamp_min(eps)
    th = th.clamp_min(eps)

    px1, py1, px2, py2 = px - 0.5 * pw, py - 0.5 * ph, px + 0.5 * pw, py + 0.5 * ph
    tx1, ty1, tx2, ty2 = tx - 0.5 * tw, ty - 0.5 * th, tx + 0.5 * tw, ty + 0.5 * th

    inter_w = (torch.minimum(px2, tx2) - torch.maximum(px1, tx1)).clamp_min(0.0)
    inter_h = (torch.minimum(py2, ty2) - torch.maximum(py1, ty1)).clamp_min(0.0)
    inter = inter_w * inter_h
    union = pw * ph + tw * th - inter + eps
    iou = inter / union

    cw = (torch.maximum(px2, tx2) - torch.minimum(px1, tx1)).clamp_min(eps)
    ch = (torch.maximum(py2, ty2) - torch.minimum(py1, ty1)).clamp_min(eps)
    c2 = cw * cw + ch * ch + eps
    rho2 = (px - tx) ** 2 + (py - ty) ** 2

    v = (4.0 / (math.pi ** 2)) * (torch.atan(tw / th) - torch.atan(pw / ph)) ** 2
    with torch.no_grad():
        alpha = v / (1.0 - iou + v + eps)
    ciou = iou - (rho2 / c2 + alpha * v)
    return iou, ciou


def nwd_similarity_xywh(
    pred_xywh: torch.Tensor,
    target_xywh: torch.Tensor,
    constant_c: float = 12.8,
    eps: float = 1e-7,
) -> torch.Tensor:
    """Computes Normalized Gaussian Wasserstein Distance similarity in (0, 1] for [N, 4] (cx, cy, w, h) boxes."""
    px, py, pw, ph = pred_xywh.unbind(dim=-1)
    tx, ty, tw, th = target_xywh.unbind(dim=-1)
    center_dist2 = (px - tx) ** 2 + (py - ty) ** 2
    size_dist2 = 0.25 * ((pw - tw) ** 2 + (ph - th) ** 2)
    w2_squared = (center_dist2 + size_dist2).clamp_min(0.0)
    return torch.exp(-torch.sqrt(w2_squared + eps) / max(float(constant_c), eps))


def blended_nwd_ciou_loss(
    pred_xywh: torch.Tensor,
    target_xywh: torch.Tensor,
    image_size: float = 640.0,
    nwd_weight: float = 0.5,
    nwd_constant: float = 12.8,
    small_area_max: float = 0.01,
) -> dict[str, torch.Tensor]:
    """Computes scale-routed (1 - w) * (1 - CIoU) + w * (1 - NWD) box loss and TAL alignment metric."""
    iou, ciou = box_iou_ciou_xywh(pred_xywh, target_xywh)
    nwd = nwd_similarity_xywh(pred_xywh, target_xywh, constant_c=nwd_constant)
    norm_area = (target_xywh[..., 2] * target_xywh[..., 3]) / max(image_size * image_size, 1.0)
    is_small = norm_area <= small_area_max
    w = torch.where(is_small, torch.full_like(norm_area, float(nwd_weight)), torch.zeros_like(norm_area))
    ciou_loss = 1.0 - ciou
    nwd_loss = 1.0 - nwd
    total_loss = (1.0 - w) * ciou_loss + w * nwd_loss
    blended_metric = (1.0 - w) * iou.clamp_min(0.0) + w * nwd
    return {
        "loss": total_loss.mean(),
        "perBoxLoss": total_loss,
        "iou": iou,
        "nwd": nwd,
        "blendedMetric": blended_metric,
        "smallMask": is_small,
    }


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    eval_labels = document(refs["evalLabels"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "nwd_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "nwd_training_role_required")
    q.require(eval_labels.get("role") in ("development", "calibration") and not eval_labels.get("trainingEligible", False), "nwd_eval_role_violation")

    torch.manual_seed(params["seed"])
    pred_boxes = torch.tensor(
        [r.get("predBox", [100.0, 100.0, 20.0, 10.0]) for r in rows],
        dtype=torch.float32,
        requires_grad=True,
    )
    target_boxes = torch.tensor(
        [r.get("targetBox", [101.5, 100.5, 20.0, 10.0]) for r in rows],
        dtype=torch.float32,
    )
    optimizer = torch.optim.SGD([pred_boxes], lr=0.25)
    history = []
    for epoch in range(1, EPOCHS + 1):
        optimizer.zero_grad()
        metrics = blended_nwd_ciou_loss(
            pred_boxes,
            target_boxes,
            nwd_weight=params["nwdWeight"],
            nwd_constant=params["nwdConstant"],
            small_area_max=params["smallAreaMax"],
        )
        loss = metrics["loss"]
        loss.backward()
        optimizer.step()
        history.append({
            "epoch": epoch,
            "trainLoss": float(loss.detach().item()),
            "meanIoU": float(metrics["iou"].detach().mean().item()),
            "meanNWD": float(metrics["nwd"].detach().mean().item()),
        })

    torch.save({"seed": params["seed"], "parameters": params, "boxes": pred_boxes.detach()}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    summary = {
        "version": "nwd-detector-train-v1",
        "parameters": params,
        "epochs": EPOCHS,
        "finalTrainLoss": history[-1]["trainLoss"],
        "finalMeanIoU": history[-1]["meanIoU"],
        "finalMeanNWD": history[-1]["meanNWD"],
        "smallTargetCount": int(metrics["smallMask"].sum().item()),
        "modelAccepted": False,
    }
    q.save(OUT / "benchmark_summary.json", summary)
