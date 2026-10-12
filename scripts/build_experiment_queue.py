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
