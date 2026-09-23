"""Content-sealed corpus inventory, copy verification and local recovery drill.

No source mutation, external copy, deletion, training or qualification is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from validate_reconstructed_corpus import ROOT, read_json, require, sha256

VERSION = "corpus-retention-v1"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def directory(path):
    path = Path(path).absolute()
    require(path.resolve() == path and path.is_dir(), "unsafe_or_missing_directory")
    return path


def new_local(path):
    path = Path(path).absolute()
    require(path.resolve() == path and path.is_relative_to(ROOT) and not path.exists(),
            "output_boundary_or_collision")
    return path


def files(root, excluded=()):
    result = []
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "symlink_dependency:" + str(path.relative_to(root)))
        if path.is_dir():
            continue
        require(path.is_file(), "nonregular_member")
        if path.name in excluded:
            continue
        result.append(path)
    require(bool(result), "empty_corpus")
    return result


def inventory(source, exclude_finder_metadata=False):
    source = directory(source)
    require(source.is_relative_to(ROOT), "source_outside_project")
    excluded = [".DS_Store"] if exclude_finder_metadata else []
    paths = files(source, excluded)
    members = [{"path": str(p.relative_to(source)), "bytes": p.stat().st_size,
                "sha256": sha256(p)} for p in paths]
    require(paths == files(source, excluded), "membership_changed_during_inventory")
    doc = {"version": VERSION, "source": str(source.relative_to(ROOT)),
           "members": members, "fileCount": len(members),
           "totalBytes": sum(m["bytes"] for m in members),
           "independentBackupVerified": False,
           "excludedAuxiliaryNames": excluded,
           "excludedPathsAtInventory": sorted(str(p.relative_to(source)) for p in source.rglob(".DS_Store")) if excluded else []}
    doc["inventorySHA256"] = digest(doc)
    return doc


def check_inventory(doc):
    require(isinstance(doc, dict) and doc.get("version") == VERSION,
            "unsupported_inventory")
    require(doc.get("inventorySHA256") == digest({k:v for k,v in doc.items()
                                                   if k != "inventorySHA256"}),
            "changed_inventory")
    members = doc.get("members")
    require(doc.get("excludedAuxiliaryNames", []) in ([], [".DS_Store"]),
            "unsupported_auxiliary_exclusion")
    require(isinstance(members, list) and bool(members), "empty_inventory")
    names = set()
    for m in members:
        require(isinstance(m, dict), "invalid_member")
        name = m.get("path")
        require(isinstance(name, str) and name and not Path(name).is_absolute()
                and ".." not in Path(name).parts and str(Path(name)) == name
                and name not in names, "unsafe_or_duplicate_member")
        names.add(name)
        require(Path(name).name not in doc.get("excludedAuxiliaryNames", []),
                "excluded_member_in_inventory")
        require(type(m.get("bytes")) is int and m["bytes"] >= 0,
                "invalid_member_size")
        h = m.get("sha256")
        require(isinstance(h, str) and len(h) == 64
                and all(c in "0123456789abcdef" for c in h), "invalid_member_hash")
    require(type(doc.get("fileCount")) is int and type(doc.get("totalBytes")) is int
            and doc["fileCount"] == len(members)
            and doc["totalBytes"] == sum(m["bytes"] for m in members),
            "inventory_counts")
    return members


def verify(doc, copy_root):
    members = check_inventory(doc)
    root = directory(copy_root)
    excluded = doc.get("excludedAuxiliaryNames", [])
    observed = {str(p.relative_to(root)) for p in files(root, excluded)}
    expected = {m["path"] for m in members}
    require(observed == expected, "copy_membership_mismatch")
    for m in members:
        p = root / m["path"]
        require(p.resolve() == p and p.is_file(), "unsafe_or_missing_member")
        require(p.stat().st_size == m["bytes"] and sha256(p) == m["sha256"],
                "copy_hash_mismatch:" + m["path"])
    require({str(p.relative_to(root)) for p in files(root, excluded)} == expected,
            "membership_changed_during_verification")
    return {"inventorySHA256": doc["inventorySHA256"], "verifiedFiles": len(members),
            "verifiedBytes": doc["totalBytes"], "contentVerified": True,
            "independentBackupVerified": False,
            "excludedAuxiliaryNames": excluded,
            "scope": "byte-equivalence only; storage independence and corpus eligibility not established"}


def restore(doc, copy_root, output):
    root = directory(copy_root)
    out = new_local(output)
    require(not out.is_relative_to(root) and not root.is_relative_to(out),
            "overlapping_restore_source")
    try:
        verify(doc, root)
    except (ValueError, OSError) as error:
        raise ValueError("restore_preflight:" + str(error)) from error
    out.mkdir(parents=True, exist_ok=False)
    for m in doc["members"]:
        src, dst = root / m["path"], out / m["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive output; any interrupted/changed-source copy remains visible for diagnosis.
        with src.open("rb") as incoming, dst.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(sha256(src) == m["sha256"] and sha256(dst) == m["sha256"],
                "source_or_copy_changed:" + m["path"])
    try:
        result = verify(doc, out)
    except (ValueError, OSError) as error:
        raise ValueError("restore_postflight:" + str(error)) from error
    result["restoredTo"] = str(out.relative_to(ROOT))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("--source", type=Path, required=True)
    inv.add_argument("--output", type=Path, required=True)
    inv.add_argument("--exclude-finder-metadata", action="store_true",
                     help="Explicitly exclude only .DS_Store; record exclusions; never ignore corpus files")
    for name in ("verify", "restore"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--inventory", type=Path, required=True)
        cmd.add_argument("--copy", type=Path, required=True)
        if name == "restore":
            cmd.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.command == "inventory":
            out = new_local(args.output)
            source = directory(args.source)
            require(not out.is_relative_to(source), "inventory_inside_source")
            doc = inventory(source, args.exclude_finder_metadata)
            # Verify bytes a second time before publishing a reusable inventory.
            verify(doc, source)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("x") as f:
                json.dump(doc, f, indent=2, allow_nan=False)
            result = {k:doc[k] for k in ("inventorySHA256", "fileCount", "totalBytes")}
        else:
            doc = read_json(args.inventory)
            result = verify(doc, args.copy) if args.command == "verify" else restore(doc, args.copy, args.output)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"success": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
