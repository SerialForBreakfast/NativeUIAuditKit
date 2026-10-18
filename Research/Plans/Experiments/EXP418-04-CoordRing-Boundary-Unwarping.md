# EXP418-04 — Coordinate-Aware Boundary-Strip Unwarping (`CoordRing`, `B405-232` / Template `T70`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Representations` (`REP`). Priority: `P1`.
Parent task: `B405-075` / `B405-077`. Template: `T70` (`coord_ring_crop418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Backlog410.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Backlog410.md) (`B405-073`, `B405-074`, `B405-075`, `B405-114`), `Maximum-mini-NUIAK` established three critical properties of `FocusRingClassifier`:
1. The model is extremely sensitive to vertical boundary alignment (`2 px` vertical shift or `+4 px` height change loses up to `66 of 72` selections).
2. `aspect-fit` letterboxing (`B405-114`) fails because variable black padding shifts global BatchNorm statistics and edge positions.
3. Stretching a crop with `0.16` expansion into `256 x 256` works well for near-square posters, but severely distorts extreme aspect ratios: on a `1400 x 64 px` Settings row, the `0.16` horizontal expansion (`224 px` per side) and vertical expansion (`10 px` per side) map to the same `31 px` margin in `256 x 256`, making the vertical ring stroke 22 times thicker in model pixels than the horizontal ring stroke!

### SOTA Method: CoordConv Boundary Distance Encoding + Canonical Perimeter Strip Unwarping
Inspired by **CoordConv** (Liu et al., *An Intriguing Failing of Convolutional Neural Networks and the CoordConv Solution*) and **Polar / Perimeter Boundary Unwrapping** for contour classification:
1. **Signed Boundary-Distance Channels (`coord-5ch`)**: Append two deterministic geometry channels to the `256 x 256` RGB tensor:
   - Channel 3: Signed horizontal distance from the true control body edge $d_x(u, v) \in [-1, +1]$ (`0.0` at the body left/right boundary, `+1.0` at the outer crop edge, `< 0` inside the control body).
   - Channel 4: True pixel aspect ratio and vertical signed distance $d_y(u, v) \in [-1, +1]$ scaled by physical stroke thickness.
2. **Canonical Perimeter-Ring Unwarping (`perimeter-strip`)**: Sample the 4 border bands (Top, Bottom, Left, Right) around the control body at isotropic physical thickness (`24 px` inward body + `32 px` outward halo = `56 px` band depth) and tile them into a `256 x 256` canvas without aspect-ratio compression of the stroke thickness.

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Providing explicit boundary-distance coordinates (`coord-5ch`) or isotropic perimeter strips (`perimeter-strip`) improves focus classification on wide Settings rows, compact buttons, and tall cards while preserving 100 % of poster successes.

### Experimental Arms
All arms use the matched `NCTRL417` training and development membership (`7,200` samples per epoch), seed `371`, 30 epochs, and fixed-last selection:
1. `control` (`encoding = 'rgb-stretch'`): Standard 3-channel stretched `0.16` crop.
2. `coord-5ch` (`encoding = 'coord-5ch'`): 5-channel `MobileNetV4ConvSmall` where channels 0–2 load `fdr038-retention234` weights and channels 3–4 of `conv_stem` initialize to `0.0` (guaranteeing exact functional equivalence at step 0).
3. `rgb-ring-mask` (`encoding = 'rgb-ring-mask'`): 3-channel input that attenuates the interior content core (`> 24 px` inside the body) by `50 %` so the classifier cannot overfit to interior artwork textures (`B405-043`).
4. `perimeter-strip` (`encoding = 'perimeter-strip'`): 3-channel unwarped isotropic border strips (`4 x 64 x 256` bands stacked vertically into `256 x 256`).

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: An encoding arm gains `>= 6` selections across native wide rows, buttons, and tall controls, maintains `0` losses on retained poster groups (`HCF402`), and keeps `<= 2 px` box-shift losses at `0`.
- **Contradicted**: Every alternative encoding loses poster successes or increases sensitivity to `2 px` box shifts.
- **Inconclusive**: Any arm fails to complete 30 epochs or evaluation on reserved groups.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` solves the fundamental geometry problem of classifying focus across aspect ratios ranging from `1:1` icons to `22:1` full-width list rows.
  - `rgb-ring-mask` and `perimeter-strip` keep `in_chans = 3`, requiring zero changes to the Core ML image input signature in `NativeUIDetectionSession`. If `coord-5ch` wins, `FocusRingClassifier.swift` can pass a `1 x 5 x 256 x 256` `MLMultiArray` or bake the fixed `0.16` coordinate grid as a constant buffer inside the Core ML graph!
- **If Contradicted**:
  - `Maximum-mini-NUIAK` confirms that the standard `0.16` stretched RGB crop with `±2 px` jitter is already optimal for `MobileNetV4ConvSmall`.

---

## 4. Template `T70` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T70': (
    {'configuration', 'initialization', 'membership'},
    {'encoding', 'seed'},
    'coord_ring_crop418.run',
    'training',
    'training',
),
```

### Inputs and Parameters
- **Inputs**:
  - `configuration`: Pinned JSON configuration (`coord-ring-config-v1`).
  - `initialization`: Pinned starting checkpoint (`fdr038-retention234/weights/best.pt`).
  - `membership`: Pinned `crops.json` manifest.
- **Parameters**:
  - `encoding`: `str` in `{'rgb-stretch', 'coord-5ch', 'rgb-ring-mask', 'perimeter-strip'}`.
  - `seed`: `int` in `{371, 372, 373}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T70",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-181-coordring",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the matched mixed artwork and native-control corpus, does coordinate-aware boundary encoding (coord-5ch, rgb-ring-mask, or perimeter-strip) improve wide-row and tall-control focus selection without losing poster successes?",
  "decision": "Support an encoding that gains at least 6 correct selections on wide rows, buttons, and tall controls with 0 lost successes on retained poster groups.",
  "outcomes": {
    "supported": "Adopt the winning boundary representation for multi-family FocusRing training and test Core ML export.",
    "contradicted": "Keep the 3-channel 0.16 stretched RGB crop representation.",
    "inconclusive": "Complete all 4 arms and T37/T41 evaluations before deciding."
  },
  "shared": {
    "inputs": {
      "configuration": {"file": "Research/ResearchSpecs/EXP418/t58-coord-ring-config.json"},
      "initialization": {"file": "NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt"},
      "membership": {"job": "nctrl417-membership-mixed", "output": "crops.json"}
    },
    "parameters": {"seed": 371}
  },
  "arms": [
    {"id": "control", "job": "nctrl417-train-mixed"},
    {"id": "coord-5ch", "label": "5-channel RGB + signed boundary distance", "parameters": {"encoding": "coord-5ch"}},
    {"id": "rgb-ring-mask", "label": "3-channel RGB with 50% interior core attenuation", "parameters": {"encoding": "rgb-ring-mask"}},
    {"id": "perimeter-strip", "label": "3-channel unwarped 4-side perimeter strips", "parameters": {"encoding": "perimeter-strip"}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/coord_ring_crop418.py`**:
   - Implement deterministic tensor transforms for `rgb-stretch`, `coord-5ch`, `rgb-ring-mask`, and `perimeter-strip`.
   - For `coord-5ch`, construct `MobileNetV4ConvSmall(num_classes=1, in_chans=5)`, copy the 3-channel `conv_stem.weight` into `[:, :3, :, :]`, and zero-initialize `[:, 3:, :, :]`.
   - Score each trained model on the development splits and write `benchmark_summary.json`.
2. **Create `scripts/test_coord_ring_crop418.py`**:
   - Verify that at initialization (step 0), `coord-5ch` outputs identical logits (`max diff == 0.0`) to the 3-channel model on any RGB crop.
   - Verify shape invariants and deterministic reproducibility across all 4 encodings.

### Reference Adapter Code (`scripts/coord_ring_crop418.py`)
```python
"""T70: Coordinate-aware boundary distance and perimeter-strip crop representations."""
import torch
from torch import nn
import research_queue as q

OUT = None
ENCODINGS = ('rgb-stretch', 'coord-5ch', 'rgb-ring-mask', 'perimeter-strip')
SEEDS = (371, 372, 373)
EXPANSION = 0.16


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'encoding', 'seed'}, 'coord_ring_parameters')
    enc, seed = value['encoding'], value['seed']
    q.require(enc in ENCODINGS, 'encoding_invalid')
    q.require(seed in SEEDS, 'seed_invalid')
    return enc, int(seed)


def boundary_grid(size: int = 256, expansion: float = EXPANSION, device: str = 'cpu') -> torch.Tensor:
    """Return [2, size, size] signed distance to the nominal body edge in a 0.16 expanded crop."""
    margin = expansion / (1.0 + 2.0 * expansion)
    coords = torch.linspace(0.0, 1.0, size, device=device)
    yy, xx = torch.meshgrid(coords, coords, indexing='ij')
    dx = torch.maximum(margin - xx, xx - (1.0 - margin)) / margin
    dy = torch.maximum(margin - yy, yy - (1.0 - margin)) / margin
    return torch.stack([dx.clamp(-1.0, 1.0), dy.clamp(-1.0, 1.0)], dim=0)


def encode_crop_batch(rgb_bchw: torch.Tensor, encoding: str) -> torch.Tensor:
    """Transform [B, 3, 256, 256] crop batch into the requested representation."""
    if encoding == 'rgb-stretch':
        return rgb_bchw
    b, _, h, w = rgb_bchw.shape
    grid = boundary_grid(h, EXPANSION, device=rgb_bchw.device).unsqueeze(0).expand(b, -1, -1, -1)
    if encoding == 'coord-5ch':
        return torch.cat([rgb_bchw, grid], dim=1)
    if encoding == 'rgb-ring-mask':
        inside = (grid[:, 0:1] < -0.25) & (grid[:, 1:2] < -0.25)
        scale = torch.where(inside, torch.tensor(0.5, device=rgb_bchw.device), torch.tensor(1.0, device=rgb_bchw.device))
        return rgb_bchw * scale
    # perimeter-strip: stack top, bottom, left(rotated), right(rotated) 64x256 bands into 256x256
    band = h // 4
    top = rgb_bchw[:, :, :band, :]
    bottom = rgb_bchw[:, :, h - band:, :]
    left = rgb_bchw[:, :, :, :band].transpose(-2, -1)
    right = rgb_bchw[:, :, :, w - band:].transpose(-2, -1)
    return torch.cat([top, bottom, left, right], dim=2)
```

### Resource and Time Budget
- **Preparation**: 60 min to 120 min.
- **Execution**: 3 new training runs (about 550 s each, 1,800 s ceiling, 2 GiB cap) plus evaluation jobs.
- **Review**: 15 min via `backlog_pipeline.py review`.
