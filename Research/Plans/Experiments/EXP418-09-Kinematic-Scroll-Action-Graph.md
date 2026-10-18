# EXP418-09 — Kinematic Phase-Correlation Scroll Decoupling and Action-Graph Decoding (`B405-237` / Template `T75`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Before/after focus` (`PAIR`). Priority: `P1`.
Parent task: `FOCUS-TRANSITION-49` / `ENG405-05`. Template: `T75` (`kinematic_transition418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) (`B405-062` to `B405-066`, `B405-126`), `Maximum-mini-NUIAK` and `Sillycon-TTR` (`Autonav`) need to classify what happened between a `before` frame $I_t$ and an `after` frame $I_{t+1}$ following a remote directional press $a_t \in \{\text{Up, Down, Left, Right}\}$:
- **Viewport Scrolling (`B405-064`)**: In a long Settings list or media grid, pressing `Down` often scrolls the entire list upward by $(\Delta x, \Delta y) = (0, -110\text{ px})$ while the focused highlight stays at the exact same screen Y coordinate (on the newly arrived item). Frame-to-frame spatial difference models confuse this with either a whole-screen change or a no-op!
- **Animated Backgrounds & Content Swaps (`B405-062`, `B405-065`)**: When a hero banner cross-fades or a preview video plays behind unfocused controls, pixel-difference models trigger false focus movements (`587` false changes in `FOCUS348` baseline).
- **Boundary No-Op Actions (`B405-063`)**: Pressing `Left` at the leftmost column produces a subtle bounce animation and returns to the same control.

### SOTA Method: Fourier Phase-Correlation Scroll Registration + Kinematic Action-Cone Decoding
Instead of feeding raw unaligned frame pairs into a black-box CNN, this experiment decomposes the two-frame transition into two explicit physical components:
1. **Sub-Pixel Fourier Phase Correlation (Foroosh et al.)**: Compute the normalized cross-power spectrum between non-hero structural regions of $I_t$ and $I_{t+1}$:

$$R(\omega_x, \omega_y) = \frac{\mathcal{F}(I_t) \cdot \mathcal{F}(I_{t+1})^*}{\bigl|\mathcal{F}(I_t) \cdot \mathcal{F}(I_{t+1})^*\bigr| + \epsilon}, \quad (\Delta x_{\text{scroll}}, \Delta y_{\text{scroll}}) = \arg\max_{(x, y)} \mathcal{F}^{-1}(R)$$

   This registers viewport translation $(\Delta x_{\text{scroll}}, \Delta y_{\text{scroll}})$ in `< 8 ms` on CPU, completely invariant to localized hero artwork cross-fades (because phase correlation measures coherent global translation peak prominence $p_{\text{peak}}$).
2. **Kinematic Action-Conditioned Graph Decoding**: Given candidate boxes $\{b_i^{(t)}\}$ and $\{b_j^{(t+1)}\}$ with single-frame crop scores and pairwise transition scores:
   - Map $b_i^{(t)}$ into scroll-compensated coordinates $\tilde{b}_i^{(t)} = b_i^{(t)} + (\Delta x_{\text{scroll}}, \Delta y_{\text{scroll}})$.
   - Enforce **Action-Cone Compatibility**: for action $a_t = \text{Down}$, a valid focus transition from $\tilde{b}_i^{(t)}$ to $b_j^{(t+1)}$ must lie within the downward kinematic half-cone ($\Delta y > 8\text{ px}$, $|\text{atan2}(\Delta x, \Delta y)| \le \theta_{\max}$) **or** exhibit coherent upward viewport scroll ($\Delta y_{\text{scroll}} < -16\text{ px}$) with focus transferring to the new item occupying slot $b_i^{(t)}$!

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Adding Fourier Phase-Correlation scroll registration and kinematic action-cone decoding to `T47` ordered-pair scoring separates `focus-moved`, `viewport-scrolled`, `no-op-boundary`, and `content-only-change` without losing any of the `106` `D1` / `FOCUS366` movement successes.

### Experimental Arms
All arms run on the pinned `D1` / `FOCUS366` development pairs (`408` pairs) plus retained scrolling, no-op, and content-change pairs using the pinned transition model (`reports/work/FOCUS-329/run/last.pt`):
1. `control` (`compensationMode = 'none'`, `actionConeDegrees = 180`): Uncompensated `T47` baseline (`temporal_pairs414.py`). Must reproduce the stored `T47` counts exactly (`106` movement successes, `0` losses).
2. `phase-scroll-only` (`compensationMode = 'phase-scroll'`, `actionConeDegrees = 180`): Align `before` boxes by $(\Delta x_{\text{scroll}}, \Delta y_{\text{scroll}})$ before scoring candidate transitions.
3. `kinematic-cone-60` (`compensationMode = 'phase-scroll-plus-cone'`, `actionConeDegrees = 60`): Scroll registration + $\pm 60^\circ$ directional cone gating when `action` metadata is present.
4. `kinematic-cone-45` (`compensationMode = 'phase-scroll-plus-cone'`, `actionConeDegrees = 45`): Scroll registration + stricter $\pm 45^\circ$ directional cone gating.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: An arm reduces false movement detections on content-only, scrolling, and no-op pairs by `>= 50 %` (or gains `>= 15` correct transition classifications) while losing `0` of the `106` baseline movement successes (`lostPriorSuccesses == []`).
- **Contradicted**: Scroll registration or action-cone gating loses baseline movement successes.
- **Inconclusive**: Pair manifests lack action or endpoint geometry metadata.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` unblocks `B405-062`, `B405-063`, `B405-064`, and `B405-065` without needing another fragile 30-epoch transition training run (`B405-126`).
  - `Sillycon-TTR` (`Autonav` and `tvos-safe-navigation`) gets a fast, closed-loop transition verifier that tells the crawler whether a remote press moved focus, scrolled the list, or hit a boundary wall.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` logs the exact pairs where focus jumps outside the $\pm 60^\circ$ cone (such as ragged grid row wraps where pressing `Down` jumps diagonally left to a wide banner) and widens the wrap rule before retraining.

---

## 4. Template `T75` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T75': (
    {'pairs', 'model'},
    {'compensationMode', 'actionConeDegrees'},
    'kinematic_transition418.run',
    'artifact',
    'diagnostic',
),
```

### Inputs and Parameters
- **Inputs**:
  - `pairs`: Pinned ordered-pair manifest (`temporal-pairs-v1`).
  - `model`: Pinned transition or crop model checkpoint.
- **Parameters**:
  - `compensationMode`: `str` in `{'none', 'phase-scroll', 'phase-scroll-plus-cone'}`.
  - `actionConeDegrees`: `int` in `{45, 60, 90, 180}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T75",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-186-kinematic",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the 408 D1 and FOCUS366 development pairs, does Fourier phase-correlation scroll registration and kinematic action-cone gating reduce false focus changes on scroll and content-change pairs while losing 0 of 106 movement successes?",
  "decision": "Support a compensationMode and actionConeDegrees that reduces false changes or recovers missed transitions with 0 lostPriorSuccesses on the 106 baseline movement successes.",
  "outcomes": {
    "supported": "Adopt phase-scroll and kinematic cone decoding in T47/T75 and expose scroll vectors in NativeUIAuditCLI pair diagnostics.",
    "contradicted": "Keep uncompensated T47 pair scoring and add diagonal grid-wrap exceptions before retesting.",
    "inconclusive": "Complete all 4 arms and verify control parity against T47."
  },
  "shared": {
    "inputs": {
      "pairs": {"file": "Research/ResearchSpecs/FOCUS366/focus366-dev-pairs.json"},
      "model": {"file": "reports/work/FOCUS-329/run/last.pt"}
    }
  },
  "arms": [
    {"id": "control", "label": "Uncompensated T47 baseline", "parameters": {"compensationMode": "none", "actionConeDegrees": 180}},
    {"id": "phase-scroll", "label": "FFT phase-correlation scroll registration", "parameters": {"compensationMode": "phase-scroll", "actionConeDegrees": 180}},
    {"id": "cone-60", "label": "Phase scroll + 60-deg action cone", "parameters": {"compensationMode": "phase-scroll-plus-cone", "actionConeDegrees": 60}},
    {"id": "cone-45", "label": "Phase scroll + 45-deg action cone", "parameters": {"compensationMode": "phase-scroll-plus-cone", "actionConeDegrees": 45}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/kinematic_transition418.py`**:
   - Wrap `temporal_pairs414.py` (`T47`) so `compensationMode = 'none'` reproduces the exact `T47` benchmark summary.
   - Implement `estimate_scroll_vector(img_before, img_after)` using Hann-windowed 2D FFT phase correlation at `480 x 270` grayscale scale.
   - Implement `action_cone_compatible(box_before, box_after, scroll_dx, scroll_dy, action, max_deg)`.
2. **Create `scripts/test_kinematic_transition418.py`**:
   - Verify sub-pixel accuracy of `estimate_scroll_vector` on synthetic shifted images (`dx = 0, dy = -48`) even when a `200 x 200` hero patch changes completely.
   - Verify `action_cone_compatible` for `Up`, `Down`, `Left`, `Right`, and `no-op` cases.

### Reference Adapter Code (`scripts/kinematic_transition418.py`)
```python
"""T75: Kinematic phase-correlation scroll registration and directional action-cone decoding."""
import math
import numpy as np
import research_queue as q

OUT = None
MODES = ('none', 'phase-scroll', 'phase-scroll-plus-cone')
CONES = (45, 60, 90, 180)
ACTION_VECTORS = {'up': (0.0, -1.0), 'down': (0.0, 1.0), 'left': (-1.0, 0.0), 'right': (1.0, 0.0)}


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'compensationMode', 'actionConeDegrees'}, 'kinematic_params')
    mode, cone = value['compensationMode'], value['actionConeDegrees']
    q.require(mode in MODES, 'kinematic_mode_invalid')
    q.require(cone in CONES, 'kinematic_cone_invalid')
    return mode, int(cone)


def estimate_scroll_fft(gray_a: np.ndarray, gray_b: np.ndarray) -> tuple[float, float, float]:
    """Compute (dx, dy, peak_snr) global scroll shift from gray_a to gray_b using Hann-windowed phase correlation."""
    h, w = gray_a.shape
    win_y = np.hanning(h)[:, None]
    win_x = np.hanning(w)[None, :]
    win = (win_y * win_x).astype(np.float32)
    fa = np.fft.rfft2((gray_a.astype(np.float32) - gray_a.mean()) * win)
    fb = np.fft.rfft2((gray_b.astype(np.float32) - gray_b.mean()) * win)
    cross = (fa * np.conj(fb)) / (np.abs(fa * np.conj(fb)) + 1e-7)
    corr = np.fft.irfft2(cross, s=(h, w))
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    peak = float(corr[py, px])
    dy = float(py - h if py > h // 2 else py)
    dx = float(px - w if px > w // 2 else px)
    return dx, dy, peak


def in_action_cone(
    c_before: tuple[float, float],
    c_after: tuple[float, float],
    action: str | None,
    max_degrees: int,
    min_step_px: float = 6.0,
) -> bool:
    """Return True if the displacement vector from c_before to c_after aligns with action within max_degrees."""
    if action not in ACTION_VECTORS or max_degrees >= 180:
        return True
    vx, vy = c_after[0] - c_before[0], c_after[1] - c_before[1]
    mag = math.hypot(vx, vy)
    if mag < min_step_px:
        return False
    ax, ay = ACTION_VECTORS[action]
    cos_theta = (vx * ax + vy * ay) / mag
    return cos_theta >= math.cos(math.radians(max_degrees))
```

### Resource and Time Budget
- **Preparation**: 45 min.
- **Execution**: 4 diagnostic jobs taking 15 s to 40 s each (within the 800 s and 100 MB standing diagnostic class).
- **Review**: 10 min via `backlog_pipeline.py review`.
