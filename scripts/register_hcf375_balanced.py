"""Register HCF375 balanced joint training and evaluation pipeline (ASD-STE100)."""
from pathlib import Path
import research_queue as q
from research_campaign340 import pin


def register():
    """Register balanced HCF + Standard model training and evaluation experiments."""
    folder = q.ROOT / "Research/ResearchSpecs/HCF375"
    folder.mkdir(parents=True, exist_ok=True)

    r4_folder = q.ROOT / "Research/ResearchSpecs/HCF371-r4"
    design_pin = pin(r4_folder / "design.json")

    code_names = [
        "hcf_study371.py",
        "hcf_compare371.py",
        "hcf_training375.py",
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

    crop_weight_path = q.ROOT / "NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt"
    crop_inputs = code_inputs + [pin(crop_weight_path)]

    yolo_weight_path = q.ROOT / "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt"
    yolo_inputs = code_inputs + [pin(yolo_weight_path)]

    # 1. Configs
    crop_cfg = dict(
        profile="balanced",
        initialization=pin(crop_weight_path),
        inputs=crop_inputs,
    )
    crop_cfg_path = folder / "hcf375-70-crop-train-config.json"
    q.save(crop_cfg_path, crop_cfg, replace=True)

    detector_cfg = dict(
        profile="balanced",
        initialization=pin(yolo_weight_path),
        inputs=yolo_inputs,
    )
    detector_cfg_path = folder / "hcf375-71-detector-train-config.json"
    q.save(detector_cfg_path, detector_cfg, replace=True)

    eval_cfg_src = q.ROOT / "Research/ResearchSpecs/HCF371/hcf371-80-crop-evaluate-config.json"
    eval_cfg = q.load(eval_cfg_src)
    eval_cfg["candidate"] = True
    crop_eval_cfg_path = folder / "hcf375-80-crop-evaluate-config.json"
    q.save(crop_eval_cfg_path, eval_cfg, replace=True)

    detector_eval_cfg_src = q.ROOT / "Research/ResearchSpecs/HCF371-r5/hcf371r5-80-detector-evaluate-config.json"
    detector_eval_cfg = q.load(detector_eval_cfg_src)
    detector_eval_cfg_path = folder / "hcf375-81-detector-evaluate-config.json"
    q.save(detector_eval_cfg_path, detector_eval_cfg, replace=True)

    # 2. Specs
    # Job 1: hcf375-70-crop-train
    p_crops = q.load(q.QUEUE / "jobs/hcf371r4-50-crops/spec.json")
    spec_crop_train = dict(
        version=q.SPEC_VERSION,
        id="hcf375-70-crop-train",
        task="HCF375",
        owner="Local-Runner-NUIAK",
        kind="confirm",
        authority="training",
        hypothesis="Train balanced MobileNetV4 crop classifier on 50% HCF and 50% Standard crops.",
        decisionRule="Use 30 epochs, patience 10, MPS accelerated. Eliminate the 2 retained center losses.",
        inputs=crop_inputs,
        stage=[dict(**{"from": pin(crop_cfg_path)}, to="config.json")],
        dependencies=[
            dict(job="hcf371r4-50-crops", specSHA256=q.text_digest(p_crops), outputs=["crops.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_training375.crop"],
            outputAttributes=["hcf_training375.OUT"],
        ),
        training=dict(
            acceptanceEvidence="Eliminate standard profile center misses while preserving HCF recall gains.",
            epochs=30,
            experimentLogRunId="HCF375",
            initialization=pin(crop_weight_path),
            membership=[design_pin],
            resume="restart",
            storageBudgetBytes=2147483648,
        ),
        limits=dict(timeoutSeconds=1800, maxOutputBytes=100_000_000, maxAttempts=1),
    )
    p_crop_train_file = folder / "hcf375-70-crop-train.json"
    q.save(p_crop_train_file, spec_crop_train, replace=True)
    q.submit(p_crop_train_file)
    print("Submitted hcf375-70-crop-train")

    # Job 2: hcf375-71-detector-train
    p_catalog = q.load(q.QUEUE / "jobs/hcf371r4-40-catalog/spec.json")
    spec_det_train = dict(
        version=q.SPEC_VERSION,
        id="hcf375-71-detector-train",
        task="HCF375",
        owner="Local-Runner-NUIAK",
        kind="confirm",
        authority="training",
        hypothesis="Train balanced YOLO11n object detector on 50% HCF and 50% Standard full frames.",
        decisionRule="Use 30 epochs, patience 10, MPS accelerated. Eliminate standard profile center misses.",
        inputs=yolo_inputs,
        stage=[dict(**{"from": pin(detector_cfg_path)}, to="config.json")],
        dependencies=[
            dict(job="hcf371r4-40-catalog", specSHA256=q.text_digest(p_catalog), outputs=["admission.json"])
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_training375.detector"],
            outputAttributes=["hcf_training375.OUT"],
        ),
        training=dict(
            acceptanceEvidence="Eliminate standard profile center misses while preserving HCF recall gains.",
            epochs=30,
            experimentLogRunId="HCF375",
            initialization=pin(yolo_weight_path),
            membership=[design_pin],
            resume="restart",
            storageBudgetBytes=2147483648,
        ),
        limits=dict(timeoutSeconds=1800, maxOutputBytes=100_000_000, maxAttempts=1),
    )
    p_det_train_file = folder / "hcf375-71-detector-train.json"
    q.save(p_det_train_file, spec_det_train, replace=True)
    q.submit(p_det_train_file)
    print("Submitted hcf375-71-detector-train")

    # Job 3: hcf375-80-crop-evaluate
    p_retained = q.load(q.QUEUE / "jobs/hcf371-00-retained/spec.json")
    spec_crop_eval = dict(
        version=q.SPEC_VERSION,
        id="hcf375-80-crop-evaluate",
        task="HCF375",
        owner="Local-Runner-NUIAK",
        kind="screen",
        authority="diagnostic",
        hypothesis="Does the balanced MobileNetV4 candidate eliminate the 2 retained center losses?",
        decisionRule="Zero lost previous successes required. Evaluate on 264 withheld frames.",
        inputs=crop_inputs,
        stage=[dict(**{"from": pin(crop_eval_cfg_path)}, to="config.json")],
        dependencies=[
            dict(job="hcf375-70-crop-train", specSHA256=q.text_digest(spec_crop_train), outputs=["model.json"]),
            dict(job="hcf371r4-40-catalog", specSHA256=q.text_digest(p_catalog), outputs=["admission.json"]),
            dict(job="hcf371-00-retained", specSHA256=q.text_digest(p_retained), outputs=["admission.json"]),
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.candidate_crop"],
            outputAttributes=["hcf_compare371.OUT"],
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1),
    )
    p_crop_eval_file = folder / "hcf375-80-crop-evaluate.json"
    q.save(p_crop_eval_file, spec_crop_eval, replace=True)
    q.submit(p_crop_eval_file)
    print("Submitted hcf375-80-crop-evaluate")

    # Job 4: hcf375-81-detector-evaluate
    spec_det_eval = dict(
        version=q.SPEC_VERSION,
        id="hcf375-81-detector-evaluate",
        task="HCF375",
        owner="Local-Runner-NUIAK",
        kind="screen",
        authority="diagnostic",
        hypothesis="Does the balanced YOLO11n candidate eliminate standard-profile center misses?",
        decisionRule="Zero false positives and zero retained losses required. Evaluate on 264 withheld frames.",
        inputs=yolo_inputs,
        stage=[dict(**{"from": pin(detector_eval_cfg_path)}, to="config.json")],
        dependencies=[
            dict(job="hcf375-71-detector-train", specSHA256=q.text_digest(spec_det_train), outputs=["model.json"]),
            dict(job="hcf371r4-40-catalog", specSHA256=q.text_digest(p_catalog), outputs=["admission.json"]),
            dict(job="hcf371-00-retained", specSHA256=q.text_digest(p_retained), outputs=["admission.json"]),
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.candidate_detector"],
            outputAttributes=["hcf_compare371.OUT"],
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1),
    )
    p_det_eval_file = folder / "hcf375-81-detector-evaluate.json"
    q.save(p_det_eval_file, spec_det_eval, replace=True)
    q.submit(p_det_eval_file)
    print("Submitted hcf375-81-detector-evaluate")

    # Job 5: hcf375-90-decision
    p_rules = q.load(q.QUEUE / "jobs/hcf371r4-60-rules/spec.json")
    p_base = q.load(q.QUEUE / "jobs/hcf371r4-61-baseline/spec.json")
    spec_decision = dict(
        version=q.SPEC_VERSION,
        id="hcf375-90-decision",
        task="HCF375",
        owner="Local-Runner-NUIAK",
        kind="confirm",
        authority="diagnostic",
        hypothesis="Determine if either balanced candidate passes all model gate criteria.",
        decisionRule="Require zero retained losses, zero false positives, and recall >= 50% before promotion.",
        inputs=code_inputs,
        stage=[],
        dependencies=[
            dict(job="hcf371r4-60-rules", specSHA256=q.text_digest(p_rules), outputs=["comparison.json"]),
            dict(job="hcf371r4-61-baseline", specSHA256=q.text_digest(p_base), outputs=["comparison.json"]),
            dict(job="hcf375-80-crop-evaluate", specSHA256=q.text_digest(spec_crop_eval), outputs=["comparison.json"]),
            dict(job="hcf375-81-detector-evaluate", specSHA256=q.text_digest(spec_det_eval), outputs=["comparison.json"]),
        ],
        adapter=dict(
            type="python-callable",
            steps=["hcf_compare371.decision"],
            outputAttributes=["hcf_compare371.OUT"],
        ),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1),
    )
    p_decision_file = folder / "hcf375-90-decision.json"
    q.save(p_decision_file, spec_decision, replace=True)
    q.submit(p_decision_file)
    print("Submitted hcf375-90-decision")

    print("\nHCF375 balanced pipeline registered successfully.")


if __name__ == "__main__":
    register()
