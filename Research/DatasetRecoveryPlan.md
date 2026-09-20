# P0 — Recover dataset evidence and establish a usable evaluation corpus

**Revision:** 4, 2026-09-19. **Parent:** TASK-DATA-01. Execution state/owner: Tasks.md. P0-A/P0-B/P0-C are separate assignments using the common contract in ImplementationPlans.md. Recovery is not a global software gate. Accepted default when originals cannot be recovered is a versioned reconstruction, never silent replacement.

## Assignment and context

The original holdout has 2,000 manifest entries and 2,000 labels but zero resolvable images. Train/validation are also incomplete. See [read-only inspection](../reports/dataset_availability_2026-09-19.md). The suspected agent deletion is unconfirmed. Do not describe it as established fact or use missing data as a reason to overwrite historical evaluation evidence.

Follow AGENTS.md, WorkerWorkflow.md, nativeui-worker-execution, BP-34/52, and K-11. Relevant code is `scripts/export_coco.py` (symlinked image export), plus the existing dataset manifests and any generator/provenance records. Read model skill only if later authorized evaluation actually enters scope.

**Permitted in the first assignment:** Read-only source/backup discovery, provenance analysis, and additive reports under `reports/work/P0/`. A small diagnostic script under `scripts/` is allowed if needed after mandatory pre-code reading. Do not change dataset links, labels, source images, exporters, or report metrics. No recovery software installation, volume mounting, system snapshots/restores, hardware access, git writes, or broad home-directory search. No training/inference in P0.

## P0-A — Bounded recovery assessment

**Existing work:** inspect and preserve `scripts/assess_dataset_recovery.py` before adding another implementation. It was untracked during planning and is not accepted merely by its presence. Coordinate ownership and review its output/side effects before running. Permitted file changes are bounded diagnostic fixes/tests and additive reports; all source corpora remain read-only.

1. Preserve the manifest/report hashes in the inspection report and create an inventory of every manifest entry: split, path, link target, file existence, label existence/hash, and any surviving provenance. Capture evidence before any proposed mutation; do not remove broken links.
2. Identify the original dataset locations from research/export metadata. Check those exact paths and known source manifests, documented archives, and explicitly available backup locations read-only. Use manifest-driven candidate lookup rather than recursively scanning large trees or the user's home. An external source may be read; all agent-created copies/reports must stay in-project.
3. Search relevant checked-in docs/logs for relocation or cleanup records. Git cannot recover ignored PNGs merely because labels or export scripts are tracked. Do not assign responsibility from a missing path or timestamps. Request a specific backup/archive location from the maintainer only when bounded evidence-based discovery is exhausted.
4. Match recovery candidates using historical content hashes where available, then provenance, sample IDs, source annotations, generator revision/seed/configuration, image dimensions, and split identity. Filenames and seeds alone are insufficient. Record which identity claims can and cannot be established.
5. Report a recovery decision with exact source/destination, counts by split, disk-space estimate, verification method, unresolved mismatches, and whether any operation requires new authority. No blind rerun of `export_coco.py`: it may rewrite labels and links and erase useful evidence.

**P0-A acceptance:** Inventory accounts for all 17,040 manifest entries; recovery candidates and missing entries are explicit; surviving artifacts remain unchanged; the recommendation is one of exact/provenance-supported recovery, uncertain candidate corpus, or new corpus reconstruction. Every claim cites evidence. Preserve existing `reports/work/P0/` outputs from the assessment script; the revision-4 handoff is `reports/work/P0-A/handoff.md` and may link those outputs without moving/overwriting them. Architect reviews before dispatching P0-B or P0-C.

## P0-B — Staged recovery and verification (separate assignment)

If suitable sources are found, prepare a concrete copy/relink plan in a new in-project corpus directory. Prefer independent recoverable image copies for the evaluation set over links into a disposable generator tree. Retain existing manifests, labels, and broken links as evidence; no in-place overwrite. External backup/system restore remains a maintainer operation when required.

Check free space before copying; decode every image, validate dimensions and paired ground truth, verify recorded content hashes where available, preserve original split membership, and check duplicates/leakage across train/validation/test. Produce a content-hashed manifest, provenance report, and explicit corpus status. Do not silently drop missing/corrupt entries or shrink the holdout.

**Recovery classes:**

- **Verified original:** Historical content hashes or equivalent trustworthy immutable provenance establish identity of all required images/labels. Mark the 2,000-image test corpus reproducible only after complete verification.
- **Recovered candidate, identity uncertain:** Bytes and labels are usable but original identity cannot be established. Assign a new corpus ID and run Run 009 as a new baseline later; do not claim reproduction of 0.586.
- **Regenerated corpus:** If originals are unrecoverable, record that limitation. Prepare a separate generator plan with source version, seeds, OS/rendering environment, new image+annotation pairs, family splits, and new corpus version. Do not pair newly rendered pixels with old labels without verification or call it the original holdout. Generator execution is outside this recovery assignment.

For a changed corpus, evaluate Run 009 and future candidates on the same new version. Keep the historical 0.586 report intact and report any results as non-comparable to it. Architect review must establish leakage controls and the revised DS-G8 evaluation protocol before any shipping claim; thresholds are not relaxed because data is missing.

**P0-B acceptance:** Either a verified original corpus or an explicitly versioned replacement is documented with complete file/decode/annotation/provenance checks. Test-corpus readiness and training-corpus readiness are separate statuses: restoring 2,000 holdout images does not restore the 11,984-image training set. No completion claim based solely on a manifest, label count, or the disappearance of dangling links.

## P0-C — Versioned reconstruction fallback

**Inputs:** completed P0-A establishing that originals cannot be recovered through bounded known sources, reviewed reconstruction configuration, generator code and available rendering prerequisites. **Scope:** separately assigned generator/configuration changes and generation; no restore into old paths, training, or model promotion. Preserve old labels/links/reports. Follow generator platform rules and BP-01–11/15/27/32/34/52.

1. Pin generator revision, rendering OS/device/scale, seeds, template families, frozen 41-class taxonomy and split algorithm. P0-C uses family-level allocation: test is the architecture's fixed `CardDetail`, `WizardStepFlow`, `NotificationCenter`, `GalleryPage`, `MultiSectionForm`, `SettingsToggleDense`, `EmptyState`, and `OnboardingPage` holdout; validation is `TabViewNavigation`, `SearchResults`, `PickerDateEntry`, and `SettingsDisclosure`; all other families, including hard negatives and accessibility variants of a family, are train only. Resolve the original dataset-location rule before generation: all agent-created outputs go to the gitignored `NativeUITrainer/reconstructed_corpora/` in-project reconstruction tree, never a nested NativeUIAuditKit-Dataset tree or an external original. Simulator app-container staging is permitted only for this explicit regeneration, begins from a reset GeneratorRunner app container, and is copied only to a new, empty in-repository destination. Any required external producer operation belongs to a separately authorized workflow.
2. Generate fresh image+annotation pairs with content hashes. Never pair new pixels with historical labels by filename. Validate full decoding, dimensions/boxes, family separation, class/style coverage and duplicate content. The failed WKWebView/`HardNegative_2` route is excluded from P0-C; report `webContent` as uncovered legacy compatibility metadata, not as a generated class.
3. Publish new corpus version/lineage and independent readiness for train/val/test; missing class/style coverage is explicit and blocks applicable gates. Freeze manifests before model evaluation.
4. Establish retention owner, immutable membership and a verified recovery procedure; an in-checkout copy is not an independent backup. External backup creation needs its own authorized workflow.

**Acceptance:** reproducible generation configuration, complete paired corpus with leakage/coverage reports, and clearly new identity. This packet ends at eligible corpus creation; P1-B supplies the new Run 009 baseline without direct historical 0.586 comparison. **Next:** P1-B/P3-B and P5-B when their other prerequisites are met. Handoff: reports/work/P0-C/handoff.md.

## Dependencies and productive work meanwhile

Revision-4 packet contracts in [ImplementationPlans.md](ImplementationPlans.md) govern acceptance: P1-A/P2-A/P3-A/P4-A/P4-B/P5-A software can be accepted independently of recovery. P0 is a prerequisite for real-corpus use, not a global development gate. H1/P4-L producer compatibility does not depend on restoring the iOS holdout.

- P1 serializer and missing-image preflight tests may proceed. Its full Run 009 inference criterion waits on an accepted usable test corpus and correct historical/replacement labeling.
- P2 comparison code/tests may proceed after the P1 schema is reviewed. Preserve historical metrics separately from current `imagesAvailable`, `predictionsAvailable`, and reproducibility status; never equate report existence with runnable data.
- P3 selection code/tests may proceed, but no real frozen suite or baseline can be accepted from labels alone. Freeze from the accepted corpus version only.
- P4 offline ingest/assembly tests continue. Actual assembly with the Phase 6a source waits on full required split readiness.
- P5 configuration/preflight continues and must fail launch eligibility on missing pixels. Training waits on both restored/rebuilt eligible training data and the independent live fixture prerequisites.

## Preservation deliverable

Before resuming expensive work, document ownership and retention of source corpora, the dependency from exports to symlink targets, an immutable content manifest, and a tested recovery path. A symlink export is not a backup. Do not delete any source tree until all dependent datasets and evaluation records are accounted for and the maintainer explicitly authorizes the exact deletion. Copying data elsewhere in the same checkout improves isolation but is not an independent backup.
