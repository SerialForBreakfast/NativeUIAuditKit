# ADR-0015: Context-Aware and Unified tvOS Focus Detection Architecture

- Date: 2026-09-30
- Status: Proposed / Active
- Scope: tvOS FocusRing detection pipeline, crop representations, and model architecture.
- Relates to: [ADR-0008](ADR-0008-Simulator-First-tvOS-FocusRing-Development.md), [ADR-0010](ADR-0010-Hard-Negative-Diversity-and-Edge-Case-Induction.md), [FocusRingDetectorSpec](FocusRingDetectorSpec.md).

---

## 1. Context and Problem Statement

Focus ring detection on tvOS has absorbed immense engineering effort across 21 iterations (`FDR001` through `FDR021`), yet continues to struggle on realistic evaluation sets (e.g., artwork focus recall remaining at 1/12 or 2/12, and single unselected buttons causing false positives).

Diagnosis of the FDR experimental series reveals fundamental architectural limitations in the current setup:
1. **The 577-Parameter Linear Probe Bottleneck:**
   The current architecture freezes an ImageNet-pretrained MobileNetV3-small backbone and trains only a single 577-parameter linear head (`nn.Linear(576, 1)`) on pre-extracted feature vectors. A linear probe cannot capture the subtle non-linear visual transformations of the tvOS focus engine (specular sheen, drop shadow expansion, dynamic border glow, and parallax depth).
2. **Context Blindness in Isolated 16% Crops:**
   The model evaluates isolated 256×256 crops expanded by 16% around nominal bounds. On tvOS, "focus" is fundamentally a **relational property**:
   - An artwork card is "focused" because it is scaled up 1.1x relative to its neighbors, has a white border outline, or casts an elevated shadow onto the background shelf.
   - Without seeing the neighboring unfocused cards or background canvas, an isolated crop of high-contrast movie artwork often confuses the linear classifier.
3. **Micro-Dataset Overfitting:**
   Training on ~980 crops and evaluating on only 14 complete frames and 18 retention crops has turned the project into an exercise in overfitting to specific frame quirks (such as debugging individual frame pixels or alpha vs. straight RGB channel differences) rather than learning generalizable focus features.

---

## 2. Decision Drivers

- **Generalizable Focus Detection:** Reliably detect focused state across diverse tvOS UI motifs: standard buttons, segmented tabs, poster artwork cards, and collection rows.
- **Relational / Contextual Awareness:** Provide the model with visual contrast between the target control and its surrounding environment.
- **End-to-End Representational Capacity:** Allow the model backbone to adapt its spatial filters to focus-specific visual cues rather than relying on generic frozen ImageNet weights.

---

## 3. Considered Options

- **Option A (Continue Linear Probe Tweaks):** Continue fine-tuning loss weights, OHEM thresholds, and manual crop additions for the 577-parameter head.
- **Option B (Context-Aware Dual-Crop / Multi-Scale Classifier):** Feed the classifier a dual-stream input: a tight crop of the control plus a wider contextual crop of the surrounding neighborhood (30–50% margin), fine-tuning the top layers of the backbone.
- **Option C (Unified Single-Stage Focus Detection in YOLO — Selected Long-Term):**
  - Incorporate focus state directly into the primary tvOS YOLO detector (e.g., classes `button_focused` vs. `button_unfocused`, `artwork_focused` vs. `artwork_unfocused`, or an auxiliary focus classification head).
  - YOLO processes the full 1920×1080 screen with full context, naturally observing relative scale, shadow elevation, and neighbor contrast in a single pass.
- **Option D (Hybrid Transition):** Implement Option B immediately for the standalone crop pipeline using synthetic TVTestRigFixture data, while preparing Option C for the unified detector.

---

## 4. Decision

We adopt **Option D (Hybrid Transition)**:

### 4.1 Immediate: End-to-End Fine-Tuning with Context Margins
1. **Unfreeze Backbone Adaptation:** Retire the frozen-feature 577-parameter probe. Fine-tune the upper convolutional blocks of MobileNetV3 (or a lightweight ConvNeXt-Femto backbone) end-to-end on focus crops.
2. **Expand Context Boundary:** Increase crop context from 16% to 35% margin or adopt dual-resolution input (tight control + surrounding context), ensuring shadows and scale displacement relative to the background are visible.
3. **Synthetic Scale over Micro-Manual Curation:** Replace manual 4-frame collection cycles with synthetic generation via `TVTestRigFixture`, rendering thousands of focused/unfocused pairs across varied backgrounds, poster artwork, and layouts.

### 4.2 Long-Term: Unified Single-Stage Focus Detection in YOLO
1. Merge focus classification into the primary tvOS YOLO11 detector.
2. Because YOLO operates on the complete letterboxed 1080p screen, it inherently possesses global context: it sees which item is enlarged, which item has a focus ring, and which items are dimmed.
3. Eliminates the fragile two-stage crop-and-classify pipeline entirely, reducing inference latency and eliminating crop alignment errors.

---

## 5. Consequences

### Positive
- **Drastic Generalization Improvement:** End-to-end training and contextual margins enable the model to learn actual focus cues (glow, scale, border) rather than memorizing artwork textures.
- **Eliminates Manual Crop Accounting:** Stops the cycle of debugging 58-crop additions, alpha channel parsing, and single-frame score flips.
- **Unified tvOS Inference Pipeline:** Moving to single-stage YOLO focus detection halves the CoreML compute graph overhead and eliminates crop extraction logic in consumer apps.

### Negative / Tradeoffs
- **Retraining Required:** Requires running a full backbone fine-tuning run rather than sub-minute linear head fits on cached features.
- **Dataset Generation Requirement:** Requires generating a synthetic training corpus of at least 5,000 diverse tvOS frames with programmatic focus states.
