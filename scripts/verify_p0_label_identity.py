#!/usr/bin/env python3
"""Create append-only P0-A label identity evidence from existing manifests.

This diagnostic reads only manifest-listed labels. It neither resolves image
symlinks nor changes labels, images, manifests, caches, or historical reports.
Its outputs are new files below ``reports/work/P0-A`` and it refuses reuse.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
YOLO_ROOT = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
OUTPUT_ROOT = PROJECT_ROOT / "reports" / "work" / "P0-A"
MANIFESTS = {split: YOLO_ROOT / f"{split}.txt" for split in ("train", "val", "test")}


class VerificationError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def label_for_manifest_image(image: Path, verified_roots: dict[Path, Path]) -> Path:
    root = image.parent.parent / "labels"
    try:
        if root not in verified_roots:
            resolved_root = root.resolve(strict=True)
            resolved_root.relative_to(PROJECT_ROOT.resolve())
            if not resolved_root.is_dir():
                raise VerificationError(f"label root is not a directory: {root}")
            verified_roots[root] = resolved_root
    except (OSError, ValueError) as error:
        raise VerificationError(f"label root outside project or missing: {root}") from error
    label = verified_roots[root] / f"{image.stem}.txt"
    if not label.is_file():
        raise VerificationError(f"label is not a regular file: {label}")
    return label


def manifest_members() -> list[tuple[str, int, Path]]:
    members: list[tuple[str, int, Path]] = []
    for split, manifest in MANIFESTS.items():
        if not manifest.is_file():
            raise VerificationError(f"missing manifest: {manifest}")
        for line_number, value in enumerate(manifest.read_text().splitlines(), 1):
            raw = value.strip()
            if raw:
                members.append((split, line_number, Path(raw)))
    return members


def collect(members: list[tuple[str, int, Path]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    split_counts: dict[str, int] = {}
    verified_roots: dict[Path, Path] = {}
    for split, line_number, image in members:
        count = 0
        label = label_for_manifest_image(image, verified_roots)
        rows.append(
            {
                "split": split,
                "manifestLine": line_number,
                "imageID": image.stem,
                "labelPath": repo_relative(label),
                "labelSizeBytes": label.stat().st_size,
                "labelSHA256": sha256_file(label),
            }
        )
        split_counts[split] = split_counts.get(split, 0) + 1
    identities = [(row["split"], row["imageID"], row["labelSHA256"]) for row in rows]
    if len({(row["split"], row["imageID"]) for row in rows}) != len(rows):
        raise VerificationError("duplicate split/image identifier")
    canonical = json.dumps(sorted(identities), separators=(",", ":")).encode()
    return rows, {
        "formatVersion": "p0-label-identity-v1",
        "manifestHashes": {split: sha256_file(path) for split, path in MANIFESTS.items()},
        "splitCounts": split_counts,
        "totalLabels": len(rows),
        "canonicalLabelIdentitySHA256": hashlib.sha256(canonical).hexdigest(),
    }


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("x") as output:
        for row in rows:
            output.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-start", type=int)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    if args.finalize == (args.chunk_start is not None):
        raise VerificationError("select exactly one of --finalize or --chunk-start")
    if args.chunk_size <= 0:
        raise VerificationError("chunk size must be positive")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows_path = OUTPUT_ROOT / "label_identity.jsonl"
    summary_path = OUTPUT_ROOT / "label_identity_summary.json"
    members = manifest_members()
    if not args.finalize:
        if args.chunk_start < 0 or args.chunk_start >= len(members):
            raise VerificationError("chunk start outside manifest")
        chunk_path = OUTPUT_ROOT / f"label_identity_chunk_{args.chunk_start:05d}.jsonl"
        if chunk_path.exists():
            raise VerificationError("refusing to overwrite P0-A identity chunk")
        rows, summary = collect(members[args.chunk_start:args.chunk_start + args.chunk_size])
        write_rows(chunk_path, rows)
        print(json.dumps({"chunk": repo_relative(chunk_path), "rows": len(rows), "totalManifestMembers": len(members), "splitCounts": summary["splitCounts"]}, sort_keys=True))
        return 0
    if rows_path.exists() or summary_path.exists():
        raise VerificationError("refusing to overwrite P0-A identity evidence")
    rows = []
    for chunk_path in sorted(OUTPUT_ROOT.glob("label_identity_chunk_*.jsonl")):
        rows.extend(json.loads(line) for line in chunk_path.read_text().splitlines() if line)
    expected = {(split, line, image.stem) for split, line, image in members}
    unique: dict[tuple[object, object, object], dict[str, object]] = {}
    duplicate_chunk_rows = 0
    for row in rows:
        key = (row["split"], row["manifestLine"], row["imageID"])
        prior = unique.get(key)
        if prior is not None:
            if prior != row:
                raise VerificationError("conflicting duplicate chunk evidence")
            duplicate_chunk_rows += 1
        else:
            unique[key] = row
    if expected != set(unique):
        raise VerificationError("incomplete chunk evidence")
    rows = [unique[key] for key in sorted(unique)]
    _, summary = collect([])
    summary["splitCounts"] = {split: sum(1 for row in rows if row["split"] == split) for split in MANIFESTS}
    summary["totalLabels"] = len(rows)
    summary["duplicateChunkRowsValidated"] = duplicate_chunk_rows
    identities = [(row["split"], row["imageID"], row["labelSHA256"]) for row in rows]
    summary["canonicalLabelIdentitySHA256"] = hashlib.sha256(json.dumps(sorted(identities), separators=(",", ":")).encode()).hexdigest()
    write_rows(rows_path, rows)
    with summary_path.open("x") as output:
        json.dump(summary, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
