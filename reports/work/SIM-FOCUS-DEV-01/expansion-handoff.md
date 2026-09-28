# Simulator training-data expansion — usable data ready, model decision pending

2026-09-27 local / 2026-09-28 UTC. Supersedes the earlier12-pair smoke handoff for
current status; its immutable evidence and original manifests are preserved.

## Outcome

**52 reviewed native-bracket pairs admitted as training candidates**, including40
new pairs from ten completed jobs. The real assembly preserves all221 original
candidate pairs and9 retention pairs, and adds52: **273 training pairs /546 crops,
9 retention pairs /18 crops**. No model run, new weights, export or promotion.

| Outcome | Evidence / limit |
|---|---|
| Software | Actual review/import/assembly integration;93 focused regressions and offline Swift build/123 tests pass. |
| Data | 52 pairs admitted;104 frame files/65 distinct frames;104 crop uses/102 distinct crops. All related Fixture development sources, not independent validation or native Photos. |
| Integration | Three calibration plus ten four-control expansion jobs completed through matched local TTR, native-v2 export, verified receipt and production crops. Nine-control dock blocked; remote EXT-CAP unqualified. |
| Model gate | Unassessed. Original ten independent-coverage blockers and existing selection policy retained. No run allocated or new candidate/validation inference performed. |

## Complete collection accounting

Frozen plan: `expansion-plan.json`, SHA256
`48761ff75e446e8e26567f5dc7e664e9596a70da189119423a2e67996734df55`.
New collection target94 pair slots:40 captured,9 slots in the failed r02 job,
45 not attempted after its geometry failure. These are target slots—not54 known
corrupt pairs or a silently reduced success denominator. Prior12 pairs retained.

Successful new recipes r01/r03/r05/r07/r09/r11: grid_matrix,4,dark,regular,standard,
seed20260928 with artwork,bright_unfocused,gray_placeholder,blank_placeholder,
high_contrast,photos_like. r13–r16: media_shelf,4,high_contrast,spacious,standard,
same seed with artwork,bright_unfocused,gray_placeholder,photos_like. Prior12
calibration pairs include the working four-control photos-like dock. All use one
conservative related group; different palettes/seeds are not independent sources.

Every completed job exported18 files: **234 original files /603,875,651 bytes**
reverified against producer sizes/hashes. All52 pairs pass native labels, per-state
geometry, strict source intake and16%-expanded256×256 production cropping. Agent
visual QA covers all104 crops plus numbered full-frame context in13 sheets.
[Visual review](expansion-visual-review.md) binds the inventory and exact IDs.

All52 pairs admitted;0 complete-pair duplicates,0 contradictory-label exclusions,
0 evaluation-overlap exclusions. Two positive crops repeat between old bright
`synth-0/1` and r03 `synth-0/1`; their negatives differ. Preserve these matched pairs
but report102 distinct crop pixels, not104. Repeated baseline frames also do not
inflate independent support. Whole-screen unique-focus accuracy is not established:
the unfocused target's baseline focus is on Reference frame outside the target set.

Nine-control dock job300649B2-3A37-4E67-8619-1CEFCD9BA633 failed
`telemetry_bracket:identityMismatch` before/after focus observations. Two controls
were partly/fully clipped; clipping is observed, not proven causal. No failed-job
artifact admitted or unchanged retry. r04/r06/r08/r10/r12 remain unattempted.
[Amendment and resume condition](expansion-amendment.md): producer-backed remedy
or separately reviewed changed geometry. Fresh readiness/settled state passed
before unrelated four-control work continued. No telemetry checks were weakened.

## Admission and reproducibility

`scripts/focus_fixture_review.py` renders retained evidence only; no inference or
automatic approval. `scripts/focus_training_extension.py` reconstructs the immutable
base, checks reviewed additions with current production crops, accounts for every
pair and preserves retention, sampling, configuration and launch blockers. Existing
assembly/trainer entrypoints dispatch this version explicitly. Source manifests
remain development-purpose; thirteen hash-bound `focus-source-review-v1` records
approve training candidate use under the maintainer's present assignment.

Base historical runtime replay is not widened to new inputs. The frozen reserved
validation/final-challenge crop metadata supplies exact-pixel overlap checks; no
reserved final-challenge pixels are opened, scored or visually mined. Historical
protected evidence is revalidated by the unchanged base assembly, without scoring.

Extension protocol:
`53d358966d36e0c36387eae84e9cdf488fb46676885ad908986fe5b8d445a4de`.
Actual assembly CLI completed successfully with564 rows. Actual trainer preflight
completed with configurationValid=true,launchEligible=false,executionAuthorized=false
(expected exit2, empty stderr). All ten original independent appearance-validation/
final-challenge coverage blockers remain, plus missing_experiment_approval because
no exact launch protocol has been approved/recorded. Merely adding an approval file
cannot remove the ten coverage blockers; tests verify that separation. Sampling
mass remains0.5 Fixture/0.5 native (floating-point representation on the latter).
This is a successfully executed readiness check, not a model-launch pass.
Ordinary dataset-mode preflight rejects this extension with
`development_protocol_requires_explicit_experiment_mode` (expected exit2).

Key retained artifacts (all paths relative to this report directory):

- `frozen-input-index.json`: exact source manifests/reviews, receipts, base, reserved metadata, code and protocol hashes.
- `extension-input.json`, `training-extension/focus_dataset_manifest.json`: reproducible actual assembly inputs/result.
- `expansion-accounting.json`: every corpus, receipt bytes/hashes, duplicate pixel uses, pair dispositions and preserved base.
- `review-sheets/inventory.json` and13 numbered PNGs: full-frame context, pairs and exact image/bounds bindings.
- `source-training-reviews/`:13 explicit immutable source reviews; no raw split rewrite.
- `extension-preflight.json`, `extension-default-path-rejection.json`: real trainer checks; no execute flag used.
- `expansion-regressions-final.log`, `expansion-swift-build.log`, `expansion-swift-test.log`:93 Python tests, zero-warning offline build,14 XCTest+109 Swift Testing passes.

Final read-only verification checked all53 frozen references and104 reviewed
frame/crop bindings against the visual inventory. Both preflight output directory
names remain absent: no model/training directory created. `git diff --check` passes.

Raw trees: `dataset/tvos_captures/sim-focus-dev-01-{smoke,bright,dock}` and
`dataset/tvos_captures/sim-focus-expansion-rNN`. Reviewed/QA production crops are
under matching `dataset/focus_ring/` directories. Bulky evidence is gitignored.
No original file deleted or overwritten. Assembly reproduction uses the ordinary
`focus_mixed_assembly.py --input …/extension-input.json --output <fresh-project-directory>`;
preflight uses `train_focus_ring_detector.py --experiment-protocol …/training-extension/focus_dataset_manifest.json
--experiment-arm warm-stretch --name <unused-safe-name> --preflight`.

## Remaining decision and priority

The source data is usable; the original model selection policy still lacks required
independent appearance validation/challenge support, including Photos buttons.
Do not ask again for generic Simulator permission. **Human decision:** approve the
[one bounded retention-selected development experiment](selection-decision.md),
or retain full selection requirements and collect eligible independent coverage.
The proposed change selects only among epochs retaining18/18 accuracy on the nine
existing native retention pairs, by minimum retention BCE. That is deliberately
weaker development evidence and must not be smuggled into the full protocol.

Meanwhile TTR's next action is the scoped nine-control bracket diagnosis, already
published/read back at `/Volumes/SharedStatusFile/nuiak/status.yaml`; no peer
acknowledgment is claimed. [Coordination receipt](coordination.md). Local success
does not qualify remote pairing or profile switching. No custom photograph/Top
Shelf asset pipeline, Photos telemetry, arbitrary focus-color control, dense-grid
support or physical transfer has been demonstrated by these procedural examples.

All capture jobs are terminal. Final coordinator evidence has no active command
or observation,queue0,disconnected,NUIAK disabled. Simulator/Fixture left running;
no unrelated resource released. About40GiB disk remained after collection.
Recurring helper diagnostic-file persistenceFailed24 remains an observed logging
limitation, not a capture failure or permission to repair the producer.
