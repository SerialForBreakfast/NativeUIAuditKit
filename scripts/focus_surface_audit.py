"""Byte/pixel overlap audit for frozen surface QA; no model or qualification bypass."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from focus_dataset_contract import ROOT, pixel_digest
from focus_mixed_assembly import reference, checked
from focus_surface_intake import fresh, write
from focus_surface_evaluation import seal_check


def overlap(samples, known):
    pixels = defaultdict(list)
    prior = []
    for row in samples:
        for kind, sha in (("frame", row["framePixelSHA256"]), ("crop", row["crop"]["pixelSHA256"])):
            pixels[sha].append({"id": row["id"], "group": row["group"], "role": row["role"],
                                "label": row["label"] if kind == "crop" else None, "kind": kind})
            if sha in known:
                prior.append({"id": row["id"], "kind": kind, "prior": sorted(known[sha])})
    cross = [{"pixelSHA256": sha, "members": members} for sha, members in pixels.items()
             if len({r["role"] for r in members}) > 1]
    contradictions = [{"pixelSHA256": sha, "members": members} for sha, members in pixels.items()
                      if len({r["label"] for r in members if r["kind"] == "crop"}) > 1]
    return {"priorOverlap": prior, "crossRolePixelGroups": cross, "contradictoryCropGroups": contradictions,
            "uniquePixels": len(pixels), "independenceEstablished": False}


def audit(crops_path, history, output):
    output = fresh(output); doc = json.loads(crops_path.read_text()); seal_check(doc)
    known = defaultdict(set); inventory = {}; refs = []
    def add(record, name):
        ref = {k: record[k] for k in ("path", "sha256")}
        checked(ref)
        if ref["path"] not in inventory:
            inventory[ref["path"]] = {**ref, "pixelSHA256": pixel_digest(ROOT, ref)}
        known[inventory[ref["path"]]["pixelSHA256"]].add(name)
    for path in history:
        ref = reference(path); refs.append(ref); raw = json.loads(checked(ref).read_text()); name = str(path)
        if "samples" in raw:
            seal_check(raw, "protocolSHA256")
            for row in raw["samples"]:
                for kind in ("frame", "crop"): add(row[kind], name)
        elif "remotesSamples" in raw:
            seal_check(raw, "auditSHA256")
            for row in raw["remotesSamples"]:
                for kind in ("frame", "crop"): add(row[kind], name)
            for visual in raw["visualDiagnostics"]:
                checked(visual["protocol"])
                for frame in visual["frames"]: add(frame, name)
        elif "pairs" in raw:
            # Legacy corpus pixels are audited, not relabeled or admitted.
            for pair in raw["pairs"]:
                for role in ("focused", "unfocused"):
                    add(reference(path.parent / pair[role + "_crop"]), name)
        else:
            raise ValueError("unsupported_history_inventory")
    for ref in refs: checked(ref)
    # Current raw frames/crops are checked separately from retained metadata hashes.
    for row in doc["samples"]:
        checked({k: row[k] for k in ("path", "sha256")})
        checked({k: row["crop"][k] for k in ("path", "sha256")})
    result = {"version": "surface-overlap-audit-v1", "crops": reference(crops_path), "history": refs,
              "priorInventory": list(inventory.values()), **overlap(doc["samples"], known),
              "support": {group: dict(Counter(r["stratum"] for r in doc["samples"]
                                             if r["group"] == group and r["kind"] == "pair" and r["label"] == 1))
                          for group in sorted({r["group"] for r in doc["samples"]})},
              "lineageBlockers": ["exact producer source revision unavailable locally; renderer/assets ancestry unreviewed",
                                  "all received groups and existing Fixture development share seed7; existing seed-edge policy retained",
                                  "Photos buttons absent; detail-action is Fixture-only; all supplied themes dark"],
              "finalChallengeScored": False}
    output.parent.mkdir(parents=True, exist_ok=True); write(output, result)
    print(json.dumps({"priorImages": len(inventory), "priorOverlap": len(result["priorOverlap"]),
                      "crossRolePixelGroups": len(result["crossRolePixelGroups"]),
                      "contradictoryCropGroups": len(result["contradictoryCropGroups"]), "support": result["support"]}))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crops", type=Path, required=True)
    parser.add_argument("--history", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try: audit(args.crops, args.history, args.output)
    except (ValueError, OSError, KeyError, TypeError) as error: parser.exit(2, str(error) + "\n")
