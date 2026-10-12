#!/usr/bin/env python3
"""Build and register large-scale backlog of major research experiments (ASD-STE100)."""
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

def register_large_scale_backlog():
    configs_dir = ROOT / "reports/work/research-configs"
    specs_dir = ROOT / "reports/work/research-specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    experiments = [
        # Batch 12: Dual-Scale Edge Crop Fusion (exp-66 to exp-70)
        {
            "id": "exp-66-big-dualscale-shelf",
            "task": "EXP-BIG-01",
            "hypothesis": "Dual-scale edge fusion (128px high-res + 256px context) increases shelf accuracy above 0.96",
            "decision": "Adopt dual-scale fusion if shelf accuracy improves by more than 4 percentage points",
            "config": {"job_id": "exp-66-big-dualscale-shelf", "manifest_path": MANIFEST_PATH, "dimension": "dual_scale_edge_fusion", "edge_window_scale": 2.0, "target_archetype": "shelf", "theme": "all"}
        },
        {
            "id": "exp-67-big-dualscale-maze",
            "task": "EXP-BIG-02",
            "hypothesis": "Dual-scale edge fusion resolves abutting cell ambiguity in dense focus mazes",
            "decision": "Verify focus maze accuracy exceeds 0.95 with edge window fusion",
            "config": {"job_id": "exp-67-big-dualscale-maze", "manifest_path": MANIFEST_PATH, "dimension": "dual_scale_edge_fusion", "edge_window_scale": 2.0, "target_archetype": "focus_maze", "theme": "all"}
        },
        {
            "id": "exp-68-big-dualscale-lowcontrast",
            "task": "EXP-BIG-03",
            "hypothesis": "Dual-scale edge fusion recovers low-contrast theme accuracy from 0.85 to above 0.94",
            "decision": "Flag low-contrast resolution if dual-scale accuracy delta exceeds +8 percentage points",
            "config": {"job_id": "exp-68-big-dualscale-lowcontrast", "manifest_path": MANIFEST_PATH, "dimension": "dual_scale_edge_fusion", "edge_window_scale": 2.0, "target_archetype": "all", "theme": "dark_low_contrast"}
        },
        {
            "id": "exp-69-big-dualscale-window15",
            "task": "EXP-BIG-04",
            "hypothesis": "Edge window scale 1.5x balances local stroke detail and computational cost",
            "decision": "Verify 1.5x window scale achieves >0.95 accuracy",
            "config": {"job_id": "exp-69-big-dualscale-window15", "manifest_path": MANIFEST_PATH, "dimension": "dual_scale_edge_fusion", "edge_window_scale": 1.5, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-70-big-dualscale-window25",
            "task": "EXP-BIG-05",
            "hypothesis": "Edge window scale 2.5x maximizes stroke gradient separation across high-DPI displays",
            "decision": "Verify 2.5x window scale achieves >0.96 accuracy",
            "config": {"job_id": "exp-70-big-dualscale-window25", "manifest_path": MANIFEST_PATH, "dimension": "dual_scale_edge_fusion", "edge_window_scale": 2.5, "target_archetype": "all", "theme": "all"}
        },

        # Batch 13: Contrastive Loss Formulation & SupCon Scaling (exp-71 to exp-75)
        {
            "id": "exp-71-big-supcon-all",
            "task": "EXP-BIG-06",
            "hypothesis": "Supervised Contrastive (SupCon) multi-positive loss outperforms pairwise triplet loss",
            "decision": "Adopt SupCon loss if overall multi-theme accuracy exceeds 0.955",
            "config": {"job_id": "exp-71-big-supcon-all", "manifest_path": MANIFEST_PATH, "dimension": "supcon_contrastive_loss", "objective": "supcon", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-72-big-supcon-infonce-cmp",
            "task": "EXP-BIG-07",
            "hypothesis": "SupCon achieves tighter inter-cluster separation than InfoNCE on low-contrast themes",
            "decision": "Verify SupCon maintains >0.95 accuracy on dark_low_contrast theme",
            "config": {"job_id": "exp-72-big-supcon-infonce-cmp", "manifest_path": MANIFEST_PATH, "dimension": "supcon_contrastive_loss", "objective": "supcon", "target_archetype": "all", "theme": "dark_low_contrast"}
        },
        {
            "id": "exp-73-big-supcon-margin05",
            "task": "EXP-BIG-08",
            "hypothesis": "SupCon margin 0.5 optimizes boundary separation across cards",
            "decision": "Verify SupCon margin 0.5 achieves peak accuracy",
            "config": {"job_id": "exp-73-big-supcon-margin05", "manifest_path": MANIFEST_PATH, "dimension": "supcon_contrastive_loss", "objective": "supcon", "margin": 0.5, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-74-big-supcon-margin08",
            "task": "EXP-BIG-09",
            "hypothesis": "SupCon hard margin 0.8 enforces strict separation on abutting shelf posters",
            "decision": "Verify margin 0.8 maintains convergence stability",
            "config": {"job_id": "exp-74-big-supcon-margin08", "manifest_path": MANIFEST_PATH, "dimension": "supcon_contrastive_loss", "objective": "supcon", "margin": 0.8, "target_archetype": "shelf", "theme": "all"}
        },
        {
            "id": "exp-75-big-supcon-hard-negatives",
            "task": "EXP-BIG-10",
            "hypothesis": "Hard negative mining on adjacent cards eliminates false focus shifts",
            "decision": "Verify hard negative mining prevents adjacent card misclassification",
            "config": {"job_id": "exp-75-big-supcon-hard-negatives", "manifest_path": MANIFEST_PATH, "dimension": "supcon_contrastive_loss", "objective": "supcon", "mining": "hardest", "target_archetype": "grid", "theme": "all"}
        },

        # Batch 14: 3D Perspective Elevation & Parallax Pitch (exp-76 to exp-80)
        {
            "id": "exp-76-big-perspective-pitch-2deg",
            "task": "EXP-BIG-11",
            "hypothesis": "Subtle 2-degree perspective pitch elevation matches native tvOS resting tilt",
            "decision": "Verify 2-degree pitch maintains >0.94 accuracy",
            "config": {"job_id": "exp-76-big-perspective-pitch-2deg", "manifest_path": MANIFEST_PATH, "dimension": "perspective_pitch_elevation", "pitch_deg": 2.0, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-77-big-perspective-pitch-4deg",
            "task": "EXP-BIG-12",
            "hypothesis": "4-degree perspective pitch elevation produces peak 3D focus pop-out separation",
            "decision": "Verify 4-degree pitch achieves >0.95 accuracy",
            "config": {"job_id": "exp-77-big-perspective-pitch-4deg", "manifest_path": MANIFEST_PATH, "dimension": "perspective_pitch_elevation", "pitch_deg": 4.0, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-78-big-perspective-pitch-6deg",
            "task": "EXP-BIG-13",
            "hypothesis": "6-degree perspective pitch begins to introduce trapezoidal boundary distortion",
            "decision": "Measure accuracy degradation threshold under high tilt",
            "config": {"job_id": "exp-78-big-perspective-pitch-6deg", "manifest_path": MANIFEST_PATH, "dimension": "perspective_pitch_elevation", "pitch_deg": 6.0, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-79-big-perspective-pitch-8deg",
            "task": "EXP-BIG-14",
            "hypothesis": "8-degree perspective pitch degrades accuracy below 0.90 due to projection distortion",
            "decision": "Confirm upper pitch limit for synthetic parallax generation",
            "config": {"job_id": "exp-79-big-perspective-pitch-8deg", "manifest_path": MANIFEST_PATH, "dimension": "perspective_pitch_elevation", "pitch_deg": 8.0, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-80-big-perspective-multi-theme",
            "task": "EXP-BIG-15",
            "hypothesis": "4-degree perspective tilt maintains separation across dark and light themes",
            "decision": "Verify perspective tilt stability across all 3 visual themes",
            "config": {"job_id": "exp-80-big-perspective-multi-theme", "manifest_path": MANIFEST_PATH, "dimension": "perspective_pitch_elevation", "pitch_deg": 4.0, "target_archetype": "all", "theme": "all"}
        },

        # Batch 15: Backbone Architecture & Attention Pooling (exp-81 to exp-85)
        {
            "id": "exp-81-big-backbone-yolo11n",
            "task": "EXP-BIG-16",
            "hypothesis": "YOLO11n convolutional backbone provides proven baseline on Apple Neural Engine",
            "decision": "Confirm YOLO11n baseline accuracy at 0.952",
            "config": {"job_id": "exp-81-big-backbone-yolo11n", "manifest_path": MANIFEST_PATH, "dimension": "backbone_architecture_sweep", "backbone": "yolo11n", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-82-big-backbone-mobilenetv4",
            "task": "EXP-BIG-17",
            "hypothesis": "MobileNetV4-ConvSmall offers sub-1ms inference with acceptable accuracy trade-off",
            "decision": "Evaluate MobileNetV4 efficiency trade-off vs YOLO11n",
            "config": {"job_id": "exp-82-big-backbone-mobilenetv4", "manifest_path": MANIFEST_PATH, "dimension": "backbone_architecture_sweep", "backbone": "mobilenetv4", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-83-big-backbone-vit-tiny",
            "task": "EXP-BIG-18",
            "hypothesis": "ViT-tiny with Multi-Head Attention Pooling captures non-local focus ring halos",
            "decision": "Promote ViT backbone if accuracy exceeds 0.960",
            "config": {"job_id": "exp-83-big-backbone-vit-tiny", "manifest_path": MANIFEST_PATH, "dimension": "backbone_architecture_sweep", "backbone": "vit_tiny_attention", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-84-big-backbone-vit-lowcontrast",
            "task": "EXP-BIG-19",
            "hypothesis": "ViT-tiny attention pooling significantly outperforms CNNs on low-contrast themes",
            "decision": "Verify ViT attention maintains >0.95 accuracy on dark_low_contrast",
            "config": {"job_id": "exp-84-big-backbone-vit-lowcontrast", "manifest_path": MANIFEST_PATH, "dimension": "backbone_architecture_sweep", "backbone": "vit_tiny_attention", "target_archetype": "all", "theme": "dark_low_contrast"}
        },
        {
            "id": "exp-85-big-backbone-vit-dense",
            "task": "EXP-BIG-20",
            "hypothesis": "ViT-tiny attention pooling isolates dense focus maze cells without boundary bleed",
            "decision": "Verify ViT accuracy exceeds 0.95 on focus_maze archetype",
            "config": {"job_id": "exp-85-big-backbone-vit-dense", "manifest_path": MANIFEST_PATH, "dimension": "backbone_architecture_sweep", "backbone": "vit_tiny_attention", "target_archetype": "focus_maze", "theme": "all"}
        },

        # Batch 16: Multi-Task Auxiliary Heads (exp-86 to exp-90)
        {
            "id": "exp-86-big-multitask-dualhead",
            "task": "EXP-BIG-21",
            "hypothesis": "Joint prediction of focus state and bounding box regularizes representation",
            "decision": "Verify dual-head multitask model achieves >0.95 accuracy",
            "config": {"job_id": "exp-86-big-multitask-dualhead", "manifest_path": MANIFEST_PATH, "dimension": "multitask_auxiliary_head", "aux_heads": ["focus_ring", "bounding_box"], "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-87-big-multitask-trihead",
            "task": "EXP-BIG-22",
            "hypothesis": "Adding theme classification as 3rd auxiliary head enhances contrast awareness",
            "decision": "Verify tri-head multitask model achieves >0.955 accuracy",
            "config": {"job_id": "exp-87-big-multitask-trihead", "manifest_path": MANIFEST_PATH, "dimension": "multitask_auxiliary_head", "aux_heads": ["focus_ring", "bounding_box", "theme_classifier"], "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-88-big-multitask-quadhead",
            "task": "EXP-BIG-23",
            "hypothesis": "Adding archetype classifier as 4th head produces universal tvOS feature representations",
            "decision": "Verify quad-head model maintains convergence across all 7 archetypes",
            "config": {"job_id": "exp-88-big-multitask-quadhead", "manifest_path": MANIFEST_PATH, "dimension": "multitask_auxiliary_head", "aux_heads": ["focus_ring", "bounding_box", "theme_classifier", "archetype_classifier"], "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-89-big-multitask-lowcontrast",
            "task": "EXP-BIG-24",
            "hypothesis": "Multi-task theme awareness head protects against low-contrast performance drops",
            "decision": "Verify tri-head model improves dark_low_contrast accuracy above 0.93",
            "config": {"job_id": "exp-89-big-multitask-lowcontrast", "manifest_path": MANIFEST_PATH, "dimension": "multitask_auxiliary_head", "aux_heads": ["focus_ring", "bounding_box", "theme_classifier"], "target_archetype": "all", "theme": "dark_low_contrast"}
        },
        {
            "id": "exp-90-big-multitask-regularization",
            "task": "EXP-BIG-25",
            "hypothesis": "Balanced auxiliary loss weighting (1.0 focus, 0.25 bbox, 0.10 theme) optimizes overall accuracy",
            "decision": "Confirm optimal multi-task loss weighting",
            "config": {"job_id": "exp-90-big-multitask-regularization", "manifest_path": MANIFEST_PATH, "dimension": "multitask_auxiliary_head", "aux_heads": ["focus_ring", "bounding_box", "theme_classifier"], "weights": [1.0, 0.25, 0.10], "target_archetype": "all", "theme": "all"}
        },

        # Batch 17: HDR & EDR Luminance Headroom (exp-91 to exp-95)
        {
            "id": "exp-91-big-hdr-1000nits",
            "task": "EXP-BIG-26",
            "hypothesis": "1000-nit specular highlight simulation achieves >0.96 accuracy on Apple TV 4K HDR",
            "decision": "Validate HDR specular highlight accuracy gain",
            "config": {"job_id": "exp-91-big-hdr-1000nits", "manifest_path": MANIFEST_PATH, "dimension": "hdr_edr_headroom", "peak_nits": 1000, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-92-big-hdr-600nits",
            "task": "EXP-BIG-27",
            "hypothesis": "600-nit HDR headroom provides substantial contrast gain over standard dynamic range",
            "decision": "Verify 600-nit HDR achieves >0.945 accuracy",
            "config": {"job_id": "exp-92-big-hdr-600nits", "manifest_path": MANIFEST_PATH, "dimension": "hdr_edr_headroom", "peak_nits": 600, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-93-big-hdr-400nits",
            "task": "EXP-BIG-28",
            "hypothesis": "400-nit entry-level HDR headroom marks the transition boundary from SDR",
            "decision": "Measure transition inflection from SDR to HDR",
            "config": {"job_id": "exp-93-big-hdr-400nits", "manifest_path": MANIFEST_PATH, "dimension": "hdr_edr_headroom", "peak_nits": 400, "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-94-big-hdr-sdr-cmp",
            "task": "EXP-BIG-29",
            "hypothesis": "HDR displays provide a 3.4 percentage point discrimination advantage over SDR",
            "decision": "Confirm dynamic range advantage across archetypes",
            "config": {"job_id": "exp-94-big-hdr-sdr-cmp", "manifest_path": MANIFEST_PATH, "dimension": "hdr_edr_headroom", "peak_nits": 1000, "target_archetype": "shelf", "theme": "all"}
        },
        {
            "id": "exp-95-big-hdr-lowcontrast",
            "task": "EXP-BIG-30",
            "hypothesis": "HDR specular highlight restores low-contrast dark themes to parity with standard themes",
            "decision": "Verify HDR eliminates the low-contrast vulnerability gap",
            "config": {"job_id": "exp-95-big-hdr-lowcontrast", "manifest_path": MANIFEST_PATH, "dimension": "hdr_edr_headroom", "peak_nits": 1000, "target_archetype": "all", "theme": "dark_low_contrast"}
        },

        # Batch 18: Quantization, Latency & ANE Precision (exp-96 to exp-100)
        {
            "id": "exp-96-big-quant-fp32",
            "task": "EXP-BIG-31",
            "hypothesis": "Unquantized FP32 baseline sets theoretical upper bound on precision",
            "decision": "Establish FP32 reference metric at 0.953",
            "config": {"job_id": "exp-96-big-quant-fp32", "manifest_path": MANIFEST_PATH, "dimension": "quantization_ane_precision", "precision": "fp32", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-97-big-quant-fp16",
            "task": "EXP-BIG-32",
            "hypothesis": "CoreML FP16 half-precision matches FP32 within 0.1 percentage point on Apple Neural Engine",
            "decision": "Validate FP16 production deployment parity",
            "config": {"job_id": "exp-97-big-quant-fp16", "manifest_path": MANIFEST_PATH, "dimension": "quantization_ane_precision", "precision": "fp16", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-98-big-quant-int8",
            "task": "EXP-BIG-33",
            "hypothesis": "INT8 post-training quantization retains >94.5% accuracy while cutting memory by 48%",
            "decision": "Approve INT8 quantization for embedded edge deployment if accuracy loss < 0.8 pp",
            "config": {"job_id": "exp-98-big-quant-int8", "manifest_path": MANIFEST_PATH, "dimension": "quantization_ane_precision", "precision": "int8", "target_archetype": "all", "theme": "all"}
        },
        {
            "id": "exp-99-big-quant-int8-lowcontrast",
            "task": "EXP-BIG-34",
            "hypothesis": "INT8 quantization does not amplify the low-contrast degradation effect",
            "decision": "Verify INT8 precision retention on dark_low_contrast theme",
            "config": {"job_id": "exp-99-big-quant-int8-lowcontrast", "manifest_path": MANIFEST_PATH, "dimension": "quantization_ane_precision", "precision": "int8", "target_archetype": "all", "theme": "dark_low_contrast"}
        },
        {
            "id": "exp-100-big-quant-pareto-frontier",
            "task": "EXP-BIG-35",
            "hypothesis": "Optimal operational trade-off point is FP16 for accuracy and INT8 for high-frequency scrolling",
            "decision": "Establish multi-precision dual deployment policy in ProductRoadmap",
            "config": {"job_id": "exp-100-big-quant-pareto-frontier", "manifest_path": MANIFEST_PATH, "dimension": "quantization_ane_precision", "precision": "fp16", "target_archetype": "all", "theme": "all"}
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
    submitted = register_large_scale_backlog()
    print(f"Registered {len(submitted)} large-scale backlog experiments.")
