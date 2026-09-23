# APPEAR-B1 — balanced appearance development adapter

| Outcome | Result |
|---|---|
| Software verified | Integrated assembly/experiment/production-rejection paths;91 offline Python tests and required Swift build/tests pass |
| Data eligible |212 proposed training pairs +9 native retention-validation pairs; original source admission unchanged; independent appearance evaluation absent |
| Integration qualified | Real442-row assembly passes; actual trainer preflight returns the required launch blockers; no new producer/runtime qualification |
| Model gate passed | Not assessed; no inference, model deserialization, training or export |

## Implementation and criteria

New `scripts/focus_appearance_experiment.py` provides the separate versioned contract
documented in `Research/schemas/focus-appearance-experiment-v1.md`. Existing
focus_mixed_assembly and focus_learning_experiment dispatch it. Production preflight
rejects it outside explicit experiment mode. Legacy development protocols retain
their original sampling/checkpoint semantics. Trainer selection is extended, not forked.
No public library API or Swift implementation changes.

- Reconstruct original/native/retained membership and production crop provenance;
  regenerate the APPEAR-B proposal audit and compare stable content/seals. Keep
  protected Remotes and known Home/Photos inventory out of training/selection.
- Add ten independently reviewed APPEAR-C v1.5 pairs without changing origin roles.
  Source manifests/reviews/receipts/raw bytes and the old proposal remain untouched.
  The separate catalog quarantine is not included.
- Freeze424 training samples and18 native retention samples. Both direct/TTR
  Fixture transports share one logical sampling/seed namespace:50% native and50%
  Fixture, then equal strata and labels. Effective weight-vector sample size131.06
  is concentration, not independence or demonstrated optimality.
- Six connected components including protected Remotes: all172 Fixture candidate
  pairs join one training component. Native root/general/apps remain training;
  Accessibility remains validation; Remotes remains known challenge. Zero
  cross-partition conflicts or complete duplicate pairs.20 partial duplicate-crop
  groups (53 sample occurrences) are retained within their components and disclosed,
  not counted as independent support.
- Require two unrelated components with both labels in each of five appearance
  strata for validation and final challenge. Check known-use, source eligibility,
  original lineage, reserved families, seeds and exact raw/crop pixels in one graph.
  Final challenge is audited at preflight but excluded from trainer data loaders.
- Require a frozen reference-bound retention accuracy floor at0.85; select minimum
  equal-native/appearance-validation BCE among eligible epochs, earliest tie.
  No eligible epoch means explicit failed result, never fallback to last.pt.
- Bind approval to exact protocol/run/arm; retain log-before-model-import and
  safe-new-output safeguards. Reject explicit conflicting configuration flags.

## Verification

Base HEAD9012c1f351c408897348f791b5355553725f15b8. Preserved pre-existing changes in
Research/Tasks, harvest_sidecar_v2, harvest_bundle_validation, harvest_focus_pairs,
test_ttr_sidecar_v2, test_ttr_appearance and APPEAR-C/TTR-CATALOG reports.

Approved Python is focus-export-01 under user Application Support; invocations set
PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH=scripts. Tests use `.build` temporary trees.
Synthetic source/model/approval fixtures are explicitly test-only; no test launches
training or imports torch. New B1 tests exercise actual assembly/trainer dispatch
with deterministic source-boundary fakes, while retained consumer suites validate
real schema mechanics and this handoff's CLI run validates genuine bytes.

`final-tests.log`:91 tests,5.881s,exit0. Includes complete synthetic all-input case,
absent/stale approval, absent evaluation/selection, conflicting old policy/floor,
changed reference/checkpoint/proposal weights, label conflicts/incomplete pairs,
duplicate pairs, combined transitive lineage, cross-adapter seeds, known evaluation
reuse, output collisions, nonfinite scoring, production rejection, no model imports,
configuration override rejection and legacy contract regressions. Earlier
`focused-tests.log` preserves one invocation error: nonexistent test module name;
corrected modules passed88 tests, then expanded final91. No failing behavior concealed.

`swift-build.log`:exit0,3.95s. `swift-test.log`:exit0,14 XCTest plus93 Swift Testing
tests pass (Swift Testing2.490s). Normal-host scoped approvals avoided the known
nested-sandbox denial; tests explicitly approved normal CoreML Library cache use.
Configurable caches/logs/TMPDIR remain project-local; no permission/security changes.
Later Python-only test additions do not change the Swift dependency scope.

Real commands:

```sh
python reports/work/APPEAR-B1/prepare_input.py
python scripts/focus_mixed_assembly.py --input reports/work/APPEAR-B1/input.json --output reports/work/APPEAR-B1/dataset
python scripts/train_focus_ring_detector.py --experiment-protocol reports/work/APPEAR-B1/dataset/focus_dataset_manifest.json --experiment-arm warm-stretch --name appear-b1-preflight-only --preflight
python scripts/train_focus_ring_detector.py --dataset reports/work/APPEAR-B1/dataset --name appear-b1-production-rejection --preflight
```

Assembly exit0; `assembly.log` and frozen dataset manifest record protocol content
hash `cf7501f215c247647579b9e5b045305c7a4c3a00f0c5acf62818312dd18a7038`.
Filesystem wall window06:27:47–06:31:27Z, approximately220s; original-source
reconstruction/recropping dominates, not tests. Production preflight exit2 with
development_protocol_requires_explicit_experiment_mode, as required. Experimental
preflight exit2, configurationValid:true, launchEligible:false, executionAuthorized:false:
ten role/stratum support gaps, unresolved_checkpoint_selection and
missing_experiment_approval. `preflight.json` retains the full report; stderr empty.
Filesystem wall window06:31:55–06:35:36Z, approximately221s. Both placeholder run
directories remain absent. Source reconstruction is intentionally repeated at the
execution-facing boundary; no unvalidated cache shortcut was introduced.

Assigned software tranche is complete for review: all applicable acceptance criteria
have integrated evidence; missing real evaluation/approval is the expected launch
boundary, not incomplete software. No owned process remains. `git diff --check` passes.

## Remaining gates and next action

No independent appearance validation/final challenge exists for any of the five
required strata. No reference-bound checkpoint floor or new execution approval is
invented. Native validation is retention only; known challenge/development failures
do not become untouched evaluation. The old advisory proposal remains non-executable.

Next: qualify separately reserved evaluation families under an explicitly bounded
capture assignment, freeze validation/challenge and reference predictions, review
the selection floor/configuration, then request one candidate authorization. The
schema provides a safe placeholder launch template, not an allocated experiment ID.
No scale collection, model promotion or automated retry follows from this packet.

BP-86 records the observed multi-adapter sampling/lineage lesson. Worker execution
and model-workflow skills kept the full integration/test/handoff boundary and
separate model authority. SMB coordination is not applicable: local adapter work
does not change TTR's current request or require a new producer action. Prior
APPEAR-C intake publication remains accurate; no status noise was added.
