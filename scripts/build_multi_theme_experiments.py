#!/usr/bin/env python3
"""Register multi-theme research queue experiments on local corpus (ASD-STE100)."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import research_queue

MANIFEST_PATH = "/Volumes/training-drive/data/NUIAK/live/crop-triplets-multi-theme-20261012/focus_dataset_manifest.json"

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
        "owner": "NUIAK-Runner",
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

def register_multi_theme_experiments():
    configs_dir = ROOT / "reports/work/research-configs"
    specs_dir = ROOT / "reports/work/research-specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    experiments = [
        # Batch 9: Multi-Theme Archetype Baselines (exp-51 to exp-57)
        {
            "id": "exp-51-mt-shelf",
            "task": "EXP-MT-01",
            "hypothesis": "Multi-theme shelf poster cards maintain >90% accuracy with 1.13x elevation",
            "decision": "Verify shelf accuracy exceeds 0.90 across multi-theme corpus",
            "config": {
                "job_id": "exp-51-mt-shelf",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "shelf",
                "theme": "all"
            }
        },
        {
            "id": "exp-52-mt-grid",
            "task": "EXP-MT-02",
            "hypothesis": "Multi-theme 16:9 grid cards maintain >92% accuracy across themes",
            "decision": "Verify grid accuracy exceeds 0.92 across multi-theme corpus",
            "config": {
                "job_id": "exp-52-mt-grid",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "grid",
                "theme": "all"
            }
        },
        {
            "id": "exp-53-mt-hero",
            "task": "EXP-MT-03",
            "hypothesis": "Hero detail pill buttons retain focus ring integrity across themes",
            "decision": "Verify pill button accuracy exceeds 0.90 across multi-theme corpus",
            "config": {
                "job_id": "exp-53-mt-hero",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "hero_detail",
                "theme": "all"
            }
        },
        {
            "id": "exp-54-mt-top-nav",
            "task": "EXP-MT-04",
            "hypothesis": "Segmented tab bar items maintain high contrast across themes",
            "decision": "Verify tab item accuracy exceeds 0.92 across multi-theme corpus",
            "config": {
                "job_id": "exp-54-mt-top-nav",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "top_nav_shelf",
                "theme": "all"
            }
        },
        {
            "id": "exp-55-mt-settings",
            "task": "EXP-MT-05",
            "hypothesis": "Settings list row cells preserve separation across themes",
            "decision": "Verify settings row accuracy exceeds 0.90 across multi-theme corpus",
            "config": {
                "job_id": "exp-55-mt-settings",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "settings_list",
                "theme": "all"
            }
        },
        {
            "id": "exp-56-mt-action-dialog",
            "task": "EXP-MT-06",
            "hypothesis": "Modal action dialog buttons maintain focus prominence across themes",
            "decision": "Verify action dialog accuracy exceeds 0.88 across multi-theme corpus",
            "config": {
                "job_id": "exp-56-mt-action-dialog",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "action_dialog",
                "theme": "all"
            }
        },
        {
            "id": "exp-57-mt-focus-maze",
            "task": "EXP-MT-07",
            "hypothesis": "Tightly abutting maze cells exhibit contrast degradation in low-contrast themes",
            "decision": "Flag maze degradation if accuracy falls below 0.85 across multi-theme corpus",
            "config": {
                "job_id": "exp-57-mt-focus-maze",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "focus_maze",
                "theme": "all"
            }
        },
        # Batch 10: Cross-Theme Divergence Comparison (exp-58 to exp-60)
        {
            "id": "exp-58-theme-dark-standard",
            "task": "EXP-MT-08",
            "hypothesis": "Standard dark tvOS theme provides baseline contrast margin above 0.93",
            "decision": "Verify dark standard baseline accuracy exceeds 0.93 across archetypes",
            "config": {
                "job_id": "exp-58-theme-dark-standard",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "all",
                "theme": "dark_standard"
            }
        },
        {
            "id": "exp-59-theme-light-standard",
            "task": "EXP-MT-09",
            "hypothesis": "Light tvOS theme achieves parity with dark theme (>0.93) using dark focus stroke",
            "decision": "Verify light standard accuracy matches dark baseline within 1 percentage point",
            "config": {
                "job_id": "exp-59-theme-light-standard",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "all",
                "theme": "light_standard"
            }
        },
        {
            "id": "exp-60-theme-dark-low-contrast",
            "task": "EXP-MT-10",
            "hypothesis": "Low-contrast charcoal theme drops contrast margin by 8 percentage points",
            "decision": "Flag theme vulnerability if low-contrast accuracy falls below 0.88",
            "config": {
                "job_id": "exp-60-theme-dark-low-contrast",
                "manifest_path": MANIFEST_PATH,
                "target_archetype": "all",
                "theme": "dark_low_contrast"
            }
        },
        # Batch 11: Multi-Theme Stress & Contrastive Regularization (exp-61 to exp-65)
        {
            "id": "exp-61-mt-spatial-shift-10px",
            "task": "EXP-MT-11",
            "hypothesis": "10 px micro-shift creates acute edge ambiguity across multi-theme corpus",
            "decision": "Verify shift inflection zone accuracy is between 0.90 and 0.92",
            "config": {
                "job_id": "exp-61-mt-spatial-shift-10px",
                "manifest_path": MANIFEST_PATH,
                "dimension": "spatial_shift_micro",
                "shift_px": 10,
                "target_archetype": "all",
                "theme": "all"
            }
        },
        {
            "id": "exp-62-mt-photometric-gamma-130",
            "task": "EXP-MT-12",
            "hypothesis": "High-luminance gamma 1.30 wash-out degrades light theme contrast more than dark theme",
            "decision": "Verify gamma wash-out degrades accuracy below 0.90",
            "config": {
                "job_id": "exp-62-mt-photometric-gamma-130",
                "manifest_path": MANIFEST_PATH,
                "dimension": "photometric_gamma",
                "gamma": 1.30,
                "target_archetype": "all",
                "theme": "all"
            }
        },
        {
            "id": "exp-63-mt-scrim-modal-alpha",
            "task": "EXP-MT-13",
            "hypothesis": "Semi-transparent scrim alpha 0.45 improves modal button separation across themes",
            "decision": "Verify scrim alpha 0.45 achieves >0.94 accuracy across themes",
            "config": {
                "job_id": "exp-63-mt-scrim-modal-alpha",
                "manifest_path": MANIFEST_PATH,
                "dimension": "scrim_alpha_sweep",
                "scrim_alpha": 0.45,
                "target_archetype": "all",
                "theme": "all"
            }
        },
        {
            "id": "exp-64-mt-elevation-113",
            "task": "EXP-MT-14",
            "hypothesis": "1.13x elevation expansion is optimal across all 3 visual themes",
            "decision": "Verify 1.13x expansion achieves peak accuracy >0.95 across themes",
            "config": {
                "job_id": "exp-64-mt-elevation-113",
                "manifest_path": MANIFEST_PATH,
                "dimension": "scale_jitter_sweep",
                "elevation_scale": 1.13,
                "target_archetype": "all",
                "theme": "all"
            }
        },
        {
            "id": "exp-65-mt-infonce-temp007",
            "task": "EXP-MT-15",
            "hypothesis": "InfoNCE temperature 0.07 preserves sharp negative separation across low-contrast themes",
            "decision": "Verify temperature 0.07 achieves >0.94 accuracy across themes",
            "config": {
                "job_id": "exp-65-mt-infonce-temp007",
                "manifest_path": MANIFEST_PATH,
                "dimension": "temperature_scaling",
                "temperature": 0.07,
                "target_archetype": "all",
                "theme": "all"
            }
        }
    ]

    submitted = []
    for exp in experiments:
        spec = create_spec(exp["id"], exp["task"], exp["hypothesis"], exp["decision"], exp["config"], configs_dir)
        spec_file = specs_dir / f"{exp['id']}.json"
        spec_file.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
        try:
            research_queue.submit(spec_file)
            submitted.append(exp["id"])
            print(f"Submitted {exp['id']}")
        except ValueError as e:
            if "job_exists" in str(e):
                print(f"Already submitted: {exp['id']}")
            else:
                raise
    return submitted

if __name__ == "__main__":
    submitted = register_multi_theme_experiments()
    print(f"Registered {len(submitted)} multi-theme experiments.")
