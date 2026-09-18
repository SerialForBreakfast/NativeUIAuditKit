#!/usr/bin/env python3
"""
export_focus_ring_coreml.py — Export FocusRingDetector .pt → FP16 CoreML.

Uses torch.jit.trace → coremltools, bypassing the ONNX step (no `onnx` package needed).

Usage:
  .venv-coreml/bin/python scripts/export_focus_ring_coreml.py \\
      --weights NativeUITrainer/focus_ring_runs/fdr001/weights/best.pt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR":    str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME":      str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
for _k, _v in _os_env_defaults.items():
    os.environ.setdefault(_k, _v)
    Path(_v).mkdir(parents=True, exist_ok=True)

MAX_MB = 5.0
INPUT_SIZE = 256


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export FocusRingDetector model to FP16 CoreML")
    p.add_argument("--weights", required=True, help="Path to best.pt checkpoint")
    p.add_argument("--output-dir", default=None,
                   help="Export directory (default: <weights>/../export/)")
    p.add_argument("--model", default="mobilenetv4_conv_small")
    return p.parse_args()


def dir_size_mb(path: Path) -> float:
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)


def main() -> int:
    args = parse_args()
    weights = Path(args.weights).expanduser()
    if not weights.is_absolute():
        weights = (PROJECT_ROOT / weights).resolve()
    if not weights.is_file():
        print(f"ERROR: weights not found: {weights}")
        return 1

    export_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else weights.parent.parent / "export"
    )
    export_dir.mkdir(parents=True, exist_ok=True)

    # --- imports ---
    import importlib.util
    import torch
    import torch.nn as nn

    try:
        import coremltools as ct
    except ImportError as e:
        print(f"ERROR: {e}. Run with .venv-coreml (has coremltools).")
        return 1

    # --- load backbone from checkpoint ---
    ckpt = torch.load(weights, map_location="cpu", weights_only=False)
    model_name = ckpt.get("model_name", args.model) if isinstance(ckpt, dict) else args.model
    state = ckpt["state_dict"] if isinstance(ckpt, dict) and "state_dict" in ckpt else ckpt

    bb_path = Path(__file__).with_name("focus_ring_backbone.py")
    spec = importlib.util.spec_from_file_location("focus_ring_backbone", bb_path)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load {bb_path}")
        return 1
    bb_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb_mod)
    backbone = bb_mod.mobilenetv4_conv_small(pretrained=False, num_classes=1)
    backbone.load_state_dict(state)
    backbone.eval()

    class ExportWrapper(nn.Module):
        """Maps logits to the spec output contract: is_focused_prob, confidence."""

        def __init__(self, inner: nn.Module) -> None:
            super().__init__()
            self.inner = inner

        def forward(self, x: torch.Tensor) -> tuple:
            logits = self.inner(x).reshape(-1)[:1]
            prob = torch.sigmoid(logits)
            conf = (prob - 0.5).abs() * 2.0
            return prob.reshape(1), conf.reshape(1)

    wrapped = ExportWrapper(backbone)
    wrapped.eval()
    example = torch.zeros(1, 3, INPUT_SIZE, INPUT_SIZE)

    # --- torch.jit.trace → CoreML (no onnx package required) ---
    traced = torch.jit.trace(wrapped, example)
    traced.eval()

    mlmodel = ct.convert(
        traced,
        inputs=[
            ct.ImageType(
                name="image",
                shape=ct.Shape(shape=(1, 3, INPUT_SIZE, INPUT_SIZE)),
                scale=1 / 255.0,
                color_layout=ct.colorlayout.RGB,
            )
        ],
        outputs=[
            ct.TensorType(name="is_focused_prob"),
            ct.TensorType(name="confidence"),
        ],
        convert_to="mlprogram",
        compute_precision=ct.precision.FLOAT16,
        minimum_deployment_target=ct.target.macOS15,
    )

    # Required metadata (Research/FocusRingDetectorSpec.md §9)
    mlmodel.short_description = "Binary classifier: tvOS UI element focus state"
    mlmodel.author = "NativeUIAuditKit"
    mlmodel.user_defined_metadata["modelID"] = "focus-ring-detector-v1.0"
    mlmodel.user_defined_metadata["versionString"] = "1.0.0"
    mlmodel.user_defined_metadata["focusThreshold"] = "0.85"
    mlmodel.user_defined_metadata["ambiguityThreshold"] = "0.70"
    mlmodel.user_defined_metadata["backboneArchitecture"] = model_name

    pkg = export_dir / "FocusRingDetector.mlpackage"
    mlmodel.save(str(pkg))
    size_mb = dir_size_mb(pkg)
    print(f"Exported {pkg} ({size_mb:.2f} MB)")

    report = {
        "generatedAt": utc_now(),
        "weights": str(weights),
        "model_name": model_name,
        "mlpackage": str(pkg),
        "size_mb": size_mb,
        "size_gate_pass": size_mb <= MAX_MB,
    }
    report_path = export_dir / "focus_ring_detector_training_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    if size_mb > MAX_MB:
        print(f"ERROR: {pkg.name} is {size_mb:.2f} MB, exceeds {MAX_MB} MB budget")
        return 1

    print(
        f"\nSize gate: {size_mb:.2f} MB <= {MAX_MB} MB PASS\n"
        "\nNext: compile to .mlmodelc:\n"
        f"  xcrun coremlc compile {pkg} {export_dir}\n"
        "Then copy FocusRingDetector.mlmodelc into:\n"
        "  NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/\n"
        "And add to Package.swift NativeUIAuditKitModels target:\n"
        '  .copy("Resources/FocusRingDetector.mlmodelc")'
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
