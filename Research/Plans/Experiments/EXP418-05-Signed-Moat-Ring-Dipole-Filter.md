# EXP418-05 — Signed Moat-Ring Dipole Filter for Theme-Invariant Proposals (`B405-233` / Template `T71`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Optional HCF` (`HCF`). Priority: `P0`.
Parent task: `ACTIONS417` / `B405-161`. Template: `T71` (`dipole_ring_proposals418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Groom20261017.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Groom20261017.md) (`B405-161`), `Maximum-mini-NUIAK` measured the pixel profile of focused HCF controls on light backgrounds (`4K` resolution, from outside inward):
- Background: gray level `239` to `249`
- Outer white HCF ring: gray level `255` (`13 px` wide)
- Transition band: gray level `167` to `174` (`5 px` wide)
- Inner dark moat: gray level `17` (`8 px` wide)
- Control body interior

Every existing kernel (`outer-ring-v2`, `short-side-v1`, `interpolation-high-v1`, and `inner-moat-v1`) produces **0 proposals on light backgrounds** (`0 of 4` in `B405-158` and `B405-161`). The fixed `160` brightness threshold merges the `255` ring directly into the `239–249` background!

### SOTA Method: Concentric Signed Dipole / Steerable Matched Boundary Filter
In classical and modern edge/contour detection (Canny, Marr-Hildreth LoG, and Oriented Phase Congruency / Signed Edge Dipoles), a double-band boundary (a bright outer ring paired with a dark inner moat) is a **concentric signed dipole**.

Instead of thresholding absolute grayscale intensity $I(x, y) \ge 160$, we define the radial outward-minus-inward dipole response at scale $(r_{\text{ring}}, r_{\text{moat}})$:

$$D(x, y) = \max_{\|\delta\| \le r_{\text{ring}}} I(x + \delta) - \min_{\|\eta\| \le r_{\text{ring}} + r_{\text{moat}}} I(x + \eta)$$

paired with a directional verification along the 4 box sides that checks **outward brightness > inward moat brightness**:

$$I_{\text{ring}}(\text{side}) - I_{\text{moat}}(\text{side}) \ge \Delta_{\text{dipole}} \quad \text{and} \quad \max\bigl(|I_{\text{ring}} - I_{\text{bg}}|, |I_{\text{bg}} - I_{\text{moat}}|\bigr) \ge \Delta_{\text{bg}}$$

On a dark background (`bg = 20`, `ring = 255`, `moat = 17`), $|I_{\text{ring}} - I_{\text{bg}}| = 235$. On a light background (`bg = 245`, `ring = 255`, `moat = 17`), $|I_{\text{bg}} - I_{\text{moat}}| = 228$ and $I_{\text{ring}} - I_{\text{moat}} = 238$! One unified mathematical operator detects both dark-theme and light-theme HCF rings without knowing the background theme in advance.

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Replacing the fixed `160` brightness connected-component gate with a Signed Ring-Moat Dipole filter recovers proposals and jitter crop selections on light-background HCF frames (`B405-161`) while preserving all `44 of 44` dark-background HCF proposals (`B405-172`) and keeping `0` proposals on Standard and no-focus frames.

### Experimental Arms
All arms run on the combined development bundle (the 9 retained `HCF402` captures, the 3 independent `B405-164` captures, and the light-background `HCF402` capture) and score mapped proposals with the pinned jitter seed-371 model (`jitter413-train-jitter-r2`):
1. `control` (`dipoleMode = 'frozen-inner-v1'`, `minDipoleContrast = 0.12`): Reproduces the `B405-155` / `B405-165` inner-moat kernel (`44 of 44` dark HCF, `0 of 4` light HCF).
2. `dark-moat-polarity` (`dipoleMode = 'dark-moat-component'`, `minDipoleContrast = 0.25`): Connected components on the dark moat ($I \le 64$ adjacent to $I \ge 220$ outer ring) unioned with the inner-moat kernel.
3. `signed-dipole-v1` (`dipoleMode = 'signed-dipole-v1'`, `minDipoleContrast = 0.35`): Unified concentric dipole component ($I_{\text{ring}} - I_{\text{moat}} \ge 0.35 \times 255$) with outward-ring / inward-moat ordering check on all 4 sides.
4. `signed-dipole-strict` (`dipoleMode = 'signed-dipole-v1'`, `minDipoleContrast = 0.45`): Stricter dipole contrast gate (`0.45`).

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: An arm recovers `>= 3 of 4` focused light-background HCF frames (`B405-161`) with mapped jitter selection, preserves `44 of 44` dark-background HCF selections, and produces `0` proposals on Standard and no-focus frames.
- **Contradicted**: Every dipole mode either misses the light-background frames or introduces false proposals on Standard or no-focus frames.
- **Inconclusive**: Any capture or scoring arm is incomplete.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` immediately closes `B405-158`, `B405-159`, and `B405-161` (all `P0` blockers in [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md)).
  - `Maximum-mini-NUIAK` can send a single 15-line kernel upgrade (`outer-ring-v3-dipole`) to `Maximum-mini-TTR` and `Sillycon-TTR` that supports both dark and light backgrounds!
- **If Contradicted**:
  - If dark-moat components trigger false candidates on dark UI elements inside light themes, `Maximum-mini-NUIAK` will gate the polarity branch on the frame's median background luma (`median_luma >= 180`).

---

## 4. Template `T71` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T71': (
    {'bundle', 'model', 'tool'},
    {'dipoleMode', 'minDipoleContrast'},
    'dipole_ring_proposals418.run',
    'artifact',
    'diagnostic',
),
```

### Inputs and Parameters
- **Inputs**:
  - `bundle`: Pinned JSON bundle listing dark, light, Standard, and no-focus native captures (`dipole-proposal-bundle-v1`).
  - `model`: Pinned jitter crop classifier checkpoint (`jitter413-train-jitter-r2`).
  - `tool`: Pinned `FocusRingTool` binary for production crop extraction.
- **Parameters**:
  - `dipoleMode`: `str` in `{'frozen-inner-v1', 'dark-moat-component', 'signed-dipole-v1'}`.
  - `minDipoleContrast`: `float` in `{0.12, 0.25, 0.35, 0.45}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T71",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-182-dipole",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the combined dark and light HCF development captures, does a signed ring-moat dipole proposal filter recover light-background HCF focus selections while preserving all 44 dark HCF selections and 0 Standard or no-focus proposals?",
  "decision": "Support a dipoleMode and minDipoleContrast that selects at least 3 of 4 light-background HCF frames, keeps 44 of 44 dark HCF frames, and adds 0 Standard or no-focus proposals.",
  "outcomes": {
    "supported": "Port the winning signed-dipole gate into the Swift outer-ring kernel and propose v3 to Maximum-mini-TTR.",
    "contradicted": "Use a frame median-luminance switch to enable moat inversion only when background luma exceeds 180.",
    "inconclusive": "Complete all 4 arms before deciding."
  },
  "shared": {
    "inputs": {
      "bundle": {"file": "Research/Experiments/dipole-light-dark-bundle418.json"},
      "model": {"file": "reports/work/research-queue/jobs/jitter413-train-jitter-r2/attempts/1/out/final.pt"},
      "tool": {"file": ".build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool"}
    }
  },
  "arms": [
    {"id": "control", "label": "frozen-inner-v1 (0.12)", "parameters": {"dipoleMode": "frozen-inner-v1", "minDipoleContrast": 0.12}},
    {"id": "dark-moat", "label": "dark-moat-component (0.25)", "parameters": {"dipoleMode": "dark-moat-component", "minDipoleContrast": 0.25}},
    {"id": "dipole-035", "label": "signed-dipole-v1 (0.35)", "parameters": {"dipoleMode": "signed-dipole-v1", "minDipoleContrast": 0.35}},
    {"id": "dipole-045", "label": "signed-dipole-v1 (0.45)", "parameters": {"dipoleMode": "signed-dipole-v1", "minDipoleContrast": 0.45}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/dipole_ring_proposals418.py`**:
   - Draw each `3840 x 2160` frame to `960 x 540` grayscale using high-quality bilinear/area interpolation (matching `interpolation-high-short-side-v1`).
   - Implement `dipole_candidates(gray, mode, min_contrast)` that extracts connected components and verifies concentric radial polarity (`outer_ring >= 220` and `inner_moat <= 64` with `outer_ring - inner_moat >= min_contrast * 255`) along all 4 sides using short-side sampling.
   - Map outer ring bounds to body bounds via the pinned `hcf401-fixed-mapping` insets and score crops with `FocusRingTool` + jitter model.
2. **Create `scripts/test_dipole_ring_proposals418.py`**:
   - Test that `frozen-inner-v1` reproduces the exact proposal boxes of `B405-155`.
   - Test synthetic light-background (`bg = 245, ring = 255, moat = 17`) and dark-background (`bg = 20, ring = 255, moat = 17`) rectangles, plus negative Standard cards (`bg = 245, card = 30`, no outer white ring).

### Reference Adapter Code (`scripts/dipole_ring_proposals418.py`)
```python
"""T71: Signed Moat-Ring Dipole proposal generator for light and dark HCF backgrounds."""
import numpy as np
from scipy import ndimage
import research_queue as q

OUT = None
MODES = ('frozen-inner-v1', 'dark-moat-component', 'signed-dipole-v1')
CONTRASTS = (0.12, 0.25, 0.35, 0.45)


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'dipoleMode', 'minDipoleContrast'}, 'dipole_parameters')
    mode, contrast = value['dipoleMode'], value['minDipoleContrast']
    q.require(mode in MODES, 'dipole_mode_invalid')
    q.require(contrast in CONTRASTS, 'dipole_contrast_invalid')
    return mode, float(contrast)


def verify_concentric_dipole_side(
    pix: np.ndarray,
    box: tuple[int, int, int, int],
    band: int,
    horizontal: bool,
    leading: bool,
    min_dipole: float,
) -> tuple[float, float]:
    """Verify that each side has a bright outer ring (>= 215/255) and a dark inner moat separated by min_dipole."""
    left, right, top, bottom = box
    lo, hi = (left, right) if horizontal else (top, bottom)
    span = hi - lo + 1
    inset = max(1, span // 3 if span < 48 else span // 5)
    edge = (top if leading else bottom) if horizontal else (left if leading else right)
    direction = 1 if leading else -1
    h, w = pix.shape

    def sample(along: int, across: int) -> float:
        y, x = (across, along) if horizontal else (along, across)
        y = max(0, min(h - 1, y))
        x = max(0, min(w - 1, x))
        return float(pix[y, x]) / 255.0

    supported = count = 0
    total_dipole = 0.0
    for along in range(lo + inset, hi - inset + 1):
        ring_peak = max(sample(along, edge + direction * k) for k in range(-2, band))
        moat_min = min(sample(along, edge + direction * k) for k in range(1, band + 3))
        outer_bg = sample(along, edge - direction * (band + 2))
        dipole = ring_peak - moat_min
        bg_sep = max(ring_peak - outer_bg, outer_bg - moat_min)
        if ring_peak >= (160.0 / 255.0) and dipole >= min_dipole and bg_sep >= 0.12:
            supported += 1
        total_dipole += dipole
        count += 1
    return (supported / count, total_dipole / count) if count else (0.0, 0.0)
```

### Resource and Time Budget
- **Preparation**: 45 min.
- **Execution**: 4 diagnostic jobs at 30 s to 60 s each (within the 800 s and 100 MB standing diagnostic class).
- **Review**: 10 min via `backlog_pipeline.py review`.
