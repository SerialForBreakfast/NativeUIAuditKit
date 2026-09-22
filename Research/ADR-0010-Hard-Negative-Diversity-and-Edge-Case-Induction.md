# ADR-0010: Hard-Negative Diversity, Rendering Noise, and Edge-Case Induction for FocusRing & Object Detection

- **Status:** Accepted
- **Date:** 2026-09-22
- **Deciders:** NativeUIAuditKit maintainer and architecture
- **Applies to:** FocusRingDetector (`FOCUS-DET-05`, `fdr002+`), tvOS/iOS Synthetic Generators, Fixture Training (`tvos-fixture-training`)
- **Related:** [ADR-0007](ADR-0007-VoiceOver-Navigation-Focus-Alignment.md), [ADR-0008](ADR-0008-Simulator-First-tvOS-FocusRing-Development.md), [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md), and [CurrentState.md](CurrentState.md)

---

## 1. Context & Diagnosis

During training of `fdr001` (FocusRing Stage 2 classifier) on initial live physical Apple TV captures:
- Training achieved **100% test accuracy** (270/270), 0.0 FPR, and 0.0 FNR.
- However, the hard-negative split evaluation yielded **\(n=0\)** (`focus_ring_detector_hard_negative_eval.json`).
- All 1,500 harvested pairs came exclusively from the default dark theme (`theme: "dark"`).
- Consequently, the model's apparent perfection is an artifact of **narrow, homogeneous data distribution**. In the real world, tvOS interfaces present difficult visual edge cases that fool simple brightness or contour heuristics:
  1. **Light Mode & High-Luminance Artwork:** White poster cards, bright photo thumbnails, and light-theme system panels have naturally high brightness, triggering false-positive focus classifications.
  2. **Specular Glare & HDMI/Capture Noise:** Compression artifacts, slight frame jitter, and dynamic range shifts in video capture cards mimic or mask subtle focus halo blooms.
  3. **Translucent Glassmorphism & Under-Panel Motion:** Moving backgrounds beneath blurred glass sheets (tvOS materials) create dynamic edge contrast that can be mistaken for active focus rings.
  4. **Unfocused Selected vs. Focused Unselected:** Elements that are in a "selected" state (e.g., active tab) but not currently holding remote focus, or VoiceOver focus borders distinct from interaction focus.

If synthetic or fixture-harvested datasets only test clean resting states vs. clean focused states in dark mode, the model cannot generalize to production tvOS applications.

---

## 2. Decision: Edge-Case Induction Strategy

We establish a mandatory, structured edge-case injection matrix for all subsequent training rounds (`fdr002+` and full-frame detector retraining):

### D1: Hard-Negative Quota Floor
- Any prospective candidate dataset must satisfy a strict **non-vacuous hard-negative quota**:
  - Minimum **500 hard-negative pairs** across `light` and `highContrast` themes.
  - Specifically targeted control types: `imageView` (bright artwork) and `collectionItem` (cards with white backgrounds or high internal contrast).
  - Validation splits must maintain a dedicated hard-negative stratum with verified unfocused ground truth; evaluations that report \(n=0\) hard negatives fail validation automatically.

### D2: Controlled Photometric Noise & Distortion Pipeline
To ensure models learn invariant focus ring features (specular geometry, uniform border expansion, radial bloom) rather than luminance tricks:
1. **Photometric Jitter:** Controlled contrast ($\pm 10\%$) and brightness shifts ($\pm 10\%$) applied dynamically during crop extraction.
2. **HDMI/AirPlay Compression Emulation:** Subtle Gaussian noise ($\sigma \in [0.1, 0.4]$) and JPEG/HEVC block-boundary simulation to mimic real capture card video streams.
3. **Background Luminance Inversion:** Synthetic background injection for component cards (rendering unfocused dark cards against pure white backdrops and vice-versa).
4. **Zero Geometric Distortion Rule (Preserved):** Maintain strict 16% crop padding and zero random scaling/cropping/flipping (per BP-46 and FocusRing Spec §6) to prevent corrupting the physical geometry of tvOS focus halos.

### D3: Decoupled Focus States (VoiceOver vs Interaction)
Per ADR-0007, incorporate explicit negative cases where:
- VoiceOver accessibility border is present on Item A, but interaction focus is on Item B.
- Neither item may be classified as focused by the interaction focus detector unless certified by the interaction focus engine.

---

## 3. Implementation Plan & Gate Requirements

1. **Dataset Harvest (`harvest_focus_pairs.py` / `tvos_live_harvest.py` / Direct Sim Generator):**
   - Harvest sweeps must cycle explicitly through `light`, `dark`, and `highContrast` themes in `gridMatrix` and `mediaShelf` scenes.
2. **Preflight Enforcement (`focus_training_preflight.py` & `physical_focus_readiness.py`):**
   - Assert `hard_negative_count >= 100` in the held-out test split before launching any candidate training.
3. **Evaluation Protocol (`eval_focus_ring_detector.py`):**
   - Must evaluate and output both general test metrics and the dedicated `hard_negative_eval.json` with \(n \ge 100\).
   - Gate threshold: Hard-negative False Positive Rate $\le 0.5\%$.
