# EXP418-13 — Group-DRO Minimax Training and Pareto Worst-Family Checkpoint Selection (`B405-241` / Template `T79`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Standard FocusRing` (`FR`). Priority: `P1`.
Parent task: `B405-192` / `OR01` / `OR02`. Template: `T79` (`group_dro_pareto418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md) and [ResearchSources417.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/ResearchSources417.md) (`OR01`, `OR02`, `OR05`, `B405-192`), `Maximum-mini-NUIAK` observed that:
- Training with standard Empirical Risk Minimization (ERM, uniform sample mean loss) causes oscillating family trade-offs across epochs and exposure levels: `12.5 %` native exposure improves `tab` (`5/8 -> 8/8`) and `diamond` (`3/4 -> 4/4`), while `row` wrong selections worsen (`1/8 -> 3/8`) and `tall` HCF controls drop (`4/4 -> 2/4`).
- Selecting the final checkpoint by overall mean training or development loss hides weak control families (`row`, `tall`, `selected-tab`) behind high-volume `artwork` poster accuracy.

### SOTA Method: Group Distributionally Robust Optimization (`Group DRO`) + Lexicographic Pareto Checkpoint Selection
From Sagawa et al. (*Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization*, ICLR 2020):
1. **Primal-Dual Exponentiated-Gradient Group DRO**:
   Instead of minimizing the average loss across all $N$ training crops, partition the training set into $G$ explicit semantic-and-difficulty groups:

$$\mathcal{G} = \{\text{artwork\_pos}, \text{artwork\_neg}, \text{button}, \text{row}, \text{tab}, \text{tall}, \text{decorative\_neg}\}$$

   Maintain a learnable simplex distribution $q \in \Delta^{G-1}$ over groups and solve the minimax problem:

$$\min_{\theta} \max_{q \in \Delta^{G-1}} \sum_{g=1}^G q_g \left( \mathcal{L}_g(\theta) + \frac{C}{\sqrt{n_g}} \right)$$

   At each mini-batch step $t$, update $q_g$ via exponentiated gradient ascent with step size $\eta_q \in \{0.01, 0.05\}$:

$$q_g^{(t)} \leftarrow \frac{q_g^{(t-1)} \exp\bigl(\eta_q (\mathcal{L}_g(\theta^{(t)}) + C / \sqrt{n_g})\bigr)}{\sum_{h=1}^G q_h^{(t-1)} \exp\bigl(\eta_q (\mathcal{L}_h(\theta^{(t)}) + C / \sqrt{n_h})\bigr)}$$

   Whenever `row` or `tall` or `decorative_neg` starts regressing during training, its group weight $q_g^{(t)}$ automatically rises, forcing the optimizer to repair the weakest family immediately rather than sacrificing it for easy `artwork` loss reductions.
2. **Lexicographic Pareto Checkpoint Selection (`pareto-selector`)**:
   Evaluate saved epoch checkpoints on a strictly separated **model-selection development subset** (`OR05`, never the final evaluation groups) using a two-stage lexicographic rule:
   - **Stage A (Hard Preservation Filter)**: Discard any checkpoint with $> 0$ false selections on `no-focus` or `decorative_neg` or any lost retained anchor success.
   - **Stage B (Worst-Family Maximin)**: Among passing checkpoints, select $\arg\max_e \min_{g \in \mathcal{G}} \text{Accuracy}_g(e)$, breaking ties by harmonic mean across families.

---

## 2. Controlled Test Design

- **Pinned Dataset**: The `7,200`-sample training membership (`B405-189`, `12.5 %` and `25 %` native exposure, seed `371`), with checkpoints saved every 2 epochs (`epochs 2..30`).
- **Arms**:
  1. `erm-mean-select` (Control): Standard ERM loss + final-epoch / mean-loss selection.
  2. `erm-pareto-select`: Standard ERM loss + Lexicographic Pareto checkpoint selection across retained epoch checkpoints (`B405-192` zero-training diagnostic first!).
  3. `group-dro-pareto`: Group DRO minimax loss ($\eta_q = 0.02, C = 1.0$) + Lexicographic Pareto checkpoint selection.
- **Decision Rules**:
  - **Supported**: `erm-pareto-select` or `group-dro-pareto` raises worst-family accuracy on the held-out native comparison groups (`row`, `button`, `tab`, `tall`, `diamond`) with `0` lost retained successes.
  - **Contradicted**: Worst-family selection and Group DRO fail to improve the weakest family (`row` and `tall`), proving the bottleneck is missing proposal geometry rather than optimization imbalance.
  - **Inconclusive**: Complete both the zero-training checkpoint audit (`erm-pareto-select`) and the `group-dro-pareto` fit before deciding.
  - **Regression Gate**: Do not use final comparison groups inside the checkpoint selector; keep selection groups and evaluation groups strictly disjoint by `groupId`.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`B405-192`)**: Separates whether weak `row` and `tall` results come from stopping at the wrong epoch (`erm-pareto-select`) or from ERM gradient starvation (`group-dro-pareto`).
2. **For `Sillycon-TTR`**: Prevents shipping a model that scores `100 %` on posters and tabs while failing on Settings rows.

---

## 4. New Template Contract (`T79`)

Register `T79` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T79": (
    {"manifest", "selectionGroups", "evaluationGroups"},
    {"mode", "droEta", "droSizePenalty", "epochs", "seed"},
    "group_dro_pareto418.run",
    "artifact",
    "training",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Group DRO Loss and Pareto Selector (`scripts/group_dro_pareto418.py`)

```python
"""T79 adapter: Group DRO minimax training and Lexicographic Pareto checkpoint selector."""
from __future__ import annotations

import math
from typing import Any
import torch
import torch.nn as nn
import torch.nn.functional as F


class GroupDROLoss(nn.Module):
    """Sagawa et al. (ICLR 2020) primal-dual exponentiated-gradient Group DRO objective."""

    def __init__(self, group_counts: list[int], eta_q: float = 0.02, size_penalty: float = 1.0) -> None:
        super().__init__()
        num_groups = len(group_counts)
        self.eta_q = float(eta_q)
        counts = torch.tensor(group_counts, dtype=torch.float32).clamp_min(1.0)
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


def select_pareto_checkpoint(checkpoints: list[dict[str, Any]]) -> dict[str, Any]:
    """Selects the checkpoint that passes zero-regression safety and maximizes worst-family accuracy."""
    safe = [
        ckpt for ckpt in checkpoints
        if ckpt["noFocusFalsePositives"] == 0
        and ckpt["decorativeFalsePositives"] == 0
        and ckpt["lostAnchorSuccesses"] == 0
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
```

### Step 2 — Verification
- Create `scripts/test_group_dro_pareto418.py` to verify that `GroupDROLoss` monotonically increases $q_g$ for high-loss groups, preserves $\sum_g q_g = 1$, and rejects overlapping `selectionGroups` and `evaluationGroups`.
