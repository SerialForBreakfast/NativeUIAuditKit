#!/usr/bin/env python3
"""Bounded, read-only assessment of the Phase 6a image corpus.

This is P0-A from Research/DatasetRecoveryPlan.md. It reads the existing YOLO
manifests and labels, checks only documented source roots, and writes additive
evidence under reports/work/P0/. It never relinks, copies, deletes, or rewrites
dataset files or historical reports.

The manifest is the authority for membership. Do not replace the manifest with
a directory scan: the source directories are large on APFS and the exported
image paths may be symlinks (BP-34/BP-52).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
YOLO_ROOT = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
REPORTS_ROOT = PROJECT_ROOT / "reports"
OUT_ROOT = REPORTS_ROOT / "work" / "P0"
SOURCE_ROOT = PROJECT_ROOT / "dataset" / "dataset"
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"
EXPORT_REPORT = YOLO_ROOT / "export_report.json"
HISTORICAL_EVAL = REPORTS_ROOT / "eval_results_phase6a.json"
CHECKPOINT = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6a_r009" / "weights" / "best.pt"

MANIFESTS = {
    "train": YOLO_ROOT / "train.txt",
    "val": YOLO_ROOT / "val.txt",
    "test": YOLO_ROOT / "test.txt",
}

TEXT_SUFFIXES = {
    ".md",
    ".json",
    ".txt",
    ".py",
    ".swift",
    ".yaml",
    ".yml",
    ".toml",
    ".plist",
    ".gitignore",
}
SEARCH_TERMS = (
    "NativeUIAuditKit-Dataset",
    "dataset/dataset",
    "backup",
    "archive",
    "relocat",
    "cleanup",
    "deleted",
    "removed",
    "img_001801",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_info(path: Path) -> dict[str, Any] | None:
    """Read file size/hash and PNG dimensions with one open per file."""
    try:
        with path.open("rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            prefix = handle.read(24)
            digest = hashlib.sha256(prefix)
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except (OSError, ValueError):
        return None

    dimensions = None
    if prefix[:8] == b"\x89PNG\r\n\x1a\n" and prefix[12:16] == b"IHDR":
        width = int.from_bytes(prefix[16:20], "big")
        height = int.from_bytes(prefix[20:24], "big")
        if width > 0 and height > 0:
            dimensions = [width, height]
    return {"sizeBytes": size, "sha256": digest.hexdigest(), "pngDimensions": dimensions}


def repo_path(path: Path) -> str:
    try:
        # Preserve symlink paths in the inventory. Resolving here would replace
        # the manifest's exported image path with its (possibly missing) target.
        absolute = Path(os.path.abspath(path))
        return str(absolute.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def json_hash(path: Path) -> str | None:
    return sha256_file(path)


def label_cache_hash(split: str) -> str | None:
    """Read the surviving Ultralytics cache identity without opening each label."""
    cache = YOLO_ROOT / split / "labels.cache"
    try:
        payload = cache.read_bytes()
    except OSError:
        return None
    match = re.search(rb"hash.{0,256}?([0-9a-f]{64})", payload, flags=re.DOTALL)
    return match.group(1).decode("ascii") if match else None


def png_dimensions(path: Path) -> list[int] | None:
    info = file_info(path)
    return info["pngDimensions"] if info else None


def read_manifest(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def git_output(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def source_candidates() -> list[dict[str, Any]]:
    export_source: Path | None = None
    try:
        export_source = Path(json.loads(EXPORT_REPORT.read_text()).get("source", "")).expanduser()
    except (OSError, json.JSONDecodeError, TypeError):
        pass

    # These are exact paths documented by the exporter/provenance. This is
    # intentionally not a recursive home-directory or volume search.
    candidates: list[tuple[str, Path]] = []
    if export_source:
        candidates.append(("export_report.source", export_source))
    candidates.extend(
        [
            ("in_repo_dataset_root", SOURCE_ROOT),
            ("in_repo_dataset_parent", PROJECT_ROOT / "dataset"),
            ("trainer_source_dataset", PROJECT_ROOT / "NativeUITrainer" / "source_dataset"),
            ("documented_sibling_dataset", PROJECT_ROOT.parent / "NativeUIAuditKit-Dataset"),
            ("documented_home_dataset", Path.home() / "NativeUIAuditKit-Dataset"),
        ]
    )

    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for name, root in candidates:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        result.append({"name": name, "path": repo_path(root), "exists": root.exists(), "is_dir": root.is_dir()})
    return result


def search_checked_in_evidence() -> list[dict[str, Any]]:
    tracked = [Path(p) for p in git_output("ls-files").splitlines() if p]
    explicit = [
        Path("Research/DatasetRecoveryPlan.md"),
        Path("Research/ImplementationPlans.md"),
        Path("Research/WorkerWorkflow.md"),
        Path("Research/WorkerKnowledge.md"),
        Path("reports/dataset_availability_2026-09-19.md"),
    ]
    paths = sorted({p for p in tracked + explicit if (PROJECT_ROOT / p).is_file()})
    matches: list[dict[str, Any]] = []
    pattern = re.compile("|".join(re.escape(term) for term in SEARCH_TERMS), re.IGNORECASE)
    for relative in paths:
        absolute = PROJECT_ROOT / relative
        if absolute.stat().st_size > 5 * 1024 * 1024:
            continue
        try:
            lines = absolute.read_text(errors="replace").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            if not pattern.search(line):
                continue
            matches.append(
                {
                    "file": str(relative),
                    "line": line_number,
                    "text": line[:400],
                }
            )
    return matches


def inventory_entries() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    split_counts: dict[str, Counter[str]] = {}
    target_rel_counts: Counter[str] = Counter()
    target_paths: dict[str, Path] = {}
    raw_records: list[dict[str, Any]] = []

    for split, manifest in MANIFESTS.items():
        rows = read_manifest(manifest)
        counters: Counter[str] = Counter()
        split_counts[split] = counters
        seen_paths: set[str] = set()
        seen_stems: set[str] = set()
        for line_number, raw_path in enumerate(rows, 1):
            image = Path(raw_path).expanduser()
            # Resolve labels beside the manifest-listed image tree. The main
            # export uses <split>/images + <split>/labels, while the surviving
            # batch_6a8 entries use their own sibling split directories.
            label = image.parent.parent / "labels" / f"{image.stem}.txt"
            is_link = image.is_symlink()
            link_target = os.readlink(image) if is_link else None
            resolved_target = (image.parent / link_target).resolve(strict=False) if link_target else image
            target_rel: str | None
            try:
                target_rel = str(resolved_target.relative_to(SOURCE_ROOT.resolve(strict=False)))
            except ValueError:
                target_rel = None

            if str(image) in seen_paths:
                counters["duplicate_manifest_path"] += 1
            if image.stem in seen_stems:
                counters["duplicate_stem"] += 1
            seen_paths.add(str(image))
            seen_stems.add(image.stem)

            if target_rel:
                target_rel_counts[target_rel] += 1
                target_paths[target_rel] = resolved_target

            image_info = file_info(image)
            raw_records.append(
                {
                    "split": split,
                    "manifestLine": line_number,
                    "image": image,
                    "imageStem": image.stem,
                    "isSymlink": is_link,
                    "linkTarget": link_target,
                    "resolvedTarget": resolved_target,
                    "targetRelativeToSourceRoot": target_rel,
                    "imageInfo": image_info,
                    "label": label,
                }
            )
    for raw in raw_records:
        split = raw["split"]
        counters = split_counts[split]
        image_info = raw["imageInfo"]
        label = raw["label"]
        try:
            label_stat = label.stat() if label.is_file() else None
        except OSError:
            label_stat = None
        if image_info is not None:
            counters["resolvable_image"] += 1
        elif raw["isSymlink"]:
            counters["broken_symlink"] += 1
        else:
            counters["missing_image"] += 1
        if label_stat is not None:
            counters["label_present"] += 1
        else:
            counters["label_missing"] += 1
        entries.append(
            {
                "split": split,
                "manifestLine": raw["manifestLine"],
                "imagePath": repo_path(raw["image"]),
                "imageStem": raw["imageStem"],
                "isSymlink": raw["isSymlink"],
                "linkTarget": raw["linkTarget"],
                "resolvedTarget": repo_path(raw["resolvedTarget"]),
                "targetRelativeToSourceRoot": raw["targetRelativeToSourceRoot"],
                "imageExists": image_info is not None,
                "imageSizeBytes": image_info["sizeBytes"] if image_info else None,
                "imageSHA256": image_info["sha256"] if image_info else None,
                "pngDimensions": image_info["pngDimensions"] if image_info else None,
                "labelPath": repo_path(raw["label"]),
                "labelExists": label_stat is not None,
                "labelSizeBytes": label_stat.st_size if label_stat else None,
                "labelSHA256": None,
                "labelHashStatus": "not_read_per_file; see surviving labels.cache identity",
            }
        )

    manifest_hashes = {split: sha256_file(path) for split, path in MANIFESTS.items()}
    summary = {
        "manifestEntries": len(entries),
        "manifestHashes": manifest_hashes,
        "splitCounts": {split: dict(counts) for split, counts in split_counts.items()},
        "uniqueManifestPaths": len({entry["imagePath"] for entry in entries}),
        "uniqueStems": len({entry["imageStem"] for entry in entries}),
        "targetPathCount": len(target_rel_counts),
        "duplicateTargetPaths": sum(1 for count in target_rel_counts.values() if count > 1),
        "targetPathSample": sorted(target_rel_counts.items())[:10],
        "survivingLabelCacheHashes": {split: label_cache_hash(split) for split in MANIFESTS},
        "perFileLabelHashes": False,
    }
    return entries, {"summary": summary, "targetPaths": target_paths}


def candidate_coverage(target_paths: dict[str, Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in source_candidates():
        root = Path(candidate["path"])
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        present = 0
        checked = len(target_paths)
        examples: list[str] = []
        if root.is_dir():
            # Skip entire absent split directories instead of probing thousands
            # of paths beneath them on APFS.
            for relative in sorted(target_paths):
                top_level = relative.split("/", 1)[0]
                if not (root / top_level).is_dir():
                    continue
                path = root / relative
                if path.is_file():
                    present += 1
                    if len(examples) < 5:
                        examples.append(repo_path(path))
        row = dict(candidate)
        row.update(
            {
                "expectedUniqueSourceFiles": checked,
                "presentUniqueSourceFiles": present,
                "manifestJson": repo_path(root / "manifest.json"),
                "manifestJsonExists": (root / "manifest.json").is_file(),
                "presentExamples": examples,
            }
        )
        rows.append(row)
    return rows


def known_artifacts(entries: list[dict[str, Any]]) -> dict[str, Any]:
    test_stems = {entry["imageStem"] for entry in entries if entry["split"] == "test"}
    blurred_dir = REPORTS_ROOT / "blurred_eval_images"
    prediction_dir = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6a_r009_test_pred" / "labels"
    blurred_files = sorted(blurred_dir.glob("img_*.png")) if blurred_dir.is_dir() else []
    prediction_files = sorted(prediction_dir.glob("*.txt")) if prediction_dir.is_dir() else []
    blurred_stems = {path.stem for path in blurred_files}
    prediction_stems = {path.stem for path in prediction_files}
    return {
        "blurredEvalImages": {
            "path": repo_path(blurred_dir),
            "count": len(blurred_files),
            "overlapWithTestManifest": len(blurred_stems & test_stems),
            "dimensionsSample": png_dimensions(blurred_files[0]) if blurred_files else None,
            "classification": "derived blurred outputs; not original holdout pixels",
        },
        "historicalPredictionLabels": {
            "path": repo_path(prediction_dir),
            "count": len(prediction_files),
            "overlapWithTestManifest": len(prediction_stems & test_stems),
            "classification": "historical predictions without source image bytes; not recovery candidates",
        },
    }


def write_outputs(entries: list[dict[str, Any]], inventory_meta: dict[str, Any]) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    inventory_path = OUT_ROOT / "manifest_inventory.jsonl"
    with inventory_path.open("w") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")

    candidates = candidate_coverage(inventory_meta["targetPaths"])
    candidate_path = OUT_ROOT / "candidate_sources.json"
    candidate_path.write_text(json.dumps(candidates, indent=2, sort_keys=True) + "\n")

    evidence = search_checked_in_evidence()
    evidence_path = OUT_ROOT / "provenance_search.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")

    artifact_hashes = {
        "trainManifest": sha256_file(MANIFESTS["train"]),
        "valManifest": sha256_file(MANIFESTS["val"]),
        "testManifest": sha256_file(MANIFESTS["test"]),
        "categoryMap": json_hash(CATEGORY_MAP),
        "exportReport": json_hash(EXPORT_REPORT),
        "historicalEval": json_hash(HISTORICAL_EVAL),
        "run009BestCheckpoint": sha256_file(CHECKPOINT),
    }
    summary = inventory_meta["summary"]
    report = {
        "generatedAt": utc_now(),
        "gitHead": git_output("rev-parse", "HEAD"),
        "artifactHashes": artifact_hashes,
        "inventory": summary,
        "candidates": candidates,
        "knownArtifacts": known_artifacts(entries),
        "provenanceSearchMatches": len(evidence),
        "inventoryFile": str(inventory_path.relative_to(PROJECT_ROOT)),
        "recommendation": (
            "No exact original source was found in the bounded documented locations. "
            "Request a specific backup/archive location from the maintainer or conduct a "
            "separately reviewed replacement-corpus proposal. Do not relink, regenerate, "
            "or run evaluation under the historical corpus identity."
        ),
    }
    (OUT_ROOT / "assessment_data.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    split_rows = []
    for split, counts in summary["splitCounts"].items():
        entry_count = sum(
            counts.get(key, 0)
            for key in ("resolvable_image", "broken_symlink", "missing_image")
        )
        split_rows.append(
            f"| {split} | {entry_count} | {counts.get('resolvable_image', 0)} | "
            f"{counts.get('broken_symlink', 0)} | {counts.get('missing_image', 0)} | "
            f"{counts.get('label_present', 0)} |"
        )
    candidate_rows = []
    for candidate in candidates:
        candidate_rows.append(
            f"| `{candidate['name']}` | `{candidate['path']}` | "
            f"{'yes' if candidate['exists'] else 'no'} | "
            f"{candidate['presentUniqueSourceFiles']}/{candidate['expectedUniqueSourceFiles']} | "
            f"{'yes' if candidate['manifestJsonExists'] else 'no'} |"
        )
    report_text = f"""# P0-A Dataset Recovery Assessment

Generated: {report['generatedAt']}  
Git HEAD: `{report['gitHead']}`

## Decision

The original Phase 6a image corpus was not recovered in the bounded search. The
assessment is **not evidence that the originals are destroyed**; it records only
that no exact source was found at the documented paths searched here. The next
safe action is to obtain a specific backup/archive location from the maintainer,
or to obtain approval for a separately versioned replacement-corpus proposal.

Do not relink the historical export, rerun `export_coco.py` over the old output,
pair regenerated pixels with surviving labels, or report the historical 0.585669
mAP50 as currently reproducible.

## Manifest inventory

The complete machine-readable inventory is
[`manifest_inventory.jsonl`](manifest_inventory.jsonl). It contains one record
per manifest entry, including link target, image/label existence, label size,
available image hash/dimensions, and stable repository-relative paths where
possible. Per-file label content hashes were not read during this bounded pass;
the surviving per-split `labels.cache` identity hashes are recorded instead.

| Split | Entries | Resolvable images | Broken symlinks | Other missing images | Labels |
|---|---:|---:|---:|---:|---:|
{chr(10).join(split_rows)}

Total entries: **{summary['manifestEntries']}**  
Unique manifest paths: **{summary['uniqueManifestPaths']}**  
Unique source target paths: **{summary['targetPathCount']}**  
Duplicate manifest paths: **{summary['uniqueManifestPaths'] != summary['manifestEntries']}**

The surviving labels and historical report are preserved. The label and manifest
hashes, plus the Run 009 checkpoint hash when present, are recorded in
[`assessment_data.json`](assessment_data.json).

The per-file label hash field is intentionally `null` with an explicit status:
the label corpus is evidence to preserve, but opening the large surviving label
directories caused repeated multi-minute filesystem stalls during this
read-only assessment. The existing Ultralytics cache hashes provide a surviving
split-level identity signal; they are not substitutes for per-file content
hashes and do not qualify image recovery.

## Bounded source lookup

The lookup checked only exact paths documented by `export_coco.py`, provenance
records, and the recovery plan. It did not recursively scan the home directory,
mount volumes, install recovery tools, or mutate any source.

| Candidate | Path | Root exists | Present expected source files | Root manifest |
|---|---|---:|---:|---:|
{chr(10).join(candidate_rows)}

Full candidate details are in
[`candidate_sources.json`](candidate_sources.json). No candidate met the
identity threshold for original-corpus recovery.

## Surviving derived artifacts

- `reports/blurred_eval_images/` contains 200 blurred images from the historical
  evaluation pass. They are derived outputs, not original holdout pixels.
- `NativeUITrainer/yolo_runs/phase6a_r009_test_pred/labels/` contains 2,000
  historical prediction label files. They do not restore image bytes, image
  hashes, or source provenance.

These artifacts are catalogued in `assessment_data.json` and were not modified.

## Provenance and recovery limits

The bounded checked-in evidence search found {len(evidence)} matching lines;
details are in [`provenance_search.json`](provenance_search.json). The repository
records the synthetic dataset as an external `NativeUIAuditKit-Dataset` store,
but that documented store was not present at the searched sibling or home path.
Git does not contain the ignored PNG corpus.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Account for all 17,040 entries | PASS | `manifest_inventory.jsonl`, `assessment_data.json` |
| Account for every label and preserve hash evidence | PARTIAL | All 17,040 labels exist; per-split `labels.cache` identity hashes recorded; per-file content hashes deferred |
| Preserve existing artifacts | PASS | No dataset links, labels, weights, or historical reports changed |
| Identify documented source locations | PASS | `candidate_sources.json`, `provenance_search.json` |
| Establish exact original recovery | NOT ESTABLISHED | No candidate source had matching files |
| Recommend next action without inventing provenance | PASS | Request specific backup/archive or review a new corpus version |

## Handoff status

P0-A is **review-ready**, not accepted. The per-file label hash field is the one
known evidence limitation in this assessment; the surviving cache identities and
label sizes are recorded, but they are not equivalent to per-file content hashes.
P0-B must not begin until a specific
source is supplied and the architect reviews whether its identity is verified,
uncertain, or a new corpus. The independent training-corpus readiness remains
unresolved even if the 2,000-image test holdout is recovered.
"""
    (OUT_ROOT / "assessment.md").write_text(report_text)

    handoff = f"""# P0-A Handoff

Status: **review**  
Packet: `P0-A`  
Evidence: [`assessment.md`](assessment.md)

P0-A completed a bounded, read-only recovery assessment. The full 17,040-entry
inventory is in `manifest_inventory.jsonl`; source candidates and provenance
matches are in `candidate_sources.json` and `provenance_search.json`.

## Outcome and changed paths

- Base revision inspected: `{report['gitHead']}`.
- The working tree already contained unrelated research/task changes; those were
  preserved. This packet added `scripts/assess_dataset_recovery.py`, generated
  `reports/work/P0/*`, and updated the P0-A queue row in `Tasks.md` to `review`.
- No source files, links, labels, checkpoints, or historical reports were changed.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Inventory all 17,040 entries | PASS | `manifest_inventory.jsonl` |
| Test pixels available | FAIL / blocked | 0 of 2,000 test images resolve |
| Train/validation original pixels available | PARTIAL | 1,441 train and 360 validation batch images resolve; original synthetic links remain broken |
| Documented candidate roots checked | PASS | `candidate_sources.json` — 0/15,239 expected original source files found |
| Exact original recovery established | NOT ESTABLISHED | No candidate source matched |
| Per-file label content hashes | DEFERRED | Label existence/size and surviving cache identity hashes recorded; no label bytes were rewritten |

## Verification commands

- `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/assess_dataset_recovery.py` — exit 0.
- Focused inventory assertions — passed: 17,040 rows, all labels present, split counts verified, five candidate roots with zero matching source files.
- `git diff --check` — exit 0.
- `swift build` — passed on the bounded retry with in-project compiler cache.
- `swift test` — passed on the bounded retry: 14 XCTest cases and 90 Swift Testing tests, 0 failures.

No source files, links, labels, checkpoints, or historical reports were changed.
No recovery, regeneration, inference, training, or external write was attempted.

All 17,040 labels were accounted for by manifest-relative existence and size.
Per-file label content hashes were not collected because the large surviving
label directories caused repeated filesystem stalls; surviving per-split cache
identity hashes are recorded in `assessment_data.json` and the inventory marks
this limitation explicitly.

## Remaining risks and resume condition

The historical Run 009 aggregate report remains historical and non-reproducible
until usable test pixels are recovered or a new corpus is explicitly versioned.
The surviving `batch_6a8` images are separate fixture artifacts and must not be
treated as recovered synthetic holdout pixels. No P0-B staging, reconstruction,
inference, or training is authorized by this handoff.

The resume condition is a maintainer-supplied, bounded backup/archive location or
an architect-reviewed replacement-corpus decision. P0-B must stage into a new
in-project corpus directory and verify every image before any data-dependent
evaluation or training.

No new BestPractices entry was added: the observed failure is already covered by
BP-52, with the concrete evidence recorded here.
"""
    (OUT_ROOT / "handoff.md").write_text(handoff)


def main() -> int:
    missing = [str(path) for path in [*MANIFESTS.values(), CATEGORY_MAP, EXPORT_REPORT] if not path.is_file()]
    if missing:
        print("Required evidence files are missing:", file=sys.stderr)
        for path in missing:
            print(f"  {path}", file=sys.stderr)
        return 1
    entries, inventory_meta = inventory_entries()
    write_outputs(entries, inventory_meta)
    print(f"Wrote {OUT_ROOT.relative_to(PROJECT_ROOT)}")
    print(f"Inventory entries: {len(entries)}")
    print(json.dumps(inventory_meta["summary"]["splitCounts"], sort_keys=True))
    print(f"Candidate report: {repo_path(OUT_ROOT / 'candidate_sources.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
