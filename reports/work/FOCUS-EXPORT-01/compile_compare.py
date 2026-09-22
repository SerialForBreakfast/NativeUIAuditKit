"""One-shot bounded compile and parity run; preserve outputs on every failure."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
sys.path.insert(0, str(root/"scripts"))
from focus_ring_baseline import artifact_digest

export = root/"NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-01"
package = export/"FocusRingDetector.mlpackage"
compiled = export/"compiled"
if compiled.exists(): raise SystemExit("output_collision")
package_hash = artifact_digest(package)
compiled.mkdir()
environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(root/".build/debug-output/focus-launch/tmp")}
commands = [
    ["xcrun", "coremlc", "compile", str(package), str(compiled)],
    [str(root/".venv-yolo/bin/python"), "scripts/focus_export_parity.py",
        "--reference", "reports/work/OS-FOCUS-03/challenge-after.json",
        "--reference-sha256", "11ff841cf437e4699aadc8cfdb7053ccf74ffc07f70edbee0966ac135c71a21a",
        "--model", str(compiled/"FocusRingDetector.mlmodelc"),
        "--export-report", str(export/"focus_ring_detector_training_report.json"),
        "--protocol", "reports/work/OS-FOCUS-03/corpus-01/protocol.json",
        "--output", str(here/"parity.json")]]
ledger = []
for name, command in zip(("compile", "compare"), commands, strict=True):
    start = time.monotonic()
    with (here/(name+".log")).open("x") as log:
        try: code = subprocess.run(command, cwd=root, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=180).returncode
        except subprocess.TimeoutExpired: code = 124
    row = {"stage": name, "command": command, "exitCode": code, "elapsedSeconds": time.monotonic()-start}
    ledger.append(row)
    with (here/(name+"-execution.json")).open("x") as stream: json.dump(row, stream, indent=2)
    print(json.dumps(row), flush=True)
    if code: raise SystemExit(code)
if artifact_digest(package) != package_hash: raise SystemExit("changed_package")
size = sum(p.stat().st_size for p in package.rglob("*") if p.is_file())
with (here/"artifact.json").open("x") as stream:
    json.dump({"packageSHA256": package_hash, "compiledSHA256": artifact_digest(compiled/"FocusRingDetector.mlmodelc"),
        "packageBytes": size, "packageMiB": size/1024**2, "packageDecimalMB": size/1_000_000,
        "within5MiB": size <= 5*1024**2, "within5DecimalMB": size <= 5_000_000,
        "releaseEligible": False}, stream, indent=2)
