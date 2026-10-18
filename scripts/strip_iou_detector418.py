"""T81 adapter: Anisotropic Strip Pooling and 1D Marginal Projection IoU (Strip-IoU) for wide UI rows."""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import research_queue as q
from nwd_detector_train418 import box_iou_ciou_xywh
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None
EPOCHS = 30


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"projIouWeight", "enableStripPooling", "seed"},
        "strip_iou_parameters",
    )
    pw = values["projIouWeight"]
    enable_spm = values["enableStripPooling"]
    seed = values["seed"]
    q.require(
        isinstance(pw, (int, float)) and not isinstance(pw, bool) and math.isfinite(pw) and 0.0 <= pw <= 1.0,
        "strip_iou_weight_range",
    )
    q.require(isinstance(enable_spm, bool), "strip_iou_enable_bool")
    q.require(isinstance(seed, int) and not isinstance(seed, bool) and seed > 0, "strip_iou_seed")
    return dict(projIouWeight=float(pw), enableStripPooling=bool(enable_spm), seed=int(seed))


def marginal_projection_iou_loss_xywh(
    pred_xywh: torch.Tensor,
    target_xywh: torch.Tensor,
    proj_iou_weight: float = 0.40,
    eps: float = 1e-7,
) -> dict[str, torch.Tensor]:
    """Computes blended 2D CIoU + 1D horizontal/vertical marginal GIoU loss for elongated rows and bars."""
    iou_2d, ciou_2d = box_iou_ciou_xywh(pred_xywh, target_xywh, eps=eps)
    px, py, pw, ph = pred_xywh.unbind(dim=-1)
    tx, ty, tw, th = target_xywh.unbind(dim=-1)
    px1, px2 = px - 0.5 * pw, px + 0.5 * pw
    py1, py2 = py - 0.5 * ph, py + 0.5 * ph
    tx1, tx2 = tx - 0.5 * tw, tx + 0.5 * tw
    ty1, ty2 = ty - 0.5 * th, ty + 0.5 * th

    inter_x = (torch.minimum(px2, tx2) - torch.maximum(px1, tx1)).clamp_min(0.0)
    union_x = pw.clamp_min(eps) + tw.clamp_min(eps) - inter_x + eps
    enclose_x = (torch.maximum(px2, tx2) - torch.minimum(px1, tx1)).clamp_min(eps)
    giou_x = (inter_x / union_x) - ((enclose_x - union_x) / enclose_x)

    inter_y = (torch.minimum(py2, ty2) - torch.maximum(py1, ty1)).clamp_min(0.0)
    union_y = ph.clamp_min(eps) + th.clamp_min(eps) - inter_y + eps
    enclose_y = (torch.maximum(py2, ty2) - torch.minimum(py1, ty1)).clamp_min(eps)
    giou_y = (inter_y / union_y) - ((enclose_y - union_y) / enclose_y)

    proj_loss = 0.5 * ((1.0 - giou_x) + (1.0 - giou_y))
    ciou_loss = 1.0 - ciou_2d
    w = float(proj_iou_weight)
    total = (1.0 - w) * ciou_loss + w * proj_loss
    return {
        "loss": total.mean(),
        "perBoxLoss": total,
        "iou2d": iou_2d,
        "giouX": giou_x,
        "giouY": giou_y,
    }


class AnisotropicStripPooling(nn.Module):
    """Hou et al. (CVPR 2020) Horizontal (H x 1) and Vertical (1 x W) Strip Pooling residual module."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.conv_h = nn.Conv1d(channels, channels, kernel_size=3, padding=1, groups=channels, bias=False)
        self.conv_w = nn.Conv1d(channels, channels, kernel_size=3, padding=1, groups=channels, bias=False)
        self.fuse = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, h, w = x.shape
        pool_h = self.conv_h(x.mean(dim=3)).unsqueeze(3).expand(b, c, h, w)
        pool_w = self.conv_w(x.mean(dim=2)).unsqueeze(2).expand(b, c, h, w)
        gate = self.fuse(pool_h + pool_w)
        return x * (1.0 + gate)


def run() -> None:
    spec = q.load(OUT.parents[2] / "spec.json")
    cfg = spec["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    config = document(refs["configuration"])
    membership = document(refs["membership"])
    eval_labels = document(refs["evalLabels"])
    checked(refs["initialization"]).read_bytes()

    q.require(config.get("initialization") == refs["initialization"], "strip_iou_config_init_mismatch")
    rows = membership.get("rows", [])
    q.require(rows and all(r.get("role") == "training" for r in rows), "strip_iou_training_role_required")
    q.require(eval_labels.get("role") in ("development", "calibration") and not eval_labels.get("trainingEligible", False), "strip_iou_eval_role_violation")

    torch.manual_seed(params["seed"])
    spm = AnisotropicStripPooling(channels=8)
    feat = torch.randn(2, 8, 16, 32)
    pooled = spm(feat) if params["enableStripPooling"] else feat

    pred_boxes = torch.tensor(
        [r.get("predBox", [700.0, 200.0, 1100.0, 56.0]) for r in rows],
        dtype=torch.float32,
        requires_grad=True,
    )
    target_boxes = torch.tensor(
        [r.get("targetBox", [760.0, 202.0, 1400.0, 56.0]) for r in rows],
        dtype=torch.float32,
    )
    opt = torch.optim.SGD([pred_boxes], lr=15.0)
    history = []
    for epoch in range(1, EPOCHS + 1):
        opt.zero_grad()
        res = marginal_projection_iou_loss_xywh(pred_boxes, target_boxes, proj_iou_weight=params["projIouWeight"])
        res["loss"].backward()
        opt.step()
        history.append({
            "epoch": epoch,
            "trainLoss": float(res["loss"].detach().item()),
            "meanIoU2D": float(res["iou2d"].detach().mean().item()),
            "meanGIoUX": float(res["giouX"].detach().mean().item()),
        })

    torch.save({"parameters": params, "boxes": pred_boxes.detach(), "featureShape": list(pooled.shape)}, OUT / "final.pt")
    q.save(OUT / "history.json", history)
    q.save(OUT / "fit.json", {"epochs": EPOCHS, "seed": params["seed"], "parameters": params, "modelAccepted": False})
    q.save(
        OUT / "benchmark_summary.json",
        {
            "version": "strip-iou-detector-v1",
            "parameters": params,
            "epochs": EPOCHS,
            "finalTrainLoss": history[-1]["trainLoss"],
            "finalMeanIoU2D": history[-1]["meanIoU2D"],
            "finalMeanGIoUX": history[-1]["meanGIoUX"],
            "modelAccepted": False,
        },
    )
