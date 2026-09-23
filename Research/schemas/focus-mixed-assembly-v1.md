# FocusRing mixed-source assembly v1

Implementation: `scripts/focus_mixed_assembly.py`. Canonical assignment:
[OS-FOCUS-04](../Plans/NativeOSFocus.md#os-focus-04--incremental-native-and-fixture-corpus).
This is a NUIAK derived-data contract, not a TVTestRig wire change.

## Inputs and invocation

`focus-assembly-input-v1` requires `sources` (unique IDs), a local hash-bound
`baseline` file reference, and optionally a hash-bound `previous` assembly manifest.
Every file reference is `{ "path": "project/relative/file", "sha256": "..." }`.
Each source is `{ "id": "stable-source-id", "manifest": <reference>, "review":
<reference> }`. References reject missing files, traversal, symlinks and hash drift.

Each external `focus-source-review-v1` JSON contains:

- `manifestSHA256`: exact source file bytes, not the source's internal content digest.
- `reviewer`, `reviewReference`: reviewed evidence attribution, not authentication.
- `priorUse`: `development`, `untouched`, or `test-only`.
- `relationshipsKnown`: explicit cross-source lineage review; false blocks launch.
- `trainingApproved`: source-specific approval; false blocks its active training,
  validation or test use, but permits retained diagnostic membership.
- `pairs`: exact pair-ID mapping to `partition` and canonical `relatedGroup`.
- Optional `priorReview` hash-binds an older review. Optional `supersedesReview`
  binds the prior review when revising admission without altering membership.

Run with the approved project interpreter, from the repository root:

```sh
python scripts/focus_mixed_assembly.py --input <input.json> --output <new-directory>
python scripts/train_focus_ring_detector.py --dataset <new-directory> --name <unused-name> --preflight
```

Assembly produces only `focus_dataset_manifest.json` in an exclusively new directory.
Images/checkpoints remain at their original paths. Preflight imports no Torch,
launches no model, creates no training output and returns exit2 for blockers.
Native and runtime-fixture validation may invoke the offline production crop helper;
this is not a metadata-only check, simulator operation, or model inference.

## Source behavior

Native `native-os-focus-dataset-v1` sources must be complete, source-hash-bound,
runtime-current and reconstructed through the native journey/pair validator.
Stored bounds/truth must equal reconstruction; crops must equal current production
pixels. Old runtime crops require a separate preserved recrop/review, not relabeling
their identity. Legacy missing `screenID` retains the established `settings/root`
interpretation. Style remains `unknown`; AX kind is not renamed a fixture class.

Fixture v1.2–1.5 use their existing strict source validators. V1.2 remains Pillow
inspection evidence, not runtime-parity training data. V1.3 may advance with
review/approval and all required gates. V1.4/v1.5 remain development-only. Pair and
frame label-source strings remain distinct, including native AX interval evidence.
Visual-only Home/Photos review manifests and prediction-derived labels are rejected.

All source original partitions are retained except reviewed native development
membership may be assigned train/validation for a separately approved experiment.
Development-used data cannot become untouched final test. No derived manifest or
passing parser is execution authority or authenticated device identity.

## Frozen output and incremental additions

The output binds input references, samples with original/crop file and decoded-pixel
hashes, geometry, truth, runtime identity, source kind, intrinsic/related lineage,
partition, scene/style/control support, and eligibility blockers. Its canonical
content digest is `assemblySHA256`; trainer preflight reconstructs it before use.
Cross-partition decoded-frame/crop duplicates or related groups reject. Duplicate
pairs and same crop pixels with contradictory labels reject within partitions too.
Multiple different elements sharing one source frame remain valid pairs.

`sampling` freezes equal source-kind/scene/style/control-stratum weights using
**training samples only**; the total weight equals the training sample count.
The existing trainer uses these weights in seeded sampling with replacement, not
validation/test statistics. Both labels of a pair retain equal weight. This is a
declared sampling policy, not a demonstrated model-quality improvement.

An additive version retains every old input manifest and sample; no deletion,
repartitioning or relabeling. It records added source/sample IDs and review revisions.
A superseding hash-bound review can change admission blockers only; unchanged
samples retain bytes, lineage, prior-use classification and split. Historical
versions remain readable evidence, never overwritten.

## Training boundary

The assembly CLI additionally dispatches `focus-development-input-v1` to the
[separate development-experiment adapter](focus-development-experiment-v1.md).
Its output is not `focus-mixed-assembly-v1`: production loading still rejects it.
Existing production source admission, additive retention and quotas below are
unchanged. Experimental role mapping is explicit, never a rewritten source manifest.

Full preflight retains the established30-epoch/64-batch/3e-4 MobileNetV4 configuration.
The baseline reference is for later comparison, not an implicit warm start.
Only fixture rows count toward fixture scene/theme/hard-negative quotas; native
Settings rows are auxiliary. Development-only rows neither train nor satisfy quotas;
their blockers are separately reported. Unknown cross-source relationships still
block launch. Configuration validity and launch eligibility are independent.

After actual corpus review, `training_approval.json` beside the assembly must contain
`version: focus-assembly-approval-v1`, `approved: true`, `assemblySHA256`, `reviewer`
and `reviewReference`. This file must reflect real maintainer approval; agents must
not create approval to remove a blocker. Execution additionally requires separate
authority and an experiment-log entry binding exact assembly digest/run name.
Validation selects checkpoints; test membership is not loaded during training.
No production replacement or model gate follows from assembly acceptance.
