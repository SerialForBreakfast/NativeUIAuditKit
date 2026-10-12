#!/usr/bin/env python3
"""Build and submit diverse test experiment specs to research queue (ASD-STE100)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import research_queue

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def create_spec(spec_id, task, hypothesis, decision_rule, config_data, configs_dir):
    configs_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = configs_dir / f"{spec_id}.json"
    cfg_path.write_text(json.dumps(config_data, indent=2, sort_keys=True) + "\n")
    cfg_hash = digest(cfg_path)
    cfg_rel = str(cfg_path.relative_to(ROOT))

    evaluator_path = ROOT / "scripts/benchmark_evaluator.py"
    evaluator_hash = digest(evaluator_path)
    evaluator_rel = "scripts/benchmark_evaluator.py"

    spec = {
        "version": "research-spec-v1",
        "id": spec_id,
        "task": task,
        "owner": "Maximum-mini-NUIAK",
        "hypothesis": hypothesis,
        "decisionRule": decision_rule,
        "kind": "screen",
        "authority": "diagnostic",
        "adapter": {
            "type": "python-callable",
            "steps": ["benchmark_evaluator.run"],
            "outputAttributes": ["benchmark_evaluator.OUTPUT_DIR"]
        },
        "inputs": [
            {"path": evaluator_rel, "sha256": evaluator_hash}
        ],
        "stage": [
            {
                "from": {"path": cfg_rel, "sha256": cfg_hash},
                "to": "config.json"
            }
        ],
        "limits": {
            "timeoutSeconds": 300,
            "maxOutputBytes": 10485760,
            "maxAttempts": 2
        }
    }
    return spec

def build_queue():
    configs_dir = ROOT / "reports/work/research-configs"
    specs_dir = ROOT / "reports/work/research-specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    experiments = [
        {
            "id": "exp-01-focus-contrast",
            "task": "OPP-01",
            "hypothesis": "Dark artwork backdrops lower focus ring contrast margin by more than 30%",
            "decision": "Flag contrast vulnerability if low-contrast accuracy drops below 85%",
            "config": {
                "job_id": "exp-01-focus-contrast",
                "theme": "dark_low_contrast",
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-02-dense-bleed",
            "task": "OPP-02",
            "hypothesis": "Abutting shelf cards cause bounding box drift exceeding 5% IoU",
            "decision": "Reject crop pairs if box overlap exceeds 5% bleed threshold",
            "config": {
                "job_id": "exp-02-dense-bleed",
                "theme": "dark_standard",
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-03-maze-traps",
            "task": "OPP-03",
            "hypothesis": "Stationary barrier traps in focus mazes reduce navigation policy accuracy",
            "decision": "Verify contrastive negative separation on absorbing barrier nodes",
            "config": {
                "job_id": "exp-03-maze-traps",
                "theme": "all",
                "target_archetype": "focus_maze"
            }
        },
        {
            "id": "exp-04-interruptions",
            "task": "OPP-04",
            "hypothesis": "APNs notification banners and 0.45 scrim sheets cause false element detections",
            "decision": "Enforce false positive rate below 0.005 under simulated interruptions",
            "config": {
                "job_id": "exp-04-interruptions",
                "theme": "all",
                "target_archetype": "action_dialog"
            }
        },
        {
            "id": "exp-05-truncation-ellipsis",
            "task": "OPP-05",
            "hypothesis": "Trailing ellipsis truncation degrades optical text recognition confidence",
            "decision": "Require OCR token confidence above 0.85 on truncated settings titles",
            "config": {
                "job_id": "exp-05-truncation-ellipsis",
                "theme": "dark_standard",
                "target_archetype": "settings_list"
            }
        },
        {
            "id": "exp-06-hard-negative-spatial",
            "task": "EXP-01",
            "hypothesis": "Negative crops shifted by only 10-20px maintain embedding separation > 0.85 from 1.13x focused positive cards",
            "decision": "Require accuracy >= 0.85 on spatially close negative crops",
            "config": {
                "job_id": "exp-06-hard-negative-spatial",
                "dimension": "spatial_discrimination",
                "target_archetype": "shelf",
                "spatial_shift_px": 20
            }
        },
        {
            "id": "exp-07-dynamic-gradient-contrast",
            "task": "EXP-02",
            "hypothesis": "Dynamic multi-color gradient backdrops maintain focus ring detection accuracy above 0.85",
            "decision": "Verify contrast margin resilience without false positives on radial gradient backdrops",
            "config": {
                "job_id": "exp-07-dynamic-gradient-contrast",
                "dimension": "gradient_contrast",
                "target_archetype": "hero_detail",
                "theme": "dark_low_contrast"
            }
        },
        {
            "id": "exp-08-hcf-dual-mode",
            "task": "EXP-03",
            "hypothesis": "High Contrast Focus multi-layer accessibility border achieves > 0.90 accuracy alongside standard 3px white ring",
            "decision": "Verify detection across both standard and high contrast accessibility focus modes",
            "config": {
                "job_id": "exp-08-hcf-dual-mode",
                "dimension": "hcf_dual_mode",
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-09-aspect-ratio-elevation",
            "task": "EXP-04",
            "hypothesis": "Physical 1.13x scale expansion maintains detection invariance across 1:1, 2:3, and 16:9 aspect ratios",
            "decision": "Confirm detection accuracy >= 0.88 across all card aspect ratios under 1.13x scale",
            "config": {
                "job_id": "exp-09-aspect-ratio-elevation",
                "dimension": "aspect_ratio_elevation",
                "elevation_scale": 1.13,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-10-shadow-occlusion",
            "task": "EXP-06",
            "hypothesis": "Drop shadow occlusions overlapping adjacent neighbor card margins by 15-25px do not trigger false negatives",
            "decision": "Maintain recall > 0.85 under partial adjacent edge drop shadow occlusion",
            "config": {
                "job_id": "exp-10-shadow-occlusion",
                "dimension": "shadow_occlusion",
                "target_archetype": "shelf",
                "occlusion_px": 25
            }
        },
        {
            "id": "exp-11-high-luminance-bleed",
            "task": "EXP-07",
            "hypothesis": "Bright cards on high-luminance canvas with contrast below 1.2:1 maintain false negative rate < 0.15",
            "decision": "Enforce detection accuracy >= 0.85 on high-luminance dialog backgrounds",
            "config": {
                "job_id": "exp-11-high-luminance-bleed",
                "dimension": "luminance_bleed",
                "target_archetype": "action_dialog",
                "theme": "light_standard"
            }
        },
        {
            "id": "exp-12-text-undimming-attribution",
            "task": "EXP-05",
            "hypothesis": "Dynamic text label un-dimming relative to neighboring tiles provides positive focus feature attribution",
            "decision": "Verify text label un-dimming separation indicator > 0.85 in settings and list views",
            "config": {
                "job_id": "exp-12-text-undimming-attribution",
                "dimension": "text_undimming",
                "target_archetype": "settings_list"
            }
        },
        {
            "id": "exp-13-hardware-domain-transfer",
            "task": "EXP-08",
            "hypothesis": "Synthetic headless crops transfer zero-shot to physical Apple TV HD hardware within 0.88% scale delta",
            "decision": "Confirm zero-shot hardware transfer accuracy >= 0.90 without physical training leakage",
            "config": {
                "job_id": "exp-13-hardware-domain-transfer",
                "dimension": "hardware_transfer",
                "target_archetype": "all"
            }
        },
        {
            "id": "exp-14-resolution-scale-jitter",
            "task": "EXP-09",
            "hypothesis": "Multi-scale crop resolution across 128px, 256px, and 512px maintains scale jitter invariance",
            "decision": "Confirm resolution invariance accuracy >= 0.90 across multi-resolution crops",
            "config": {
                "job_id": "exp-14-resolution-scale-jitter",
                "dimension": "resolution_scale_jitter",
                "target_archetype": "top_nav_shelf"
            }
        },
        {
            "id": "exp-15-temporal-motion-settlement",
            "task": "EXP-10",
            "hypothesis": "Temporal motion blur interpolation from 1.00x to 1.13x exhibits a distinct settlement threshold",
            "decision": "Verify model discriminates settled focus from in-flight remote transitions",
            "config": {
                "job_id": "exp-15-temporal-motion-settlement",
                "dimension": "temporal_settlement",
                "target_archetype": "focus_maze"
            }
        },
        {
            "id": "exp-16-maze-absorbing-barrier",
            "task": "EXP-11",
            "hypothesis": "Absorbing barrier nodes in deep maze layouts do not cause negative-to-positive focus leakage",
            "decision": "Confirm maze barrier separation accuracy >= 0.88 without path ambiguity",
            "config": {
                "job_id": "exp-16-maze-absorbing-barrier",
                "dimension": "maze_absorbing_barrier",
                "target_archetype": "focus_maze"
            }
        },
        {
            "id": "exp-17-modal-scrim-transparency",
            "task": "EXP-12",
            "hypothesis": "Modal sheet scrim alpha values between 0.20 and 0.60 correctly suppress background focus candidates",
            "decision": "Enforce zero false positive detections on dimmed background elements under modal sheet",
            "config": {
                "job_id": "exp-17-modal-scrim-transparency",
                "dimension": "modal_scrim_transparency",
                "target_archetype": "action_dialog",
                "overlay": "scrim_modal_sheet"
            }
        },
        {
            "id": "exp-18-dense-card-abutting",
            "task": "EXP-13",
            "hypothesis": "Abutting shelf tiles with 0 px margin maintain IoU bleed < 0.05 under 1.13x elevation",
            "decision": "Confirm abutting tile bounding box IoU bleed stays below 5% threshold",
            "config": {
                "job_id": "exp-18-dense-card-abutting",
                "dimension": "dense_card_abutting",
                "target_archetype": "shelf",
                "density": "dense_abutting"
            }
        },
        {
            "id": "exp-19-extreme-aspect-ratios",
            "task": "EXP-14",
            "hypothesis": "Extreme aspect ratios (21:9 panoramic and 9:16 vertical) maintain focus detection accuracy above 0.88",
            "decision": "Require focus detection accuracy >= 0.88 across extreme aspect ratios",
            "config": {
                "job_id": "exp-19-extreme-aspect-ratios",
                "dimension": "extreme_aspect_ratios",
                "target_archetype": "hero_detail"
            }
        },
        {
            "id": "exp-20-focus-bias-spatial-corners",
            "task": "EXP-15",
            "hypothesis": "Spatial focus bias targeted at canvas boundary corners maintains detection recall >= 0.90",
            "decision": "Confirm detection recall >= 0.90 on extreme corner focus positions",
            "config": {
                "job_id": "exp-20-focus-bias-spatial-corners",
                "dimension": "focus_bias_corners",
                "target_archetype": "top_nav_shelf",
                "spatial_bias": "top_left"
            }
        },
        {
            "id": "exp-21-shift-02px",
            "task": "EXP-16",
            "hypothesis": "A 2 px shift registers as the same active card body rather than a negative",
            "decision": "Accuracy >= 0.95 on micro positive shifts",
            "config": {
                "job_id": "exp-21-shift-02px",
                "dimension": "spatial_shift_micro",
                "shift_px": 2,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-22-shift-05px",
            "task": "EXP-17",
            "hypothesis": "Model separates card edge border from immediate inner content under 5 px shift",
            "decision": "Accuracy >= 0.93 on edge margin retention",
            "config": {
                "job_id": "exp-22-shift-05px",
                "dimension": "spatial_shift_micro",
                "shift_px": 5,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-23-shift-10px",
            "task": "EXP-18",
            "hypothesis": "A 10 px displacement transitions to a hard negative candidate",
            "decision": "Separation accuracy >= 0.90",
            "config": {
                "job_id": "exp-23-shift-10px",
                "dimension": "spatial_shift_micro",
                "shift_px": 10,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-24-shift-15px",
            "task": "EXP-19",
            "hypothesis": "Model isolates abutting card margins without boundary ambiguity at 15 px shift",
            "decision": "Separation accuracy >= 0.90",
            "config": {
                "job_id": "exp-24-shift-15px",
                "dimension": "spatial_shift_micro",
                "shift_px": 15,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-25-shift-20px",
            "task": "EXP-20",
            "hypothesis": "A 20 px adjacent shift provides complete negative isolation",
            "decision": "Separation accuracy >= 0.92",
            "config": {
                "job_id": "exp-25-shift-20px",
                "dimension": "spatial_shift_micro",
                "shift_px": 20,
                "target_archetype": "top_nav_shelf"
            }
        },
        {
            "id": "exp-26-shift-25px",
            "task": "EXP-21",
            "hypothesis": "A full 25 px row-step displacement eliminates all focus leakage",
            "decision": "Separation accuracy >= 0.94",
            "config": {
                "job_id": "exp-26-shift-25px",
                "dimension": "spatial_shift_micro",
                "shift_px": 25,
                "target_archetype": "settings_list"
            }
        },
        {
            "id": "exp-27-gamma-07-dark",
            "task": "EXP-22",
            "hypothesis": "Underexposed gamma (0.7) retains 3 px white stroke visibility",
            "decision": "Accuracy >= 0.88 on low luminance",
            "config": {
                "job_id": "exp-27-gamma-07-dark",
                "dimension": "photometric_gamma",
                "gamma": 0.7,
                "theme": "dark_standard"
            }
        },
        {
            "id": "exp-28-gamma-09-shadow",
            "task": "EXP-23",
            "hypothesis": "Deep shadow crushing obscures the subtle focus halo",
            "decision": "Accuracy >= 0.88 on crushed shadows",
            "config": {
                "job_id": "exp-28-gamma-09-shadow",
                "dimension": "photometric_gamma",
                "gamma": 0.9,
                "theme": "dark_low_contrast"
            }
        },
        {
            "id": "exp-29-gamma-11-sdr",
            "task": "EXP-24",
            "hypothesis": "Standard SDR brightness curve matches baseline physical accuracy",
            "decision": "Accuracy >= 0.94 on nominal curve",
            "config": {
                "job_id": "exp-29-gamma-11-sdr",
                "dimension": "photometric_gamma",
                "gamma": 1.1,
                "theme": "light_standard"
            }
        },
        {
            "id": "exp-30-gamma-13-bright",
            "task": "EXP-25",
            "hypothesis": "Overexposed gamma (1.3) washes out light card focus rings",
            "decision": "Accuracy >= 0.87 on high luminance",
            "config": {
                "job_id": "exp-30-gamma-13-bright",
                "dimension": "photometric_gamma",
                "gamma": 1.3,
                "theme": "light_standard"
            }
        },
        {
            "id": "exp-31-vibrant-radial-art",
            "task": "EXP-26",
            "hypothesis": "Saturated poster gradients do not trigger false positive focus rings",
            "decision": "False positive rate < 0.01",
            "config": {
                "job_id": "exp-31-vibrant-radial-art",
                "dimension": "gradient_contrast",
                "target_archetype": "hero_detail",
                "theme": "dark_standard"
            }
        },
        {
            "id": "exp-32-extreme-low-contrast",
            "task": "EXP-27",
            "hypothesis": "Model detects focus when ring-to-backdrop contrast is < 1.15:1",
            "decision": "Accuracy >= 0.85 on subtle contrast",
            "config": {
                "job_id": "exp-32-extreme-low-contrast",
                "dimension": "gradient_contrast",
                "target_archetype": "shelf",
                "theme": "dark_low_contrast"
            }
        },
        {
            "id": "exp-33-scrim-alpha-15",
            "task": "EXP-28",
            "hypothesis": "A faint 0.15 scrim allows valid focus detection on foreground sheet",
            "decision": "Accuracy >= 0.92 on modal target",
            "config": {
                "job_id": "exp-33-scrim-alpha-15",
                "dimension": "scrim_alpha_sweep",
                "scrim_alpha": 0.15,
                "target_archetype": "action_dialog"
            }
        },
        {
            "id": "exp-34-scrim-alpha-30",
            "task": "EXP-29",
            "hypothesis": "A 0.30 scrim suppresses background focus candidates by 50%",
            "decision": "Background candidate suppression > 50%",
            "config": {
                "job_id": "exp-34-scrim-alpha-30",
                "dimension": "scrim_alpha_sweep",
                "scrim_alpha": 0.30,
                "target_archetype": "action_dialog"
            }
        },
        {
            "id": "exp-35-scrim-alpha-50",
            "task": "EXP-30",
            "hypothesis": "A 0.50 standard sheet eliminates background false focus",
            "decision": "Background false positive rate < 0.005",
            "config": {
                "job_id": "exp-35-scrim-alpha-50",
                "dimension": "scrim_alpha_sweep",
                "scrim_alpha": 0.50,
                "target_archetype": "action_dialog"
            }
        },
        {
            "id": "exp-36-scrim-alpha-70",
            "task": "EXP-31",
            "hypothesis": "A heavy 0.70 scrim preserves foreground modal button detection",
            "decision": "Accuracy >= 0.95 on foreground dialog",
            "config": {
                "job_id": "exp-36-scrim-alpha-70",
                "dimension": "scrim_alpha_sweep",
                "scrim_alpha": 0.70,
                "target_archetype": "action_dialog"
            }
        },
        {
            "id": "exp-37-dense-abutting-shadow",
            "task": "EXP-32",
            "hypothesis": "Overlapping 1.13x card drop shadows do not trigger false negatives",
            "decision": "Recall >= 0.88 under 20 px overlap",
            "config": {
                "job_id": "exp-37-dense-abutting-shadow",
                "dimension": "shadow_occlusion",
                "target_archetype": "shelf",
                "density": "dense_abutting",
                "occlusion_px": 20
            }
        },
        {
            "id": "exp-38-hud-toast-banner",
            "task": "EXP-33",
            "hypothesis": "Transient top HUD banner does not degrade shelf focus detection",
            "decision": "Accuracy >= 0.93 during HUD overlay",
            "config": {
                "job_id": "exp-38-hud-toast-banner",
                "dimension": "modal_scrim_transparency",
                "target_archetype": "shelf",
                "overlay": "hud_toast"
            }
        },
        {
            "id": "exp-39-motion-blur-05",
            "task": "EXP-34",
            "hypothesis": "Mild camera jitter (sigma 0.5) preserves focus classification",
            "decision": "Accuracy >= 0.92 on settled focus",
            "config": {
                "job_id": "exp-39-motion-blur-05",
                "dimension": "motion_blur_sigma",
                "sigma": 0.5,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-40-motion-blur-15",
            "task": "EXP-35",
            "hypothesis": "Rapid swipe blur (sigma 1.5) suppresses premature focus assertion",
            "decision": "Transition suppression >= 0.85",
            "config": {
                "job_id": "exp-40-motion-blur-15",
                "dimension": "motion_blur_sigma",
                "sigma": 1.5,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-41-motion-blur-30",
            "task": "EXP-36",
            "hypothesis": "Heavy motion blur (sigma 3.0) yields zero false positive focus locks",
            "decision": "False positive rate < 0.002",
            "config": {
                "job_id": "exp-41-motion-blur-30",
                "dimension": "motion_blur_sigma",
                "sigma": 3.0,
                "target_archetype": "grid",
                "min_threshold": 0.80
            }
        },
        {
            "id": "exp-42-scale-jitter-108",
            "task": "EXP-37",
            "hypothesis": "Model detects subtle third-party elevation of 1.08x",
            "decision": "Accuracy >= 0.88 on subtle scale",
            "config": {
                "job_id": "exp-42-scale-jitter-108",
                "dimension": "scale_jitter_sweep",
                "elevation_scale": 1.08,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-43-scale-jitter-113",
            "task": "EXP-38",
            "hypothesis": "Physical ground truth elevation of 1.13x maintains peak accuracy",
            "decision": "Accuracy >= 0.95 on calibrated scale",
            "config": {
                "job_id": "exp-43-scale-jitter-113",
                "dimension": "scale_jitter_sweep",
                "elevation_scale": 1.13,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-44-scale-jitter-118",
            "task": "EXP-39",
            "hypothesis": "Exaggerated 1.18x elevation maintains card aspect ratio invariance",
            "decision": "Accuracy >= 0.92 on large scale",
            "config": {
                "job_id": "exp-44-scale-jitter-118",
                "dimension": "scale_jitter_sweep",
                "elevation_scale": 1.18,
                "target_archetype": "hero_detail"
            }
        },
        {
            "id": "exp-45-margin-02",
            "task": "EXP-40",
            "hypothesis": "Small margin (0.2) tests embedding separation baseline",
            "decision": "Inter-class separation > 0.40",
            "config": {
                "job_id": "exp-45-margin-02",
                "dimension": "contrastive_margin",
                "margin": 0.2,
                "target_archetype": "grid",
                "min_threshold": 0.85
            }
        },
        {
            "id": "exp-46-margin-05",
            "task": "EXP-41",
            "hypothesis": "Standard margin (0.5) provides balanced separation",
            "decision": "Accuracy >= 0.92 across triplets",
            "config": {
                "job_id": "exp-46-margin-05",
                "dimension": "contrastive_margin",
                "margin": 0.5,
                "target_archetype": "grid"
            }
        },
        {
            "id": "exp-47-margin-08",
            "task": "EXP-42",
            "hypothesis": "Wide margin (0.8) forces tighter clusters for subtle rings",
            "decision": "Embedding separation > 0.75",
            "config": {
                "job_id": "exp-47-margin-08",
                "dimension": "contrastive_margin",
                "margin": 0.8,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-48-margin-10",
            "task": "EXP-43",
            "hypothesis": "Strict margin (1.0) maintains gradient stability",
            "decision": "Gradient stability index >= 0.88",
            "config": {
                "job_id": "exp-48-margin-10",
                "dimension": "contrastive_margin",
                "margin": 1.0,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-49-temp-007",
            "task": "EXP-44",
            "hypothesis": "Standard InfoNCE temperature (0.07) optimizes hard negative penalty",
            "decision": "Hard negative accuracy >= 0.93",
            "config": {
                "job_id": "exp-49-temp-007",
                "dimension": "temperature_scaling",
                "temperature": 0.07,
                "target_archetype": "shelf"
            }
        },
        {
            "id": "exp-50-temp-015",
            "task": "EXP-45",
            "hypothesis": "Higher temperature (0.15) maintains focus ring boundary resolution",
            "decision": "Accuracy >= 0.89 on boundary cases",
            "config": {
                "job_id": "exp-50-temp-015",
                "dimension": "temperature_scaling",
                "temperature": 0.15,
                "target_archetype": "top_nav_shelf"
            }
        }
    ]

    submitted = []
    queue_jobs_dir = research_queue.QUEUE / "jobs"
    for exp in experiments:
        job_target = queue_jobs_dir / exp["id"] / "spec.json"
        if job_target.exists():
            submitted.append({"id": exp["id"], "task": exp["task"], "status": "already_submitted"})
            continue

        spec = create_spec(
            exp["id"], exp["task"], exp["hypothesis"], exp["decision"], exp["config"], configs_dir
        )
        spec_path = specs_dir / f"{exp['id']}.json"
        spec_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        
        status = research_queue.submit(spec_path)
        submitted.append({"id": exp["id"], "task": exp["task"], "status": status})

    return submitted

if __name__ == "__main__":
    results = build_queue()
    print(json.dumps(results, indent=2))
