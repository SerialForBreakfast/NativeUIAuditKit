"""One bounded import/export in the maintainer-approved external environment."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
       "TMPDIR": str(root/".build/debug-output/focus-launch/tmp"),
       "TORCH_HOME": str(root/"NativeUITrainer/.torch"),
       "MPLCONFIGDIR": str(root/"NativeUITrainer/.mplconfig")}
stages = [
    ("isolated-import", 60, [sys.executable, "-u", "-c",
      "import torch,coremltools; print('torch',torch.__version__,'coremltools',coremltools.__version__)"]),
    ("isolated-export", 600, [sys.executable, "-u", "scripts/export_focus_ring_coreml.py",
      "--weights", "NativeUITrainer/focus_ring_runs/fdr007-native-incremental/weights/best.pt",
      "--output-dir", "NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-01",
      "--experimental-id", "fdr007-native-incremental"]),
]
for name, deadline, command in stages:
    start = time.monotonic()
    with (here/(name+".log")).open("x") as log:
        try:
            code = subprocess.run(command, cwd=root, env=env, stdout=log,
                                  stderr=subprocess.STDOUT, timeout=deadline).returncode
        except subprocess.TimeoutExpired:
            code = 124
    receipt = {"stage": name, "command": command, "exitCode": code,
               "elapsedSeconds": time.monotonic()-start, "deadlineSeconds": deadline}
    with (here/(name+".json")).open("x") as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps(receipt), flush=True)
    if code:
        raise SystemExit(code)
