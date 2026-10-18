# EXP418-03 — Within-Screen Set-Contrastive Focus Ranking (`B405-231` / Template `T69`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Standard FocusRing` (`FR`). Priority: `P0`.
Parent task: `GROOM-20261017` / `B405-177`. Template: `T69` (`set_contrastive_focus418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Groom20261017.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Groom20261017.md) (`B405-169`, `B405-176`), `Maximum-mini-NUIAK` observed that:
- The jitter crop model scores `0 of 16` on native selected-tab frames (`B405-169`, all scores `<= 0.21`) and `0 of 24` on native button, row, and unselected tab frames (`B405-176`, max scores `0.01` to `0.72`).
- Even the retained model misses 4 focused tabs because their independent sigmoid probabilities land just below the fixed `0.85` threshold (`0.78` to `0.84`), while unfocused tabs on the same screen score `< 0.05`.
- On screens with decorative white borders (`B405-005`) or selected-but-unfocused tabs (`B405-027`), scoring each crop in isolation ignores the baseline visual style of the rest of the screen.

### SOTA Method: Supervised Contrastive Learning (SupCon) + Plackett-Luce Set Ranking (ListMLE)
Focus on tvOS is a **within-screen relational property**: at most 1 element on a screen holds focus, and its focus cue (scale growth, drop shadow, platter brightness, or HCF ring) stands out *relative to peer controls in the same layout region*.

This experiment combines two SOTA objectives on top of `MobileNetV4ConvSmall`:
1. **Supervised Contrastive Loss (SupCon)** (Khosla et al., *Supervised Contrastive Learning*) on the L2-normalized 1280-d embedding $\hat{z}_i = \text{norm}(\text{norm\_head}(x_i))$, pulling focused embeddings together across control families (`artwork`, `button`, `row`, `tab`) while pushing unfocused and selected-unfocused hard negatives apart.
2. **Screen-Set Plackett-Luce / ListMLE Loss with Learnable Abstention Dustbin** (inspired by SuperGlue dustbin assignment, Sarlin et al.): for a screen $S$ with $K$ candidate crops $\{x_1, \dots, x_K\}$, append a learnable scalar dustbin logit $\tau_{\text{no-focus}}$ and minimize cross-entropy over the $(K + 1)$-way distribution:

$$\mathcal{L}_{\text{set}}(S) = -\log \frac{\exp(s_{y^*} / T)}{\sum_{k=1}^{K} \exp(s_k / T) + \exp(\tau_{\text{no-focus}} / T)}$$

where $y^* \in \{1, \dots, K\}$ for focused screens and $y^* = K + 1$ (the dustbin) for no-focus screens (`B405-004`).

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Adding within-screen set ranking (`ListMLE` + dustbin) or `SupCon` auxiliary loss to the matched `NCTRL417` training corpus eliminates threshold calibration misses across native buttons, rows, and tabs while maintaining 100 % abstention on no-focus screens.

### Experimental Arms
All arms use the exact `nctrl417-membership-mixed` training and development crops (`7,200` samples per epoch), `fdr038-retention234` initialization, seed `371`, and 30 epochs. Only `lossMode` changes:
1. `control` (`lossMode = 'bce-only'`, `temperature = 1.0`): Independent binary cross-entropy baseline (reuses `nctrl417-train-mixed`).
2. `supcon-aux` (`lossMode = 'bce-plus-supcon'`, `temperature = 0.10`): `BCE + 0.25 * SupCon` on 1280-d embeddings.
3. `set-listmle` (`lossMode = 'bce-plus-listmle'`, `temperature = 0.50`): `0.5 * BCE + 0.5 * ScreenSetListMLE` with learnable dustbin threshold.
4. `hybrid-set-supcon` (`lossMode = 'bce-supcon-listmle'`, `temperature = 0.25`): Combined `BCE + 0.20 * SupCon + 0.30 * ScreenSetListMLE`.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: The candidate improves native button, row, and tab selection over the `BCE` control on the 6 reserved development groups (`B405-177`), selects `0` selected-but-unfocused tabs (`B405-167`), abstains on 100 % of no-focus screens (`B405-164`, `HCF402`), and loses `0` retained artwork successes.
- **Contradicted**: Set ranking increases false selections on no-focus screens or loses retained artwork successes.
- **Inconclusive**: Screen-group batching drops unique crop exposure or evaluation arms remain incomplete.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` proves that native-control abstentions (`scores 0.60–0.84` vs peer scores `< 0.05`) are caused by independent scalar thresholding rather than backbone feature failure.
  - Because `MobileNetV4ConvSmall` still outputs 1 scalar logit per crop and $\tau_{\text{no-focus}}$ is a single constant (`1.7346` at $p = 0.85$), the exported Core ML model remains a drop-in replacement for `FocusRingDetector.mlmodelc` in `NativeUIDetectionSession` and `Sillycon-TTR`!
- **If Contradicted**:
  - `Maximum-mini-NUIAK` knows that the 3-channel stretched crop representation itself lacks the visual features for native buttons/rows, prioritizing `EXP418-04` (`CoordRing` boundary unwarping).

---

## 4. Template `T69` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T69': (
    {'configuration', 'initialization', 'membership'},
    {'lossMode', 'temperature', 'seed'},
    'set_contrastive_focus418.run',
    'training',
    'training',
),
```

### Inputs and Parameters
- **Inputs**:
  - `configuration`: Pinned JSON training configuration (`set-contrastive-config-v1`).
  - `initialization`: Pinned starting checkpoint (`fdr038-retention234/weights/best.pt`).
  - `membership`: Pinned `crops.json` with frame and group linkage.
- **Parameters**:
  - `lossMode`: `str` in `{'bce-only', 'bce-plus-supcon', 'bce-plus-listmle', 'bce-supcon-listmle'}`.
  - `temperature`: `float` in `{0.10, 0.25, 0.50, 1.0}`.
  - `seed`: `int` in `{371, 372, 373}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T69",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-180-setrank",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the matched mixed artwork and native-control membership, does adding SupCon or within-screen ListMLE ranking with a no-focus dustbin improve native button, row, and tab focus selection without false selections on no-focus screens?",
  "decision": "Support the lossMode with the highest native-family selection count that makes 0 wrong selections, 0 selected-unfocused tab selections, and 0 losses on artwork or no-focus groups.",
  "outcomes": {
    "supported": "Adopt the winning set-contrastive objective for FocusRingDetector training and verify across seeds 372 and 373.",
    "contradicted": "Keep scalar BCE training and test T70 coordinate-aware boundary encoding.",
    "inconclusive": "Complete all training and T37 native evaluation arms before deciding."
  },
  "shared": {
    "inputs": {
      "configuration": {"file": "Research/ResearchSpecs/EXP418/t57-set-contrastive-config.json"},
      "initialization": {"file": "NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt"},
      "membership": {"job": "nctrl417-membership-mixed", "output": "crops.json"}
    },
    "parameters": {"seed": 371}
  },
  "arms": [
    {"id": "control", "job": "nctrl417-train-mixed"},
    {"id": "supcon-aux", "label": "BCE + 0.25 SupCon (T=0.10)", "parameters": {"lossMode": "bce-plus-supcon", "temperature": 0.10}},
    {"id": "set-listmle", "label": "BCE + ListMLE Dustbin (T=0.50)", "parameters": {"lossMode": "bce-plus-listmle", "temperature": 0.50}},
    {"id": "hybrid-set-supcon", "label": "BCE + SupCon + ListMLE (T=0.25)", "parameters": {"lossMode": "bce-supcon-listmle", "temperature": 0.25}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/set_contrastive_focus418.py`**:
   - Extract penultimate 1280-d features from `model.norm_head` alongside `model.classifier` logits using a forward hook (so `MobileNetV4ConvSmall` code in `focus_ring_backbone.py` stays 100 % untouched and pinned hashes do not change!).
   - Implement `supcon_loss(features, labels, temperature)` and `screen_listmle_loss(logits, labels, frame_ids, dustbin_logit, temperature)`.
   - Save `final.pt` in the exact `state_dict` format expected by `T37`, `T41`, and `T10` Core ML export.
2. **Create `scripts/test_set_contrastive_focus418.py`**:
   - Test that `lossMode = 'bce-only'` produces identical gradients and weights to `train_native_hcf`.
   - Test that `supcon_loss` and `screen_listmle_loss` handle single-positive screens, no-focus screens (`all labels == 0`), and single-crop degenerate sets without `NaN`.

### Reference Adapter Code (`scripts/set_contrastive_focus418.py`)
```python
"""T69: Within-screen Set-Contrastive (SupCon + ListMLE dustbin) FocusRing training."""
import math
import torch
import torch.nn.functional as F
import research_queue as q

OUT = None
MODES = ('bce-only', 'bce-plus-supcon', 'bce-plus-listmle', 'bce-supcon-listmle')
TEMPS = (0.10, 0.25, 0.50, 1.0)
SEEDS = (371, 372, 373)


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'lossMode', 'temperature', 'seed'}, 'set_contrastive_params')
    mode, temp, seed = value['lossMode'], value['temperature'], value['seed']
    q.require(mode in MODES, 'loss_mode_invalid')
    q.require(temp in TEMPS, 'temperature_invalid')
    q.require(seed in SEEDS, 'seed_invalid')
    return mode, float(temp), int(seed)


def supcon_loss(embeddings: torch.Tensor, labels: torch.Tensor, temperature: float = 0.10) -> torch.Tensor:
    """Supervised contrastive loss over L2-normalized [B, D] embeddings."""
    z = F.normalize(embeddings, p=2, dim=-1)
    sim = torch.matmul(z, z.T) / temperature
    b = labels.shape[0]
    eye = torch.eye(b, device=labels.device, dtype=torch.bool)
    same_class = (labels.unsqueeze(0) == labels.unsqueeze(1)) & (~eye)
    if not same_class.any():
        return embeddings.sum() * 0.0
    logits_max, _ = torch.max(sim.masked_fill(eye, -1e9), dim=1, keepdim=True)
    logits = sim - logits_max.detach()
    exp_logits = torch.exp(logits).masked_fill(eye, 0.0)
    log_prob = logits - torch.log(exp_logits.sum(dim=1, keepdim=True) + 1e-7)
    pos_counts = same_class.float().sum(dim=1).clamp(min=1.0)
    mean_log_prob_pos = (same_class.float() * log_prob).sum(dim=1) / pos_counts
    valid = same_class.any(dim=1).float()
    return -(valid * mean_log_prob_pos).sum() / valid.sum().clamp(min=1.0)


def batch_screen_listmle(
    logits: torch.Tensor,
    labels: torch.Tensor,
    frame_ids: list[str],
    dustbin_logit: float = 1.7346,
    temperature: float = 0.50,
) -> torch.Tensor:
    """Compute Plackett-Luce NLL across candidate crops grouped by screen frame_id."""
    losses = []
    unique_frames = sorted(set(frame_ids))
    for fid in unique_frames:
        idx = [i for i, f in enumerate(frame_ids) if f == fid]
        if len(idx) < 2 and labels[idx[0]].item() > 0.5:
            continue
        sub_logits = logits[idx].reshape(-1) / temperature
        sub_labels = labels[idx].reshape(-1)
        dust = torch.tensor([dustbin_logit / temperature], device=logits.device, dtype=logits.dtype)
        all_scores = torch.cat([sub_logits, dust], dim=0)
        pos = (sub_labels > 0.5).nonzero(as_tuple=False).reshape(-1)
        target_idx = int(pos[0].item()) if pos.numel() == 1 else len(all_scores) - 1
        target = torch.tensor([target_idx], device=logits.device, dtype=torch.long)
        losses.append(F.cross_entropy(all_scores.unsqueeze(0), target))
    if not losses:
        return logits.sum() * 0.0
    return torch.stack(losses).mean()
```

### Resource and Time Budget
- **Preparation**: 45 min to 90 min.
- **Execution**: 3 new training jobs (about 550 s each, 1,800 s ceiling, 2 GiB cap) plus T37 native and artwork regression jobs.
- **Review**: 15 min via `backlog_pipeline.py review`.
