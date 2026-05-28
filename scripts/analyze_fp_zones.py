#!/usr/bin/env python3
"""
analyze_fp_zones.py
NativeUIAuditKit/scripts

Identifies which GT element classes appear in the y-zones where textField false
positives were observed:
  • y=0.15–0.35  (upper-mid — 36 false-class textField FPs)
  • y=0.75–1.00  (bottom — 70 false-class textField FPs)

Runs over all validation images (not just textField images) to find what the
model is likely confusing with textFields in those strips.

Also reports:
  • Overall GT class distribution per zone (across all images)
  • Which non-textField classes dominate each zone
  • Candidate hard-negative element types to generate

Usage:
  python3 scripts/analyze_fp_zones.py
"""

import json
from collections import defaultdict

ANN_PATH = (
    "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/"
    "812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/"
    "E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset/createml_export/"
    "validation/annotations.json"
)

STRIP_H_FRAC = 0.22   # strip height as fraction of image height
STRIDE_FRAC  = 0.11   # 50% overlap → stride = stripH / 2

# The two FP-heavy zones (y-start of strip, from diagnose_textfield_fps.swift)
ZONES = {
    "upper-mid (y=0.15–0.35)": (0.15, 0.35),
    "bottom    (y=0.75–1.00)": (0.75, 1.00),
}

def strip_start_fracs(image_h_px=1):
    """Return list of strip y-start fractions for an image."""
    stripH = max(1, int(image_h_px * STRIP_H_FRAC))
    stride  = max(1, stripH // 2)
    fracs = []
    y = 0
    while y + stripH <= image_h_px:
        fracs.append(y / image_h_px)
        y += stride
    return fracs

def box_cy(ann_box):
    """Return cy (top-left normalized) from a Create ML annotation box."""
    return ann_box["coordinates"]["y"]

def box_y1(ann_box):
    c = ann_box["coordinates"]
    return c["y"] - c["height"] / 2

def box_y2(ann_box):
    c = ann_box["coordinates"]
    return c["y"] + c["height"] / 2

def strip_captures_box(strip_y_frac, ann_box):
    """Does the strip at strip_y_frac (height=STRIP_H_FRAC) overlap the element?"""
    s_top = strip_y_frac
    s_bot = strip_y_frac + STRIP_H_FRAC
    e_top = box_y1(ann_box)
    e_bot = box_y2(ann_box)
    # overlap if strip_top < elem_bot AND strip_bot > elem_top
    return s_top < e_bot and s_bot > e_top

with open(ANN_PATH) as f:
    data = json.load(f)

print(f"Loaded {len(data)} validation images\n")
print("=" * 70)

for zone_name, (lo, hi) in ZONES.items():
    # For each image: which strips fall in this zone?
    # For each such strip: which GT elements does it capture?
    zone_class_counts = defaultdict(int)
    zone_images_with_match = 0
    total_strips_in_zone = 0

    for entry in data:
        # Approximate strip starts (assume normalised coords, image-height-independent)
        # Use 100 units as stand-in since all coords are normalised
        strip_fracs = strip_start_fracs(100)
        zone_strips = [f for f in strip_fracs if lo <= f < hi]
        if not zone_strips:
            continue

        matched = set()
        for ann in entry["annotation"]:
            for sf in zone_strips:
                if strip_captures_box(sf, ann):
                    zone_class_counts[ann["label"]] += 1
                    matched.add(ann["label"])
                    break  # count element once per image even if multiple strips hit it

        if matched:
            zone_images_with_match += 1
        total_strips_in_zone += len(zone_strips)

    print(f"\nZone: {zone_name}")
    print(f"  Strip y-range: [{lo:.2f}, {hi:.2f}]  strip height={STRIP_H_FRAC:.2f}")
    print(f"  Images with ≥1 GT element captured in this zone: {zone_images_with_match}")
    print()
    print("  GT class counts in this zone (sorted by frequency):")
    total = sum(zone_class_counts.values())
    for cls, cnt in sorted(zone_class_counts.items(), key=lambda x: -x[1]):
        pct = cnt / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 2)
        marker = "  ← textField FP zone" if cls != "textField" else "  ← (real textField)"
        print(f"    {cls:<22} {cnt:>5}  ({pct:5.1f}%)  {bar}{marker}")

print("\n" + "=" * 70)
print("\nInterpretation:")
print("  Non-textField elements that appear frequently in both FP zones are the")
print("  primary candidates for hard-negative strip generation in Run 005.")
print("  Generate strips containing ONLY those elements (no textField label),")
print("  so the model learns they are NOT textFields in strip context.")
