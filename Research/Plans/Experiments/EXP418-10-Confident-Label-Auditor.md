# EXP418-10 — Confident Learning & OCR-Geometry Automated Label-Completeness Auditor (`B405-238` / Template `T76`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `iOS detection` (`IOS`) and `iOS generation` (`IGEN`). Priority: `P0`.
Parent task: `B405-129` / `EXP-REVIEW-04`. Template: `T76` (`confident_label_auditor418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Backlog410.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Backlog410.md) (`B405-117`, `B405-129`) and [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md):
- On the 2,000 withheld iOS frames, Run 013 predicts **194 `navigationBar` boxes** and **297 `textField` boxes** at high confidence (`>= 0.25`, with `184` remaining above `0.40`) that overlap **no ground-truth label** (`IoU == 0.0`).
- Similarly, on the 46 reviewed real tvOS frames (`INFERENCE412`), lowering detector confidence from `0.50` to `0.25` adds `290` unmatched boxes whose true status (unlabeled real UI element vs detector false positive) is unknown.
- In [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) line 108, reviewing these 491 unmatched iOS boxes and building the `EXP-REVIEW-04` flagged review importer are listed as human bottlenecks.

### SOTA Method: Object-Detection Confident Learning + Tri-Modal Self-Verification
Inspired by **Confident Learning** (Northcutt et al., *Confident Learning: Estimating Uncertainty in Dataset Labels*) and **Multi-Modal Grounding Verification**:
When a trained detector predicts a bounding box $\hat{b}$ with high confidence $p \ge 0.40$ where the ground-truth annotation set $\mathcal{Y}$ has no box, how can we distinguish a **missing ground-truth annotation** (an annotation bug in `GeneratorRunner` or human labeling) from a **detector hallucination** without human inspection of every box?

We require **Tri-Modal Independent Agreement** across three orthogonal signals:
1. **Cross-Model / Multi-Scale Detector Consensus ($S_{\text{det}}$)**: Does a second independent checkpoint (e.g., Run 009 vs Run 013, or `640 px` vs `960 px` inference) independently predict the same box with $\text{IoU} \ge 0.65$?
2. **Physical Rendered-Body Platter Verification ($S_{\text{body}}$)**: Using `body_measure417` (`T46` rendered-body gate), does the image pixel region inside $\hat{b}$ exhibit a physical UI platter boundary (distinct interior/exterior luminance contrast $\ge 24$ gray levels or horizontal separator line for `navigationBar`, and uniform perimeter ring $\ge 0.85$ for `textField`)?
3. **Vision OCR / Rectangular Contour Grounding ($S_{\text{ocr}}$)**: Does `VNRecognizeTextRequest` or `VNDetectRectanglesRequest` (`vision_annotation_probe`) find an aligned text string (e.g., placeholder text inside `textField` or title/back-button text inside `navigationBar`) contained within $\hat{b}$ ($\text{IoA} \ge 0.60$)?

When all three independent modalities agree ($S_{\text{det}} \land S_{\text{body}} \land S_{\text{ocr}}$), the unmatched box is classified as a **Verified Missing Ground-Truth Annotation** and linked directly back to the `GeneratorRunner` template family that omitted the label!

---

## 2. Controlled Test and Decision Rules

### Hypothesis
The Tri-Modal Confident Label Auditor achieves `>= 95 %` precision and `>= 90 %` recall on a seeded synthetic benchmark of 100 intentionally dropped ground-truth labels, and resolves `>= 80 %` of the 491 unmatched `navigationBar` and `textField` boxes in `B405-129` into deterministic generator family fixes without human visual review.

### Experimental Arms
All arms run on the pinned 2,000-frame iOS bundle (`detector-case-ios-r013.json`) plus a seeded validation control where 100 known-good ground-truth boxes (`50 navigationBar`, `50 textField`) are masked out to measure auditor precision and recall:
1. `control` (`auditRule = 'confidence-only'`, `minConfidence = 0.40`): Naive confidence threshold (`conf >= 0.40`) without cross-model, body-contrast, or OCR verification.
2. `dual-model-only` (`auditRule = 'cross-model-consensus'`, `minConfidence = 0.25`): Require Run 009 and Run 013 box agreement (`IoU >= 0.65`).
3. `platter-body-only` (`auditRule = 'rendered-body-gate'`, `minConfidence = 0.25`): Require `body_measure417` rendered-platter pass on the unmatched box.
4. `confident-tri-modal` (`auditRule = 'confident-tri-modal'`, `minConfidence = 0.25`): Require cross-model/multi-scale consensus + rendered-body platter/separator pass + OCR/rectangle containment.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: `confident-tri-modal` achieves `>= 95 %` precision and `>= 90 %` recall on the 100 masked control labels (`0` false relabeling of empty background patches), and groups the verified missing labels in `B405-129` by `GeneratorRunner` template family.
- **Contradicted**: Tri-modal auditing has `< 90 %` precision on the masked control labels (risking false label injection).
- **Inconclusive**: Image files or OCR/body measurements are missing for any candidate frame.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` immediately resolves human review item 1 in [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) (`B405-129`: the 194 `navigationBar` and 297 `textField` boxes) and pinpoints the exact SwiftUI generator families in `NativeUIDatasetGenerator` that draw a search bar or navigation header without emitting a ground-truth annotation!
  - `Maximum-mini-NUIAK` also fulfills `EXP-REVIEW-04` for `Sillycon-TTR` by providing a deterministic JSON intake schema and automated triage receipt (`missing-ground-truth`, `true-false-positive`, `ambiguous-human-review`).
- **If Contradicted**:
  - `Maximum-mini-NUIAK` retains only the ambiguous subset for human visual inspection, still cutting manual review volume by 60 % to 80 %.

---

## 4. Template `T76` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T76': (
    {'bundle', 'secondaryScorecard', 'probeCache'},
    {'auditRule', 'minConfidence'},
    'confident_label_auditor418.run',
    'artifact',
    'diagnostic',
),
```

### Inputs and Parameters
- **Inputs**:
  - `bundle`: Pinned `T42` detector case bundle (`detector-case-inputs-v1`).
  - `secondaryScorecard`: Pinned second model or multi-scale scorecard for consensus checking.
  - `probeCache`: Pinned `body_measure417` and `vision_annotation_probe` OCR/rectangle measurements on the unmatched candidate boxes.
- **Parameters**:
  - `auditRule`: `str` in `{'confidence-only', 'cross-model-consensus', 'rendered-body-gate', 'confident-tri-modal'}`.
  - `minConfidence`: `float` in `{0.25, 0.40}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T76",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-187-auditor",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the 491 unmatched iOS navigationBar and textField predictions (B405-129) and 100 masked ground-truth control labels, does tri-modal Confident Learning (consensus + rendered-body + OCR) recover missing labels at >= 95% precision?",
  "decision": "Support confident-tri-modal if it reaches >= 95% precision and >= 90% recall on the 100 masked control labels and partitions the 491 B405-129 boxes by generator family.",
  "outcomes": {
    "supported": "File exact generator annotation repairs for the identified SwiftUI families and close B405-129 and EXP-REVIEW-04.",
    "contradicted": "Export only the cross-model consensus subset for manual maintainer inspection.",
    "inconclusive": "Complete probe measurements on all 491 unmatched boxes before deciding."
  },
  "shared": {
    "inputs": {
      "bundle": {"file": "Research/Experiments/detector-case-ios-r013.json"},
      "secondaryScorecard": {"file": "Research/Experiments/detector-case-ios-r013-c040.json"},
      "probeCache": {"file": "Research/Experiments/b418-unmatched-probe-cache.json"}
    }
  },
  "arms": [
    {"id": "control", "label": "Naive confidence >= 0.40 only", "parameters": {"auditRule": "confidence-only", "minConfidence": 0.40}},
    {"id": "consensus", "label": "Cross-model box consensus (IoU >= 0.65)", "parameters": {"auditRule": "cross-model-consensus", "minConfidence": 0.25}},
    {"id": "body-gate", "label": "Rendered-body platter contrast gate", "parameters": {"auditRule": "rendered-body-gate", "minConfidence": 0.25}},
    {"id": "tri-modal", "label": "Tri-modal consensus + body + OCR", "parameters": {"auditRule": "confident-tri-modal", "minConfidence": 0.25}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/confident_label_auditor418.py`**:
   - Extract unmatched candidate predictions (`navigationBar`, `textField`, and optional classes) from `bundle`.
   - Evaluate the 100 masked ground-truth control boxes (seeded deterministically from true labels that pass `body_measure417`) to compute exact auditor `precision`, `recall`, and `false_relabel_count`.
   - Partition the 491 `B405-129` unmatched boxes into `missing-ground-truth-label`, `true-detector-false-positive`, and `ambiguous-human-review`, grouped by template `family`.
   - Note: The auditor **never** modifies or relabels evaluation files automatically (preserving `AGENTS.md` data-role safety rules); it writes a structured diagnostic report and `EXP-REVIEW-04` receipt.
2. **Create `scripts/test_confident_label_auditor418.py`**:
   - Verify that `confident-tri-modal` rejects synthetic hallucinated boxes on flat backgrounds (`false_relabel_count == 0`).
   - Verify `EXP-REVIEW-04` receipt schema compliance.

### Reference Adapter Code (`scripts/confident_label_auditor418.py`)
```python
"""T76: Confident Learning & Tri-Modal (Consensus + Rendered-Body + OCR) Label-Completeness Auditor."""
from collections import Counter
import research_queue as q

OUT = None
RULES = ('confidence-only', 'cross-model-consensus', 'rendered-body-gate', 'confident-tri-modal')
CONFS = (0.25, 0.40)


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'auditRule', 'minConfidence'}, 'auditor_parameters')
    rule, conf = value['auditRule'], value['minConfidence']
    q.require(rule in RULES, 'auditor_rule_invalid')
    q.require(conf in CONFS, 'auditor_conf_invalid')
    return rule, float(conf)


def triage_unmatched_box(box: dict, rule: str, min_conf: float) -> str:
    """Classify 1 unmatched prediction into missing-ground-truth, true-false-positive, or ambiguous."""
    if box['confidence'] < min_conf:
        return 'true-false-positive'
    if rule == 'confidence-only':
        return 'missing-ground-truth'
    has_consensus = box.get('secondaryIoU', 0.0) >= 0.65
    if rule == 'cross-model-consensus':
        return 'missing-ground-truth' if has_consensus else 'true-false-positive'
    has_body = box.get('bodyStatus') == 'pass' and box.get('foregroundDelta', 0.0) >= 24.0
    if rule == 'rendered-body-gate':
        return 'missing-ground-truth' if has_body else 'true-false-positive'
    # confident-tri-modal
    has_ocr_or_chrome = box.get('ocrIoA', 0.0) >= 0.50 or box.get('chromeSeparator', False)
    if has_consensus and has_body and has_ocr_or_chrome:
        return 'missing-ground-truth'
    if not has_body and box.get('secondaryIoU', 0.0) < 0.30:
        return 'true-false-positive'
    return 'ambiguous-human-review'
```

### Resource and Time Budget
- **Preparation**: 45 min.
- **Execution**: 4 diagnostic jobs taking 5 s to 15 s each (within the 800 s and 100 MB standing diagnostic class).
- **Review**: 10 min via `backlog_pipeline.py review`.
