# Approved iOS reconstruction count amendment

Maintainer approval:2026-09-23, “Yes. I approve.” in response to the explicit
12,540 train /2,400 validation /2,000 test proposal. Total16,940 is unchanged.
No existing family, image, annotation, split assignment or historical report moved.

Applied to validate_reconstructed_corpus.EXPECTED; LEGACY_EXPECTED preserves
12,340/2,400/2,200 for callers reproducing historical checks through the existing
explicit expected argument. Reports retain exact expectedSplitCounts and now name
the approved policy or explicit override. Regression asserts both totals and maps.
Queue, living snapshot, iOS plan and original decision record reference approval.

Verification:30 reconstruction/retention tests pass (tests.log,0.317s); final offline
Swift build/test logs alongside this handoff. Python bytecode disabled; Swift offline
resolution and all module/temp/cache/config/security outputs rooted under the
project's .build/ios-retention-check. No full14,340-image decode repeated solely to
change arithmetic; prior byte-bound audit remains historical evidence, not a new
corpus pass. Diff check passes.

Software verified; new data eligibility not assessed; native integration not run;
model gates not assessed. Current preserved prefix remains10,140/2,400/1,800.
The unchanged remainder is2,400 train+200 test: UIKitControls700, UIKitForm700,
UIKitList700, UIKitToggleForm300 and WizardStepFlow200.

Next: fresh r6 exact-target/source/build/container preflight and native seed-variation
qualification before the five remaining batches. The old continue_r5.py is not reusable
unchanged: it pins a7,500-member r5 prefix, old container and existing r5 result/output
paths. Do not rerun it or erase staging. Preserve r5 rejected evidence and the14,340
prefix. Separate visual-probe execution and training approval were not granted by
this count decision. Local iOS-only change: shared status not applicable.
