"""Reproduce final PER-02/05/06 CLI reports on explicitly synthetic evidence.

PER-04's completed-bundle → crop → baseline path is exercised in the separately
logged physical integration suite, not faked by a shared report wrapper.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"scripts"))
from generate_identity_fixture import corpus, policy
from generate_transition_fixture import generate
from test_perception_benchmark import case, predictions
from test_perception_completion import observations

out = Path(__file__).resolve().parent
work = ROOT/".build/debug-output/perception-acceptance/replay"
work.mkdir(exist_ok=False)
for name, value in (("perception", {"formatVersion":"perception-benchmark-v1","cases":[case()]}),
                    ("predictions",predictions()),("observations",observations()),
                    ("identity",corpus()),("identity-policy",policy())):
    (work/f"{name}.json").write_text(json.dumps(value,sort_keys=True))
transitions = generate(work/"transitions")
commands = [
    ["perception_benchmark.py", "--manifest",work/"perception.json","--predictions",work/"predictions.json",
     "--observations",work/"observations.json","--output",out/"perception-replay.json"],
    ["transition_benchmark.py","--manifest",transitions/"manifest.json","--policy",transitions/"policy.json",
     "--output",out/"transition-replay.json"],
    ["identity_benchmark.py","--manifest",work/"identity.json","--policy",work/"identity-policy.json",
     "--output",out/"identity-replay.json"],
]
for command in commands:
    subprocess.run([sys.executable,str(ROOT/"scripts"/command[0]), *map(str,command[1:])],
                   cwd=ROOT, env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},check=True)
