# STORAGE-LIVE-01 — SSD-backed artifact reads

October3 maintainer authorized explicit storage-root support and verified bulk
migration. Preserve logical repo-relative identities and sealed manifest bytes.
Use an ignored local registry at `reports/storage/locations.json`: exact nonoverlapping
artifact prefixes map to one verified local APFS volume and separate physical roots.
No symlink substitution, arbitrary external paths, remote mounts or output routing.
Missing/wrong mount, unsafe paths and overlapping mappings fail closed. Physical
paths can be converted back to logical references by shared input helpers; new
outputs remain local and cannot target a mapped prefix. Original files remain until
hash verification and real consumer checks succeed; then delete exact verified copies.

Implement shared input resolution and integrate manifest/ref helpers plus reconstructed
corpus validation. Test local compatibility, path traversal, unknown external paths,
missing/wrong volume, ambiguous mappings, logical hash stability and output rejection.
Run actual retained transition inventory/intake from SSD, with identical corpus hash,
and focused tests plus one offline Swift build/test pass. No training or new inference.
First migrate substantial report artifact trees, retaining compact handoffs locally.
Do not move symlink-based YOLO corpora until their readers/export paths are qualified.
Record migration inventories, restore instructions, I/O measurements and measured free
space. A single SSD copy is storage, not a redundant backup; do not weaken data gates.

## STORAGE-LIVE-02 — dependency audit and retained r5 prefix

Continue the approved storage tranche without changing dataset roles. Inspect incoming
symlinks and actual YOLO/source readers before removing corpus roots. The r7 export
contains absolute links to the combined corpus; its evaluator and other historical
readers also directly access that root. Leave r7 and the current r6 prefix local until
an integrated export/reader migration is qualified. Do not silently break old manifests.

The inactive `.build/debug-output/p0c-resume/r5-verified-prefix` has no incoming
symlinks in the inspected trainer/dataset/report/debug trees and no matching references
in scripts or research documentation. Copy it to the matching SSD live prefix using
the existing migration tool, seal and verify all content, register explicit resolution,
and verify through that resolver before reclaim. Preserve tracked files and failed-run
evidence. Retain receipt and registry on both local metadata storage and SSD. This is
retention compatibility, not a renewed semantic/data-eligibility qualification.

Acceptance: full source/destination inventory equality, post-removal resolved inventory
verification, unchanged active transition membership, recorded reclaimed bytes and disk
free space. No code changes are needed for this bounded migration; reuse existing tests.
Next: versioned SSD-backed YOLO exports plus all active consumers, tested without training.

## STORAGE-LIVE-03 — active iOS dataset compatibility (next implementation tranche)

Execution refinement: migrate regular r7, r8 and addon corpus roots. Preserve the
r6 continuation prefix/export for historical recovery. Existing YOLO image links
may be individually rebound to the registered SSD copy after a sealed link-target
inventory and byte verification; do not replace corpus directories with symlinks.
Record original link text for recovery, reject tracked links and ambiguous targets,
and validate all bindings before any change. Link changes are recoverable, not a
transaction; an interruption requires inspection. Sealed manifests, labels and split
lists stay byte-identical. This is an explicit storage compatibility change, not
new data admission. New exports are isolated; no model export or training occurs.

Observed constraint:39,487r7 export files are tracked. Preserve those links and local
r7 targets; do not create a machine-specific mass diff. Stage/qualify its SSD copy
and an isolated export now. Reclaim r8/addon only after untracked-link checks. The
maintainer must remove the old r7 export from Git tracking before its links can be
rebound and its redundant source reclaimed. No agent Git writes.

Qualification found5,171unmanifested duplicate-named pairs (for example `img_000066 2.png`)
in the retained r7 tree. The legacy directory-scanning exporter includes them. Add an
explicit manifest-members-only export mode with path, duplicate, missing-pair and image
hash checks; preserve the historical default for callers without frozen manifests. The
SSD export must match the19,740declared members, never silently admit these extra files.
Retain the first failed export separately; do not delete source evidence or change splits.

Inputs: sealed r7/r8 source manifests, current YOLO labels and split lists, existing
storage registry, and retained evaluation manifests. No new training or data roles.

1. Inventory every incoming image link into r7 and r6, including r8 exports; freeze
   link text, resolved content hashes and split membership. Identify active readers
   separately from historical reconstruction tools that may require explicit restore.
2. Extend `export_coco` explicit-input handling, `eval_run013.prepare`, page regeneration
   and `integrate_ios42` input reads to use the registered resolver. Preserve logical
   provenance; output/cache paths remain local. Never relax output boundaries globally.
3. Build an isolated versioned export pointing to verified SSD images, with the same
   label bytes and membership. Qualify prediction-artifact loading and configuration-only
   training preflight. Test wrong/missing mount, dangling links, altered image/label,
   unknown external target, mixed source versions, collision and cache containment.
4. Resolve compatibility of existing sealed evaluation exports before reclaim. Either
   preserve their logical-link resolution through a reviewed mechanism or explicitly
   qualify replacement manifests with unchanged content identity. Do not silently
   rewrite sealed evidence or leave historical evaluation commands unexpectedly broken.
5. Compare complete membership/hash/label inventories and representative real loader
   tensors for old/new exports. Measure repeated cold/warm loading separately from
   preprocessing; no model forward pass needed. Record actual elapsed time and limits
   of OS-cache measurements rather than claiming SSD training equivalence.
6. Only then remove verified redundant local pixels. Save restore inventory/registry,
   run focused tests and one integrated offline Swift pass, update queue and handoff.

Acceptance: no broken supported input links, exact split/content/label parity, truthful
mount failures, output isolation, actual consumer qualification and measured reclaimed
space. Source/code/environments/checkpoints stay local. If compatibility cannot be
preserved, retain those pixels and report the specific reader rather than bypass it.
