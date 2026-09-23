"""Bounded read-vs-native-import diagnosis; no dependency/model modifications."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
paths = [root/".venv-yolo/lib/python3.13/site-packages/scipy/interpolate/_rgi.py",
         root/".venv-yolo/lib/python3.13/site-packages/scipy/interpolate/_rgi_cython.cpython-313-darwin.so"]
reads = []
for path in paths:
    start = time.monotonic(); data = path.read_bytes()
    reads.append({"path": str(path.relative_to(root)), "bytes": len(data), "seconds": time.monotonic()-start,
                  "sha256": hashlib.sha256(data).hexdigest()})
with (here/"read-timing.json").open("x") as stream: json.dump(reads, stream, indent=2)
command = [str(root/".venv-yolo/bin/python"), "-X", "importtime", "-u", "-c",
    "import faulthandler; faulthandler.dump_traceback_later(30,repeat=True); import scipy.interpolate._rgi; print('isolated scipy import passed',flush=True); faulthandler.cancel_dump_traceback_later()"]
start = time.monotonic()
with (here/"isolated-scipy.log").open("x") as log:
    try: code = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT, timeout=120,
        env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","TMPDIR":str(root/".build/debug-output/focus-launch/tmp")}).returncode
    except subprocess.TimeoutExpired: code = 124
result = {"exitCode":code,"elapsedSeconds":time.monotonic()-start,"command":command}
with (here/"isolated-scipy.json").open("x") as stream: json.dump(result,stream,indent=2)
print(json.dumps(result))
