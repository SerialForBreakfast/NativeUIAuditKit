"""Bounded frozen-surface extraction/intake. No model loading or training admission."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile

from focus_dataset_contract import ROOT, FocusDataError, digest, local
from focus_mixed_assembly import reference
from harvest_bundle_validation import validate_bundle
from ttr_focus_manifest import bundle_identity, pairs_from_bundle

ROLES = {"cinema_rows": "appearance-validation", "album_grid": "appearance-validation",
         "memory_mosaic": "final-challenge", "icon_shelf": "final-challenge"}
FREEZE = "2026-09-26T03:10:28Z"


def require(ok, reason):
    if not ok:
        raise FocusDataError(reason)


def fresh(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink_output")
    path = local(path)
    require(not path.exists(), "output_collision")
    return path


def write(path, doc):
    with path.open("x") as stream:
        json.dump(doc, stream, indent=2, allow_nan=False)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_members(archive):
    members, seen, total = [], set(), 0
    for member in archive:
        require(len(members) < 1000, "archive_member_limit")
        name = PurePosixPath(member.name)
        require(not name.is_absolute() and name.parts and
                not any(p in {"..", "."} for p in name.parts) and
                "\\" not in member.name and "\0" not in member.name, "unsafe_archive_path")
        require(member.isfile() or member.isdir(), "unsafe_archive_type")
        key = str(name).casefold()
        require(key not in seen, "duplicate_archive_destination")
        seen.add(key)
        total += member.size
        require(0 <= member.size <= 32 * 1024 * 1024 and total <= 4_000_000_000,
                "archive_size_limit")
        members.append(member)
    return members, total


def extract(manifest_path, output):
    manifest_path, output = local(manifest_path), fresh(output)
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get("schema_version") == 1 and manifest.get("seed") == 7,
            "unsupported_transfer_manifest")
    entries = manifest["archives"]
    require(len(entries) == 4 and {e["group_id"] for e in entries} ==
            {"surface-v1." + k for k in ROLES}, "transfer_group_membership")
    inventory = []
    # Inspect all archives before creating the extraction tree.
    for entry in entries:
        require(Path(entry["name"]).name == entry["name"], "unsafe_archive_name")
        source = local(manifest_path.parent / entry["name"])
        require(not source.is_symlink() and source.stat().st_size == entry["bytes"]
                and sha(source) == entry["sha256"], "archive_integrity")
        group = entry["group_id"].removeprefix("surface-v1.")
        require(entry["role"] == ROLES[group], "changed_frozen_role")
        with tarfile.open(source) as archive:
            members, size = safe_members(archive)
            payload = [m for m in members if not PurePosixPath(m.name).name.startswith("._")]
            require(len(payload) == entry["entries"] and
                    all(PurePosixPath(m.name).parts[0] == group for m in payload), "archive_root_or_count")
        inventory.append({**entry, "expandedBytes": size, "totalMembers": len(members)})
    require(shutil.disk_usage(ROOT).free >= sum(e["expandedBytes"] for e in inventory) + 5_000_000_000,
            "insufficient_storage_reserve")
    output.mkdir(parents=True)
    for entry in inventory:
        source = manifest_path.parent / entry["name"]
        require(sha(source) == entry["sha256"], "changed_archive")
        with tarfile.open(source) as archive:
            members, _ = safe_members(archive)
            for member in members:
                if PurePosixPath(member.name).name.startswith("._"):
                    continue
                target = output / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source_stream, target.open("xb") as dest:
                        shutil.copyfileobj(source_stream, dest)
        require(sha(source) == entry["sha256"], "changed_archive_during_extraction")
    result = {"version": "surface-extraction-v1", "transfer": reference(manifest_path),
              "archives": inventory, "output": str(output.relative_to(ROOT))}
    write(output / "extraction.json", result)
    return result


def inspect_group(root, entry):
    """Validate raw export first; role normalization never changes raw split bytes."""
    group = entry["group_id"].removeprefix("surface-v1.")
    provenance = json.loads((root / "provenance.json").read_text())
    require(all(provenance.get(k) == entry[k] for k in ("group_id", "role", "job_id"))
            and provenance.get("seed") == 7 and provenance.get("frozen_by_nuiak_at") == FREEZE,
            "changed_provenance_role")
    bundle = root / "export"
    require(sha(bundle / "manifest.json") == entry["manifest_sha256"], "changed_export_manifest")
    contract = validate_bundle(bundle)
    require(contract["acceptedRowCount"] == entry["accepted_rows"]
            and len(contract["usableRows"]) == entry["accepted_rows"], "incomplete_intake")
    pairs = pairs_from_bundle(contract, entry["group_id"], provenance["source_revision"])
    for row in contract["usableRows"]:
        recipe = row["recipe"]
        require(recipe["surface"]["template"] == group and recipe["seed"] == 7
                and recipe["recipe_hash"] == provenance["canonical_recipe_sha256"], "changed_surface_recipe")
        scene = row["observationBinding"]["focusedScene"]
        ids = {e["element_id"] for e in scene["elements"]}
        require(ids == set(scene["focus_observation"]["plannedFocusIDs"])
                == set(scene["observation_diagnostics"]["requiredIDs"])
                and len(ids) == recipe["element_count"], "incomplete_candidate_set")
    # This is a prospective binding, not an independent source-admission assertion.
    inventory = {**bundle_identity(bundle, contract),
                 "manifest.json": sha(bundle / "manifest.json"),
                 "../provenance.json": sha(root / "provenance.json"),
                 "../recipe.json": sha(root / "recipe.json")}
    members = [{"id": p["pair_id"], "frames": p["frames"], "annotation": p["annotation"],
                "originalSplit": p["original_split"], "role": entry["role"]} for p in pairs]
    return {"group": group, "role": entry["role"], "sourceRoot": str(bundle.relative_to(ROOT)),
            "sourceRevision": provenance["source_revision"], "inventory": inventory,
            "membershipSHA256": digest(sorted(members, key=lambda r: r["id"])),
            "members": members, "pairs": pairs, "originalSplits": dict(Counter(p["original_split"] for p in pairs)),
            "independentEvaluationEligible": False,
            "blockers": ["source_relationship_review_unavailable", "same_seed_lineage_requires_source_review"],
            "reservationStatus": "role-and-membership-bound; independent-reservation-v2-admission-pending"}


def intake(extracted, output):
    extracted, output = local(extracted), fresh(output)
    extraction = json.loads((extracted / "extraction.json").read_text())
    output.mkdir(parents=True)
    groups, accounting = [], []
    for entry in extraction["archives"]:
        group = entry["group_id"].removeprefix("surface-v1.")
        try:
            result = inspect_group(extracted / group, entry)
            groups.append(result)
            accounting.extend({"group": group, "id": p["pair_id"], "state": "accepted-diagnostic-only",
                               "role": entry["role"]} for p in result["pairs"])
            write(output / (group + ".json"), result)
        except (ValueError, OSError, KeyError, TypeError) as error:
            raw = json.loads((extracted / group / "export/manifest.json").read_text())
            accounting.extend({"group": group, "id": row["id"], "state": "blocked",
                               "reason": str(error), "role": entry["role"]} for row in raw)
    result = {"version": "surface-intake-v1", "extraction": reference(extracted / "extraction.json"),
              "groups": [reference(output / (g["group"] + ".json")) for g in groups],
              "accounting": accounting, "counts": dict(Counter(r["state"] for r in accounting)),
              "expectedRows": sum(e["accepted_rows"] for e in extraction["archives"]),
              "finalChallengeScored": False, "independentEvaluationEligible": False}
    require(len(accounting) == result["expectedRows"], "row_accounting_mismatch")
    write(output / "intake.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("extract", "intake"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (extract if args.command == "extract" else intake)(args.input, args.output)
        print(json.dumps({k: result[k] for k in ("version", "counts", "expectedRows") if k in result}))
    except (ValueError, OSError, KeyError, TypeError, tarfile.TarError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
