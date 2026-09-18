---
name: tvos-fixture-training
description: >-
  Use this skill when capturing tvOS training data, benchmarking detectors on Apple TV
  hardware, sweeping TVTestRigFixture tabs, or generating synthetic UI layouts with ground truth.
---

# tvOS Fixture Training & Synthetic Harvester Protocol

This skill governs training data collection and evaluation inside `TVTestRigFixture` (`com.showblender.TVTestRigFixture`) on physical Apple TV hardware and tvOS simulators.

---

## Why the Fixture is Preferred for Training

1. **Zero System Risk:** The fixture is completely sandboxed. Buttons like `Reset All` only reset in-memory test cards—they cannot reboot hardware, wipe accounts, or disrupt video signals.
2. **Authentic Metal Shaders:** Employs real Apple TV GPU shaders, parallax tilt, specular highlights, and drop shadows that simulators cannot replicate.
3. **Multi-Class Component Showcase:** Contains native reference implementations across pickers, sliders, toggles, text fields, rating bars, and segmented controls.
4. **Seeded Defect Matrix:** Directly provides labeled ground-truth for accessibility auditing (HIG Compliant vs Missing Label vs Wrong Traits).

---

## Fixture Tab Navigation Map

The top navigation rail contains 5 distinct tabs:

| Tab Index | Name | Primary UI Surfaces & Components |
|:---:|---|---|
| **0** | **Audit** | Seeded Defect Injection Matrix, Ground Truth Audit Oracle, Interactive Probe (`ACTIVATE`), Nested Sub-Deck trigger. |
| **1** | **Detection** | Object detection benchmark cards and structured layout cards. |
| **2** | **Navigation** | Directional navigation grids, focus guides, focus trap diagnostics. |
| **3** | **Accessibility** | Binary toggle switches (`Wi-Fi`, `Closed Captions`, `Reduce Motion`, `Diagnostics`), Sliders (`Volume`, `Playback Position`), Stepper/Rating bars. |
| **4** | **Component Showcase** | 3-row segmented pickers (`Featured/Recent/Saved`, `Leading/Center/Trailing`, `Auto/HD/4K`), `Username` text field, `Search components` bar. |

---

## The $N$-Way Focus Sweep Protocol

On Apple TV, focused controls scale by 10–15%, cast intense radial drop shadows, and emit bloom glow. A robust detector must learn both the resting state and the focused distortion for every control.

### Procedure for Any Fixture View:
1. **Frame 0 (Resting Baseline):**  
   Move focus to an invisible anchor or non-interactive element. Capture all $N$ controls at rest.
2. **Frames $1 \dots N$ (Individual Focus Passes):**  
   Step focus to element $i$:
   - Settle 150ms for Metal glow shaders to finish.
   - Capture frame and pair with Schema v1.0 JSON sidecar where element $i$ has `isFocused: true` and all other elements have `isFocused: false`.

---

## Running the Automated Fixture Sweep

To execute a complete 15-frame multi-tab sweep across all controls:

```bash
# From package root:
.venv-yolo/bin/python scratch/sweep_fixture_tabs.py
```

### Verification Steps:
1. Confirm all 15 frames are saved in `dataset/tvos_fixture_captures/`.
2. Verify each PNG has a matching `.json` sidecar and `_result.json` YOLO detection file.
3. Inspect class distribution to ensure balanced instance counts:
   ```bash
   python3 -c '
   import glob, json
   from collections import Counter
   counts = Counter()
   for f in glob.glob("dataset/tvos_fixture_captures/*_result.json"):
       for d in json.load(open(f)): counts[d["type"]] += 1
   for k, v in counts.most_common(): print(f"  {k:20s}: {v}")
   '
   ```

---

## What Works vs What Doesn't

| What Works | What Fails (Do Not Repeat) |
|---|---|
| Sweeping within `TVTestRigFixture` for training data. | Crawling live system Settings or third-party apps for training data. |
| Using `wait-stable` after each directional pulse. | Firing multiple keypresses without waiting for focus animation settling. |
| Capturing both resting and focused states ($N$-way sweep). | Capturing only the resting view (model fails to detect focused controls). |
| Generating sidecars with SHA256 hashes and hardware metadata. | Creating orphan images without corresponding Schema v1.0 JSON sidecars. |
