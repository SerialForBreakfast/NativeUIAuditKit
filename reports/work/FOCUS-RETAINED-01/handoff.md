# FOCUS-RETAINED-01 — retained Fixture qualification

OS-FOCUS-04 continuation, delivered for architect review. Local-only coordination:
not applicable to SMB; no new peer action beyond previously reported maze/kitchen
issues. Existing parallel changes and raw capture evidence preserved.

## Outcome

- **Software verified:** existing receipt-chain checks and production crop runtime
  integrated into `scripts/focus_retained_review.py`. Six new regression tests;
  38 combined Python tests passed. Offline Swift build/test exit 0 (14 XCTest and
  93 Swift Testing tests). Commands, exit codes and timing: `verification.json`.
- **Data eligibility:** 36/42 recipes, 138 pairs, 276 crops audited. 90 non-maze
  pairs visually reviewed; four exact pair duplicates removed from proposed
  membership, leaving 86 candidates. These are development-review candidates,
  not an admitted training corpus. All 48 maze pairs excluded from the proposed
  run pending geometry/context review. Six kitchen-sink recipes remain absent.
- **Integration qualified:** offline retained-evidence-to-production-crop path
  checked. No current producer runtime, new capture, TTR smoke or full pilot
  qualification claimed. Historical postflight is not current readiness.
- **Model gates:** not assessed. No inference, training, export or promotion.

## Review and integrity evidence

`audit/review.json` contains raw/crop SHA-256 and decoded-pixel hashes, actual
bounds/dimensions, source receipts and interval digests. Content digest:
`b252570f635379ace8592eaff84231f3ba3137851c0378236b312fadb743b05f`.
`dispositions.json` binds all 138 per-pair decisions to that audit; digest:
`fbe1009267f38475ede2d95cb9662eabcea445267543fd00cb5965b985c451cc`.
`freeze.py` reproduces the reviewed selection and asserts exact counts; exit 0.

Three theme contact sheets cover all 180 non-maze crops; a fourth covers 12 crops
from six maze edge pairs. No additional images need displaying. Other maze crops
were automatically checked, not individually visually accepted. All six observed
maze goal pairs show bottom clipping; conservatively exclude the family from the
first experiment, without declaring every maze label wrong.

Focus can be enlargement/outline rather than brightness: primary dialog/carousel
buttons and grid controls may remain white when unfocused. Preserve those hard
appearances and fixture-observed labels. Long rows retain production square-stretch
behavior and neighboring context; no alternate cropper was introduced. Resolved
theme names are not proof of visually independent styles.

No identical decoded crop has conflicting focus labels. Five duplicate-pair groups
exist overall; four two-member groups are non-maze. Shared pixels connect both
seeds even in the non-maze subset. They cannot serve as independent train/validation
groups. Missing coverage is explicit; the failed original receipts remain failed.

## Verification and next action

Tests cover actual review CLI, incomplete/corrupt source rejection, output collision,
symlink rejection, helper membership mismatch, duplicate-group joins and role-aware
contradiction detection. Production audit exited 0; artifacts bind unchanged sources.
Python verification took 15.91s; Swift build 0.56s; Swift tests 3.10s. Capture and
external producer wait: zero. Offline crop-render duration was not separately
instrumented and is not estimated.

Next: implement the [frozen experiment contract](experiment-proposal.md) through
existing assembly/preflight/trainer entrypoints, with explicit development-only
roles and approval checks. This local software does not depend on TTR. Then obtain
authorization for one logged run. Missing independent Fixture validation limits the
claim to learning/retention diagnostics, not model generalization or production
qualification. Do not silently override existing development-only manifests.

Skills used: worker-execution for integrated acceptance; fixture-training for
observed-label/provenance and partial-output rules; model-workflow for production
crop parity, split isolation and separate training authority. TTR instructions
were consulted; no TTR operation was performed.
