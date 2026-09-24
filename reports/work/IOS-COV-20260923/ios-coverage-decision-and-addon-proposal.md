# IOS-COV: 41-Class Coverage Decision and Targeted Native Addon Proposal

**Date:** 2026-09-23  
**Author:** NUIAK Architect  
**Status:** Review-ready proposal for maintainer approval  
**Parents:** TASK-DATA-01, TASK-6a-10, TASK-6a-11  

---

## 1. Context and Established Evidence

Following the completion of the 16,940-pair `r6` reconstructed corpus ([IOS-R6 Handoff](../IOS-R6-20260923/handoff.md)) and the Run 009 PyTorch baseline evaluation on all 2,000 replacement test images ([IOS-R6-BASELINE Handoff](../IOS-R6-BASELINE-20260923/handoff.md)), the empirical data profile of NativeUIAuditKit is now rigorously established:

1. **Sealed Corpus Allocation:**
   - Total: 16,940 pairs (12,540 train / 2,400 validation / 2,000 test).
   - Zero decoded duplicates, zero cross-split leakage, 100% manifest and byte checksum verification.
2. **Current Visible Class Support Across Splits:**
   - **Train (12,540 images):** **39 / 41 classes** supported. Missing: `dynamicIsland`, `webContent`.
   - **Validation (2,400 images):** **12 / 41 classes** supported. Missing: 29 classes.
   - **Test (2,000 images):** **13 / 41 classes** supported. Missing: 28 classes.
3. **Empirical Baseline Benchmark (Run 009):**
   - Macro mAP@0.50 over the 13 supported test classes: **0.5549**.
   - Macro mAP@0.50:0.95 over the 13 supported test classes: **0.3982**.
   - 28 unsupported test classes reported as `unavailable` under P2-METRICS (AP 0.0 not imputed).

---

## 2. Gate Interpretation & Core Decisions

### Decision 1: `r6` Corpus Role — Diagnostic Baseline Only, Not Full-Taxonomy Production Candidate
- The current `r6` corpus is **accepted for diagnostic baseline evaluation and architecture iteration**, but **cannot authorize 41-class production model release (DS-G8)**.
- DS-G8 requires holdout mAP@0.50 $\ge 0.85$ across the 41-class taxonomy. Testing on a split where 28 classes have zero ground truth instances cannot satisfy this gate.

### Decision 2: `webContent` Resolution
- Historical attempts to capture `webContent` via live `WKWebView` in the generator caused runtime hangs, process timeouts, and non-deterministic rendering.
- **Resolution:** Keep `webContent` in the taxonomy (to preserve stable category IDs 0–40), but declare it an **explicit unsupported milestone exception** for synthetic generator builds until a static, offline-rendered HTML/WebKit snapshot template is implemented. No artificial AP 0.0 or fabricated placeholder boxes may be emitted.

### Decision 3: No Unilateral Taxonomy Reduction
- Under the **Taxonomy Stability** rule in `AGENTS.md`, category IDs 0–40 in `Research/schemas/category_map.json` are frozen at v1.0. 
- Models must continue to output 41 class heads. Missing classes must be addressed by targeted dataset additions, not by redefining the taxonomy.

---

## 3. Targeted Native Addon Proposal

To achieve full 41-class train/val/test coverage without destabilizing the verified 16,940-pair `r6` core, we propose a modular **Native Coverage Addon Corpus (`ios-41class-addon-v1`)**.

### 3.1 Taxonomy Breakdown of the 28 Missing Test Classes

| Category | Missing Test Classes (Total: 28) | Generator Template Strategy |
|---|---|---|
| **Contextual Containers (5)** | `actionSheet`, `alert`, `contextMenu`, `popover`, `sheet` | Modal presentation runner with overlay coordinate capture |
| **Chrome & System UI (5)** | `dynamicIsland`, `sidebar`, `statusBar`, `tabBar`, `toolbar` | Full-screen app scaffolds with explicit navigation/chrome chrome headers/footers |
| **Controls & Actions (6)** | `cancelAction`, `colorWell`, `destructiveButton`, `menuButton`, `segmentedControl`, `slider` | Dense control panels with diverse interactive states |
| **Content & Indicators (12)** | `activityIndicator`, `collectionItem`, `colorWell`, `disclosureGroup`, `homeIndicator`, `link`, `mapView`, `refreshControl`, `scrollIndicator`, `searchField`, `tooltip`, `unknown` | Specialized SwiftUI view templates rendering non-standard content |

### 3.2 Addon Architecture & Family Isolation
The addon will follow the strict family holdout protocol (BP-27):
- **4 Dedicated Addon Families:**
  1. `ModalDialogueFlow` (covers `alert`, `actionSheet`, `sheet`, `popover`, `contextMenu`, `cancelAction`, `destructiveButton`).
  2. `SystemNavigationShell` (covers `tabBar`, `toolbar`, `sidebar`, `statusBar`, `dynamicIsland`, `searchField`).
  3. `InteractiveControlPalette` (covers `colorWell`, `menuButton`, `segmentedControl`, `slider`, `disclosureGroup`).
  4. `RichContentFeed` (covers `collectionItem`, `mapView`, `activityIndicator`, `refreshControl`, `scrollIndicator`, `link`, `tooltip`).
- **Split Allocation (8:1:1 or Disjoint Family):**
  - To ensure zero data leakage, variations of each family with disjoint seeds/recipes will be partitioned strictly:
    - 2,000 Addon Train pairs
    - 400 Addon Validation pairs
    - 400 Addon Test pairs
  - Total Addon: **2,800 pairs**.
- Combined total with `r6`: **19,740 pairs** (14,540 train / 2,800 val / 2,400 test) with **100% class representation across all 3 splits**.

### 3.3 Acceptance Criteria for Addon Corpus
1. **Full Class Support:** Minimum 50 ground truth bounding boxes per class in the test split.
2. **Zero Leakage:** Deterministic family-level split isolation verified by `scripts/regression_selector.py` and `scripts/corpus_assembly.py`.
3. **Strict Coordinates:** Top-left pixel and bottom-left Vision coordinates validated via `boundsVisionNormalized` and `boundsPixels`.
4. **Offline Toolchain:** Output packaged via `export_coco.py` with content seal and retention inventory.

---

## 4. Next Action & Recommendations

1. **Maintainer Action:** Review and approve the Addon proposal scope (2,800 pairs across 4 dedicated families).
2. **Immediate Engineering Work:**
   - Implement SwiftUI view templates for `ModalDialogueFlow` and `SystemNavigationShell` in `GeneratorRunner/Templates/`.
   - Maintain the frozen Run 009 baseline (`reports/work/IOS-R6-BASELINE-20260923/`) as the reference floor for subsequent training runs.
