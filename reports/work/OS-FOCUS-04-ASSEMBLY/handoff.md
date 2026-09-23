# OS-FOCUS-04 mixed-source assembly — completed for review

2026-09-23 UTC. Base revision `11ce83e`; pre-existing dirty iOS, producer intake,
export, perception and acquisition work preserved. No capture, training, model
inference, promotion, other-repository edit or SMB operation.

| Outcome | Result |
|---|---|
| Software verified | Pass: real source adapters, assembly CLI, trainer preflight/sample loading;89 focused tests, offline build and14 XCTest+93 Swift Testing tests |
| Data eligible | Development inspection only:49 retained native pairs+2 direct dialog pairs; full training blocked by review/approval, missing test membership and fixture quotas |
| Integration qualified | Local retained-data assembly and production crop path pass; no new producer/live-runtime qualification |
| Model gate passed | Not assessed. All existing weights preserved; no new quality claim |

## Delivered

- `scripts/focus_mixed_assembly.py`: versioned native/fixture adapters; immutable
  original/crop hashes, decoded-pixel and related-group isolation; source/runtime,
  label, scene/style/control lineage; training-only sampling; additive retention.
- `scripts/focus_training_preflight.py` and `train_focus_ring_detector.py`: actual
  dataset dispatch, configuration versus launch eligibility, frozen weighted training
  sampling, assembly/log binding, validation-only checkpoint selection. Existing
  fixture and small-experiment paths retain compatibility; no new trainer.
- [Contract](../../../Research/schemas/focus-mixed-assembly-v1.md), canonical plan,
  queue, current state, roadmap and confirmed lesson updated.

Additions cannot drop old samples or move their partitions. A review-only revision
must bind its predecessor and preserve all sample truth/bytes/lineage/partition;
only admission blockers can change. Diagnostic sources remain visible without
counting toward training/quota gates. Unknown source relationships still block.
The assembly is not self-authorizing: explicit source/corpus review and separate
run authority remain required. Home/Photos visual-only reviews remain rejected as
training input. Native AX interval and fixture frame-label semantics remain distinct.

## Real evidence

Initial root integration correctly refused old cropper identities: old source
`c40042b2…`, helper`2500a5f1…`; current source`5fc98a9d…`, helper`b5dd6cf5…`.
No stale manifest was edited. The existing native intake CLI rebuilt only derived
root crops from unchanged attachments; [all24 crops reviewed](root-review.md),
12 pairs retained. Later General/Accessibility/Apps inputs were already current.

[Final assembly](final/mixed/focus_dataset_manifest.json) digest:
`40fd7aac2397145bbe6d9ae53010dea38edc765d38c09a987bef9c46b284138e`.

| Partition | Pairs | Crops | Meaning |
|---|---:|---:|---|
| Train |40|80|Prior native development assignments retained; not new production approval|
| Validation |9|18|Prior same-app development validation, not final test|
| Development |2|4|Existing direct Fixture dialog, explicitly ineligible for training|
| Test |0|0|Missing independent final-evaluation membership|

The additive CLI retained all98 native samples and added4 dialog samples. No
cross-partition pixels/lineage, duplicate pairs or conflicting crop labels were
accepted. Original sources, failed pilot outputs and old model results are unchanged.
Unknown native themes remain unknown, not invented light/dark metadata.

Real trainer `--preflight` exits2 as expected with configurationValid=true and
launchEligible=false. Exact blockers: `missing_corpus_approval`,
`missing_required_partition`, `source_training_review_required`, `underfilled_quota`.
The dialog's development-only restriction is reported separately. No training
directory, checkpoint or experiment ID was allocated. [Summary](final/summary.json).

## Acceptance and verification

| Criterion | Evidence |
|---|---|
| Native and fixture contracts retained | Real native+v1.4 integration; existing fixture/v2 tests remain green |
| Deterministic membership and additive retention |15 new tests; final native→mixed CLI addition preserves98 samples |
| Corruption, predictions, visual-only, split/label conflicts rejected | New negative tests plus existing source validators |
| Training-only weights and approval behavior | Validation/development repetition leaves weights unchanged; positive eligibility uses explicitly mocked quota/runtime only, never genuine qualification |
| Actual trainer integration | Real preflight exit2 with exact expected blockers; sample loader/positive mocked preflight verified without Torch import/training |
| Offline package checks | [Final verification](final-checks/verification.json): Python89 pass, Swift build/test exit0, no warnings |

Reproduction commands and timings are in [final execution](final/execution.json)
and [verification](final-checks/verification.json). Final native assembly32.53s,
mixed33.76s, trainer preflight34.08s; crop source validation is the dominant cost.
Focused tests3.36s, build0.71s, Swift tests3.34s. Earlier verification/assembly
iterations are retained separately and are not substituted for final evidence.
No external peer wait or simulator capture time. Approval-wait duration was not
instrumented. Two-image crop batches respect80MP limits; no measured speedup claim.

## Next meaningful model work

Use this completed assembly path to admit **different focus appearances**, not
rerun Settings-only epochs. Next bounded data tranche: audit the retained completed
Fixture recipe groups for a separately scoped, reviewed development corpus,
accounting for incomplete kitchen-sink recipes and clipping; never manually mark
the partial42-recipe pilot complete. Keep pilot lineage out of final evaluation.
Choose native/custom tiles, buttons and light/high-contrast hard negatives to target
the observed Home/Photos failures. Fresh capture needs its own authorized scope.

Before training, freeze one mixed-appearance experimental protocol and explicit
data admission if below the full6,000-pair milestone; do not pretend that a small
experiment satisfies production gates. Preserve Settings validation as a forgetting
diagnostic and Photos/Home as development-only regression checks. Select checkpoints
on validation only; compare source-level positive recall, false positives and
unique/wrong/no/multiple-focus decisions. Check export parity on unsaturated
examples. Training authorization and a pre-launch log remain separate prerequisites.

Software tranche is complete for review. No process remains running. Coordination
not applicable: this does not change the peer's next action; existing TTR artifact
request is untouched. Model-workflow and worker-execution skills guided production
crop reuse, no-training preflight, integrated verification and this bounded handoff.
