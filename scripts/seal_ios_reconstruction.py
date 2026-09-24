"""Seal a retrieved r6 corpus without modifying pixels, annotations or source staging."""
import argparse
import json
from pathlib import Path
import time

import corpus_retention as retention
import validate_reconstructed_corpus as v


def preserve_prefix(inventory, prefix, corpus):
    """Metadata may extend; every original paired/rejected byte must remain identical."""
    retention.verify(inventory, prefix)
    for member in retention.check_inventory(inventory):
        if member["path"] in {"manifest.json", "capture-ledger.json", "balance_report.md"}:
            continue
        p = v.member(corpus, member["path"])
        v.require(p.stat().st_size == member["bytes"] and v.sha256(p) == member["sha256"],
                  "prefix_byte_changed:" + member["path"])
    old = v.read_json(prefix / "manifest.json")["entries"]
    new = v.read_json(corpus / "manifest.json")["entries"]
    keyed = {m["fileName"]: m for m in new}
    v.require(len(keyed) == len(new), "duplicate_manifest_member")
    v.require(all(keyed.get(m["fileName"]) == m for m in old), "prefix_manifest_lineage_changed")
    previous = v.read_json(prefix / "capture-ledger.json")
    current = v.read_json(corpus / "capture-ledger.json")
    v.require(all(current["accepted"].get(k) == value for k, value in previous["accepted"].items()),
              "prefix_ledger_changed")
    rejections = {r["entry"]["fileName"]: r for r in current["rejected"]}
    v.require(all(rejections.get(r["entry"]["fileName"]) == r for r in previous["rejected"]),
              "prefix_rejection_changed")
    return {"prefixImagesPreserved": len(old), "pairedAndRejectedBytesPreserved": True,
            "prefixInventorySHA256": inventory["inventorySHA256"],
            "manifestAndLedgerExtendWithoutRewritingPriorMembership": True}


def write(path, value):
    with path.open("x") as out:
        json.dump(value, out, indent=2, sort_keys=True)


def verify_audited_content(audit, corpus):
    """Reuse decoding only when every audited byte and the auditor identities match.

    Finder metadata is explicitly auxiliary. Other unindexed members still fail.
    The original strict audit is never rewritten to imply it passed.
    """
    errors = audit["errors"]
    v.require(not errors or (len(errors) == 1 and errors[0]["error"] == "unindexed_members"
              and bool(errors[0]["members"]) and all(Path(p).name == ".DS_Store"
              for p in errors[0]["members"])), "non_auxiliary_audit_failure")
    v.require(audit["validatorSHA256"] == v.sha256(Path(v.__file__))
              and audit["schemaSHA256"] == v.sha256(v.SCHEMA)
              and audit["generatorSHA256"] == v.sha256(v.GENERATOR)
              and audit["manifestSHA256"] == v.sha256(corpus / "manifest.json")
              and audit["captureLedgerSHA256"] == v.sha256(corpus / "capture-ledger.json"),
              "audit_identity_changed")
    members = audit["members"]
    v.require(len(members) == audit["manifestEntries"] and all(m["valid"] for m in members)
              and len({m["path"] for m in members}) == len(members), "invalid_audited_membership")
    inventory = retention.inventory(corpus, exclude_finder_metadata=True)
    observed = {m["path"]: m["sha256"] for m in inventory["members"]}
    expected = {"manifest.json", "capture-ledger.json"}
    if "balance_report.md" in observed:
        expected.add("balance_report.md")
    for row in members + audit["rejectedDuplicates"]:
        image, annotation = row["path"], str(Path(row["path"]).with_suffix(".json"))
        v.require(observed.get(image) == row["imageSHA256"] and
                  observed.get(annotation) == row["annotationSHA256"], "audited_bytes_changed")
        expected.update((image, annotation))
    v.require(set(observed) == expected, "audited_membership_changed")
    return inventory


def seal(work, output, validated_report=None):
    work = retention.directory(work)
    output = retention.new_local(output)
    plan = v.read_json(work / "plan.json")
    corpus = retention.directory(plan["destination"])
    prefix = retention.directory(plan["prefix"])
    v.require(not output.is_relative_to(corpus) and not output.is_relative_to(prefix), "report_inside_corpus")
    retrieval = v.read_json(work / "retrieval.json")
    v.require(retrieval["destination"] == str(corpus) and
              retrieval["cleanup"] == "no_status_overrides_created; test_window_cleanup_completed",
              "cleanup_or_retrieval_unresolved")
    generation = v.read_json(work / "generate-result.json")
    v.require(generation.get("exitCode") == 0 and not generation.get("timeout"), "generation_incomplete")
    output.mkdir(parents=True)
    started = time.monotonic()
    audit = v.read_json(validated_report) if validated_report else v.validate(corpus)
    write(output / "validation.json", audit)
    inventory = verify_audited_content(audit, corpus)
    v.require(audit["manifestEntries"] == 16940 and
              audit["splitCounts"] == v.EXPECTED, "corpus_not_complete_or_valid")
    lineage = preserve_prefix(v.read_json(work / "prefix-inventory.json"), prefix, corpus)
    lineage.update({"sourcePlanSHA256": v.sha256(work / "plan.json"),
        "buildIdentitySHA256": v.sha256(work / "build-identity.json"),
        "nativeResultSHA256": v.sha256(work / "generate-result.json"),
        "retrievalSHA256": v.sha256(work / "retrieval.json"),
        "prefixBuildLineage": "retained r4/r5 completed batches; see P0-C/resumption-20260922.md",
        "newMembers": 2600, "sameVolumeOnly": True})
    write(output / "lineage.json", lineage)
    write(output / "inventory.json", inventory)
    verification = retention.verify(inventory, corpus)
    write(output / "readback.json", verification)
    result = {"version": "ios-r6-seal-v1", "manifestSHA256": audit["manifestSHA256"],
        "membershipSHA256": audit["membershipSHA256"], "inventorySHA256": inventory["inventorySHA256"],
        "splitCounts": audit["splitCounts"], "decodedDuplicateGroups": len(audit["decodedDuplicateGroups"]),
        "crossSplitPixelGroups": len(audit["crossSplitPixelGroups"]),
        "rejectedTrialsPreserved": audit["rejectedDuplicateCount"],
        "missingVisibleClasses": audit["missingVisibleClasses"],
        "validationSeconds": time.monotonic() - started,
        "structuralValidity": "passed", "semanticReview": "not_comprehensive",
        "strictDirectoryAuditPassed": audit["integrityValid"],
        "excludedAuxiliaryNames": inventory["excludedAuxiliaryNames"],
        "excludedPathsAtInventory": inventory["excludedPathsAtInventory"],
        "validationSHA256": v.sha256(output / "validation.json"),
        "trainingEligible": False, "modelGatePassed": "not_assessed",
        "independentBackupVerified": False, "retentionOwner": "maintainer",
        "retentionInstruction": "Preserve corpus, raw simulator staging, prefix and execution artifacts. Do not clean .build; independent backup destination still unassigned.",
        "next": "Separately authorize Run009 evaluation; unsupported-class AP remains unavailable, not zero."}
    write(output / "seal.json", result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--validated-report", type=Path,
                   help="Reuse a prior full audit only after identity, membership and every byte reverify")
    args = p.parse_args()
    print(json.dumps(seal(args.work, args.output, args.validated_report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
