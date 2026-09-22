"""One-shot evidence preparation; does not capture or train."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"scripts"))
from focus_learning_experiment import sha, rel

out = ROOT/"reports/work/OS-FOCUS-03"
review = out/"review.md"
def source(name, screen, split):
    path = out/name/"dataset/manifest.json"
    return {"screenID": screen, "split": split,
            "manifest": {"path": rel(path), "sha256": sha(path)},
            "review": {"path": rel(review), "sha256": sha(review)}}
records = json.loads((ROOT/"reports/work/FOCUS-EXP-01/sources.json").read_text())
records.append(source("apps-01", "settings/apps", "train"))
for name, value in [("sources.json", records), ("challenge.json", source("remotes-01", "settings/remotes", "challenge"))]:
    with (out/name).open("x") as stream:
        json.dump(value, stream, indent=2)
