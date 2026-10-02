# Corpus lifecycle — completed local implementation

Software: explicit OS/version policy, immutable hash-bound selection, original split
and connected-group checks, historical replay, and read-only cleanup recommendations.
Data: no existing corpus membership changed. Model/runtime: not applicable.

`scripts/corpus_lifecycle.py` exposes `select`, `replay`, and `cleanup`. Each command
requires a sealed catalog and explicit root; external roots also require the mounted
volume. Outputs are new project-local JSON files. Selection requires complete explicit
dispositions, preserves original splits, and excludes unsupported/unknown provenance.
Replay uses the original policy, independently of later OS-support changes.

Cleanup protects private real captures, human corrections, reference data, metadata,
and transitive retained dependencies. Rebuildable retired renders are recommendations
only; no delete command exists. A changed policy does not remove learned information
from existing weights.

Validation: ten lifecycle tests plus existing corpus-retention tests, including actual
CLI/collision behavior, hash changes, missing mounts, split leakage, missing provenance,
historical replay after retired pixels disappear, and transitive dependencies.
Evidence: `reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26/lifecycle-tests.log`.
Offline Swift build/test passed during the integrated Native26 tranche.

Next adoption: populate an explicit supported-OS policy and catalog for a selected
existing corpus. No currently supported OS was retired by this implementation.
