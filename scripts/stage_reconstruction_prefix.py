#!/usr/bin/env python3
"""Copy verified manifested members to NEW local continuation staging; never resume a simulator."""
import argparse
import json
from pathlib import Path
import shutil

import validate_reconstructed_corpus as v


def new_output(path):
    path = Path(path).absolute()
    v.require(path.resolve() == path and path.is_relative_to(v.ROOT) and not path.exists(),
              "output_boundary_or_collision")
    return path


def stage(source, output):
    source = Path(source).absolute()
    output = new_output(output)
    v.require(not output.is_relative_to(source), "output_inside_source")
    audit = v.validate(source)
    for error in audit["errors"]:
        kind = error["error"]
        v.require(kind.startswith("membership_count:") or kind in (
            "capture_ledger:capture_ledger_membership", "unindexed_members"),
            "source_not_a_valid_manifested_prefix:" + kind)
    v.require(all(row["valid"] for row in audit["members"]), "invalid_source_member")
    v.require(not audit["decodedDuplicateGroups"], "duplicate_source_members")
    ledger_path = v.member(source, "capture-ledger.json")
    ledger = v.read_json(ledger_path)
    v.require(ledger.get("version") == 1 and type(ledger.get("accepted")) is dict
              and type(ledger.get("rejected")) is list, "unsupported_source_ledger")
    names = {row["path"] for row in audit["members"]}
    accepted = {key: name for key, name in ledger["accepted"].items() if name in names}
    v.require(len(accepted) == len(names) and set(accepted.values()) == names,
              "source_ledger_missing_manifested_members")
    kept = [row for row in ledger["rejected"] if row["duplicateOf"] in names]
    omitted = [row["entry"]["fileName"] for row in ledger["rejected"] if row["duplicateOf"] not in names]
    output.mkdir(parents=True)
    paths = {"manifest.json"}
    for name in names | {row["entry"]["fileName"] for row in kept}:
        paths.update((name, str(Path(name).with_suffix(".json"))))
    for name in sorted(paths):
        src = v.member(source, name)
        dst = output / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation: preserve partial staging if a collision/error occurs.
        with src.open("rb") as incoming, dst.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        v.require(v.sha256(src) == v.sha256(dst), "copy_hash_mismatch:" + name)
    with (output / "capture-ledger.json").open("x") as stream:
        json.dump({"version": 1, "accepted": accepted, "rejected": kept}, stream, sort_keys=True)
    expected = {split: audit["splitCounts"].get(split, 0) for split in v.EXPECTED}
    result = v.validate(output, expected)
    v.require(result["integrityValid"], "staged_prefix_invalid:" + str(result["errors"]))
    v.require(result["manifestSHA256"] == audit["manifestSHA256"]
              and result["membershipSHA256"] == audit["membershipSHA256"], "prefix_membership_changed")
    v.require(v.sha256(source / "manifest.json") == audit["manifestSHA256"]
              and v.sha256(ledger_path) == audit["captureLedgerSHA256"], "source_changed_during_staging")
    return {
        "purpose": "verified-partial-continuation-staging-not-a-completed-corpus",
        "source": str(source.relative_to(v.ROOT)), "output": str(output.relative_to(v.ROOT)),
        "sourceManifestSHA256": audit["manifestSHA256"],
        "sourceLedgerSHA256": audit["captureLedgerSHA256"],
        "sourceErrors": audit["errors"],
        "omittedUncommittedAcceptedPaths": sorted(set(ledger["accepted"].values()) - names),
        "omittedRejectionPaths": omitted,
        "fullRequiredCountsUnchanged": v.EXPECTED,
        "simulatorExecution": "not_performed", "trainingEligible": False,
        "validation": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report_path = new_output(args.report)
        v.require(not report_path.is_relative_to(args.source.absolute())
                  and not report_path.is_relative_to(args.output.absolute()), "report_inside_corpus")
        report = stage(args.source, args.output)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x") as stream:
            json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        print(json.dumps({"verifiedPrefix": report["validation"]["manifestEntries"],
                          "completeCorpus": False, "trainingEligible": False}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
