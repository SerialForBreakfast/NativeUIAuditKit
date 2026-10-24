# Teacher preservation and exact training anchors

Owner: Maximum-mini-NUIAK. Date: October 23, 2026.

## Outcome

The maintainer approves activation at an idle boundary. The teacher extension, T06 binding, and T93 catalog entry are active.
The runner stops new dispatch with no active attempt. No job is cancelled.
Exact source checks refresh 7 eligible unstarted approvals. Historical specifications and attempted jobs remain unchanged.
The same runner resumes with PID 51554. No capture, model promotion, or Standard change occurs.

## Contracts

T93 accepts pinned `membership`, `original`, and `suite` inputs. It selects only unchanged training members from the original manifest.
It rejects altered source fields, duplicate IDs, changed images, evaluation overlap, and missing class support.
It emits `anchors.json`, `summary.json`, and an artifact receipt.
The helper uses source IDs and actual hashes. It does not infer ancestry from filenames.

The T06 configuration adds `teacherPreservation` with pinned `model`, pinned `anchors`, and a positive finite `weight`.
Teacher targets use the current training tensors. The penalty adds no samples or optimizer updates.
Teacher inference uses evaluation mode with detached parameters. Epoch checks verify unchanged parameters and buffers.
The trainer records anchor presentations and updates. Teacher initialization preserves the student's CPU random state.
Targets are cached by image hash. Repeated rows keep their original training weight.
Frozen-encoder combinations, checkpoint continuation, and development-selected teacher training remain unsupported.
Default T06 behavior remains unchanged when the option is absent.

## Qualification

The staged focused suite passes 23 tests in 12.866 s.
Tests include the actual crop backbone, actual trainer checkpoint output, detached gradients, changed references, and evaluation exclusion.
The trainer smoke test uses CPU and one epoch boundary. It does not establish full-run MPS behavior or model accuracy.
The isolated queue executes 2 T93 descriptions and rejects an evaluation-overlap description.
The existing comparison compiler verifies retained losses and bounded branches. No scientific results are fabricated for qualification.
Activated sources pass all 23 focused tests in 14.194 s, including both integration tests.
Offline Swift compilation succeeds after using a fresh project-local cache. The original cache contains the parked checkout path.
The full Swift suite then stalls for over 3 min. Its log and process sample remain preserved.
Only the owned Swift test processes are stopped. The full suite remains incomplete, not passed.
The first test attempt omits the staged backbone file. The corrected staging layout resolves that failure.
Another fixture runs its negative job first. Explicit ordering allows both positive jobs to execute before the expected failure.

## Prepared experiment

TEACHER495-NATIVE compares one fixed penalty with completed NCTRL417 full adaptation.
The retained control teacher and its output receipt verify. Exactly 5,400 of 7,200 training rows qualify as anchors.
The anchors span 148 source groups. Repetition does not establish independent evidence.
The candidate uses unchanged initialization, seed 371, 30 epochs, and fixed-last selection.
All 17 native, artwork, no-focus, and consumer conditions remain in the comparison suite.
A separate Standard retention request reuses the candidate scores. It adds no fit or inference work.
Any lost Standard success or new wrong selection rejects replacement. HCF remains a separate optional slice.

`teacher495-training-anchors` is approved. Both comparison graphs are registered and approved with 36 new jobs.
Private configurations and staged graph: `reports/work/TEACHER495/`.
Staged sources are qualification artifacts, not the runner's active modules.
Fresh immutable specifications use the active source. The staged graph is not submitted.

The next substantial tranche is full matched review and a correction selected from measured losses.
No additional capture or TTR source change is needed for these comparisons.
Full-run teacher integrity and model acceptance remain separate runtime gates.
The fit remains bounded to 1,800 s and 2 GiB. This is a limit, not a measured duration or overnight workload.
Private activation receipts include `active-tests.log`, `source-refresh.json`, and `active-admission.json` under `reports/work/TEACHER495/`.
At 21:02 UTC, the teacher fit runs on PID 51554. The other 35 jobs await dependencies or result conditions.
The T93 producer completes with verified outputs. Its anchor file matches the pinned training input exactly.
Activation and admission take approximately 4 min after consent. The earlier estimate covers the wider 45–90 min implementation tranche.

## ADR spike summary

| Spike | Verified finding | Remaining requirement |
|---|---|---|
| ADR 10: difficult negatives | Retained no-focus cases preserve abstention. | Observed decoration and selection-state labels. |
| ADR 19: session reuse | Adapter and bounded comparison chain are prepared. | Recovery cleanup must pass before 4 comparisons execute. |
| ADR 24: failure sampling | Diverse selection covers more groups, but not more error categories. | Keep random selection as control; result remains inconclusive. |
| ADR 22: screen context | No qualified result is recorded. | Observed context labels and an isolated comparison. |
| ADR 14: OCR correction | Text-only correction loses 2 successes per related device variant. Geometry prevents those losses without gains. | Semantic role and hierarchy evidence across independent groups. |
| ADR 11: batch efficiency | Batch size 8 reduces median step time by 13.0% and 13.9% in 2 small CPU comparisons. | Broader workload and memory evidence before changing defaults. |

These results do not establish a new model improvement. See `ADRspikes493Results.md` for scope and retained evidence.
