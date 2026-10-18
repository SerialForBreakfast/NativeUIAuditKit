# EXP418-14 — Helmholtz Free-Energy and Split Conformal Abstention Calibration (`B405-242` / Template `T80`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Standard FocusRing` (`FR`). Priority: `P0`.
Parent task: `B405-182` / `PAPER417-STATES` / `OR09` / `PM01`. Template: `T80` (`conformal_energy_abstention418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [DetectorFocusFollowup.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusFollowup.md), [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md), and [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) (`PAPER417-STATES`, `B405-182`), `Maximum-mini-NUIAK` identified four distinct failure states that the current scalar `0.85` crop threshold and single-winner rule conflate:
1. **Verified No-Focus Screen (`HCF402`, `B405-164`)**: No control on the screen has OS focus.
2. **Missing Focused Proposal (`DetectorFocusFollowup.md` line 22)**: A control has focus, but the detector missed its box (4 of 24 pilot frames), causing an unfocused competing row to be falsely selected!
3. **Ambiguous Multi-Candidate Competition (`DetectorFocusFollowup.md` line 23)**: Multiple proposals score above `0.85` (1 row and 2 tabs), causing abstention or wrong picks.
4. **Out-of-Distribution / Unfamiliar Screen (`TTRMatchedConsumer.md` line 13)**: On the 4 `Sillycon-TTR` archive frames, the `25 %` mixed candidate marks `16` unfocused crops above `0.85` because the screen style shifts all logits upward.

### SOTA Method: Helmholtz Free-Energy OOD Detection + Split Conformal Prediction Set Calibration
This fast, training-free diagnostic combines two SOTA uncertainty frameworks on cached `T57` / `T63` model logits and embeddings:
1. **Screen-Level Helmholtz Free Energy & Logit Margin Normalization** (Liu et al., *Energy-based Out-of-Distribution Detection*, NeurIPS 2020):
   For a screen with $M$ candidate crops producing logits $\mathbf{z} = (z_1, \dots, z_M)$ sorted such that $z_{(1)} \ge z_{(2)} \ge \dots \ge z_{(M)}$:
   - **Baseline Screen Energy**: $E_{\text{bg}}(\mathbf{z}) = \text{median}_{i > 1}(z_{(i)})$ measures the screen's background false-alarm drift (which jumps from `-4.2` on synthetic screens to `+2.1` on the `Sillycon-TTR` archive frames!).
   - **Peak-to-Peer Energy Margin**: $\Delta E(\mathbf{z}) = z_{(1)} - T \log \sum_{j=2}^M \exp(z_{(j)} / T)$ measures whether the top candidate stands out above the screen's competing candidates.
2. **Split Conformal Prediction Sets for Guaranteed Risk Control** (Angelopoulos & Bates, *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification*):
   - On a pinned **calibration split** $\mathcal{D}_{\text{cal}}$ (`CALIBRATION102`), define the non-conformity score for candidate $i$ on screen $s$:

$$s(x_{s, i}) = 1 - \frac{\exp(z_{s, i} / T)}{\exp(z_{s, 0} / T) + \sum_{j=1}^{M_s} \exp(z_{s, j} / T)}$$

   - Compute the finite-sample conformal quantile $\hat{q}_{1-\alpha} = \text{Quantile}\bigl(\{s(x_{s, y_s})\}_{s \in \mathcal{D}_{\text{cal}}}, \frac{\lceil (n_{\text{cal}} + 1)(1 - \alpha) \rceil}{n_{\text{cal}}}\bigr)$ at risk level $\alpha \in \{0.01, 0.05\}$.
   - At test time, form the prediction set $\hat{S}(\mathcal{C}_s) = \{i \in \{1, \dots, M_s\} : s(x_{s, i}) \le \hat{q}_{1-\alpha}\}$ and classify the screen into four explicit states required by `PAPER417-STATES` (`B405-182`):
     - `certified_focus`: $|\hat{S}| == 1$ and $\Delta E(\mathbf{z}) \ge \gamma_{\text{margin}}$
     - `verified_no_focus`: $|\hat{S}| == 0$ and $\max_i z_i < \tau_{\text{null}}$
     - `ambiguous_competition`: $|\hat{S}| \ge 2$ (reports the exact competing candidates without making a false single selection)
     - `suspected_missing_proposal_or_ood`: $E_{\text{bg}}(\mathbf{z}) > \tau_{\text{ood}}$ or moderate secondary halo activation without a dominant peak.

---

## 2. Controlled Test Design

- **Pinned Dataset**: Cached `T57` and `T63` score reports across the 8 full-screen development sets (`B405-208`, `B405-210`) and the 2 `Sillycon-TTR` consumer cohorts (`B405-205`). Split calibration and evaluation strictly by `groupId` (leave-one-family-group-out cross-calibration).
- **Arms**:
  1. `fixed-085-single` (Control): Existing production rule (`score >= 0.85` and `count == 1`).
  2. `temperature-scaled`: Post-hoc temperature scaling (`PM01`) alone.
  3. `conformal-energy-v1`: Helmholtz Free-Energy screen baseline normalization + Split Conformal prediction set ($\alpha = 0.05$).
- **Decision Rules**:
  - **Supported**: `conformal-energy-v1` reduces false-positive crops on the `Sillycon-TTR` archive (`16 -> <= 2`) and eliminates wrong selections on the `row` (`3/8 -> 0/8` wrong) and `small decoration` (`1 -> 0` wrong) sets while recovering ambiguous tabs (`+2` correct selections) and preserving `6/6` `no-focus` abstentions.
  - **Contradicted**: Conformal + energy margin calibration either loses valid single selections or fails to separate `no_focus` from `ambiguous_competition`.
  - **Inconclusive**: Verify across both `12.5 %` and `25 %` model scorecards before deciding.
  - **Regression Gate**: Require `0` false selections on `no-focus` scenes and `0` lost retained baseline selections.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Sillycon-TTR` (`Autonav`)**: Distinguishes "this screen has no focus" from "2 tabs are competing for focus" and "the focused row was missed by the detector," telling `Autonav` when to re-query or scroll versus when to abstain.
2. **For `Maximum-mini-NUIAK` (`PAPER417-STATES`, `B405-182`)**: Directly satisfies the `B405-182` requirement on cached reports in **under 15 seconds** of CPU runtime with zero training or capture.

---

## 4. New Template Contract (`T80`)

Register `T80` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T80": (
    {"calibrationReports", "evaluationReports"},
    {"alpha", "temperature", "oodEnergyThreshold"},
    "conformal_energy_abstention418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Conformal & Free-Energy Evaluator (`scripts/conformal_energy_abstention418.py`)

```python
"""T80 adapter: Helmholtz Free-Energy and Split Conformal Abstention Calibration."""
from __future__ import annotations

import math
import numpy as np


def logit_from_prob(p: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    p_clip = np.clip(p, eps, 1.0 - eps)
    return np.log(p_clip / (1.0 - p_clip))


def compute_screen_energy_metrics(probs: np.ndarray, temperature: float = 1.0, null_logit: float = 0.0) -> dict[str, object]:
    """Computes screen baseline drift, Helmholtz free energy margin, and calibrated distribution."""
    if len(probs) == 0:
        return {
            "state": "verified_no_focus",
            "selectedIndex": None,
            "bgEnergy": -10.0,
            "energyMargin": -10.0,
            "calibratedProbs": [],
        }
    z = logit_from_prob(probs)
    bg_energy = float(np.median(z)) if len(z) > 1 else float(z[0])
    # Center screen baseline drift when background median exceeds calibration OOD threshold
    z_centered = z - max(0.0, bg_energy - (-1.0))
    scaled = np.concatenate([z_centered / temperature, np.array([null_logit / temperature])])
    scaled -= np.max(scaled)
    exp_s = np.exp(scaled)
    cal_probs = exp_s[:-1] / np.sum(exp_s)

    order = np.argsort(-z_centered)
    top_z = float(z_centered[order[0]])
    rest_z = z_centered[order[1:]] if len(order) > 1 else np.array([null_logit])
    lse_rest = float(temperature * np.log(np.sum(np.exp(rest_z / temperature))))
    energy_margin = top_z - lse_rest
    return {
        "bgEnergy": bg_energy,
        "energyMargin": energy_margin,
        "calibratedProbs": cal_probs.tolist(),
        "topIndex": int(order[0]),
    }


def fit_conformal_quantile(nonconformity_scores: list[float], alpha: float = 0.05) -> float:
    n = len(nonconformity_scores)
    assert n >= 4, "Need at least 4 calibration screens"
    level = min(1.0, math.ceil((n + 1) * (1.0 - alpha)) / n)
    return float(np.quantile(np.asarray(nonconformity_scores, dtype=np.float64), level, method="higher"))
```

### Step 2 — Verification
- Add unit tests in `scripts/test_conformal_energy_abstention418.py` verifying that `conformal_energy_abstention418.py` separates `verified_no_focus`, `certified_focus`, `ambiguous_competition`, and `suspected_missing_proposal_or_ood` on synthetic and cached `T57` fixtures and enforces disjoint calibration and evaluation `groupId` sets.
