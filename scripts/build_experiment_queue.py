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
        }
    ]

    submitted = []
    for exp in experiments:
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
