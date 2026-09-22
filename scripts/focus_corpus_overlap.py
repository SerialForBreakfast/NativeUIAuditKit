"""Read-only cross-producer partition audit for qualified FocusRing manifests."""
import argparse
import json
import sys
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, pixel_digest, validate_manifest


def record_owner(owners, key, split, source, overlaps):
    previous = owners.get(key)
    if previous is not None:
        if previous[0] != split:
            raise FocusDataError("cross_corpus_split_leakage: " + repr(key))
        if previous[1] != source:
            overlaps.add((previous[1], source, key[0]))
    else:
        owners[key] = (split, source)


def audit(paths):
    owners, overlaps, inputs = {}, set(), []
    for source, path in enumerate(paths):
        doc = json.loads(path.read_text())
        rows = validate_manifest(doc, path.parent)
        inputs.append({"manifestSHA256": digest(doc), "sourceKind": doc["sourceKind"], "pairs": len(rows)})
        for row, pair in zip(rows, doc["pairs"]):
            keys = [("seed", row["seed"]), ("group", row["recipeGroup"])]
            for role in ("focused", "unfocused"):
                raw = pair["frames"][role]
                crop = {"path": pair[role+"_crop"], "sha256": pair[role+"_crop_sha256"]}
                keys.extend(("pixels", pixel_digest(root, image)) for root, image in
                            ((ROOT/doc["sourceRoot"], raw), (path.parent, crop)))
            for key in keys: record_owner(owners, key, row["split"], source, overlaps)
    return {"version": "focus-corpus-overlap-v1", "inputs": inputs, "crossPartitionLeakage": False,
            "samePartitionOverlaps": [list(x) for x in sorted(overlaps)],
            "note": "Same-partition overlaps are related evidence, not independent samples; no files modified."}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("manifests", nargs="+", type=Path)
    args = p.parse_args()
    try: print(json.dumps(audit(args.manifests), indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError) as error: print(str(error), file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
