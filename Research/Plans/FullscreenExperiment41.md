# Approved full-screen experiment and page-dot regeneration41

Maintainer subsequently removed training time constraints until further notice and
requested continued training. FSF002 is a fixed10epoch comparison using the same
initial checkpoint, exact data and scoring, with no wall-clock deadline and2GiB
output cap retained. Evaluate fixed-last once;500screens are previously exposed
held-out synthetic development evidence, not untouched final testing. This tests
whether a longer fit reduces FSF001's75misses without introducing false positives.
No hyperparameter sweep or checkpoint selection from evaluation results.

FSF002 diagnostic extension: final scoring regressed425→194exact screens, with
zero false positives and all166bottom-position targets missed. Replay both fixed
checkpoints on the same500evaluation images at candidate confidence.001, retaining
scores and matching each annotated control. This distinguishes missing localization
from confidence collapse; replay the declared.25score for consistency. Thresholds
remain unchanged for the experiment conclusion. Maximum1,000image inferences and
128MiB diagnostic output within the existing2GiB tranche output envelope. No refit.

Execution note: fit completed238.57seconds; combined300second child expired during
scoring. Retain partial receipt and finish the same fixed-checkpoint evaluation in
a separate300second/64MiB phase within the1800second tranche envelope. No second
fit, checkpoint selection or threshold change. Initial partial scoring emitted no
recoverable predictions, so the terminal pass reprocesses all500frames; it is not
claimed as exactly-once computation. New evaluator retains progress for recovery.

Maintainer approved this tranche after40: exact2000training/500evaluation full
scenes, preserving native26configuration groups, and regeneration of666affected
iOS training examples into a new version. No validation/test reassignment.

FSF001: does one epoch of full-scene YOLO learn useful native focus localization
on configuration-held-out synthetic scenes? Resident yolo11n.pt initialization,
640px, batch8, seed42, one epoch, no augmentation, fixed-last terminal evaluation
atconfidence0.25/IoU0.5. Owned child300seconds including recheck/fit/scoring,2GiB
output; full tranche1800seconds model execution. Exact membership and source
identities in generated contract/admission. Partial training is an execution result,
not a model-quality verdict. Diagnose a failed boundary before any scoped repair.

iOS: render the666sealed members using their original seeds/configuration, fixed
page-dot capture order and existing ScreenshotCapture/AnnotationWriter. Keep new
outputs separate; verify counts, IDs, PNG hashes, boxes and normalized coordinates.
Bound native generation to1200seconds and2GiB outputs. Use installed iOS26.5 runtime
and project-local explicit staging; declare standard Simulator/Xcode storage.
The resulting images reflect the current runtime, not historical OS reconstruction.
New validation coverage and iOS model retraining remain a subsequent data decision.
Verify the replacement export has exactly the666sealed members and all supported
control labels, not only the corrected page-dot label. Retain generated dataset
indexes locally rather than introducing training payloads into version control.

Serialize GPU training and Simulator rendering for interpretable timing. Build and
prepare independent work during preflight/training, then render. Finish automated
tests, status, measured results and next substantial recommendation in one handoff.
