#!/usr/bin/env python3
"""
ingest_tvos_capture.py — Ingest TVTestRig screenshots into NativeUIAuditKit dataset.

Accepts screenshots captured by TVTestRig (from tvOS Simulator or physical Apple TV)
and generates schema-compliant annotation JSON sidecars with explicit OS provenance.

Usage:
    .venv-yolo/bin/python scripts/ingest_tvos_capture.py \
        --image path/to/capture.png \
        [--metadata path/to/metadata.json] \
        [--source realAppleTVTVTestRig] \
        [--out-dir dataset/tvos_captures]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest TVTestRig screenshots for tvOS dataset")
    parser.add_argument("--image", required=True, type=Path, help="Path to screenshot PNG")
    parser.add_argument("--metadata", type=Path, default=None, help="Optional TVTestRig metadata JSON")
    parser.add_argument(
        "--source",
        choices=["tvOSSimulatorTVTestRig", "realAppleTVTVTestRig"],
        default="tvOSSimulatorTVTestRig",
        help="Capture source provenance",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "dataset" / "tvos_captures",
        help="Target directory for ingested images and sidecars",
    )
    return parser.parse_args()


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    args = parse_args()

    if not args.image.exists():
        print(f"ERROR: Image not found at {args.image}", file=sys.stderr)
        return 1

    img_sha256 = compute_sha256(args.image)

    with Image.open(args.image) as img:
        width, height = img.size

    # Validate tvOS 16:9 landscape resolution
    if (width, height) not in [(1920, 1080), (3840, 2160)]:
        print(
            f"WARNING: Unexpected tvOS resolution {width}x{height}. Standard is 1920x1080 or 3840x2160.",
            file=sys.stderr,
        )

    scale = 2 if (width, height) == (3840, 2160) else 1

    meta = {}
    if args.metadata and args.metadata.exists():
        try:
            meta = json.loads(args.metadata.read_text())
        except Exception as e:
            print(f"WARNING: Could not parse metadata JSON: {e}", file=sys.stderr)

    os_version = meta.get("osVersion", "tvOS 17.2")
    device_name = meta.get("deviceName", "Apple TV 4K")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    dest_image = out_dir / args.image.name
    if dest_image.resolve() != args.image.resolve():
        dest_image.write_bytes(args.image.read_bytes())

    sidecar = {
        "schemaVersion": "1.0",
        "imageSHA256": img_sha256,
        "captureSource": args.source,
        "image": {
            "fileName": dest_image.name,
            "pixelWidth": width,
            "pixelHeight": height,
            "scale": scale,
            "platform": "tvOS",
            "osVersion": os_version,
            "deviceName": device_name,
            "interfaceIdiom": "tv",
            "orientation": "landscape",
            "colorScheme": meta.get("colorScheme", "dark"),
            "dynamicTypeSize": "large",
            "locale": meta.get("locale", "en_US"),
            "layoutDirection": "ltr",
            "safeAreaInsets": {"top": 60, "left": 90, "bottom": 60, "right": 90},
            "reduceTransparency": False,
            "increaseContrast": False,
            "boldText": False,
            "buttonShapes": False,
            "onOffLabels": False,
            "smartInvert": False,
        },
        "generatorProfile": {
            "templateFamily": "TVTestRigCapture",
            "seed": 0,
            "generatorVersion": "tvtestrig-1.0",
            "isolationTemplate": False,
            "lowDensity": False,
            "simulatorState": {
                "time": "09:41",
                "batteryLevel": 100,
                "batteryState": "charging",
                "cellularBars": 0,
                "wifiBars": 3,
                "operatorName": "",
            },
        },
        "elements": meta.get("elements", []),
    }

    sidecar_path = out_dir / f"{dest_image.stem}.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2))

    print(f"Ingested: {dest_image}")
    print(f"Sidecar:  {sidecar_path}")
    print(f"SHA-256:  {img_sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
