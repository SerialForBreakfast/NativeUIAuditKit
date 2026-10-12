#!/usr/bin/env python3
"""Generate synthetic multi-theme crop triplets for tvOS FocusRing training (ASD-STE100)."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    Image = ImageDraw = ImageFilter = None

THEMES = {
    "dark_standard": {
        "bg": (16, 18, 26),
        "card_fill": (38, 42, 54),
        "focus_stroke": (255, 255, 255),
        "shadow": (0, 0, 0, 180),
        "resting_stroke": (55, 60, 75)
    },
    "light_standard": {
        "bg": (228, 230, 236),
        "card_fill": (250, 250, 252),
        "focus_stroke": (20, 22, 28),
        "shadow": (120, 125, 135, 130),
        "resting_stroke": (195, 200, 210)
    },
    "dark_low_contrast": {
        "bg": (22, 24, 30),
        "card_fill": (32, 35, 44),
        "focus_stroke": (95, 100, 115),
        "shadow": (0, 0, 0, 150),
        "resting_stroke": (45, 48, 58)
    }
}

ARCHETYPES = {
    "shelf": {"w": 140, "h": 200, "radius": 12, "pill": False},
    "grid": {"w": 190, "h": 120, "radius": 10, "pill": False},
    "hero_detail": {"w": 180, "h": 52, "radius": 26, "pill": True},
    "top_nav_shelf": {"w": 160, "h": 46, "radius": 23, "pill": True},
    "settings_list": {"w": 220, "h": 60, "radius": 8, "pill": False},
    "action_dialog": {"w": 180, "h": 60, "radius": 14, "pill": False},
    "focus_maze": {"w": 105, "h": 105, "radius": 8, "pill": False}
}

def compute_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def render_crop_canvas(archetype_key, theme_key, is_focused, is_negative=False):
    if Image is None:
        raise RuntimeError("Pillow is required for image synthesis.")

    arch = ARCHETYPES[archetype_key]
    th = THEMES[theme_key]

    canvas = Image.new("RGBA", (256, 256), th["bg"] + (255,))
    cx, cy = 128, 128
    w, h = arch["w"], arch["h"]
    radius = arch["radius"]

    if is_negative:
        # Render a different adjacent element or offset position
        cx = 100 if archetype_key == "focus_maze" else 128
        cy = 100 if archetype_key == "focus_maze" else 128
        w = int(w * 0.90)
        h = int(h * 0.90)

    if is_focused:
        # Apply 1.13x elevation expansion
        scale = 1.13
        fw = int(w * scale)
        fh = int(h * scale)
        fradius = int(radius * scale)
        x0 = cx - fw // 2
        y0 = cy - fh // 2
        x1 = x0 + fw
        y1 = y0 + fh

        # Draw elevation drop shadow
        shadow_layer = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        sy0 = y0 + 10
        sy1 = y1 + 10
        shadow_draw.rounded_rectangle([x0 - 4, sy0, x1 + 4, sy1 + 4], radius=fradius + 2, fill=th["shadow"])
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(12))
        canvas = Image.alpha_composite(canvas, shadow_layer)

        # Draw card body and 3 px focus ring stroke
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=fradius, fill=th["card_fill"] + (255,))
        draw.rounded_rectangle([x0, y0, x1, y1], radius=fradius, outline=th["focus_stroke"] + (255,), width=3)
    else:
        # Unfocused resting state
        x0 = cx - w // 2
        y0 = cy - h // 2
        x1 = x0 + w
        y1 = y0 + h

        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=th["card_fill"] + (255,))
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=th["resting_stroke"] + (255,), width=1)

    return canvas.convert("RGB")

def generate_multi_theme_dataset(output_dir, cases_per_theme=70):
    root = Path(output_dir)
    crops_dir = root / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)

    theme_keys = list(THEMES.keys())
    arch_keys = list(ARCHETYPES.keys())

    all_cases = []
    case_counter = 1

    for theme in theme_keys:
        for arch_idx, arch in enumerate(arch_keys):
            # Equal distribution across archetypes for each theme
            count = cases_per_theme // len(arch_keys)
            for i in range(count):
                case_id = f"synth_mt_{case_counter:03d}"
                case_dir = crops_dir / case_id
                case_dir.mkdir(parents=True, exist_ok=True)

                anchor_file = case_dir / "crop_anchor.png"
                pos_file = case_dir / "crop_positive.png"
                neg_file = case_dir / "crop_negative.png"
                manifest_file = case_dir / "crop_manifest.json"

                # Render images
                img_anchor = render_crop_canvas(arch, theme, is_focused=True, is_negative=False)
                img_pos = render_crop_canvas(arch, theme, is_focused=False, is_negative=False)
                img_neg = render_crop_canvas(arch, theme, is_focused=False, is_negative=True)

                img_anchor.save(anchor_file, format="PNG")
                img_pos.save(pos_file, format="PNG")
                img_neg.save(neg_file, format="PNG")

                sha_anchor = compute_sha256(anchor_file)
                sha_pos = compute_sha256(pos_file)
                sha_neg = compute_sha256(neg_file)

                # Write item manifest
                biases = ["balanced", "center", "edge", "top_left"]
                bias = biases[case_counter % len(biases)]

                item_meta = {
                    "schemaVersion": "contract-v1-focus-triplets",
                    "layoutType": arch,
                    "theme": theme,
                    "cropDimension": [256, 256],
                    "anchor": {
                        "center": [128, 128],
                        "node_id": f"{arch}_node_{case_counter}",
                        "is_focused": True,
                        "file": "crop_anchor.png",
                        "sha256": sha_anchor
                    },
                    "positive": {
                        "center": [128, 128],
                        "node_id": f"{arch}_node_{case_counter}",
                        "is_focused": False,
                        "file": "crop_positive.png",
                        "sha256": sha_pos
                    },
                    "negative": {
                        "center": [100, 100],
                        "node_id": f"{arch}_neg_{case_counter}",
                        "is_focused": False,
                        "file": "crop_negative.png",
                        "sha256": sha_neg
                    }
                }
                manifest_file.write_text(json.dumps(item_meta, indent=2, sort_keys=True) + "\n")

                all_cases.append({
                    "case_id": case_id,
                    "layout": arch,
                    "theme": theme,
                    "focus_bias": bias,
                    "interruption": "none",
                    "focused_node_id": f"{arch}_node_{case_counter}",
                    "crop_anchor_sha256": sha_anchor,
                    "crop_positive_sha256": sha_pos,
                    "crop_negative_sha256": sha_neg
                })
                case_counter += 1

    # Archetype and theme distributions
    arch_dist = {}
    theme_dist = {}
    bias_dist = {}
    for c in all_cases:
        a = c["layout"]
        t = c["theme"]
        b = c["focus_bias"]
        arch_dist[a] = arch_dist.get(a, 0) + 1
        theme_dist[t] = theme_dist.get(t, 0) + 1
        bias_dist[b] = bias_dist.get(b, 0) + 1

    bulk_manifest = {
        "dataset_name": "NUIAK-Multi-Theme-Crop-Triplets-20261012",
        "total_cases": len(all_cases),
        "archetypeDistribution": arch_dist,
        "themeDistribution": theme_dist,
        "biasDistribution": bias_dist,
        "cases": all_cases,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    bulk_path = root / "bulk_crop_triplets_manifest.json"
    bulk_path.write_text(json.dumps(bulk_manifest, indent=2, sort_keys=True) + "\n")
    return bulk_manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate multi-theme synthetic crop triplets.")
    parser.add_argument("output_dir", help="Output directory for generated dataset")
    parser.add_argument("--cases-per-theme", type=int, default=70, help="Cases per theme (default: 70)")
    args = parser.parse_args()

    manifest = generate_multi_theme_dataset(args.output_dir, args.cases_per_theme)
    print(f"Generated {manifest['total_cases']} cases across {len(manifest['themeDistribution'])} themes.")
