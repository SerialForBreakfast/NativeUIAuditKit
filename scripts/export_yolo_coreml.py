#!/usr/bin/env python3
"""
export_yolo_coreml.py  —  Export a trained YOLO11 .pt checkpoint to CoreML.

The exported .mlpackage can be dropped into:
  NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/

Usage:
  # IMPORTANT: use .venv-coreml (Python 3.12), NOT .venv-yolo (Python 3.14).
  # coremltools C extensions (BlobWriter) are only compiled for Python ≤ 3.13.
  .venv-coreml/bin/python scripts/export_yolo_coreml.py \\
    --weights NativeUITrainer/yolo_runs/yolo11n_e100/weights/best.pt \\
    --output  NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/

Notes:
  - nms=True bakes NMS into the CoreML graph (recommended for on-device inference).
  - imgsz must match what the model was trained at.
  - The output file is named <stem>.mlpackage beside the .pt file by default,
    then copied to --output if specified.
  - Requires coremltools (included in ultralytics dependencies).
"""

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _patch_coremltools():
    """
    Runtime monkeypatch for coremltools 9.0 + numpy 2.x incompatibility.

    coremltools 9.0 calls `int(x.val)` where x.val may be a numpy array.
    numpy 2.x disallows int() on non-0-d arrays; .item() extracts the scalar safely.
    Patching at runtime avoids touching the installed package files.
    """
    try:
        import coremltools.converters.mil.frontend.torch.ops as _ct_ops
        from coremltools.converters.mil.mil import Builder as _mb

        def _patched_cast(context, node, dtype, dtype_name):
            inputs = _ct_ops._get_inputs(context, node, expected=1)
            x = inputs[0]
            if not (len(x.shape) == 0 or all(d == 1 for d in x.shape)):
                raise ValueError("input to cast must be either a scalar or a length 1 tensor")
            if x.can_be_folded_to_const():
                if not isinstance(x.val, dtype):
                    v = x.val.item() if hasattr(x.val, "item") else x.val
                    res = _mb.const(val=dtype(v), name=node.name)
                else:
                    res = x
            elif len(x.shape) > 0:
                x = _mb.squeeze(x=x, name=node.name + "_item")
                res = _mb.cast(x=x, dtype=dtype_name, name=node.name)
            else:
                res = _mb.cast(x=x, dtype=dtype_name, name=node.name)
            context.add(res, node.name)

        _ct_ops._cast = _patched_cast
        print("  coremltools _cast monkeypatched (numpy 2.x compat)")
    except Exception as e:
        print(f"  NOTE: coremltools monkeypatch skipped ({e})")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True,
                   help="Path to trained YOLO11 .pt checkpoint")
    p.add_argument("--imgsz",   type=int, default=640,
                   help="Image size used during training (default: 640)")
    p.add_argument("--output",  default=None,
                   help="Directory to copy the .mlpackage into (optional)")
    p.add_argument("--nms",     action="store_true", default=True,
                   help="Bake NMS into the CoreML graph (default: True)")
    p.add_argument("--half",    action="store_true", default=False,
                   help="Export FP16 (smaller, slightly less accurate)")
    p.add_argument(
        "--int8",
        action="store_true",
        default=False,
        help="8-bit k-means weight palettization (Ultralytics quantize=8). Writes <stem>_int8.mlpackage.",
    )
    return p.parse_args()


def main():
    args = parse_args()
    weights = Path(args.weights).expanduser().resolve()

    if not weights.exists():
        print(f"ERROR: weights not found: {weights}")
        sys.exit(1)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not found. Use:")
        print("  .venv-yolo/bin/python scripts/export_yolo_coreml.py ...")
        sys.exit(1)

    _patch_coremltools()

    print(f"Exporting {weights} → CoreML")
    print(f"  imgsz    : {args.imgsz}")
    print(f"  nms      : {args.nms}")
    print(f"  half     : {args.half}")
    print(f"  int8     : {args.int8}")

    if args.int8:
        # Apple linear INT8 on an already-exported FP16+NMS package.
        # Ultralytics quantize=8 k-means palettization SIGKILL'd YOLO11m at
        # palettize_weights 0/227 (see BP-31).
        import coremltools as ct
        import coremltools.optimize.coreml as cto

        src = weights.with_name(weights.stem + "_fp16.mlpackage")
        if not src.is_dir():
            src = weights.with_suffix(".mlpackage")
        if not src.is_dir():
            print(f"ERROR: need an FP16 mlpackage beside the .pt (looked for {src})")
            sys.exit(1)
        dest = weights.with_name(weights.stem + "_int8.mlpackage")
        print(f"  source   : {src}")
        print("  method   : coremltools linear_quantize_weights")
        mlmodel = ct.models.MLModel(str(src))
        config = cto.OptimizationConfig(
            global_config=cto.OpLinearQuantizerConfig(mode="linear_symmetric")
        )
        quantized = cto.linear_quantize_weights(mlmodel, config)
        if dest.exists():
            shutil.rmtree(dest)
        quantized.save(str(dest))
        mlpkg = dest
        print(f"\nExported → {mlpkg}")
    else:
        # quantize=16 is FP16. nms=True defaults to FP16 when quantize is omitted.
        quantize = 16 if args.half else None
        print(f"  quantize : {quantize}")
        model = YOLO(str(weights))
        exported = model.export(
            format="coreml",
            imgsz=args.imgsz,
            nms=args.nms,
            quantize=quantize,
            verbose=True,
        )
        mlpkg = Path(exported)
        print(f"\nExported → {mlpkg}")

    if args.output:
        out_dir = Path(args.output).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / mlpkg.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(mlpkg, dest)
        print(f"Copied   → {dest}")
        print(f"\nDrop {mlpkg.name} into Xcode and update NativeUIAuditKitModels.")


if __name__ == "__main__":
    main()
