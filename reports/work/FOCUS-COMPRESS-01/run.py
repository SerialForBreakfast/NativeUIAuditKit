"""Bounded one-candidate execution; existing destinations are never reused."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
source = root / "NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-01"
destination = source.parent / "export-03-int8"
if destination.exists():
    raise SystemExit("output_collision")
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
       "TMPDIR": str(root / ".build/debug-output/focus-launch/tmp")}
commands = [
    ("compress", [sys.executable, "scripts/compress_focus_ring_coreml.py", "--package", str(source / "FocusRingDetector.mlpackage"),
        "--source-report", str(source / "focus_ring_detector_training_report.json"),
        "--source-sha256", "4d43d6f4aedb7d26e820c7c33d79fa4e21b28d64a25a683f03c6219e64ccdf02",
        "--output-dir", str(destination), "--experimental-id", "fdr007-int8-01"]),
    ("compile", ["xcrun", "coremlc", "compile", str(destination / "FocusRingDetector.mlpackage"), str(destination / "compiled")]),
    ("compare", [sys.executable, "scripts/focus_export_parity.py", "--reference", "reports/work/OS-FOCUS-03/challenge-after.json",
        "--reference-sha256", "11ff841cf437e4699aadc8cfdb7053ccf74ffc07f70edbee0966ac135c71a21a",
        "--model", str(destination / "compiled/FocusRingDetector.mlmodelc"),
        "--export-report", str(destination / "focus_ring_detector_training_report.json"),
        "--protocol", "reports/work/OS-FOCUS-03/corpus-01/protocol.json", "--output", str(here / "parity.json")])]
for name, command in commands:
    if name == "compile": (destination / "compiled").mkdir()
    start = time.monotonic()
    with (here / (name + ".log")).open("x") as log:
        try: code = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180).returncode
        except subprocess.TimeoutExpired: code = 124
    result = {"stage": name, "command": command, "exitCode": code, "elapsedSeconds": time.monotonic()-start}
    with (here / (name + "-execution.json")).open("x") as stream: json.dump(result, stream, indent=2)
    print(json.dumps(result), flush=True)
    if code: raise SystemExit(code)
