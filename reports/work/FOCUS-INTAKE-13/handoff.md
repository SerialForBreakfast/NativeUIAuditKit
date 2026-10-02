# FOCUS-INTAKE-13 — completed for review

The delivery is valid, but does not close the structural coverage gap. The new
scene-level rule is not a deployment improvement. FDR021 and all shipped models
remain unchanged. No training, encoding, device input, export or promotion occurred.

| Outcome | Evidence |
|---|---|
| Software verified |93 focused Python tests;18 scene CLI checks; whole-scene pixel counterexample; offline Swift build and134 tests pass |
| Data eligible |Integrity/native crop QA pass; human review and new training admission remain pending |
| Integration qualified |Retained producer archive imports through existing consumer; no live runtime qualification |
| Model gate passed |Not run; no replacement candidate |

## Delivery and coverage

Exact archive `ttr-artwork-verified25-recovery-20261001-r2.tar.gz`,354,584,975bytes,
SHA256 `62048f9746ea1a1f0bd7620d9a2470c1c71cb972c471e72083b5bbb7b16df62d`.
Copy/extraction used existing `synth05_receive.receive` with only this assigned entry.
All389manifest members pass sizes/hashes and exact membership;909safe archive entries
include directories/AppleDouble metadata,397,757,286expanded bytes. Original bytes
retained. Sender receipt published/read back; receiver never deletes shared files.

All25source pairs/50frames import. Projection contains50control-state pairs because
the target and its competitor both change; this is not50new capture pairs.
All1,300crops pass existing measured-body16%/256production QA. Target growth is
1.1600×width and1.16117×height. No unknown geometry silently replaced with layout bounds.

Pixels:130unique crops/1,300observations,1,170repeat observations.62unique pixels already
occur in the prior six-pair delivery;68are new against that reference. All50target
crops are new against prior six. These counts are pixel novelty, not statistical
independence. There is exactly one definitions/regions structure and one target
position (`catalog-poster-0`). Calibration ancestry remains intact, no split change.

Six prefilled random checks are ready in one queue; three targets focused and three
unfocused. [Instructions](review.md). No review window launched and no human approval
invented. Exceptions retained; recurring selected-tab and decorative-exclusion flags
do not justify asking for50redraws. Protected-source screening remained enforced.

Evidence: `artifacts/received/receipt.json`, `member-audit.json`, `coverage.json`,
`intake/report.json`, `intake/crops/crop-qa.json`, `review-readiness.json`.

## Whole-screen experiment: useful rejection, not a new detector

Added opt-in `scripts/focus_scene_transition.py`, consuming attributed control-change
results. Requires complete declared coverage, unique persistent IDs and one visual
gain plus one loss; missing context/identity/unavailable controls abstain. An optional
strict arm also requires resolved background. No threshold fitting, after-truth
selection, neural model or unconditional Home fallback. Runtime correspondence is
not implemented: retained matching remains an explicit offline assumption.

| Method |12 directions from six eligible retained pairs |
|---|---|
| Prior arrival-only alignment |11correct,1abstention |
| New opposing-changes candidate |7correct,5abstentions |
| Require all background resolved |0correct,12abstentions |

Both new arms return unchanged on12identical-image cases. These reused/reversed
screens are not24independent tests. All72real grouped cases were processed;48are
outside the pre-existing complete-frame eligibility and remain blocked. Home
growth matching and row-removal gaps remain visible, not counted as successful.

The four additional abstentions are Settings and Settings-Apps forward/reverse:
each actually has one arrival and one departure, but another control's matcher is
unavailable, triggering the full-scene gate. The fifth is the already-missed App
Store arrival. Thus the regression is specifically the all-candidate availability
requirement, not proof that measuring the departing item is harmful. The strict
arm further rejects ordinary unknown background changes. Do not hide this trade-off
by reporting only the correctly matched focused controls.

Isolated gain-only/loss-only content changes are rejected. However, a newly generated
whole screen changes two row colors in opposite directions without changing focus:
the actual pixel CLI returns departure/arrival and the actual scene CLI falsely
returns switch. Thus the rule cannot separate these visual causes. It loses valid
transitions without eliminating the key content ambiguity: do not deploy it.

Evidence: `artifacts/scene-evaluation/{protocol,result}.json` (18actual CLI checks),
`artifacts/scene-pixel-stress/audit.json` (two pixel calls plus scene call).
Tool usage: [diagnostic guide](../../../Research/FocusTransitionDiagnostic.md).

## Actionable next work

TTR's delivered48-pair proposal is aligned: four genuinely different structures
(composite card, ranked wide row, home icon, hero), two content luminances, two
backgrounds, three positions. First prove one example of each structure, including
what enlarges and parent/child bounds; then fill the matrix. This is a request for
implementation/contract planning, not new runtime dispatch from NUIAK.

Require stable scene/control IDs, measured whole-control and child/body roles,
original frames, actual focus, clipping, paired competitors and capture/action links
where available (otherwise explicit unknown). Retain no-op/content-change evidence;
gain/loss agreement alone must not create labels or action-success claims. Existing
request `nuiak-20261001-transfer10-coverage` remains the coordination identity.

Recommend structural successor before another unchanged training run; completing
17remaining same-slot pairs is not a consumer prerequisite. Genuine Settings
transition qualification still needs seven prepared endpoint reviews; do not relabel
unreviewed originals automatically. New data admission and runtime work remain separate.

## Verification and boundaries

- `python -m unittest` scene/alignment/intake/composition/sidecar/crop-readiness:
  93tests,2.371s,exit0 (`tests.log`).
- Actual retained aggregation18CLI cases pass; malformed inputs rejected without
  result, defaults disabled. Pixel counterexample preserves failed scientific outcome.
- Offline `swift build`:3.27s,no warnings; `swift test`:14XCTest+120SwiftTesting,
  zero failures (`swift-build.log`, `swift-test.log`). `git diff --check` passes.
- Output footprint checked below2GiB (`artifacts/output-budget.json`). No downloads,
  storage-service work, deletion or git writes. Pre-existing Alignment12changes preserved.
- Human sampled approval/data-use decision remain outside this completed preparation.
  No active background work is implied. [Peer publication](coordination.md).
