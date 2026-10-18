# EXP418-06 — Failure-Guided Counterfactual Twin Synthesis (`B405-234` / Template `T72`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `tvOS generation` (`TGEN`) and `iOS generation` (`IGEN`). Priority: `P1`.
Parent task: `S391-04` / `TASK-6a-10`. Template: `T72` (`counterfactual_synthesis418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Backlog410.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Backlog410.md) and [Groom20261017.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Groom20261017.md), `Maximum-mini-NUIAK` identified specific visual confusers where models fail:
- **iOS wide toggle vs listRow/picker (`B405-016`)**: Wide toggles (`width 0.5–0.9`) are misclassified as `listRow` (`232` cases) or `picker` (`151` cases).
- **tvOS selected tab vs focused tab (`B405-027`, `B405-167`, `B405-169`)**: A selected tab has a filled platter even when focus moves to another tab or down into the content grid.
- **Decorative static border vs OS HCF focus ring (`B405-005`, `B405-101`, `B405-102`)**: Authored static card borders (`2 pt` to `6 pt`) confuse brightness-based rules and crop classifiers.

Uniform random seed sweeps in `T46` and `T03` spend 90 % of rendering and training compute on easy, unambiguous elements while rarely placing a positive target next to its exact visual confuser at identical coordinates.

### SOTA Method: Counterfactual Minimal-Pair Data Synthesis
Inspired by **Counterfactual Data Augmentation (CDA)** (Kaushik et al., *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data*) and **Hard-Negative Contrastive Scene Generation**:
- Instead of sampling independent random layouts, generate **Counterfactual Twin Pairs** $(x, x^{\text{cf}})$ that share the exact same layout seed, background, typography, surrounding elements, and bounding-box coordinates, differing **only** in the single causal variable under test:
  1. `tab-selection-twins`: Keep the tab bar layout and content fixed; exhaustively pair every `selected_tab_id = i` with every `focused_element_id = j` (both on-tab $j \in \text{tabs}$ and off-tab $j \in \text{grid}$).
  2. `decoy-border-twins`: Keep the card grid fixed; pair each focused card with an identical unfocused decoy card carrying an authored static white border (`width` in `{2, 4, 6} pt`, `alpha` in `{0.6, 0.85, 1.0}`).
  3. `wide-control-twins`: Keep the iOS form row geometry fixed; swap only the trailing interactive widget among `toggle` (switch), `picker` (chevron/menu), and `stepper` (`+ / -`).

Training and evaluating on counterfactual twin pairs forces the network to attend to the true discriminating feature (e.g., the switch thumb or the concentric moat-ring) rather than layout position or row width!

---

## 2. Controlled Test and Decision Rules

### Hypothesis
At an equal capture and training budget (`48` frames), counterfactual twin synthesis produces higher hard-negative separation (measured by error-slice recall and zero false selections on decoys) than uniform random seed sampling.

### Experimental Arms
All arms use a fixed 48-frame capture budget, identical group-partition rules, and `body_measure417` rendered-body verification:
1. `control` (`counterfactualKind = 'random-seeds'`, `maxPairs = 24`): 48 frames from uniform random seeds without paired confuser mutation.
2. `tab-selection-twins` (`counterfactualKind = 'tab-selection-twins'`, `maxPairs = 24`): 24 counterfactual pairs (`48` frames) decoupling `isSelected` from `isFocused` across tab bars and content rows.
3. `decoy-border-twins` (`counterfactualKind = 'decoy-border-twins'`, `maxPairs = 24`): 24 counterfactual pairs (`48` frames) placing static white/gray borders (`2 pt`, `4 pt`, `6 pt`) on unfocused neighbor cards in both Standard and HCF profiles.
4. `wide-control-twins` (`counterfactualKind = 'wide-control-twins'`, `maxPairs = 24`): 24 iOS counterfactual pairs (`48` frames) mutating only the trailing control (`toggle`, `picker`, `stepper`, plain `listRow`) inside identical full-width row containers.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: Every twin pair passes the rendered-body gate (`0` outside labels, `<= 10 %` empty labels), achieves `>= 0.99` pixel identity outside the mutated control bounding box, and exposes `>= 3x` more hard-negative errors on the pinned baseline model than the equal-budget `random-seeds` control.
- **Contradicted**: Counterfactual mutation alters unrelated layout regions (`pixel diff > 1 %` outside the target container) or fails rendered-body bounds checks.
- **Inconclusive**: Simulator target binding (`capture_target_not_clear`) or restoration checks fail.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` unblocks `B405-005`, `B405-016`, `B405-027`, `B405-101`, and `B405-102` using local deterministic synthesis rather than waiting for external captures.
  - `Maximum-mini-TTR` and `GeneratorRunner` gain a closed-loop active-learning recipe compiler: whenever `T42` or `T37` finds a class confusion or focus decoy failure, `T72` synthesizes the exact counterfactual twin batch to repair it.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` identifies which SwiftUI/UIKit layout containers reflow unexpectedly when a child control type changes, and locks explicit frame constraints in `GeneratorRunner` and `Maximum-mini-TTR` Fixture.

---

## 4. Template `T72` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T72': (
    {'baseRecipe', 'failureSlice', 'generator'},
    {'counterfactualKind', 'maxPairs'},
    'counterfactual_synthesis418.run',
    'capture',
    'capture',
),
```

### Inputs and Parameters
- **Inputs**:
  - `baseRecipe`: Pinned seed recipe JSON (`counterfactual-base-recipe-v1`).
  - `failureSlice`: Pinned JSON failure report from `T42` or `T37` naming the target class/focus confusion.
  - `generator`: Pinned `GeneratorRunner` build receipt (`ios-generator-build-v1`) or `Maximum-mini-TTR` Fixture target binding (`native-capture-target-v1`).
- **Parameters**:
  - `counterfactualKind`: `str` in `{'random-seeds', 'tab-selection-twins', 'decoy-border-twins', 'wide-control-twins'}`.
  - `maxPairs`: `int` in `1..50` (total frames $\le 100$).

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T72",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-183-cftwins",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "At a fixed 48-frame capture budget, does counterfactual twin synthesis (tab-selection-twins, decoy-border-twins, wide-control-twins) maintain >= 0.99 background structural parity and isolate more hard-negative errors than random seeds?",
  "decision": "Support counterfactual kinds that pass all rendered-body gates, keep >= 0.99 non-target pixel parity between twins, and find at least 3x more baseline confuser errors than the random-seeds control.",
  "outcomes": {
    "supported": "Admit the passing counterfactual twin groups into the hard-negative development and training benchmarks (B405-005, B405-016, B405-027).",
    "contradicted": "Lock explicit container frame sizes in the generator before repeating counterfactual mutation.",
    "inconclusive": "Run capture when the Simulator target is free and complete restoration verification."
  },
  "shared": {
    "inputs": {
      "baseRecipe": {"file": "Research/Experiments/t46-recipes/b418-counterfactual-base.json"},
      "failureSlice": {"file": "Research/Experiments/results/B405-016.json"},
      "generator": {"file": ".build/ios-capture-t46/build-receipt-r4.json"}
    },
    "parameters": {"maxPairs": 24}
  },
  "arms": [
    {"id": "control", "label": "24 random-seed pairs (48 frames)", "parameters": {"counterfactualKind": "random-seeds"}},
    {"id": "tab-twins", "label": "24 selected-vs-focused tab twin pairs", "parameters": {"counterfactualKind": "tab-selection-twins"}},
    {"id": "border-twins", "label": "24 static-border vs focus-ring twin pairs", "parameters": {"counterfactualKind": "decoy-border-twins"}},
    {"id": "wide-twins", "label": "24 wide toggle/picker/listRow twin pairs", "parameters": {"counterfactualKind": "wide-control-twins"}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/counterfactual_synthesis418.py`**:
   - Validate `counterfactualKind` and `maxPairs`.
   - Compile paired scene definitions where `pair_id` links Twin A and Twin B into the **exact same data group and role** (preventing any train/development split leak between twins!).
   - After rendering, compute the non-target background pixel parity check (`non_target_pixel_equality >= 0.99`) and `body_measure417` rendered-body verification.
2. **Create `scripts/test_counterfactual_synthesis418.py`**:
   - Verify that Twin A and Twin B always receive identical `group` and `role` assignments.
   - Verify that non-target layout reflow (`< 0.99` pixel parity outside the mutated container) triggers an explicit `counterfactual_layout_reflow` failure.

### Reference Adapter Code (`scripts/counterfactual_synthesis418.py`)
```python
"""T72: Failure-guided counterfactual twin recipe synthesis and structural parity verification."""
import numpy as np
import research_queue as q

OUT = None
KINDS = ('random-seeds', 'tab-selection-twins', 'decoy-border-twins', 'wide-control-twins')


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'counterfactualKind', 'maxPairs'}, 'cf_parameters')
    kind, max_pairs = value['counterfactualKind'], value['maxPairs']
    q.require(kind in KINDS, 'cf_kind_invalid')
    q.require(type(max_pairs) is int and 1 <= max_pairs <= 50, 'cf_max_pairs_invalid')
    return kind, max_pairs


def verify_twin_background_parity(
    img_a: np.ndarray,
    img_b: np.ndarray,
    mutated_boxes_xywh: list[tuple[int, int, int, int]],
    pad: int = 24,
) -> float:
    """Measure fraction of identical pixels outside the padded mutated element bounding boxes."""
    q.require(img_a.shape == img_b.shape, 'twin_shape_mismatch')
    h, w = img_a.shape[:2]
    mask = np.ones((h, w), dtype=bool)
    for x, y, bw, bh in mutated_boxes_xywh:
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(w, x + bw + pad), min(h, y + bh + pad)
        mask[y0:y1, x0:x1] = False
    if not mask.any():
        return 1.0
    diff = np.abs(img_a[mask].astype(np.int16) - img_b[mask].astype(np.int16)).max(axis=-1)
    return float((diff <= 2).mean())
```

### Resource and Time Budget
- **Preparation**: 60 min to 90 min.
- **Execution**: 4 capture jobs at 180 s to 350 s each (within the 800 s and 100 MB standing capture class when the Simulator is free).
- **Review**: 15 min via `backlog_pipeline.py review`.
