"""T85 adapter: Geometric Relation Attention and Parent-Child Containment Resolver (FocusGraphFormer)."""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
MODES = ("independent-mlp", "containment-nms-rule", "focus-graph-former-v1")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"mode", "containmentIoaThreshold"},
        "focus_graph_parameters",
    )
    mode = values["mode"]
    ioa = values["containmentIoaThreshold"]
    q.require(mode in MODES, "focus_graph_mode_unknown")
    q.require(
        isinstance(ioa, (int, float)) and not isinstance(ioa, bool) and math.isfinite(ioa) and 0.50 <= ioa <= 0.99,
        "focus_graph_ioa_range",
    )
    return dict(mode=mode, containmentIoaThreshold=float(ioa))


def compute_pairwise_box_relations(boxes_xywh: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Computes 6D pairwise [dx/wi, dy/hi, log(wj/wi), log(hj/hi), IoU, IoA_contain] for [M, 4] (cx, cy, w, h) boxes."""
    q.require(boxes_xywh.ndim == 2 and boxes_xywh.shape[1] == 4 and len(boxes_xywh) >= 1, "focus_graph_box_shape")
    cx, cy, w, h = boxes_xywh.unbind(dim=-1)
    x1, y1, x2, y2 = cx - 0.5 * w, cy - 0.5 * h, cx + 0.5 * w, cy + 0.5 * h

    dx = (cx[None, :] - cx[:, None]) / w[:, None].clamp_min(eps)
    dy = (cy[None, :] - cy[:, None]) / h[:, None].clamp_min(eps)
    dw = torch.log(w[None, :].clamp_min(eps) / w[:, None].clamp_min(eps))
    dh = torch.log(h[None, :].clamp_min(eps) / h[:, None].clamp_min(eps))

    inter_x1 = torch.maximum(x1[:, None], x1[None, :])
    inter_y1 = torch.maximum(y1[:, None], y1[None, :])
    inter_x2 = torch.minimum(x2[:, None], x2[None, :])
    inter_y2 = torch.minimum(y2[:, None], y2[None, :])
    inter_area = (inter_x2 - inter_x1).clamp_min(0.0) * (inter_y2 - inter_y1).clamp_min(0.0)

    area = (w * h).clamp_min(eps)
    union_area = area[:, None] + area[None, :] - inter_area + eps
    iou = inter_area / union_area
    ioa_contain = inter_area / area[:, None]  # Fraction of box i contained inside box j
    return torch.stack([dx, dy, dw, dh, iou, ioa_contain], dim=-1)


def suppress_nested_child_candidates(
    boxes_xywh: torch.Tensor,
    scores: torch.Tensor,
    ioa_threshold: float = 0.80,
    score_threshold: float = 0.85,
) -> tuple[list[int], torch.Tensor]:
    """Suppresses nested child boxes (IoA_contain >= ioa_threshold and area_i < area_j) when parent also scores high."""
    rel = compute_pairwise_box_relations(boxes_xywh)
    ioa = rel[:, :, 5]
    areas = boxes_xywh[:, 2] * boxes_xywh[:, 3]
    m = len(scores)
    kept_indices = []
    adjusted_scores = scores.clone()

    for i in range(m):
        nested_in_active_parent = False
        for j in range(m):
            if i == j:
                continue
            if float(ioa[i, j].item()) >= ioa_threshold and float(areas[i].item()) < 0.85 * float(areas[j].item()):
                if float(scores[j].item()) >= score_threshold:
                    nested_in_active_parent = True
                    adjusted_scores[j] = torch.maximum(adjusted_scores[j], scores[i])
                    break
        if not nested_in_active_parent:
            kept_indices.append(i)
            continue
        adjusted_scores[i] = 0.0
    return kept_indices, adjusted_scores


class FocusGraphRelationHead(nn.Module):
    """1-Layer Geometric Relation Attention Head with a learnable no-focus dustbin."""

    def __init__(self, embed_dim: int = 8, hidden_dim: int = 8) -> None:
        super().__init__()
        self.q_proj = nn.Linear(embed_dim, hidden_dim)
        self.k_proj = nn.Linear(embed_dim, hidden_dim)
        self.v_proj = nn.Linear(embed_dim, hidden_dim)
        self.geom_mlp = nn.Sequential(
            nn.Linear(6, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 1),
        )
        self.out_head = nn.Linear(embed_dim + hidden_dim, 1)
        self.no_focus_dustbin = nn.Parameter(torch.tensor(1.7346))

    def forward(self, features: torch.Tensor, boxes_xywh: torch.Tensor) -> torch.Tensor:
        rel = compute_pairwise_box_relations(boxes_xywh)
        geom_bias = self.geom_mlp(rel).squeeze(-1)
        q_mat = self.q_proj(features)
        k_mat = self.k_proj(features)
        v_mat = self.v_proj(features)
        attn_logits = (q_mat @ k_mat.T) / (q_mat.shape[-1] ** 0.5) + geom_bias
        attn = F.softmax(attn_logits, dim=-1)
        context = attn @ v_mat
        scores = self.out_head(torch.cat([features, context], dim=-1)).squeeze(-1)
        return torch.cat([scores, self.no_focus_dustbin.view(1)], dim=0)


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    manifest = document(refs["screenFeaturesManifest"])
    screens = manifest.get("screens", [])
    q.require(screens and all(s.get("role") == "development" and not s.get("trainingEligible", False) for s in screens), "focus_graph_role_violation")

    rows = []
    for s in screens:
        boxes = torch.tensor(s["boxes"], dtype=torch.float32)
        scores = torch.tensor(s["scores"], dtype=torch.float32)
        if params["mode"] == "independent-mlp":
            adj = scores
            kept = list(range(len(scores)))
        else:
            kept, adj = suppress_nested_child_candidates(boxes, scores, ioa_threshold=params["containmentIoaThreshold"])
        above = [i for i, v in enumerate(adj.tolist()) if v >= 0.85]
        rows.append({
            "id": s["id"],
            "keptCandidates": kept,
            "aboveThresholdIndices": above,
            "selectedIndex": above[0] if len(above) == 1 else None,
        })

    summary = {
        "version": "focus-graph-relation-v1",
        "parameters": params,
        "screens": len(rows),
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
