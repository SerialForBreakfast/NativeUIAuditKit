"""Register HCF371-r5 revision to unblock crop training and evaluation (ASD-STE100)."""
import copy
from pathlib import Path
from research_campaign340 import pin
import research_queue as q


def register():
    folder = q.ROOT / "Research/ResearchSpecs/HCF371-r5"
    folder.mkdir(parents=True, exist_ok=True)

    r4_folder = q.ROOT / "Research/ResearchSpecs/HCF371-r4"
    design_pin = pin(r4_folder / "design.json")

    code_names = [
        "hcf_study371.py",
        "hcf_compare371.py",
        "hcf_training371.py",
        "hcf_capture362.py",
        "hcf_settings368.py",
        "qualify_hcf362.py",
        "generation352.py",
        "dataset351.py",
        "native343.py",
        "direct_tvos_capture.py",
        "hcf_spatial_audit.py",
        "focus_runtime.py",
        "focus_ring_backbone.py",
        "train_focus_ring_detector.py",
        "train_yolo.py",
        "score_hcf_pilot.py",
    ]
    code_inputs = [pin(q.ROOT / "scripts" / name) for name in code_names]
    code_inputs.append(pin(q.ROOT / ".build/arm64-apple-macosx/debug/FocusRingTool"))
    code_inputs.append(pin(q.ROOT / "Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift"))
    code_inputs.append(design_pin)

    weight_path = q.ROOT / "NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt"
    crop_inputs = code_inputs + [pin(weight_path)]

    crop_cfg_src = q.ROOT / "Research/ResearchSpecs/HCF371/hcf371-70-crop-train-config.json"
    crop_cfg = q.load(crop_cfg_src)
    crop_cfg_path = folder / "hcf371r5-70-crop-train-config.json"
    q.save(crop_cfg_path, crop_cfg, replace=True)

    eval_cfg_src = q.ROOT / "Research/ResearchSpecs/HCF371/hcf371-80-crop-evaluate-config.json"
    eval_cfg = q.load(eval_cfg_src)
    eval_cfg_path = folder / "hcf371r5-80-crop-evaluate-config.json"
    q.save(eval_cfg_path, eval_cfg, replace=True)

    # 1. hcf371r5-70-crop-train
    p_crops = q.load(q.QUEUE / "jobs/hcf371r4-50-crops/spec.json")
    spec_crop_train = dict(
        version=q.SPEC_VERSION,
        id="hcf371r5-70-crop-train",
        task="HCF371",
        owner="research-host-NUIAK",
        kind="confirm",
        authority="training",
        hypothesis="Train a native HCF crop candidate on frozen training groups with contiguous tensors.",
        decisionRule="Use 30 epochs, patience 10, and the current 1800-second runner limit. A timeout is not a successful run.",
        inputs=crop_inputs,
        stage=[dict(from_=pin(crop_cfg_path), to="config.json")],
        dependencies=[
            dict(job="hcf371r4-50-crops", specSHA256=q.text_digest(p_crops), outputs=["crops.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_training371.crop"],
            outputAttributes=["hcf_training371.OUT"]
        ),
        training=dict(
            acceptanceEvidence="Matched development gains with no lost retained successes. No automatic production promotion.",
            epochs=30,
            experimentLogRunId="HCF371",
            initialization=pin(weight_path),
            membership=[design_pin],
            resume="restart",
            storageBudgetBytes=2147483648
        ),
        limits=dict(timeoutSeconds=1800, maxOutputBytes=100_000_000, maxAttempts=1)
    )
    # Fix stage key 'from'
    spec_crop_train["stage"] = [{"from": pin(crop_cfg_path), "to": "config.json"}]
    p_crop_train_file = folder / "hcf371r5-70-crop-train.json"
    q.save(p_crop_train_file, spec_crop_train, replace=True)
    q.submit(p_crop_train_file)
    print("Submitted hcf371r5-70-crop-train")

    # 2. hcf371r5-80-crop-evaluate
    p_catalog = q.load(q.QUEUE / "jobs/hcf371r4-40-catalog/spec.json")
    p_retained = q.load(q.QUEUE / "jobs/hcf371-00-retained/spec.json")
    spec_crop_eval = dict(
        version=q.SPEC_VERSION,
        id="hcf371r5-80-crop-evaluate",
        task="HCF371",
        owner="research-host-NUIAK",
        kind="screen",
        authority="diagnostic",
        hypothesis="Does the crop candidate improve native HCF selection without losing previous successes?",
        decisionRule="Use fixed thresholds on matched development and regression images. Report every gain and loss.",
        inputs=crop_inputs,
        stage=[{"from": pin(eval_cfg_path), "to": "config.json"}],
        dependencies=[
            dict(job="hcf371r4-40-catalog", specSHA256=q.text_digest(p_catalog), outputs=["admission.json"]),
            dict(job="hcf371-00-retained", specSHA256=q.text_digest(p_retained), outputs=["admission.json"]),
            dict(job="hcf371r5-70-crop-train", specSHA256=q.text_digest(spec_crop_train), outputs=["model.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.candidate_crop"],
            outputAttributes=["hcf_compare371.OUT"]
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1)
    )
    p_crop_eval_file = folder / "hcf371r5-80-crop-evaluate.json"
    q.save(p_crop_eval_file, spec_crop_eval, replace=True)
    q.submit(p_crop_eval_file)
    print("Submitted hcf371r5-80-crop-evaluate")

    # 3. hcf371r5-80-detector-evaluate
    det_eval_cfg_src = q.ROOT / "Research/ResearchSpecs/HCF371/hcf371-80-detector-evaluate-config.json"
    det_eval_cfg = q.load(det_eval_cfg_src)
    det_eval_cfg_path = folder / "hcf371r5-80-detector-evaluate-config.json"
    q.save(det_eval_cfg_path, det_eval_cfg, replace=True)

    p_det_train = q.load(q.QUEUE / "jobs/hcf371r4-70-detector-train/spec.json")
    spec_det_eval = dict(
        version=q.SPEC_VERSION,
        id="hcf371r5-81-detector-evaluate",
        task="HCF371",
        owner="research-host-NUIAK",
        kind="screen",
        authority="diagnostic",
        hypothesis="Does the detector candidate improve native HCF selection without losing previous successes?",
        decisionRule="Use fixed thresholds on matched development and regression images. Report every gain and loss.",
        inputs=code_inputs,
        stage=[{"from": pin(det_eval_cfg_path), "to": "config.json"}],
        dependencies=[
            dict(job="hcf371r4-40-catalog", specSHA256=q.text_digest(p_catalog), outputs=["admission.json"]),
            dict(job="hcf371-00-retained", specSHA256=q.text_digest(p_retained), outputs=["admission.json"]),
            dict(job="hcf371r4-70-detector-train", specSHA256=q.text_digest(p_det_train), outputs=["model.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.detector"],
            outputAttributes=["hcf_compare371.OUT"]
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1)
    )
    p_det_eval_file = folder / "hcf371r5-81-detector-evaluate.json"
    q.save(p_det_eval_file, spec_det_eval, replace=True)
    q.submit(p_det_eval_file)
    print("Submitted hcf371r5-81-detector-evaluate")

    # 4. hcf371r5-92-decision
    p_rules = q.load(q.QUEUE / "jobs/hcf371r4-60-rules/spec.json")
    p_base = q.load(q.QUEUE / "jobs/hcf371r4-61-baseline/spec.json")
    spec_decision = dict(
        version=q.SPEC_VERSION,
        id="hcf371r5-92-decision",
        task="HCF371",
        owner="research-host-NUIAK",
        kind="screen",
        authority="diagnostic",
        hypothesis="Which method improves selection, and what still fails?",
        decisionRule="Require all 4 reports. Keep final audit sealed until a candidate and settings are frozen. No production replacement.",
        inputs=code_inputs,
        dependencies=[
            dict(job="hcf371r4-60-rules", specSHA256=q.text_digest(p_rules), outputs=["comparison.json"]),
            dict(job="hcf371r4-61-baseline", specSHA256=q.text_digest(p_base), outputs=["comparison.json"]),
            dict(job="hcf371r5-80-crop-evaluate", specSHA256=q.text_digest(spec_crop_eval), outputs=["comparison.json"]),
            dict(job="hcf371r5-81-detector-evaluate", specSHA256=q.text_digest(spec_det_eval), outputs=["comparison.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.decision"],
            outputAttributes=["hcf_compare371.OUT"]
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1)
    )
    p_decision_file = folder / "hcf371r5-92-decision.json"
    q.save(p_decision_file, spec_decision, replace=True)
    q.submit(p_decision_file)
    print("Submitted hcf371r5-92-decision")


if __name__ == "__main__":
    register()
