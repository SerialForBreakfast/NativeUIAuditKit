# EXP418-11 — Null-Space Projected Fine-Tuning (`Null-LoRA`) for Zero-Forgetting Native Adaptation (`B405-239` / Template `T77`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Standard FocusRing` (`FR`). Priority: `P0`.
Parent task: `B405-191` / `B405-195` / `TTRMatchedConsumer.md`. Template: `T77` (`nullspace_focus_train418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md) and [DetectorFocusPolicy.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusPolicy.md), `Maximum-mini-NUIAK` measured a severe stability-plasticity trade-off when adapting `FocusRingClassifier` (`MobileNetV4ConvSmall`) to native tvOS controls (`button`, `row`, `tab`):
- **At `25 %` native exposure**: The model recovers `21 of 24` known-box native controls and `4 of 4` focused `Sillycon-TTR` archive crops, **but produces 16 false positives** on the `Sillycon-TTR` Standard archive and loses the retained Standard diamond-decoration case (`score = 0.585`).
- **At `12.5 %` native exposure**: Tabs improve to `8 of 8` and Standard diamond decoration recovers (`4 of 4`), **but rows regress** (`1 of 8` wrong increases to `3 of 8` wrong) and **tall HCF controls regress** (`4 of 4` drops to `2 of 4`).

Standard gradient descent updates parameters along directions that have high variance on the retained training distribution (`artwork`, `tall`, and `diamond` hard negatives). Changing those principal directions causes catastrophic forgetting on previously solved layouts.

### SOTA Method: Orthogonal Gradient Projection / Null-Space Low-Rank Adaptation (`Null-LoRA` + `LP-FT`)
This experiment combines two state-of-the-art continual-learning methods:
1. **Linear-Probing then Fine-Tuning (`LP-FT`)** (Kumar et al., *Fine-Tuning Can Distort Pretrained Features and Underperform Out-of-Distribution*, ICLR 2022): Warm-start the classification head in the null space before unfreezing encoder blocks so random or misaligned head gradients do not corrupt early feature maps.
2. **Orthogonal Gradient Projection in the Retained Feature Null Space (`SGP` / `O-LoRA`)** (Saha et al., *Gradient Projection Memory for Continual Learning*, ICLR 2021; Wang et al., *Orthogonal Subspace Learning for Language Model Continual Learning*):
   - Given the retained anchor training set $\mathcal{D}_{\text{anchor}}$ (artwork posters, tall controls, and decorative-border hard negatives), extract the input activation matrix $X_l \in \mathbb{R}^{N \times d_l}$ at each adapted linear/pointwise layer $l$.
   - Compute the Singular Value Decomposition (SVD) of the uncentered covariance $X_l^\top X_l = U_l \Sigma_l U_l^\top$ and retain the top-$k_l$ eigenvectors $U_{l, k}$ that capture $\tau_{\text{energy}} \in \{0.95, 0.99\}$ of the retained spectral energy:

$$\frac{\sum_{i=1}^{k_l} \sigma_i}{\sum_{j=1}^{d_l} \sigma_j} \ge \tau_{\text{energy}}$$

   - Define the **Null-Space Projector** $P_{l, \perp} = I - U_{l, k} U_{l, k}^\top$.
   - Constrain all native-adaptation weight updates $\Delta W_l$ to lie strictly in the orthogonal complement:

$$\Delta W_l^{\text{null}} = \Delta W_l \cdot P_{l, \perp}$$

By construction, for any feature vector $x \in \text{span}(U_{l, k})$ belonging to the retained principal subspace, $\Delta W_l^{\text{null}} x = 0$. The fine-tuned model preserves its exact logits on the retained subspace while using the remaining $d_l - k_l$ orthogonal dimensions to separate native `button`, `row`, and `tab` focus cues.

---

## 2. Controlled Test Design

- **Pinned Dataset**: The exact `7,200`-sample training membership (`12.5 %` and `25 %` native exposure from `PAPER417-SUBSET` / `B405-189`), evaluated on all 8 full-screen development sets (`B405-208`) and the 2 `Sillycon-TTR` consumer cohorts (`B405-205`).
- **Control (`full-ft`)**: Unconstrained full fine-tuning at `25 %` native exposure (`30` epochs, seed `371`).
- **Candidate Arms**:
  1. `lp-ft`: 5 epochs linear probe + 25 epochs full fine-tuning (`OR03`).
  2. `null-proj-95`: 5 epochs linear probe + 25 epochs orthogonal gradient projection with $\tau_{\text{energy}} = 0.95$.
  3. `null-proj-99`: 5 epochs linear probe + 25 epochs orthogonal gradient projection with $\tau_{\text{energy}} = 0.99$.
- **Single Changed Variable**: Orthogonal subspace energy threshold $\tau_{\text{energy}}$ and `LP-FT` warm-up schedule.
- **Decision Rules**:
  - **Supported**: `null-proj-95` or `null-proj-99` retains `4/4` on Standard diamond decoration, `4/4` on tall HCF controls, and `0` added false positives on the `Sillycon-TTR` Standard archive while matching or beating the `16/24` detector-box native selection count.
  - **Contradicted**: Projecting out the top $95\%$ retained subspace blocks native `button`/`row`/`tab` learning (native selections drop below `12/24`).
  - **Inconclusive**: Complete all 8 full-screen comparison sets (`T57`) before deciding.
  - **Regression Gate**: Reject any arm that loses the Standard diamond-decoration case, loses any tall control, or triggers false positives on `no-focus` scenes.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Sillycon-TTR` (`MODEL-DIST-02`)**: Explains whether the `16` false positives on TTR Standard archive crops were caused by encoder feature drift during unconstrained native fine-tuning, and delivers a single unified checkpoint that needs no runtime older-model fallback (`B405-203`).
2. **For `Maximum-mini-NUIAK` (`B405-191`, `B405-195`)**: Replaces heuristic teacher weight tuning with an exact linear-algebraic null-space projection that has zero hyper-parameter sensitivity at inference time and adds `0` bytes to the exported Core ML model (`\theta_{\text{merged}} = W_0 + \Delta W^{\text{null}}`).

---

## 4. New Template Contract (`T77`)

Register `T77` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T77": (
    {"manifest", "anchorManifest", "epochs", "seed"},
    {"subspaceEnergy", "lpWarmupEpochs", "nativeDose", "batchSize"},
    "nullspace_focus_train418.run",
    "artifact",
    "training",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Subspace Basis Computation and Orthogonal Hook (`scripts/nullspace_focus_train418.py`)

```python
"""T77 adapter: Null-Space Projected Fine-Tuning (Null-LoRA + LP-FT) for FocusRingClassifier."""
from __future__ import annotations

import torch
import torch.nn as nn


class OrthogonalSubspaceProjector:
    """Projects parameter gradients onto the orthogonal complement of retained anchor activations."""

    def __init__(self, energy_threshold: float = 0.99) -> None:
        self.energy_threshold = float(energy_threshold)
        self.projectors: dict[str, torch.Tensor] = {}

    @torch.no_grad()
    def fit_anchor_subspace(
        self,
        model: nn.Module,
        anchor_loader: torch.utils.data.DataLoader,
        target_layer_names: list[str],
        device: torch.device,
    ) -> dict[str, dict[str, float]]:
        model.eval()
        cov_matrices: dict[str, torch.Tensor] = {}
        hooks = []

        def make_hook(name: str):
            def _hook(_module: nn.Module, inputs: tuple[torch.Tensor, ...], _output: torch.Tensor) -> None:
                x = inputs[0].detach()
                if x.ndim == 4:
                    # Global pool or flatten spatial positions [B, C, H, W] -> [B*H*W, C]
                    x = x.permute(0, 2, 3, 1).reshape(-1, x.shape[1])
                x = x.to(dtype=torch.float32)
                gram = x.T @ x
                cov_matrices[name] = cov_matrices[name] + gram if name in cov_matrices else gram
            return _hook

        named_modules = dict(model.named_modules())
        for name in target_layer_names:
            hooks.append(named_modules[name].register_forward_hook(make_hook(name)))

        for batch in anchor_loader:
            images = batch[0].to(device)
            model(images)

        for h in hooks:
            h.remove()

        stats: dict[str, dict[str, float]] = {}
        for name, cov in cov_matrices.items():
            u, s, _ = torch.linalg.svd(cov, full_matrices=False)
            cumulative_energy = torch.cumsum(s, dim=0) / torch.sum(s).clamp_min(1e-12)
            k = int(torch.searchsorted(cumulative_energy, self.energy_threshold).item()) + 1
            k = min(k, u.shape[1] - 1)
            u_k = u[:, :k]
            proj = torch.eye(u.shape[0], device=cov.device, dtype=torch.float32) - (u_k @ u_k.T)
            self.projectors[name] = proj
            stats[name] = {
                "totalDim": float(u.shape[0]),
                "retainedRank": float(k),
                "nullRank": float(u.shape[0] - k),
                "capturedEnergy": float(cumulative_energy[k - 1].item()),
            }
        return stats

    @torch.no_grad()
    def project_gradients(self, model: nn.Module) -> None:
        named_modules = dict(model.named_modules())
        for name, proj in self.projectors.items():
            module = named_modules[name]
            if module.weight.grad is None:
                continue
            grad = module.weight.grad
            if grad.ndim == 2:
                module.weight.grad.copy_(grad @ proj.to(grad.device, dtype=grad.dtype))
            elif grad.ndim == 4 and grad.shape[2] == 1 and grad.shape[3] == 1:
                # 1x1 pointwise convolution [C_out, C_in, 1, 1]
                c_out, c_in, _, _ = grad.shape
                projected = (grad.view(c_out, c_in) @ proj.to(grad.device, dtype=grad.dtype)).view(c_out, c_in, 1, 1)
                module.weight.grad.copy_(projected)
```

### Step 2 — Verification
- Create `scripts/test_nullspace_focus_train418.py` to verify that for any synthetic anchor batch $X$, a gradient step projected by `OrthogonalSubspaceProjector(energy_threshold=1.0)` produces $\|W_{\text{new}} X - W_{\text{old}} X\|_2 < 10^{-5}$.
