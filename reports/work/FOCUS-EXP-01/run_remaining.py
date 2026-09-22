"""One-shot serial executor for the four logged arms after cold-import diagnosis."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
ledger = []
for number, arm in ((6, "warm-stretch"), (3, "scratch-stretch"), (4, "warm-aspect-fit"), (5, "scratch-aspect-fit")):
    name = f"fdr{number:03d}-{arm}"
    command = [str(root/".venv-yolo/bin/python"), "-u", str(root/"scripts/train_focus_ring_detector.py"),
        "--experiment-protocol", str(evidence/"corpus-01/protocol.json"), "--experiment-arm", arm,
        "--name", name, "--execute", "--experiment-id", f"FDR-{number:03d}"]
    started = time.monotonic()
    print("starting", name, flush=True)
    with (evidence/f"fdr{number:03d}.log").open("x") as log:
        process = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(root/".build/debug-output/focus-launch/tmp")})
        try: code = process.wait(timeout=600)
        except subprocess.TimeoutExpired:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            code = 124
    ledger.append({"name": name, "pid": process.pid, "exitCode": code, "elapsedSeconds": time.monotonic()-started})
    print(json.dumps(ledger[-1]), flush=True)
    with (evidence/f"fdr{number:03d}-execution.json").open("x") as stream: json.dump(ledger[-1], stream, indent=2)
    if code: sys.exit(code)
