# Training Dataset Size Estimations
**NativeUIAuditKit — Storage Planning Document**  
*Last updated: 2026-05-19 | Based on measured Phases 3+4 output*

---

## TL;DR

| Milestone | Cumulative dataset size | Free space needed |
|---|---|---|
| Phases 3+4 (already generated) | **735 MB** | — |
| + Phase 5a (known-bad, 580 images) | **867 MB** | 132 MB |
| + Phase 5b (20 new SwiftUI templates, 8,000 images) | **3.4 GB** | 2.6 GB |
| + Phase 5b-21 (accessibility sweep, ~2,000 images) | **4.1 GB** | 640 MB |
| + Real-world validation set (200 App Store screenshots) | **4.3 GB** | ~160 MB |
| **Full iOS dataset (all phases complete)** | **~4.3 GB** | — |
| + Phase 6.1 tvOS dataset (~6,000 images) | **~6.7 GB** | ~2.5 GB |
| + Phase 6.2 macOS dataset (~6,000 images) | **~9.8 GB** | ~3.1 GB |
| + Trained CoreML model files (all 3 platforms) | **~10.1 GB** | ~300 MB |

**Current free disk space: 17 GB** — sufficient for the full roadmap, with ~7 GB remaining as buffer.

---

## ⚠️ Critical Warning: Dataset Is Inside Dropbox

The current output path is:

```
NativeUIAuditKit/.build/debug-output/dataset/
```

This is inside the Dropbox-synced folder. Although Xcode's `.build/` directory is often excluded from Dropbox by `.dropboxignore`, you should **verify this before generating Phase 5b** (which would add ~2.5 GB). If Dropbox is syncing `.build/`, it will:

1. Consume your Dropbox cloud quota
2. Slow generation runs significantly (Dropbox tries to upload each PNG as it lands)
3. Cause spurious "file in use" conflicts

**Recommended fix:** Configure the dataset output path to write outside Dropbox entirely, e.g. `~/NativeUIDataset/` or an external drive.

---

## Measured Baselines

Phases 3 and 4 are fully generated (2,700 images). All estimates below derive from this measured data.

### Per-file measured sizes

| Metric | PNG | JSON annotation |
|---|---|---|
| Count | 2,700 | 2,700 |
| Total | 711.7 MB | 23.3 MB |
| Average | 263.6 KB | 8.8 KB |
| Median | 213.1 KB | 7.4 KB |
| Minimum | 92.6 KB | 2.6 KB |
| Maximum | 1,425.5 KB | 24.7 KB |

Manifest file at 2,700 entries: **1.71 MB** (~0.65 KB per entry, grows linearly).

### Per-template-family PNG averages (measured)

| Template family | Scale | Count | Avg PNG size | Canvas (px) |
|---|---|---|---|---|
| Alert | @2x | 100 | 1,033 KB | 750 × 1,334 |
| Alert | @3x | 100 | 1,062 KB | 1,179 × 2,556 |
| LoginForm | @2x | 100 | 137 KB | 750 × 1,334 |
| LoginForm | @3x | 100 | 185 KB | 1,179 × 2,556 |
| SettingsList | @2x | 100 | 361 KB | 750 × 1,334 |
| SettingsList | @3x | 100 | 314 KB | 1,179 × 2,556 |
| UIKitControls | @2x | 350 | 211 KB | 750 × 1,334 |
| UIKitControls | @3x | 350 | 227 KB | 1,179 × 2,556 |
| UIKitForm | @2x | 350 | 103 KB | 750 × 1,334 |
| UIKitForm | @3x | 350 | 191 KB | 1,179 × 2,556 |
| UIKitList | @2x | 350 | 213 KB | 750 × 1,334 |
| UIKitList | @3x | 350 | 254 KB | 1,179 × 2,556 |

**Key observations:**
- Alert is an outlier (6–7× larger than UIKit forms) because the alert card renders over a transparent-then-blurred background that generates high-entropy pixel data — poor PNG compression.
- The @3x/@2x size ratio is 1.3–1.8×, not the 2.25× expected from pixel area. PNG's compression reuses repeated patterns across the larger canvas.
- UIKit templates are 30–40% smaller than equivalent SwiftUI templates; they render simpler, more uniform pixel patterns.

---

## Phase-by-Phase Estimates

### Phase 3 — Initial SwiftUI Templates (complete ✅)

3 templates × 200 images = 600 images

| Template | Avg PNG | Total PNG | Total JSON |
|---|---|---|---|
| Alert | 1,048 KB | 210 MB | 1.8 MB |
| LoginForm | 161 KB | 32 MB | 1.8 MB |
| SettingsList | 337 KB | 67 MB | 1.8 MB |
| **Subtotal** | | **309 MB** | **5.4 MB** |

**Phase 3 total (measured): 314 MB**

---

### Phase 4 — UIKit Generator (complete ✅)

3 templates × 700 images = 2,100 images

| Template | Avg PNG | Total PNG | Total JSON |
|---|---|---|---|
| UIKitForm | 147 KB | 103 MB | 6.2 MB |
| UIKitList | 234 KB | 164 MB | 6.2 MB |
| UIKitControls | 219 KB | 153 MB | 6.2 MB |
| **Subtotal** | | **420 MB** | **18.6 MB** |

**Phase 4 total (measured): 421 MB**

---

### Phases 3+4 Combined (measured on disk)

**735 MB** (PNG 712 MB + JSON 23 MB + manifest 1.7 MB)

---

### Phase 5a — Known-Bad UIKit Templates (580 images, pending)

9 templates, 40–60 images each. These are UIKit VCs rendering explicitly broken layouts. Estimated PNG sizes based on visual complexity:

| Template | Images | Basis for estimate | Avg PNG | Total PNG |
|---|---|---|---|---|
| TruncatedLabel | 60 | Solid bg, text rows | 160 KB | 9.6 MB |
| ClippedContent | 60 | UIImageView gradients | 280 KB | 16.8 MB |
| SmallHitTarget | 60 | Simple buttons, white bg | 170 KB | 10.2 MB |
| OverlappingControls | 60 | Filled buttons, coloured | 260 KB | 15.6 MB |
| DynamicTypeOverflow | 60 | Clipped text, white bg | 160 KB | 9.6 MB |
| RTLMirroringFailure | 40 | Mixed elements | 220 KB | 8.8 MB |
| OffScreenElement | 60 | Scrolled list, white | 190 KB | 11.4 MB |
| OccludedElement | 60 | Sheet overlay, buttons | 240 KB | 14.4 MB |
| HardNegative (×3 types) | 120 | Gradients, WebView, overlay | 420 KB | 50.4 MB |
| **Total** | **580** | | **~230 KB avg** | **147 MB** |

JSON annotations: 580 × 7 KB = 4.1 MB (known-bad JSONs are slightly smaller — fewer annotated elements)

**Phase 5a total: ~151 MB**

---

### Phase 5b — Extended SwiftUI Templates (8,000 images, pending)

20 templates × 400 images each. Categorised by background complexity:

#### Category A: Simple / white system background (~160 KB avg)

| Template | Visual character | Avg PNG est. |
|---|---|---|
| FormValidation | White form, text fields | 160 KB |
| SearchResults | White list + search bar | 200 KB |
| LoadingSkeleton | Grey placeholders, white bg | 180 KB |
| Stepper | White list rows | 200 KB |

*400 images × 4 templates = 1,600 images × 185 KB avg = 296 MB*

#### Category B: List-based with some chrome / colour (~330 KB avg)

| Template | Visual character | Avg PNG est. |
|---|---|---|
| TabViewNavigation | Tab chrome + list content | 350 KB |
| SettingsDisclosure | Disclosure groups, list | 320 KB |
| RefreshControl | List + spinner | 220 KB |
| RTLMirror | Settings list, flipped | 320 KB |
| ProgressActivity | Grey containers, progress | 240 KB |

*400 images × 5 templates = 2,000 images × 290 KB avg = 580 MB*

#### Category C: Modal overlays / cards (~270 KB avg)

| Template | Visual character | Avg PNG est. |
|---|---|---|
| Sheet | Dimmed bg + card | 260 KB |
| ActionSheet | Dimmed bg + action list | 280 KB |
| Popover | Background + card | 250 KB |
| ContextMenu | Dimmed bg + menu list | 300 KB |
| PickerDateEntry | White + date picker wheel | 250 KB |

*400 images × 5 templates = 2,000 images × 268 KB avg = 536 MB*

#### Category D: Colourful / gradient backgrounds (~480 KB avg)

| Template | Visual character | Avg PNG est. |
|---|---|---|
| EmptyState | Tinted icon, solid/gradient bg | 420 KB |
| MediaCardGrid | Coloured thumbnail cards | 550 KB |
| OnboardingPage | Vivid gradient hero section | 520 KB |
| LiquidGlassNav | Gradient bg (exercises blur) | 480 KB |
| LiquidGlassTab | Gradient bg + tab chrome | 500 KB |
| MapOverlays | Procedural tile grid | 380 KB |

*400 images × 6 templates = 2,400 images × 475 KB avg = 1,140 MB*

#### Phase 5b totals

| Category | Images | PNG total |
|---|---|---|
| A: Simple white | 1,600 | 296 MB |
| B: List/chrome | 2,000 | 580 MB |
| C: Modal overlays | 2,000 | 536 MB |
| D: Colourful/gradient | 2,400 | 1,140 MB |
| **All Phase 5b** | **8,000** | **2,552 MB** |

JSON annotations: 8,000 × 9 KB = 72 MB

**Phase 5b total: ~2,624 MB (~2.6 GB)**

---

### Phase 5b-21 — Accessibility Variant Sweep (~2,000 images, pending)

Accessibility variants are additional renders of existing templates under modified settings (reduceTransparency, increaseContrast, boldText, buttonShapes). Visual complexity is similar to the base templates.

- Count: ≥2,000 images (spec minimum)
- Avg PNG: ~310 KB (weighted mix of template categories)
- PNG total: 2,000 × 310 KB = 620 MB
- JSON total: 2,000 × 9 KB = 18 MB

**Phase 5b-21 total: ~638 MB**

---

### Real-World Validation Set — 200 App Store Screenshots (manual, future)

200 personally-captured screenshots from a physical device. Real screenshots have higher entropy than generated images (photos, varied UI, gradients, icons).

- Avg PNG size: ~800 KB (real-world screenshots at @3x are larger than synthetic)
- PNG total: 200 × 800 KB = 160 MB
- Manual annotation JSONs: 200 × 12 KB = 2.4 MB (more complex, manually written)

**Validation set total: ~162 MB**

---

### Phase 6.1 — tvOS Dataset (~6,000 images, future)

tvOS canvas: 1920×1080 @1x (standard). Pixel area: ~2.07 megapixels. Comparable to iPhone @2x (1.0 MP) but with simpler, grid-based layouts typical of 10-foot UI. Estimated avg PNG: ~380 KB.

- Count: ~6,000 images (estimate — tvOS has fewer template archetypes than iOS)
- PNG total: 6,000 × 380 KB = 2,280 MB
- JSON total: 6,000 × 9 KB = 54 MB

**Phase 6.1 tvOS total: ~2,334 MB (~2.3 GB)**

---

### Phase 6.2 — macOS Dataset (~6,000 images, future)

macOS canvas: 1440×900 @2x = 2880×1800 pixels. Pixel area: ~5.18 megapixels — the largest canvas in the project. Dense toolbar UIs with many elements per screen drive higher PNG entropy. Estimated avg PNG: ~520 KB.

- Count: ~6,000 images (estimate)
- PNG total: 6,000 × 520 KB = 3,120 MB
- JSON total: 6,000 × 9 KB = 54 MB

**Phase 6.2 macOS total: ~3,174 MB (~3.1 GB)**

---

### Trained CoreML Model Files

CoreML `.mlpackage` bundles for three models. YOLOv8-nano/small at 41 classes:

| Model | Estimated size |
|---|---|
| NativeUIModel_iOS (41 classes) | 40–80 MB |
| NativeUIModel_tvOS (41 classes) | 40–80 MB |
| NativeUIModel_macOS (41 classes) | 40–80 MB |
| Training logs + validation curves | ~50 MB |
| **Total** | **~220 MB** |

---

## Full Roadmap Summary

| Phase | Images | PNG | JSON + manifest | **Phase total** | **Cumulative** |
|---|---|---|---|---|---|
| Phase 3 (✅ complete) | 600 | 309 MB | 5 MB | 314 MB | 314 MB |
| Phase 4 (✅ complete) | 2,100 | 420 MB | 19 MB | 439 MB | 735 MB |
| Phase 5a — Known-bad (pending) | 580 | 147 MB | 4 MB | 151 MB | 886 MB |
| Phase 5b — 20 SwiftUI templates (pending) | 8,000 | 2,552 MB | 72 MB | 2,624 MB | 3,510 MB |
| Phase 5b-21 — Accessibility sweep (pending) | 2,000 | 620 MB | 18 MB | 638 MB | 4,148 MB |
| Real-world validation set (future) | 200 | 160 MB | 2 MB | 162 MB | 4,310 MB |
| Phase 6.1 — tvOS dataset (future) | 6,000 | 2,280 MB | 54 MB | 2,334 MB | 6,644 MB |
| Phase 6.2 — macOS dataset (future) | 6,000 | 3,120 MB | 54 MB | 3,174 MB | 9,818 MB |
| Trained CoreML model files (future) | — | — | — | 220 MB | **10,038 MB** |

**Full roadmap: ~10 GB total dataset storage.**

---

## Disk Space Planning

### Current status

| Item | Size |
|---|---|
| Total disk capacity | 926 GB |
| Current disk usage | 875 GB |
| **Current free space** | **17 GB** |
| Already-generated dataset | 735 MB |
| Xcode `.build/` artifacts (project) | ~350 MB (excl. dataset) |

### Space required by phase completion

| When | Additional space needed | Running free space |
|---|---|---|
| Now (after Phase 4) | 0 | 17 GB |
| After Phase 5a | 151 MB | ~16.9 GB |
| After Phase 5b | 2,624 MB | ~14.3 GB |
| After Phase 5b-21 | 638 MB | ~13.6 GB |
| After real-world validation | 162 MB | ~13.5 GB |
| After Phase 6.1 (tvOS) | 2,334 MB | ~11.1 GB |
| After Phase 6.2 (macOS) | 3,174 MB | ~8.0 GB |
| After model training artifacts | 220 MB | **~7.7 GB remaining** |

**Conclusion: 17 GB is sufficient to complete the entire roadmap**, with approximately **7.7 GB headroom** remaining. That is a comfortable margin if no other large files are added to this volume.

---

## Recommendations

### 1. Move dataset output outside Dropbox immediately (high priority)

The current dataset path is inside `Dropbox/Documents/GitHub/NativeUIAuditKit/.build/`. Before running Phase 5b (which adds ~2.6 GB), confirm `.build/` is excluded from Dropbox sync:

```bash
# Check whether .build is ignored by Dropbox
cat ~/.dropbox/.dropbox_ignore 2>/dev/null
# Or check macOS extended attribute
xattr -p com.dropbox.ignored \
  ~/Dropbox/My\ Mac\ \(MacBook-Air\)/Documents/GitHub/NativeUIAuditKit/.build 2>/dev/null
```

If not excluded, add it:

```bash
xattr -w com.dropbox.ignored 1 \
  ~/Dropbox/My\ Mac\ \(MacBook-Air\)/Documents/GitHub/NativeUIAuditKit/.build
```

Alternatively, configure the generator to write to `~/NativeUIDataset/` (outside Dropbox entirely) and update the `datasetDir` path in `GenerateDatasetTests.swift`.

### 2. Archive completed phases before generating the next

Once a phase is fully generated and spot-checked, compress the split directories:

```bash
# Example: archive Phase 3+4 images into a single .tar.zst
# (zstd gives ~30% compression on UI PNGs at fast speed)
cd ~/NativeUIDataset
tar -I 'zstd -10' -cf dataset_phases34.tar.zst train/ validation/ test/
```

A 30% compression ratio would shrink the 735 MB Phase 3+4 dataset to ~515 MB. Realistically, generated UI screenshots (large uniform regions) compress well — 35–45% reduction is plausible.

### 3. Do not generate tvOS/macOS datasets on this Mac

The tvOS + macOS datasets add ~5.5 GB. Given the 17 GB free space, this is technically possible but leaves less than 8 GB headroom — a marginal buffer on a disk that is 99% full. Consider:

- Generating tvOS/macOS datasets on an external drive (SSD recommended for the I/O rate during XCTest runs)
- Or waiting until Phase 6.1 to reassess free space (it may improve as old files are cleaned)

### 4. Plan for training infrastructure separately

PyTorch / YOLOv8 training runs are not expected to happen on this Mac (they require GPU acceleration, typically a cloud VM or a Mac with Apple Silicon's MPS backend). The dataset just needs to be exportable. The ~10 GB dataset can be compressed to ~6–7 GB for transfer using zstd.

---

## Estimation Confidence

| Phase | Confidence | Notes |
|---|---|---|
| Phase 5a (known-bad) | **High** — within ±15% | Same UIKit rendering path as Phases 3+4; similar element density |
| Phase 5b simple/list templates | **High** — within ±20% | Structurally similar to LoginForm/SettingsList baselines |
| Phase 5b gradient templates | **Medium** — within ±30% | No baseline for full-screen gradient backgrounds in this renderer |
| Phase 5b-21 accessibility | **Medium** — within ±25% | Count depends on final accessibility sweep implementation |
| Phase 6.1 tvOS | **Low** — within ±40% | No tvOS images generated yet; canvas size is an estimate |
| Phase 6.2 macOS | **Low** — within ±40% | No macOS images generated yet; toolbar density is unknown |

A single generated Phase 5b batch (any template × 10 seeds) will provide a precise anchor for the Phase 5b estimates before committing to the full 8,000-image run.
