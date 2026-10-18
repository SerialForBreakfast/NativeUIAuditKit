# EXP418-17 — Background-Inpainted Contextual Counterfactual Crops (`ContextSwap`, `B405-245` / Template `T83`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Representations` (`REP`). Priority: `P1`.
Parent task: `B405-198` / `RD07` / `TTRMatchedConsumer.md`. Template: `T83` (`context_counterfactual_crops418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [ResearchDiscovery417.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/ResearchDiscovery417.md) (`B405-198`) and [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md), `Maximum-mini-NUIAK` identified a crucial open question:
- Production cropping expands every control bounding box by `0.16` (`16 %` of width and height on each side) before resizing to `256 x 256`.
- On dense screens (`Sillycon-TTR` Standard archive with `16` false positives, small Standard decoration with `1` wrong selection, and adjacent tab bars), the `0.16` outer ring includes **neighboring controls, section dividers, and high-contrast background edges**.
- Earlier margin sweeps (`B405-075`, `0.08` vs `0.16` vs `0.24`) changed the **effective pixel scale of the control** inside the `256 x 256` tensor, confounding context removal with control magnification!

As stated in `ResearchDiscovery417.md` line 19:
> "`B405-198` isolates context without resizing the control. It differs from earlier margin tests that change effective control scale."

### SOTA Method: Concentric Tri-Zone Causal Decomposition & Telea Harmonic Context Inpainting
Inspired by **Counterfactual Visual Explanations** (Goyal et al., ICML 2019) and **Fast Marching Harmonic Inpainting** (Telea, *An Image Inpainting Technique Based on the Fast Marching Method*):
Given a `256 x 256` crop produced with the standard `0.16` margin, the true control body occupies the central `[35, 221] x [35, 221]` box. We partition the `256 x 256` pixel grid into three exact concentric zones without changing control scale by a single pixel:
1. **Interior Body Zone $Z_{\text{in}}$**: `[41, 215] x [41, 215]` (control content inside the boundary).
2. **Focus Boundary Halo Zone $Z_{\text{halo}}$**: `[23, 233] x [23, 233] \setminus Z_{\text{in}}$ (the `18 px` band straddling the control edge where OS focus rings, specular borders, and drop shadows physically live).
3. **Outer Context Zone $Z_{\text{ctx}}$**: `[0, 256] x [0, 256] \setminus [23, 233]^2$ (the outer `23 px` border where neighbor controls, dividers, and background clutter appear).

We perform three zero-resizing causal interventions on cached crops:
- **Intervention A (`ctx-harmonic-neutral`)**: Replace $Z_{\text{ctx}}$ with the radial outward harmonic clamping of the outer boundary of $Z_{\text{halo}}$ smoothed with a $1\text{D}$ tangential Gaussian filter, removing neighbor control edges from $Z_{\text{ctx}}$ while keeping $Z_{\text{in}} \cup Z_{\text{halo}}$ 100 % bit-identical.
- **Intervention B (`ctx-transplant`)**: Swap $Z_{\text{ctx}}$ between focused and unfocused peer controls from the same screen.
- **Intervention C (`interior-neutral`)**: Replace $Z_{\text{in}}$ with its mean RGB color while keeping $Z_{\text{halo}} \cup Z_{\text{ctx}}$ 100 % bit-identical.

---

## 2. Controlled Test Design

- **Pinned Dataset**: The 20 `Sillycon-TTR` Standard archive crops (`B405-205`), the 8 full-screen development case sets (`B405-208`: rows, tabs, buttons, small decoration, diamond decoration, tall controls, edge clearance, no-focus), and retained artwork crops.
- **Arms**:
  1. `original-crop` (Control): Unmodified `0.16`-margin `256 x 256` crops.
  2. `ctx-harmonic-neutral`: Outer context zone $Z_{\text{ctx}}$ neutralized at fixed control scale.
  3. `ctx-transplant`: Outer context zone $Z_{\text{ctx}}$ swapped with same-screen distractors.
  4. `interior-neutral`: Interior body zone $Z_{\text{in}}$ neutralized to isolate halo-only sensitivity.
- **Decision Rules**:
  - **Supported**: If `ctx-harmonic-neutral` eliminates the small-decoration wrong selection and reduces the `16` `Sillycon-TTR` false positives by `>= 50 %` while preserving `>= 98 %` of true focused selections, outer neighbor bleed in $Z_{\text{ctx}}$ is the proven cause; adopt `ctx-harmonic-neutral` masking in preprocessing and training (`B405-198`).
  - **Contradicted**: If false positives remain unchanged under `ctx-harmonic-neutral` but disappear under `interior-neutral`, the false positives come from interior control platter/text appearance rather than surrounding context.
  - **Inconclusive**: Run both the baseline checkpoint and the `12.5 %` / `25 %` native candidates across all 4 arms before deciding.
  - **Regression Gate**: Do not modify $Z_{\text{halo}}$ pixels or resize the control body in any intervention.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`B405-198`)**: Delivers an exact causal attribution breakdown ($\Delta \text{score}_{\text{ctx}}$ vs $\Delta \text{score}_{\text{halo}}$ vs $\Delta \text{score}_{\text{in}}$) for every false positive and missed focus case in **under 30 seconds** without new captures or training.
2. **For `Sillycon-TTR`**: Determines whether masking outside neighbor boxes before cropping (`ctx-harmonic-neutral`) immediately cleans up live-screen false positives on crowded menus.

---

## 4. New Template Contract (`T83`)

Register `T83` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T83": (
    {"cropsManifest", "model"},
    {"interventionMode", "haloOuterPx", "bodyInnerInsetPx"},
    "context_counterfactual_crops418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Scale-Preserving Concentric Zone Intervention (`scripts/context_counterfactual_crops418.py`)

```python
"""T83 adapter: Scale-preserving concentric zone counterfactual crop interventions (B405-198)."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


def apply_concentric_intervention(
    crop_rgb: np.ndarray,
    mode: str,
    halo_outer_px: int = 23,
    body_inner_inset_px: int = 41,
    donor_rgb: np.ndarray | None = None,
) -> np.ndarray:
    """Applies a scale-preserving intervention to Z_ctx or Z_in while keeping Z_halo bit-identical."""
    assert crop_rgb.shape == (256, 256, 3) and crop_rgb.dtype == np.uint8
    out = crop_rgb.copy()
    h0, h1 = halo_outer_px, 256 - halo_outer_px
    b0, b1 = body_inner_inset_px, 256 - body_inner_inset_px

    if mode == "original-crop":
        return out
    if mode == "ctx-harmonic-neutral":
        # Clamp halo outer perimeter outward into Z_ctx and smooth tangentially
        clamped = out.astype(np.float32)
        clamped[:h0, h0:h1] = clamped[h0 : h0 + 1, h0:h1]
        clamped[h1:, h0:h1] = clamped[h1 - 1 : h1, h0:h1]
        clamped[:, :h0] = clamped[:, h0 : h0 + 1]
        clamped[:, h1:] = clamped[:, h1 - 1 : h1]
        smoothed = gaussian_filter(clamped, sigma=(6.0, 6.0, 0.0))
        out[:] = np.clip(np.rint(smoothed), 0, 255).astype(np.uint8)
        # Restore Z_halo and Z_in bit-identically
        out[h0:h1, h0:h1] = crop_rgb[h0:h1, h0:h1]
        return out
    if mode == "ctx-transplant":
        assert donor_rgb is not None and donor_rgb.shape == crop_rgb.shape
        out[:] = donor_rgb
        out[h0:h1, h0:h1] = crop_rgb[h0:h1, h0:h1]
        return out
    if mode == "interior-neutral":
        mean_color = np.rint(crop_rgb[b0:b1, b0:b1].mean(axis=(0, 1))).astype(np.uint8)
        out[b0:b1, b0:b1] = mean_color
        return out
    raise ValueError(f"Unsupported interventionMode: {mode}")
```

### Step 2 — Verification
- Create `scripts/test_context_counterfactual_crops418.py` to verify that `ctx-harmonic-neutral` and `ctx-transplant` keep every pixel in `[halo_outer_px : 256 - halo_outer_px, halo_outer_px : 256 - halo_outer_px]` 100 % bit-identical (`np.array_equal`) to `crop_rgb`.
