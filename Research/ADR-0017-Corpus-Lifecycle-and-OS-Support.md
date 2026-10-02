# ADR-0017: Corpus lifecycle and OS support

- Status: Accepted by maintainer, October 2, 2026
- Scope: Dataset maintenance, reproducibility and proportionate retention

## Decision

Maintain a versioned corpus with an explicit supported-OS policy, rather than an
ever-growing training folder. The exact supported-version window remains a
maintainer decision; this ADR does not retire any currently supported version.

Every admitted example must be traceable to its OS/runtime, generator/app revision,
UI family, source kind, annotation version, recipe, seed and source assets where
applicable. Preserve asset licenses. Unknown historical metadata stays unknown.

Dataset membership has four dispositions: active training, evaluation-only,
historical reference and retired. Immutable experiment manifests record the exact
membership and grouping used. A later lifecycle change creates a new manifest; it
does not rewrite past experiments or move related variants across their split.

Review coverage when an OS release changes relevant UI behavior or a regression is
demonstrated. Compare new renders and annotations with representative prior examples.
Age alone is not a reason to remove visually relevant data. Report supported OS and
UI-family results separately so aggregate improvement cannot conceal a regression.

Retiring examples affects future training only. Deleting data does not remove its
influence from existing weights. Train and evaluate a replacement on the revised
membership before promotion; preserve the previous selected model and its manifest
for rollback. Training, export and promotion retain their execution authorization.

Keep a small frozen reference benchmark for each meaningful OS rendering generation,
alongside the evolving current benchmark. Identify previously inspected/development
examples honestly; historical comparisons are not untouched independent tests.

## Retention proportional to a hobby/research project

- Preserve real-device captures and human annotations/corrections privately. Personal
  device material remains local and is excluded from future cloud storage by default.
- Treat bulk synthetic renders, derived crops, feature caches and intermediate
  checkpoints as rebuildable after their active experiment and dependencies end.
  A three-copy backup policy or NAS is not required for replaceable synthetic data.
- Preserve compact recipes, seeds, source assets/licenses, generator/runtime identities,
  membership manifests, benchmark results, selected weights and representative failure
  examples. Human corrections to synthetic data are retained with their source lineage.
- Before removing an old runtime, retain representative pixels for important historical
  appearances. Recipes cannot guarantee pixel-identical regeneration after OS changes
  or when the original renderer/runtime is unavailable.
- Cleanup uses an exact candidate inventory, dependency checks and a maintainer-approved
  deletion scope. This ADR authorizes policy, not immediate deletion, migration, runtime
  removal or a recurring cleanup job. Report what is regenerable versus irreplaceable.

## Current storage application

The native-focus spike may store its corpus and scratch data in the approved local
USB directory `/Volumes/training-drive/data/NUIAK/NATIVE-FOCUS-EFFECT-SPIKE-26`.
Verify the actual mount before writes and fail closed if absent. Source, environments,
build caches and compact experiment records remain project-local. Measure generation,
writing, loading and encoding separately; introduce a local working cache only when
measured I/O warrants it. NAS/cloud setup is not part of this decision.

## Implementation and acceptance

The policy is adopted now. Automated lifecycle filtering is future implementation:
validate required provenance for new admissions; resolve explicit dispositions into
immutable manifests; reject split leakage and missing inputs; produce a read-only
retirement/cleanup report before any deletion. Test unknown versions, retired entries,
historical manifest replay and missing external mounts. Tasks.md owns this backlog.

Related: [artifact retention](ArtifactRetention.md),
[native-focus spike](Plans/NativeFocusEffectSpike26.md).
