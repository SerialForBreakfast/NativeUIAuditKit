# Full-screen input isolation and rendered page-dot repair

## Outcome

The USB full-screen loader and terminal-only evaluation caller are integrated.
All2500native26screens qualify:2000train/500evaluation in their original10groups,
zero image-copy bytes. No new model-quality result: full-scene admission is still
a draft, distinct from earlier target-crop admission.

The page-dot source repair now passes real iOS rendering, not just syntax checks:
16cases,2templates×2canvas widths×4counts. Both templates report25/40/55/70point
widths and10point height. Inspected MediaCardGrid430/five-dot and ProgressActivity375/
two-dot overlays; boxes fit the visible group. This qualifies the repair, not the
unregenerated666old corpus members or other OS versions.

## Evidence

- [Input result](input-result.json), [exact v2 draft](run-draft-v2.json).
- [Read-through benchmark](readthrough-benchmark.json): full decode qualification
  211.15seconds; subsequent all-byte recheck22.17seconds. Actual two-image USB
  preprocessing0.244seconds after import. This is not a training throughput estimate.
- [Python tests](python-tests.log):22tests, including13legacy runner regressions;
  [related tests](related-tests.log):13. Real resident YOLODataset transforms exercised;
  training caller uses a model double. Real gradient execution remains pending.
- [Swift build](swift-build.log), [Swift tests](swift-test.log):14XCTest+120SwiftTesting.
- [Native probe log](page-dot-executed.log):1test,16render cases,0failures;
  [attachment manifest](page-dot-images/manifest.json):32raw/overlay images.

## Implementation and boundaries

V2 direct reads narrowly accept the mounted native26USB subtree or project files.
Per-source hashes, pixel-duplicate and group checks remain. No original-adjacent
label or `.npy` caches are used. Both training and its unused validation loader
contain training membership only; validation/final-eval hooks are disabled. The
explicit terminal caller loads `last.pt`, checks requested epochs completed, then
scores evaluation once. Confidence0.25, matchingIoU0.5, NMSIoU0.7. TP/FP/FN and
exact-frame counts are separate; these are synthetic configuration-held-out metrics.

The parent validates/decode-checks once. Its prepared record is hash-bound into the
owned child's environment; the child rechecks every original byte hash, annotations,
admission, runtime and code, reusing pixel identities only for unchanged bytes.
The existing300second/2GiB supervisor remains, including child recheck/training/
terminal scoring; partial/timeout runs stay partial. Parent preflight is separately
measured. No admission flag was changed.

Native operation: local Xcode built GeneratorRunner into `.build/page-dot-40`;
iOS26.5targetF3EF9DB8-0B0F-4757-B653-D1628269F6FF, two canvas widths on one runtime.
First invocation skipped because SIMCTL_CHILD flag did not reach XCTest; retained
as skipped evidence. TEST_RUNNER flag executed the real probe. Attachment export
needed scoped host TestReport service access and succeeded without recapture.
Simulator cleanup found the selected device already Shutdown. Normal platform
storage was declared; all explicit artifacts are project-local. TTR update deferred.

## Next substantial tranche / decision

Approve exact full-scene use of2000training+500evaluation frames, keeping original
groups, for one bounded full-screen YOLO experiment with resident initialization,
one epoch, batch8,640pixels,seed42,300childseconds and2GiBoutputs. This evaluates
the trained detector on complete scenes; it does not automatically produce a fair
head-to-head crop comparison because that model previously scored nominated targets.
Use the existing frozen real-screen benchmark for a separately scoped transfer check.

In parallel, regenerate the666faulty page-dot training members into a new corpus
version with the verified source repair, preserving old evidence. Add genuinely
new validation cases under an explicit grouped split decision before retraining.

Software verified; input integrity qualified; exact full-screen admission pending;
model benefit unmeasured. Native page-dot geometry qualified on the stated runtime.
