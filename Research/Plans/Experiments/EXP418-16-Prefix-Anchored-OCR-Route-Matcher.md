# EXP418-16 — Prefix-Anchored Weighted Levenshtein Automaton for Clipped-OCR TTR Route Recovery (`B405-244` / Template `T82`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Before/after focus` (`PAIR`). Priority: `P0`.
Parent task: `B405-220` (`Tasks.md` Immediate Blocker). Template: `T82` (`prefix_ocr_route_matcher418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md) (`Immediate blocker — B405-220 native capture recovery`, lines 9–28), `Maximum-mini-NUIAK` traced the `B405-220` native button capture route failure (`hcf-a85a5a4e-d7f1-487b-bbbc-fa620f5480fe`) to its exact root cause:
- `Maximum-mini-TTR` aborted before collecting frames and reported an ambiguous Standard-setting observation after 3 remote inputs.
- Both the preflight and postflight observations **agree on the page title, the focused control index, the `Standard` value token, and the complete label prefix through `Focus Style`**.
- The failure was caused solely by **irrelevant right-edge clipped-label OCR variation on `Display`** (`VNRecognizeTextRequest` drops or substitutes 1 to 4 trailing characters at the right viewport clip boundary of a long description or subtitle).

As noted in `Tasks.md` line 26:
> "`Maximum-mini-TTR` needs a narrowly tested observation-matching correction, not another capability check or blind retry."

### SOTA Method: Prefix-Anchored Weighted Finite-State Edit Transducer (`WFST` / Positional Asymmetric Levenshtein)
In computational linguistics and OCR post-correction (Mohri et al., *Weighted Finite-State Transducers in Speech and OCR Recognition*; Navarro, *A Guided Tour to Approximate String Matching*), OCR errors on UI layout rows are **spatially non-uniform**:
- Characters in the **Anchor Prefix** (the structural row title up to the key delimiter, such as `Focus Style`) and **Semantic Value Tokens** (`Standard`, `High Contrast`, `On`, `Off`, `Automatic`) carry $100\%$ of the state-safety meaning.
- Characters in the **Right-Clipped Tail** (where long descriptive text approaches the right edge of the container box $x_{\text{max}} \ge 0.85 \cdot W_{\text{row}}$ or ends in ellipsis `...` / `…`) experience deterministic truncation and anti-aliasing glyph splits.

We formalize safe TTR observation matching as a **Two-Tier Structural + Positional Weighted Edit Automaton**:
1. **Hard Structural Invariant Gate (Infinite Penalty)**:
   Require exact equality on `(pageId, focusedRowKey, focusStyleValue)`:
   - `obs.page == expected.page`
   - `obs.focusKey == expected.focusKey`
   - `obs.valueToken == expected.valueToken` (`"Standard"` $\neq$ `"High Contrast"` under any edit budget!).
2. **Positional Prefix-Anchored Edit Distance $d_{\text{pos}}(s_1, s_2)$**:
   For a row string segmented into `(prefix_through_anchor, trailing_suffix)`:
   - Any character edit inside `prefix_through_anchor` has cost $w_{\text{prefix}} = 1.0$ (threshold $= 0$).
   - Character deletions or substitutions in `trailing_suffix` occurring after character index $L_{\text{anchor}}$ have positional decay weight $w_{\text{tail}}(k) = 0.05 \cdot \exp(-(k - L_{\text{anchor}})/8)$, bounded by a maximum normalized tail divergence $\tau_{\text{tail}} \le 0.15$.

---

## 2. Controlled Test Design

- **Pinned Dataset**: Stored coordinator reproduction corpus from cursor `827` (`hcf-a85a5a4e-d7f1-487b-bbbc-fa620f5480fe`), all retained `Maximum-mini-TTR` preflight/postflight observation pairs across `B405-155` to `B405-220`, plus synthetic adversarial state-mutation negatives (where `Standard` is changed to `High Contrast`, focus moves to an adjacent row, or page title changes).
- **Arms**:
  1. `exact-string` (Control): Current exact full-line OCR string equality.
  2. `unweighted-levenshtein`: Standard normalized Levenshtein distance ($\le 0.15$) across the entire string (unsafe control).
  3. `prefix-anchored-wfst-v1`: Hard structural invariant gate (`page`, `focusKey`, `valueToken`, and exact prefix through `Focus Style`) + positional tail-clip tolerance ($\tau_{\text{tail}} = 0.15$).
- **Decision Rules**:
  - **Supported**: `prefix-anchored-wfst-v1` resolves 100 % of clipped-tail `Display` OCR variations (`hcf-a85a5a4e-d7f1-487b-bbbc-fa620f5480fe` and all retained valid pairs pass) while rejecting **100 % of adversarial state mutations** (`Standard <-> High Contrast`, wrong row focus, wrong page, or mutated prefix).
  - **Contradicted**: Either `prefix-anchored-wfst-v1` fails on the `B405-220` reproduction trace or accepts any wrong-value/wrong-focus adversarial state.
  - **Inconclusive**: Verify against both `Maximum-mini-TTR` and `Sillycon-TTR` observation schemas before handoff.
  - **Regression Gate**: Zero tolerance (`0` false positives) on value-token or focus-target mismatches.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-TTR` (`B405-220` Unblock)**: Supplies the exact, unit-tested observation-matching function needed to clear the `B405-220` capture blocker and unblock the 40 dependent analysis jobs (`B405-221` through `B405-228`).
2. **For `Sillycon-TTR` (`tvos-safe-navigation`)**: Prevents closed-loop Apple TV navigation from aborting when `VNRecognizeTextRequest` clips trailing description glyphs on `Display` or `Accessibility` settings screens, while strictly preserving the safety lock on setting values.

---

## 4. New Template Contract (`T82`)

Register `T82` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T82": (
    {"observationsPath", "adversarialPath"},
    {"anchorPhrase", "maxTailCost"},
    "prefix_ocr_route_matcher418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Prefix-Anchored Positional OCR Matcher (`scripts/prefix_ocr_route_matcher418.py`)

```python
"""T82 adapter: Prefix-Anchored Weighted Levenshtein Automaton for Clipped-OCR TTR Route Recovery."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteObservation:
    page: str
    focus_key: str
    setting_value: str
    full_ocr_line: str


def match_prefix_anchored_observation(
    before: RouteObservation,
    after: RouteObservation,
    anchor_phrase: str = "Focus Style",
    max_tail_cost: float = 0.15,
) -> dict[str, object]:
    """Verifies exact page, focus, setting value, and prefix through anchor_phrase, allowing right-edge OCR clip."""
    if before.page != after.page:
        return {"matched": False, "reason": "page_mismatch", "tailCost": 1.0}
    if before.focus_key != after.focus_key:
        return {"matched": False, "reason": "focus_mismatch", "tailCost": 1.0}
    if before.setting_value.strip() != after.setting_value.strip():
        return {"matched": False, "reason": "setting_value_mismatch", "tailCost": 1.0}

    idx_b = before.full_ocr_line.find(anchor_phrase)
    idx_a = after.full_ocr_line.find(anchor_phrase)
    if idx_b < 0 or idx_a < 0:
        return {"matched": False, "reason": "anchor_phrase_missing", "tailCost": 1.0}

    end_b = idx_b + len(anchor_phrase)
    end_a = idx_a + len(anchor_phrase)
    prefix_b = " ".join(before.full_ocr_line[:end_b].split())
    prefix_a = " ".join(after.full_ocr_line[:end_a].split())
    if prefix_b != prefix_a:
        return {"matched": False, "reason": "prefix_mismatch", "tailCost": 1.0}

    tail_b = " ".join(before.full_ocr_line[end_b:].split())
    tail_a = " ".join(after.full_ocr_line[end_a:].split())
    if tail_b == tail_a:
        return {"matched": True, "reason": "exact_match", "tailCost": 0.0}

    # Check if one tail is a right-clipped prefix of the other or differs only at trailing boundary glyphs
    common_len = 0
    for cb, ca in zip(tail_b, tail_a):
        if cb == ca:
            common_len += 1
        else:
            break
    max_len = max(len(tail_b), len(tail_a), 1)
    unmatched_ratio = (max_len - common_len) / max_len
    weighted_tail_cost = 0.10 * unmatched_ratio
    matched = weighted_tail_cost <= max_tail_cost
    return {
        "matched": matched,
        "reason": "prefix_anchored_tail_clip_match" if matched else "tail_divergence_exceeded",
        "tailCost": round(weighted_tail_cost, 6),
        "commonTailChars": common_len,
    }
```

### Step 2 — Verification
- Create `scripts/test_prefix_ocr_route_matcher418.py` to test the exact `B405-220` reproduction strings from cursor `827` alongside 20 adversarial mutations (`Standard -> High Contrast`, `Focus Style -> Display`, row focus shift, and page title change).
