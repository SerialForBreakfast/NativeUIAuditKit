"""Bound import readiness only; no model load, conversion, installation or retries."""
import json
import os
from pathlib import Path
import subprocess
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--name", choices=["runtime-probe", "runtime-probe-warm"], default="runtime-probe")
name = parser.parse_args().name

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
command = [str(root/".venv-yolo/bin/python"), "-u", "-c",
    "import faulthandler; faulthandler.dump_traceback_later(30); import torch; print('torch',torch.__version__,flush=True); import coremltools; print('coremltools',coremltools.__version__,flush=True); faulthandler.cancel_dump_traceback_later()"]
start = time.monotonic()
with (here/(name+".log")).open("x") as log:
    try: code = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT, timeout=60,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(root/".build/debug-output/focus-launch/tmp"),
             "TORCH_HOME": str(root/"NativeUITrainer/.torch"), "MPLCONFIGDIR": str(root/"NativeUITrainer/.mplconfig")}).returncode
    except subprocess.TimeoutExpired: code = 124
result = {"exitCode": code, "elapsedSeconds": time.monotonic()-start, "command": command}
with (here/(name+".json")).open("x") as stream: json.dump(result, stream, indent=2)
print(json.dumps(result))
