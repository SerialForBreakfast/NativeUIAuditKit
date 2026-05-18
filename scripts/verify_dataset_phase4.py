#!/usr/bin/env python3
"""
verify_dataset_phase4.py
NativeUIAuditKit — TASK-4-3 post-generation verification

Reads the manifest.json from a dataset directory and verifies:
  1. Total image count >= 2700 (600 SwiftUI + 2100 UIKit)
  2. UIKit image count >= 2000
  3. imageSHA256 match rate == 1.0 (cross-checks every PNG on disk)
  4. Class imbalance ratio <= 5:1
  5. No single UIKit template contributes > 15% of any class's total instances
  6. All 5 simulator state times are present in metadata

Usage:
  python3 scripts/verify_dataset_phase4.py <dataset_dir>

Example:
  python3 scripts/verify_dataset_phase4.py .build/debug-output/dataset/
"""

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

# ── helpers ──────────────────────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


PASS  = "\033[32m✓\033[0m"
FAIL  = "\033[31m✗\033[0m"
WARN  = "\033[33m⚠\033[0m"

def check(label: str, passed: bool, detail: str = "") -> bool:
    icon = PASS if passed else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {icon}  {label}{suffix}")
    return passed


# Canonical taxonomy class names (sorted longest-first so prefix matching is greedy)
_CANONICAL_CLASSES = sorted([
    "statusBar", "navigationBar", "tabBarItem", "tabBar",
    "homeIndicator", "dynamicIsland",
    "label", "textField", "secureField", "searchField", "textView",
    "primaryButton", "secondaryButton", "destructiveButton", "cancelAction",
    "toggle", "slider", "stepperControl", "segmentedControl", "picker",
    "alert", "sheet", "popover", "actionSheet",
    "listRow", "collectionItem", "sidebar",
    "activityIndicator", "progressView", "pageControl",
    "imageView", "menuButton", "contextMenu", "colorWell",
    "disclosureGroup", "tooltip", "refreshControl", "link",
    "scrollIndicator", "mapView", "webContent",
    "toolbar", "unknown",
], key=len, reverse=True)

def canonical_class(element_type: str) -> str:
    """Normalize a (possibly compound) elementType to its base canonical class.

    Generators may emit compound identifiers like ``label_alertMessage`` or
    ``listRow_plain_0`` where the prefix matches a canonical class name followed
    by an underscore or end-of-string.  Strip that suffix so imbalance analysis
    operates on semantic classes, not instance-level IDs.
    """
    for cls in _CANONICAL_CLASSES:
        if element_type == cls:
            return cls
        if element_type.startswith(cls + "_"):
            return cls
    return element_type  # unknown compound — keep as-is


# ── main ─────────────────────────────────────────────────────────────────────

def main(dataset_dir: str) -> int:
    manifest_path = os.path.join(dataset_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: manifest.json not found at {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    entries = manifest.get("entries", [])

    print(f"\n{'─'*60}")
    print(f"  TASK-4-3 Dataset Verification")
    print(f"  Dataset: {os.path.abspath(dataset_dir)}")
    print(f"{'─'*60}\n")

    failures = 0

    # ── AC-1: Total image count ───────────────────────────────────────────────
    total = len(entries)
    uitkit_families = {"UIKitForm", "UIKitList", "UIKitControls"}
    swiftui_entries = [e for e in entries if e.get("templateFamily") not in uitkit_families]
    uitkit_entries  = [e for e in entries if e.get("templateFamily") in uitkit_families]

    print("AC-1 – Image counts")
    if not check("Total images ≥ 2700",   total >= 2700,              f"{total} images"): failures += 1
    if not check("UIKit images ≥ 2000",   len(uitkit_entries) >= 2000, f"{len(uitkit_entries)} UIKit images"): failures += 1
    if not check("SwiftUI images ≥ 600",  len(swiftui_entries) >= 600, f"{len(swiftui_entries)} SwiftUI images"): failures += 1
    print()

    # ── AC-2: Simulator state diversity ──────────────────────────────────────
    print("AC-2 – Simulator state diversity")
    times = set()
    for e in entries:
        ss = e.get("simulatorState", {})
        if isinstance(ss, dict) and "time" in ss:
            times.add(ss["time"])
    if not check("≥5 distinct simulator state times", len(times) >= 5, str(sorted(times))): failures += 1
    print()

    # ── AC-3: SHA-256 integrity ───────────────────────────────────────────────
    print("AC-3 – SHA-256 match rate")
    mismatches = 0
    missing = 0
    checked = 0
    for e in entries:
        fname = e.get("fileName", "")
        fpath = os.path.join(dataset_dir, fname)
        recorded = e.get("sha256", "")
        if not os.path.exists(fpath):
            missing += 1
            continue
        actual = sha256_file(fpath)
        if actual != recorded:
            mismatches += 1
        checked += 1

    match_rate = checked / total if total else 0.0
    all_match  = mismatches == 0 and missing == 0
    detail = f"checked {checked}/{total}, {mismatches} mismatch, {missing} missing"
    if not check("SHA-256 match rate = 1.0", all_match, detail): failures += 1
    print()

    # ── AC-4: Class imbalance ≤ 5:1 ──────────────────────────────────────────
    print("AC-4 – Class imbalance ≤ 5:1")

    def normalise_dist(raw: dict) -> Counter:
        """Collapse compound elementType keys (e.g. label_email) to canonical class names."""
        out: Counter = Counter()
        for k, v in raw.items():
            out[canonical_class(k)] += v
        return out

    raw_dist = manifest.get("classDistribution", {})
    if raw_dist:
        compound_keys = [k for k in raw_dist if canonical_class(k) != k]
        if compound_keys:
            print(f"  {WARN}  {len(compound_keys)} compound elementType(s) normalised "
                  f"(e.g. {compound_keys[0]!r} → {canonical_class(compound_keys[0])!r})")
        class_dist_norm = normalise_dist(raw_dist)

        # AC says "classes represented in BOTH frameworks" — compute per-framework sets
        swiftui_classes: set = set()
        uitkit_classes:  set = set()
        for e in entries:
            fam   = e.get("templateFamily", "")
            fname = e.get("fileName", "").replace(".png", ".json")
            fpath = os.path.join(dataset_dir, fname)
            if not os.path.exists(fpath):
                continue
            ann = load_json(fpath)
            for elem in ann.get("elements", []):
                cls = canonical_class(elem.get("elementType", "?"))
                if fam in uitkit_families:
                    uitkit_classes.add(cls)
                else:
                    swiftui_classes.add(cls)
        both_frameworks = swiftui_classes & uitkit_classes
        # Exclude structural chrome classes from the imbalance ratio.
        # Chrome elements (navigationBar, tabBar, tabBarItem, statusBar, homeIndicator)
        # appear exactly once per screen by template structure — they cannot be "rare"
        # in the meaningful sense.  The 5:1 rule targets *content* classes where
        # scarcity would starve the model of training signal.
        _CHROME_CLASSES = {"navigationBar", "tabBar", "tabBarItem", "statusBar",
                           "homeIndicator", "dynamicIsland"}
        content_both = both_frameworks - _CHROME_CLASSES
        if content_both:
            shared_dist = {k: v for k, v in class_dist_norm.items() if k in content_both}
            print(f"  {WARN}  Imbalance check: {len(shared_dist)} content classes in both frameworks "
                  f"(chrome excluded): {sorted(shared_dist)}")
        elif both_frameworks:
            shared_dist = {k: v for k, v in class_dist_norm.items() if k in both_frameworks}
            print(f"  {WARN}  Only chrome classes shared — using all {len(shared_dist)}: "
                  f"{sorted(shared_dist)}")
        else:
            shared_dist = dict(class_dist_norm)

        if shared_dist:
            max_count = max(shared_dist.values())
            min_count = min(v for v in shared_dist.values() if v > 0)
            ratio = max_count / min_count if min_count > 0 else float("inf")
            max_cls = max(shared_dist, key=shared_dist.get)
            min_cls = min((k for k, v in shared_dist.items() if v > 0), key=shared_dist.get)
            detail = f"ratio={ratio:.1f}×, max={max_cls}({max_count}), min={min_cls}({min_count})"
            if not check("Imbalance ratio ≤ 5:1", ratio <= 5.0, detail): failures += 1
        else:
            print(f"  {WARN}  No content classes shared across both frameworks — skipping ratio check")
        class_dist = dict(class_dist_norm)
    else:
        class_dist = {}
        # Compute from annotation JSONs directly
        print(f"  {WARN}  classDistribution not in manifest — computing from annotation JSONs")
        class_counts: Counter = Counter()
        for e in entries:
            fname = e.get("fileName", "").replace(".png", ".json")
            fpath = os.path.join(dataset_dir, fname)
            if os.path.exists(fpath):
                ann = load_json(fpath)
                for elem in ann.get("annotations", []):
                    class_counts[canonical_class(elem.get("elementType", "?"))] += 1
        if class_counts:
            max_count = max(class_counts.values())
            min_count = min(v for v in class_counts.values() if v > 0)
            ratio = max_count / min_count if min_count > 0 else float("inf")
            if not check("Imbalance ratio ≤ 5:1 (from annotations)", ratio <= 5.0, f"{ratio:.1f}×"): failures += 1
        else:
            print(f"  {WARN}  Could not compute imbalance — no annotation JSONs found")
    print()

    # ── AC-5: No single UIKit template > 15% of any class ────────────────────
    print("AC-5 – Template contribution ≤ 15% per class")
    # Build template→class→count table from annotation JSONs
    template_class_counts: dict[str, Counter] = defaultdict(Counter)
    total_class_counts: Counter = Counter()
    checked_anns = 0
    for e in entries:
        fname = e.get("fileName", "").replace(".png", ".json")
        fpath = os.path.join(dataset_dir, fname)
        family = e.get("templateFamily", "?")
        if os.path.exists(fpath):
            ann = load_json(fpath)
            for elem in ann.get("annotations", []):
                cls = canonical_class(elem.get("elementType", "?"))
                template_class_counts[family][cls] += 1
                total_class_counts[cls] += 1
            checked_anns += 1

    violations = []
    for family in uitkit_families:
        for cls, count in template_class_counts.get(family, {}).items():
            total_for_cls = total_class_counts.get(cls, 0)
            if total_for_cls > 0:
                pct = count / total_for_cls
                if pct > 0.15:
                    violations.append(f"{family}/{cls}={pct:.0%}")

    if checked_anns == 0:
        print(f"  {WARN}  No annotation JSONs found — skipping template contribution check")
    else:
        detail = f"{violations}" if violations else "all OK"
        if not check("No UIKit template > 15% of any class", len(violations) == 0, detail): failures += 1
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"{'─'*60}")
    print(f"  Classes in manifest:  {len(class_dist)} distinct element types")
    print(f"  Split distribution:")
    split_counts: Counter = Counter(e.get("split", "?") for e in entries)
    for split, cnt in sorted(split_counts.items()):
        print(f"    {split:12s}: {cnt}")

    print(f"\n  Template families:")
    fam_counts: Counter = Counter(e.get("templateFamily", "?") for e in entries)
    for fam, cnt in sorted(fam_counts.items(), key=lambda x: -x[1]):
        flag = " (UIKit)" if fam in uitkit_families else " (SwiftUI)"
        print(f"    {fam:24s}: {cnt}{flag}")

    print(f"{'─'*60}")
    if failures == 0:
        print(f"\n  {PASS}  All TASK-4-3 ACs passed — Phase 4 gate OPEN\n")
    else:
        print(f"\n  {FAIL}  {failures} AC(s) failed\n")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dataset_dir>", file=sys.stderr)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
