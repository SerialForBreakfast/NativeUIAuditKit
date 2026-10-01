# SYN-08-ASSEMBLY — native-body assembly

## Deliverable

The existing mixed assembly and trainer preflight now accept measured-body native
review batches with production crop-QA receipts. No new annotation application,
recrop, capture, feature encoding or training is needed to assemble these inputs.
Native labels remain native-observed; they are not presented as human annotations
or manufactured focused/unfocused pairs. Original source pairs are retained separately.

The assembly intentionally cannot execute a model. Exact-input data admission and
a changed-data experiment with encoding/runtime budgets are still required. An
unrelated approval cannot turn this preparation artifact into an executable run.

## Reproduce

From the repository root, choose a new output directory:

```sh
sh reports/work/SYN-08-ASSEMBLY/reproduce.sh \
  reports/work/SYN-08-ASSEMBLY/artifacts/new-dry-run
```

The output contains a complete candidate ledger, exact source/crop references,
baseline-preserving assembly, ordered encoding plan and **unapproved** admission
draft. Bulky artifacts and logs are gitignored; originals and human edits are untouched.
Existing caller: `focus_mixed_assembly.py --input <input.json> --output <new-directory>`.
Trainer caller: `train_focus_ring_detector.py --experiment-protocol <manifest> \
--experiment-arm native-body-dry-run --name syn08-dry-run-only --preflight`.
Preflight exit2 with `configurationValid:true` and `launchEligible:false` is expected
for missing admission/execution scope, not a software failure.

## Corrections discovered in the real replay

Final artifact: [content-normalized manifest](artifacts/content-normalized/focus_dataset_manifest.json),
seal `81a3bd2502fecc532ea5bf3feb766455be9fa9a64d248e43f49467b7a7cb454f`.
The earlier `retained-dry-run` is superseded: it used the overly strict generation
comparison. Keep it only as diagnostic evidence of the corrected consumer bug.

624 measured-body crop observations =16 reserved-source exclusions +608 candidates.
Of608,246 unique candidates await admission and362 are blocked. Blocking reasons
are disjoint here:313 duplicate crops,42 incomplete-body inventory,5 reserved/
evaluation overlaps and2 clipping cases requiring separate acceptance.
All272 old conflict flags resolve as generation-only differences; no genuine
annotation-content conflict remains in this replay.

| Candidate class | Focused | Unfocused | Total |
| --- | ---: | ---: | ---: |
| collectionItem | 20 | 84 | 104 |
| secondaryButton (includes current native tab mapping) | 18 | 37 | 55 |
| listRow | 24 | 51 | 75 |
| primaryButton | 2 | 4 | 6 |
| cancelAction | 2 | 4 | 6 |
| Total | 66 | 180 | 246 |

These are static controls, **not246 independent scenes or matched pairs**. All
remain related Fixture-source candidates; no independent-validation claim is made.
The ledger also accounts for1,212 non-proposed semantic/body observations:
1,140 semantic children,56 unavailable bodies and16 unsupported/nonfocusable roles.
These are observation counts, not unique controls or new training samples.

Baseline training remains986 and evaluation333; all existing weight deltas are0.
No additions are admitted, so the actual encoding plan has zero new members until
an exact-input admission selects them. Generated fixture tests separately verify
that admitted additions yield ordered encoding members and balanced sampling.

- Four frames/16 body controls in the earlier source
  `native/splits/validation/image` match the existing reserved-pixel ledger. The
  entire source bundle is excluded **before image decoding**; other bundles continue.
  This preserves earlier evaluation reservations. Geometry approval did not change roles.
- The old review comparison includes rendered-body `generation` in its annotation
  signature. Identical pixels with identical bounds/focus but different capture
  generations can therefore appear contradictory. This assembly removes only that
  counter for content comparison after native bracket validation. Original records
  and sealed review batches are unchanged. Actual geometry/label conflicts still block.
- Crop duplicates are aliases, not additional independent examples. Unsupported
  bodies, clipped cases and protected overlaps remain reasoned exclusions.

## What gets us to training

1. Finish the already-prepared sampled native/palette geometry review, without
   redrawing every synthetic control. Bind the exact accepted source recipes as
   training candidates; retain shared-renderer ancestry and existing reserved roles.
2. Use the resulting unique candidate counts—not raw capture counts—to target
   remaining artwork and other uncovered combinations in TTR's existing assignment.
   More copies of the same pixels do not add coverage. No new producer contract is
   needed for the measured-body families already delivered.
3. Approve exact candidate membership once; assembly then emits only those ordered
   new crop/label members for encoding, while preserving the existing 986 training
   and333 evaluation members and the human sampling mass.
4. Bind and implement the changed-data experiment executor against that encoding
   receipt, run one budgeted comparison, and evaluate on unchanged development/
   retention evidence. Keep independent qualification separate. Export a candidate
   for TTR testing only if its measured comparison supports that decision.

This is an assembly capability and data-readiness result, not a larger corpus
approval, accuracy gain, new model or production qualification.

## Acceptance evidence

- Software:25 assembly tests (10 native-body tests +15 existing assembly tests),
  11 training/preflight tests and44 fixture tests pass. Includes changed crop hashes,
  resealed wrong labels, crop membership/protocol mismatch, explicit admission scope,
  duplicates/conflicts, generation normalization, protected-before-decode rejection,
  weight preservation and the actual trainer rejecting `--execute` without importing
  torch. Offline Swift build passes;120 Swift Testing +14 XCTest tests pass.
- Data: baseline members/order/weights preserved;246 candidates, no admission.
  The safe native sources are revalidated against their original bracket records
  and production crop receipts. Source and review artifacts are read-only.
- Integration: retained three-batch assembly and existing mixed CLI/trainer dry-run
  exercise real sources; final caller results recorded in verification below.
- Model gate: not assessed. No feature encoding, inference, training or export.

Final caller verification: `mixed-content-normalized` returns exit0 and a manifest
identical to `content-normalized` (including the seal above). Actual trainer
`trainer-content-normalized.log` returns exit2, `configurationValid:true`,
`launchEligible:false`, `executionAuthorized:false` and the expected four blockers.
No `NativeUITrainer/focus_ring_runs/syn08-dry-run-only` directory exists. The earlier
mixed/preflight logs are superseded along with their generation-sensitive input.
All25assembly,11training and44fixture tests passed on the final implementation;
Swift build/test rerun passed and `git diff --check` passed. User commits manually.
