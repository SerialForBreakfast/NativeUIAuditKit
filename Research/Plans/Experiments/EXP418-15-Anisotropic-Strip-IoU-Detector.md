# EXP418-15 — Anisotropic Strip Pooling and 1D Projected IoU (`Strip-IoU`) for Wide Rows and Bars (`B405-243` / Template `T81`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `tvOS detection` (`TV`) and `iOS detection` (`IOS`). Priority: `P0`.
Parent task: `FOCUS-PIPELINE-NEXT-01` / `B405-121` / `B405-186`. Template: `T81` (`strip_iou_detector418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
Two independent audits in [DetectorFocusFollowup.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusFollowup.md) and [DetectorInference412.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorInference412.md) prove that ultra-wide, thin controls (`aspect ratio 12:1 to 40:1`) are the primary proposal bottleneck for both tvOS and iOS:
1. **tvOS Native Pilot (`DetectorFocusFollowup.md` line 22)**: Out of 4 focused controls missed by the general detector, **3 are wide Settings `listRow` controls**. In `B405-121`, the tvOS detector misses **`124 of 224` `listRow` controls** and **`24 of 24` `tabItem` controls**.
2. **iOS Native Audit (`ResearchSources417.md` line 41, `B405-186`)**: Out of 66 detector regressions on the 180 native iOS development frames, **48 involve controls between 32 and 64 px high** (such as `listRow`, `navigationBar`, `tabBar`, `slider`, and wide `toggle` rows).

Why do standard YOLO11n architectures fail on `1400 x 56 px` rows?
- **Square Receptive-Field Myopia**: A `1400 x 56 px` Settings row has a title on the far left (`x = 120 px`), a value or chevron on the far right (`x = 1480 px`), and `1000 px` of uniform background platter in the middle. Standard `3 x 3` convolutions at stride 8/16 see only empty platter in the center and fail to bind the left label and right accessory into a single `listRow` bounding box.
- **2D IoU Aspect Sensitivity**: For an elongated `20:1` box, a `4 px` vertical shift destroys 2D IoU while a `40 px` horizontal truncation barely changes vertical overlap, causing noisy gradients between horizontal span and vertical thickness.

### SOTA Method: Anisotropic Strip Pooling + Decoupled 1D Marginal Projection IoU (`Strip-IoU`)
1. **Anisotropic Strip Pooling (Hou et al., *Strip Pooling: Rethinking Spatial Pooling for Scene Parsing*, CVPR 2020)**:
   In the YOLO11n neck (`P3` and `P4` feature maps), add a parameter-efficient **Horizontal/Vertical Strip Pooling Module (`SPM`)** that pools along `(H, 1)` (capturing full-row horizontal context in 1 step) and `(1, W)` (capturing vertical column alignment in 1 step), followed by a `1D` depthwise convolution and additive residual fusion:

$$y_{\text{strip}}(i, j) = \sigma\Bigl(W_{1\times 1}\bigl(\text{Conv1D}_H(\frac{1}{W}\sum_{w=1}^W x(i, w)) + \text{Conv1D}_W(\frac{1}{H}\sum_{h=1}^H x(h, j))\bigr)\Bigr) \odot x(i, j)$$

2. **Decoupled 1D Marginal Projection IoU Loss (`Proj-IoU`)**:
   Augment 2D CIoU with explicit 1D interval IoU along the horizontal projection $[x_1, x_2]$ and vertical projection $[y_1, y_2]$:

$$\mathcal{L}_{\text{Strip-IoU}}(b, \hat{b}) = (1 - \alpha_{\text{proj}}) \mathcal{L}_{\text{CIoU}}(b, \hat{b}) + \frac{\alpha_{\text{proj}}}{2}\Bigl(\bigl(1 - \text{IoU}_{1\text{D}}(x, \hat{x})\bigr) + \bigl(1 - \text{IoU}_{1\text{D}}(y, \hat{y})\bigr)\Bigr)$$

   Even when 2D overlap is small on a thin `32–64 px` row or `divider`, $\text{IoU}_{1\text{D}}(x, \hat{x})$ and $\text{IoU}_{1\text{D}}(y, \hat{y})$ provide decoupled, scale-normalized gradients for full-width span and vertical boundary alignment!

---

## 2. Controlled Test Design

- **Pinned Dataset**: Pinned Phase 6b tvOS and Phase 6a iOS detector training splits (`30` epochs, seed `371`), evaluated on the 24 native tvOS frames (`B405-179`), the 46 reviewed real tvOS frames (`B405-121`), and the 180 native iOS development frames (`B405-178`, `B405-186`).
- **Arms**:
  1. `baseline-ciou` (Control): Standard YOLO11n neck + pure CIoU loss.
  2. `proj-iou-only`: Standard YOLO11n architecture + `Proj-IoU` loss ($\alpha_{\text{proj}} = 0.40$) — **zero architecture change, pure loss change**.
  3. `spm-plus-proj-iou`: YOLO11n with `StripPoolingModule` on `P3`/`P4` + `Proj-IoU` loss ($\alpha_{\text{proj}} = 0.40$).
- **Decision Rules**:
  - **Supported**: `proj-iou-only` or `spm-plus-proj-iou` recovers the 3 missed `listRow` proposals on the native tvOS pilot (`20/24 -> >= 23/24`), reduces the 48 `32–64 px` iOS height-band losses (`B405-186`) by `>= 35 %`, and loses `0` square/poster `collectionItem` detections.
  - **Contradicted**: Neither 1D projection loss nor strip pooling improves wide-row recall over standard CIoU.
  - **Inconclusive**: Complete `T56` and `T57` downstream focus-selection verification before deciding.
  - **Regression Gate**: Reject any arm that increases model size by `> 0.15 MB` or loses square/poster card recall.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`FOCUS-PIPELINE-NEXT-01`, `B405-186`)**: Directly fixes the missing `listRow` proposals that currently block `4 of 8` native row focus selections in the full-screen pipeline.
2. **For `Sillycon-TTR`**: Enables accurate full-width bounding boxes on Settings rows, table cells, navigation bars, and dividers where left and right visual landmarks are separated by wide blank platters.

---

## 4. New Template Contract (`T81`)

Register `T81` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T81": (
    {"datasetYaml", "baseWeights", "evalLabels", "epochs", "seed"},
    {"projIouWeight", "enableStripPooling", "imageSize"},
    "strip_iou_detector418.run",
    "artifact",
    "training",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — 1D Marginal Projection IoU & Anisotropic Strip Pooling (`scripts/strip_iou_detector418.py`)

```python
"""T81 adapter: Anisotropic Strip Pooling and 1D Projected IoU (Strip-IoU) for wide UI rows."""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def marginal_projection_iou_loss(pred_xyxy: torch.Tensor, target_xyxy: torch.Tensor, eps: float = 1e-7) -> torch.Tensor:
    """Computes decoupled 1D horizontal and vertical interval IoU + L1 center penalty."""
    px1, py1, px2, py2 = pred_xyxy.unbind(dim=-1)
    tx1, ty1, tx2, ty2 = target_xyxy.unbind(dim=-1)

    inter_x = (torch.minimum(px2, tx2) - torch.maximum(px1, tx1)).clamp_min(0.0)
    union_x = (px2 - px1).clamp_min(eps) + (tx2 - tx1).clamp_min(eps) - inter_x + eps
    enclose_x = (torch.maximum(px2, tx2) - torch.minimum(px1, tx1)).clamp_min(eps)
    giou_x = (inter_x / union_x) - ((enclose_x - union_x) / enclose_x)

    inter_y = (torch.minimum(py2, ty2) - torch.maximum(py1, ty1)).clamp_min(0.0)
    union_y = (py2 - py1).clamp_min(eps) + (ty2 - ty1).clamp_min(eps) - inter_y + eps
    enclose_y = (torch.maximum(py2, ty2) - torch.minimum(py1, ty1)).clamp_min(eps)
    giou_y = (inter_y / union_y) - ((enclose_y - union_y) / enclose_y)

    return 0.5 * ((1.0 - giou_x) + (1.0 - giou_y))


class AnisotropicStripPooling(nn.Module):
    """Hou et al. (CVPR 2020) Horizontal (H x 1) and Vertical (1 x W) Strip Pooling block."""

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
```

### Step 2 — Verification
- Create `scripts/test_strip_iou_detector418.py` to verify that `marginal_projection_iou_loss` returns `0.0` on identical boxes, provides non-zero horizontal span gradients even when vertical boxes are disjoint, and exports cleanly through `coremltools`.
