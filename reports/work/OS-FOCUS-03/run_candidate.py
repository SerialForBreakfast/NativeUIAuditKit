"""Execute exactly the logged candidate, bounded externally; never retry."""
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
command = [str(root/".venv-yolo/bin/python"), "-u", str(root/"scripts/train_focus_ring_detector.py"),
    "--experiment-protocol", str(evidence/"corpus-01/protocol.json"), "--experiment-arm", "warm-stretch",
    "--name", "fdr007-native-incremental", "--execute", "--experiment-id", "FDR-007"]
started = time.monotonic()
with (evidence/"fdr007-launch02.log").open("x") as log:
    process = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(root/".build/debug-output/focus-launch/tmp")})
    try: code = process.wait(timeout=600)
    except subprocess.TimeoutExpired:
        process.terminate()
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
        code = 124
result = {"pid": process.pid, "exitCode": code, "elapsedSeconds": time.monotonic()-started, "command": command}
with (evidence/"fdr007-launch02-execution.json").open("x") as stream: json.dump(result, stream, indent=2)
print(json.dumps(result), flush=True)
raise SystemExit(code)
