"""Bounded LOCAL-TOOLS-02 smoke on two retained screenshots, not a model evaluation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True, help="Fresh project-local evidence directory")
args = parser.parse_args()
OUT = (ROOT / args.output).resolve()
if ROOT not in OUT.parents:
    raise SystemExit("Output must be a new directory inside this repository")
OUT.mkdir(parents=True, exist_ok=False)
BINARY = ROOT / ".build/debug/nativeui-audit"
env = dict(os.environ, TMPDIR=str(ROOT / ".build/debug-output"))
receipts = []


def run(name, args, stdin=None):
    start = time.monotonic()
    p = subprocess.run([str(BINARY), *args], input=stdin, text=True, capture_output=True,
                       timeout=90, cwd=ROOT, env=env)
    (OUT / (name + ".json")).write_text(p.stdout)
    (OUT / (name + ".stderr.log")).write_text(p.stderr)
    receipts.append({"name": name, "args": args, "exit": p.returncode,
                     "wallSeconds": time.monotonic()-start})
    (OUT / "commands.json").write_text(json.dumps(receipts, indent=2))
    return p


fixtures = ROOT / "Tests/NativeUIAuditKitTests/Fixtures"
batch = OUT / "inputs"
batch.mkdir()
membership = []
for dest, src in [("01-ios.png", "kitchen_sink_screen.png"),
                  ("02-ios-repeat.png", "kitchen_sink_screen.png"),
                  ("03-tvos.png", "tvos_home_screen.png")]:
    original = fixtures / src
    shutil.copyfile(original, batch / dest)
    membership.append({"file": dest, "source": str(original.relative_to(ROOT)),
                       "sha256": hashlib.sha256(original.read_bytes()).hexdigest()})
(batch / "04-corrupt.png").write_bytes(b"intentional corrupt input")
(OUT / "inputs.json").write_text(json.dumps(membership, indent=2))
doctor = run("doctor", ["doctor"])
assert doctor.returncode == 0, doctor.stderr
d = json.loads(doctor.stdout)
assert not d["inferencePerformed"]

result = run("batch", ["scan-batch", str(batch), "--root", str(ROOT), "--strict"])
report = json.loads(result.stdout)
assert result.returncode == 1 and report["count"] == 4, report
assert report["failed"] == 1, report
assert all(r["status"] in ("success", "degraded") for r in report["results"][:3]), report
assert [r["runtime"]["cacheState"] for r in report["results"][:3]] == ["cold", "warm", "cold"]

messages = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25", "capabilities": {},
        "clientInfo": {"name": "runtime-smoke", "version": "1"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "audit_screenshot", "arguments": {
            "imagePath": str(fixtures / "tvos_home_screen.png"), "platform": "tvOS"}}},
]
p = run("mcp", ["mcp", "--root", str(ROOT)], "\n".join(map(json.dumps, messages))+"\n")
assert p.returncode == 0, p.stderr
responses = [json.loads(line) for line in p.stdout.splitlines()]
assert len(responses) == 3
payload = responses[-1]["result"]["structuredContent"]
assert payload["status"] in ("success", "degraded"), payload
summary = {
    "binarySHA256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
    "host": subprocess.check_output(["sw_vers"], text=True).strip(),
    "batch": [{"file": Path(r["input"]).name, "status": r["status"],
               "cache": r.get("runtime", {}).get("cacheState"),
               "totalMs": r["totalMs"],
               "timings": r.get("runtime", {}).get("result", {}).get("timings"),
               "loadAndIdentityMs": r.get("runtime", {}).get("modelLoadMs"),
               "elements": len(r.get("runtime", {}).get("result", {}).get("elements", []))}
              for r in report["results"]],
    "mcpStatus": payload["status"], "mcpMs": payload["totalMs"],
    "qualification": "runtime smoke only; no accuracy or TTR deployment claim",
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
