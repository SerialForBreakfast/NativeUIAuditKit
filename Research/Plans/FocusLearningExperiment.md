# FOCUS-EXP-01 — bounded native focus learning experiment

Assigned by maintainer 2026-09-22: “ok lets do the experiment,” following the
methodology review. Experimental learning is separate from the 6,000-pair release
milestone. This assignment authorizes the bounded local simulator collection and
four comparison arms below, not promotion, Office, TTR operations or broad DFS.

## Inputs and acquisition

Reuse the reviewed 12-pair native Settings-root development batch. Add independent
recorded visits to General and Accessibility on exact simulator
9026ECA9-77DB-4AE6-8FE6-BB239E9571FA. Verify boot/runtime and no competing runner
freshly. Each visit: activate Settings; verify root; at most 15 Up/Down setup
inputs to the named submenu; one freshly verified Select on that known disclosure;
at most 40 Up/Down capture inputs / 300 seconds; one Menu return and root check.
No submenu value/action may be selected. No settings, accounts, VoiceOver, Home,
restart or installation other than the existing isolated test runner. Normal
Xcode/simulator storage is in scope; explicit artifacts/caches remain project-local.
Unknown context/focus/cleanup stops that visit without replaying Select.

Acquisition refinement after General trial01: the native list contains25 focusable
rows, so a full reverse sweep cannot fit40inputs. Use top-boundary then bottom-
boundary coverage and one Menu return; a second full reverse pass adds no required
pair diversity. Preserve trial01 as partial, not admitted. A freshly verified
known submenu title permits one Menu reconciliation before the next bounded visit;
unrecognized contexts still stop. No setting selection or service restart.

Runtime refinement: FDR-002 exhausted its600s limit importing cold dependencies,
before any epoch/checkpoint. Preserve it as a failed runtime attempt. A subsequent
import-only probe completed in0.717s with MPS, permitting one explicitly logged
replacement (FDR-006), identical protocol. The serial launcher enforces a600s
external deadline including imports, not only cooperative batch checks. This is
not an automatic retraining loop or permission to retry poor validation results.
Host execution also requires the standard macOS-managed Metal shader cache for
MPS, outside the package. A separately scoped approval for that runtime cache was
obtained and a scalar MPS check passed. Explicit datasets/logs/checkpoints and
configured application caches stay project-local; no HOME spoofing or cache deletion.

Accessibility trial01 entered the correct page but the anticipated VoiceOver row
is absent in this simulator's visible interface. The passive postflight screenshot
confirms Accessibility/“Hover Text”; use that observed entry marker, not a guessed
physical-device row. No capture input or setting selection occurred after entry.

Freeze ROOT + GENERAL as experimental training, ACCESSIBILITY as validation before
viewing its model scores. Keep each screen journey and related variants together;
reject exact crop/full-frame leakage across the two partitions. Shared native
list styling makes this a **same-app screen-group experiment**, not independent
app/OS-family generalization. There is no final-test partition or release claim.
The earlier root batch is already development data and remains so. Manual visual
review bound to manifest hashes is required before launch. Missing groups block
the model comparison, not safe software preparation.

## Frozen comparison

Four arms: random initialization versus strict FDR-001 checkpoint initialization,
each with production 16%-expanded stretched crops versus 16%-expanded aspect-fit
black-padded crops. Same source pairs, labels, split, seed42, MobileNetV4 architecture,
RGB/255, AdamW LR0.0003, batch8, 8epochs, no augmentation. Maximum600 seconds per
arm, no downloads. This small fixed-budget comparison is not a claim of convergence
or optimal hyperparameters. Do not tune thresholds or rerun based on validation
results. Record pre-training scores and per-epoch validation loss; select minimum
validation-loss checkpoint, report both initial/final-selected metrics at0.5/0.85.
AdamW retains the existing defaults: weight decay0.01, betas(0.9,0.999), eps1e-8;
constant learning rate, BCEWithLogitsLoss, no early stopping. Device/runtime version
is recorded; a fixed seed is not a claim of cross-device bitwise reproducibility.

Use the existing trainer with a separately validated `--experiment-protocol`
entrypoint; ordinary production preflight stays unchanged. Hash-bind all inputs,
reviews, warm checkpoint and config; log each arm before execution. Strict-load
checkpoint compatibility, finite tensors, image/source hashes, disjoint groups,
new outputs and actual caller integration are required. Save protocol/runtime,
wall time, weights, and predictions. No CoreML export or package replacement here.

Shipped CoreML baseline uses production crops only. Unmodified PyTorch FDR-001
scores on identical production crops provide an export/runtime parity check; report
differences rather than assuming these artifacts behave identically. Crop variants
are diagnostic helper modes, not changes to shipped inference defaults/public API.

## Verification and handoff

Tests cover missing/tampered manifests, reviews, checkpoints, groups, labels,
duplicate pixels, unsafe paths, unsupported config, output collisions and default
production-gate preservation. Compile native runner; focused Python/Swift tests;
full offline package build/tests once integrated. Genuine capture/visual review,
training completion and model performance are separate evidence.

Deliver all four arms or exact input/runtime blocker, confusion matrices/loss,
paired comparisons, limitations, and ranked next data needs. No tiny-test result
can pass release gates. Preserve unsuccessful trials. Next is a reviewed acquisition
batch targeted at remaining errors, plus complementary qualified TTR data when
available; no automatic training loop.
