"""Freeze the human-reviewed dispositions; does not admit or repartition data."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

review_path = HERE / "audit/review.json"
review = json.loads(review_path.read_text())
assert review["reviewSHA256"] == digest({k:v for k,v in review.items() if k != "reviewSHA256"})
seen = {}
rows = []
for pair in sorted(review["pairs"], key=lambda p: (p["catalogIndex"], p["elementID"], p["pairID"])):
    row = {k:pair[k] for k in ("pairID", "catalogIndex", "family", "theme", "seed", "edgeFlags")}
    if pair["family"] == "focusMaze":
        row.update(disposition="excluded-first-experiment", reason="family viewport-clipping/context review unresolved",
                   visualReview="edge-pair-reviewed" if pair["edgeFlags"] else "not-individually-reviewed")
    else:
        key = tuple(pair[r]["cropPixelSHA256"] for r in ("focused", "unfocused"))
        row["visualReview"] = "both-production-crops-reviewed"
        if key in seen:
            row.update(disposition="duplicate-pair", representative=seen[key])
        else:
            seen[key] = pair["pairID"]
            row.update(disposition="reviewed-development-candidate")
    rows.append(row)
counts = dict(Counter(r["disposition"] for r in rows))
assert counts == {"reviewed-development-candidate":86, "duplicate-pair":4, "excluded-first-experiment":48}
doc = {"version":"focus-retained-dispositions-v1", "reviewSHA256":review["reviewSHA256"],
       "reviewFileSHA256":hashlib.sha256(review_path.read_bytes()).hexdigest(),
       "trainingEligible":False, "fullPilotComplete":False,
       "seedComponents":[[7,19]], "counts":counts, "pairs":rows,
       "reviewScope":"180 non-maze crops plus 12 maze-edge crops; all 276 crops automatically validated",
       "limitations":["No authenticated or atomic frame identity claim", "No independent Fixture validation partition",
                      "Failed source receipts remain failed; no capture completion or data admission is created"]}
doc["dispositionsSHA256"] = digest(doc)
out = HERE / "dispositions.json"
with out.open("x") as f:
    json.dump(doc,f,indent=2,allow_nan=False)
print(json.dumps({"counts":counts,"dispositionsSHA256":doc["dispositionsSHA256"]}))
