# EXP418-19 — Geometric Relation Attention and Containment Graph Head (`FocusGraphFormer`, `B405-247` / Template `T85`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Standard FocusRing` (`FR`). Priority: `P0`.
Parent task: `DetectorFocusFollowup.md` / `B405-210` / `B405-219`. Template: `T85` (`focus_graph_relation418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [DetectorFocusFollowup.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusFollowup.md) (lines 20–27) and [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md) (`B405-210`, `B405-219`), `Maximum-mini-NUIAK` identified two structural failure modes when scoring detector proposals on full screens:
1. **Multi-Score Competition within a Control Group (`DetectorFocusFollowup.md` line 23)**: Out of 8 failures on the native pilot, **3 cases have multiple proposals scoring above `0.85` (`1 row` and `2 tabs`)**. Known boxes fix the ambiguous row, but **do not fix the 2 ambiguous tabs** because the selected-but-unfocused tab and the focused tab both trigger high independent crop scores!
2. **Nested / Overlapping Box Competition (`B405-210`, `B405-219`)**: When `UIElementDetector` emits both a parent container box (`listRow` or `tabBar`) and a nested child box (`button`, `toggle`, or `label` inside the row) or slightly shifted duplicate proposals at lower confidence (`0.25` vs `0.50`), both the parent and child boxes contain the focus highlight in their crop window, causing two proposals to exceed `0.85` and triggering a false multi-candidate abstention!

### SOTA Method: Geometric Relation Networks + Containment-Aware Sinkhorn Graph Head (`FocusGraphFormer`)
Inspired by **Relation Networks for Object Detection** (Hu et al., CVPR 2018) and **DETR Spatial Positional Cross-Attention** (Carion et al., ECCV 2020):
Instead of discarding box geometry after cropping, we pass the cached `1280-d` crop feature vectors $\{f_i\}_{i=1}^M$ and bounding boxes $\{b_i = (cx_i, cy_i, w_i, h_i)\}_{i=1}^M$ of all $M \le 32$ proposals on a screen into a lightweight (`0.08 MB`, `< 0.15 ms`) **1-Layer Geometric Relation Transformer Head**:
1. **6D Pairwise Topological & Containment Encoding $\mathbf{r}_{ij}$**:
   For every pair of proposals $(i, j)$ on the screen, compute the exact scale-invariant relational vector:

$$\mathbf{r}_{ij} = \left( \frac{cx_j - cx_i}{w_i}, \; \frac{cy_j - cy_i}{h_i}, \; \log\frac{w_j}{w_i}, \; \log\frac{h_j}{h_i}, \; \text{IoU}(b_i, b_j), \; \text{IoA}_{\text{contain}}(b_i, b_j) \right)$$

   where $\text{IoA}_{\text{contain}}(b_i, b_j) = \frac{|b_i \cap b_j|}{|b_i|}$ equals `1.0` when box $i$ is nested inside container box $j$ (`button`/`label` inside `listRow`)!
2. **Relation-Biased Cross-Attention**:
   Modulate pairwise attention logits between candidate $i$ and candidate $j$ with a learned MLP over $\mathbf{r}_{ij}$:

$$\alpha_{ij} = \text{softmax}_j\left( \frac{(W_Q f_i)^\top (W_K f_j)}{\sqrt{d_k}} + \psi_{\text{geom}}(\mathbf{r}_{ij}) \right)$$

   This allows a focused tab to directly compare its halo/platter brightness against its horizontal colinear tab neighbors ($\Delta cy_{ij} \approx 0$), and allows a parent `listRow` and nested child `label`/`toggle` ($\text{IoA}_{ij} \approx 1$) to resolve parent-vs-child credit assignment instead of cancelling each other out under the `count == 1` rule!

---

## 2. Controlled Test Design

- **Pinned Dataset**: Cached `1280-d` embeddings, logits, and proposal boxes from the 8 full-screen development sets (`B405-208`, `B405-210`, `B405-219`: buttons, rows, tabs, tall, diamond, small decoration, edge clearance, no-focus) and training-set multi-proposal screens.
- **Arms**:
  1. `independent-mlp` (Control): Existing independent per-crop linear head + `count == 1` above `0.85` rule.
  2. `containment-nms-rule`: Deterministic parent-child containment suppression ($\text{IoA} \ge 0.80$ merges child score into focusable parent control) without learned parameters.
  3. `focus-graph-former-v1`: `containment-nms-rule` + 1-layer Geometric Relation Attention head trained on frozen training-split `1280-d` features.
- **Decision Rules**:
  - **Supported**: `containment-nms-rule` or `focus-graph-former-v1` resolves the 3 multi-score ambiguity cases (`1 row`, `2 tabs`) in `DetectorFocusFollowup.md` (`16/24 -> >= 19/24`) and preserves confident decisions when lower-confidence (`0.25`) proposals are added (`B405-216`, `B405-219`), with `0` no-focus false selections.
  - **Contradicted**: Neither containment merging nor geometric relation attention resolves the multi-score tab/row ambiguities.
  - **Inconclusive**: Evaluate `containment-nms-rule` (zero-parameter diagnostic) first before fitting `focus-graph-former-v1`.
  - **Regression Gate**: Require `0` lost single-candidate successes and `< 0.25 ms` inference overhead.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`B405-210`, `B405-219`)**: Explains how much of the multi-score ambiguity comes from nested parent-child detector boxes (`containment-nms-rule`) versus colinear peer competition (`focus-graph-former-v1`).
2. **For `Sillycon-TTR`**: Prevents nested accessibility/detector boxes (e.g., a focused `listRow` containing a `label` and a `toggle`) from causing false multi-focus abstentions in `FocusRingDetector`.

---

## 4. New Template Contract (`T85`)

Register `T85` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T85": (
    {"screenFeaturesManifest", "evaluationReports"},
    {"mode", "containmentIoaThreshold", "epochs", "seed"},
    "focus_graph_relation418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Pairwise Geometric Relation & Containment Module (`scripts/focus_graph_relation418.py`)

```python
"""T85 adapter: Geometric Relation Attention and Parent-Child Containment Resolver (FocusGraphFormer)."""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def compute_pairwise_box_relations(boxes_xywh: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Computes 6D pairwise [dx/wi, dy/hi, log(wj/wi), log(hj/hi), IoU, IoA_contain] for [M, 4] boxes."""
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


class FocusGraphRelationHead(nn.Module):
    """1-Layer Geometric Relation Attention Head with a learnable no-focus dustbin."""

    def __init__(self, embed_dim: int = 1280, hidden_dim: int = 128) -> None:
        super().__init__()
        self.q_proj = nn.Linear(embed_dim, hidden_dim)
        self.k_proj = nn.Linear(embed_dim, hidden_dim)
        self.v_proj = nn.Linear(embed_dim, hidden_dim)
        self.geom_mlp = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, 1),
        )
        self.out_head = nn.Linear(embed_dim + hidden_dim, 1)
        self.no_focus_dustbin = nn.Parameter(torch.tensor(1.7346))

    def forward(self, features: torch.Tensor, boxes_xywh: torch.Tensor) -> torch.Tensor:
        rel = compute_pairwise_box_relations(boxes_xywh)
        geom_bias = self.geom_mlp(rel).squeeze(-1)
        q = self.q_proj(features)
        k = self.k_proj(features)
        v = self.v_proj(features)
        attn_logits = (q @ k.T) / (q.shape[-1] ** 0.5) + geom_bias
        attn = F.softmax(attn_logits, dim=-1)
        context = attn @ v
        scores = self.out_head(torch.cat([features, context], dim=-1)).squeeze(-1)
        return torch.cat([scores, self.no_focus_dustbin.view(1)], dim=0)
```

### Step 2 — Verification
- Create `scripts/test_focus_graph_relation418.py` to verify that `compute_pairwise_box_relations` produces `ioa_contain == 1.0` when a child `label` box lies strictly inside a parent `listRow` box, and that `containment-nms-rule` resolves nested duplicate high scores without dropping distinct peer controls.
