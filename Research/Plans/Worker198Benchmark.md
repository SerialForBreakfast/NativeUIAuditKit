# WORKER198-B representative detector input handoff

## Next bounded outcome: resident full-trainer lifecycle

Kernel revision03 accepted; do not repeat it. Reuse its verified512training-only
examples/Run022initializer and resident8.4.173 environment to qualify the actual
Ultralytics training lifecycle. This is the remaining B integration work, not a
new model-quality candidate or C/D data substitution.

Worker implements a thin adapter around the resident trainer, not another training
loop. Two fresh repetitions, two epochs each, batch4,640square,workers0,AdamW1e-4,
nbs64,warmup_epochs0,constant learning rate,seed42,float32/AMPoff/TF32off; disable
augmentation/cache/pretrained downloads and resume. Preserve all41class labels.
Use the same training membership for validation explicitly as diagnostics only.
Retain normal validation, checkpoint and end-of-training paths. Record actual
shuffle/order and optimizer updates; expected128minibatches/epoch and8updates,
16updates/run. If resident behavior differs, report the mismatch without silently
overriding internals or changing the target count. No kernel-to-full speed claim.

Before execution: input/source/environment checks, resolved configuration and
output collision/storage guard; focused tests on count instrumentation, missing
weights/data, accidental download/resume and diagnostics-only validation role.
Record source/config hashes and run registration locally before launch. Within
this bounded assignment, passing preflight/tests permits execution and a combined
source/result return; no additional proposal-only exchange. Any material config,
data-role or trainer-loop redesign returns for review first.

Budget1800seconds/2GiB for both repetitions; single GPU job, first failure stops,
no automatic retry. Capture actual optimizer events and validation invocations;
split setup/train/validation/save/final-validation time without double-counting.
Keep checkpoints locally and verify resident reload/inference finite on the same
two training smoke examples. Return compact source/tests, raw lifecycle events,
effective config, terminal counts/timing/memory and hashes, not weights/images.
No held-out accuracy, promotion, Mac comparison or installation is authorized.

Acceptance establishes a reusable full-trainer worker path. NUIAK subsequently
supplies C/D's eligible evaluation bundle; those jobs remain separate and gated.

## Memory-qualified revision after attempt02 OOM

Returned traceback confirms batch8 float32 forward OOM during disposable warmup:
7.60GiB device,6.94GiB Torch allocated,51.19MiB device free,14MiB failed allocation.
No timed repetition completed; warmup optimizer updates were not instrumented before
failure and must remain unknown. The environment/launcher issue is resolved.

One new finite revision compares physical batch2/4, two repetitions each, retaining
512ordered examples,640square,float32,nbs64 and8timed optimizer steps. Accumulation
32/16 respectively. Warmup exactly64examples (32/16batches) so both execute one
disposable optimizer step, then restore all state/loader as before. Record warmup
updates separately. Lower physical batches change batchnorm behavior; matching
accumulation is not numerical/quality equivalence. No AMP, resolution, model or
snapshot-policy changes in this comparison. First failure/OOM stops without sweep.

Worker may implement only these explicit parameter/counter changes, test cadence,
full512order and state restoration for both batch sizes, then execute once if all
preflight/tests pass and fresh output/storage checks succeed. Record source hash
before launch and return changed source/tests with timings. Any broader change
returns for review before execution. Same1800seconds/2GiB, no installation, no
production-speed or model-quality claim. This replaces the non-fitting8/16arm,
not an unchanged retry; remaining model training remains independently actionable.

## Resident benchmark policy reconciled

Historical decisions below explain the progression. The batch2/4 revision above
is the sole current execution contract; older batch8/16 and ten-batch warmup text
must not be used for a new launch.

October6 receiver reports corrected intake complete and two-example CPU/CUDA smoke
passed. Accept8.4.173for worker-only batch8/16comparison, not parity with Mac8.4.124.
Implement one512-example timed epoch, two repetitions, warmup_epochs=0 during timing,
fixed nbs64accumulation with measured8updates per epoch. Disposable10batch warmup
must restore all state including batchnorm buffers and accumulation counters.
Record rect-induced tensor shapes: differing shapes confound a pure batch-size claim.
The immutable implementation request contains runner acceptance and bounded return
requirements. Source/test review still precedes full benchmark launch.

## October 6 receiver correction and compatibility stage

The receiver verified the archive but correctly rejected the initializer against
our undersized member limit. Preserve the delivered archive. A supplemental request
permits only its exact 40,539,244-byte initializer (SHA pinned in the manifest) up
to 41,000,000 bytes; all other members remain capped at 32,000,000 bytes, total
60,000,000 bytes and 1,100 members. Future packers must validate these bounds before
publication and serialize them in the manifest.

Pixel hashes bind UTF-8 `str((width, height))`, including parentheses/comma/space,
followed immediately by Pillow-converted RGB uint8 row-major bytes; no EXIF
orientation operation. They are not hashes of RGB bytes alone. Record the encoding
and a fixed test vector. File SHA remains the transfer-integrity authority.

Authorize one resident 8.4.173 CPU/CUDA float32 inference compatibility smoke on
the first two ordered manifest examples, with TF32/AMP disabled, no augmentation,
640 letterbox and identical preprocessed tensors. Maximum 10 minutes/256 MiB new
outputs, no retries, installation, training or promotion. Record actual versions,
checkpoint/input hashes, preprocessing, output shapes and finite checks. Compare
raw pre-NMS outputs using atol=1e-4, rtol=1e-3 as a diagnostic tolerance, reporting
max absolute/relative errors and post-NMS disagreement separately. A failure is
diagnostic evidence, not authority to relax thresholds. This only tests the resident
worker backend; it does not establish 8.4.124 parity or cross-machine speedup.
Return the instrumented benchmark runner for review alongside the smoke, preserving
nbs64 optimizer cadence. Full B training timing remains a subsequent stage.

Package512distinct admitted ROI196 training crops, selected deterministically by
SHA256(imageID), with unchanged all-class labels, parent/group/window lineage,
41-class mapping and Run022 initializer. No evaluation or local-only GLOBAL146
focus tensors. Selection is a throughput workload, not an independent accuracy set.
Preserve original training corpus and use a new ignored output directory.

Bound packing to1GiBpayload/2GiBnew outputs. Verify source seals, every image/label
hash, decode, label geometry and decoded-pixel uniqueness before archive publication.
Return exact archive members/bytes/hash via the existing named SMB receipt protocol.

The package unlocks worker preparation, not unchecked execution: local Ultralytics
8.4.124 differs from worker-reported8.4.173. Worker must identify supported source
parity or an explicit version-difference arm without installing/downloading. Preserve
all finite checks. Ultralytics accumulation (`nbs=64`) means512examples/batch is not
necessarily optimizer-update count: instrument actual updates and report accumulation.
Do not copy the tiny-head assumption of64/32updates into this detector workload.

Preprocessing is existing640letterbox, all augmentations disabled, float32/no AMP,
workers0, fixed order/initial weights, fresh optimizer state. Use AdamW/lr1e-4 as the
recorded training baseline; benchmark scheduling/validation policy and CPU/CUDA parity
tolerances require an executable reviewed runner before launch. Candidate checkpoints
from timing tests are discarded from promotion consideration, not selected by accuracy.
Two repetitions; batch8control, batch16conditional on memory, no third arm yet.
Training-only diagnostics may be scored, never called held-out evaluation.

Acceptance of this handoff:512unique intact examples, exact class/lineage/config pins,
bounded regular-file archive, no protected images, verified transfer and distinct
worker acknowledgment. Full B acceptance still requires timed execution/parity/reload
evidence. NUIAK retains ownership of experiment approval and final efficacy judgment.
