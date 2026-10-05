# IOS149 — current coverage and next detector improvement

Software verified; retained labels/hash lineage verified, no new data admission.
Native rendering/inference not performed. DS-G8 remains failed/open; no promotion.

## Correct current state

The initial old Run013 queue pointed to work already completed in38–42. This audit
first quantified the frozen r7 baseline, then reconciled against the newer r8 corpus.
The old findings are corroboration, not new discovery. No repair or resolution
experiment was repeated. Updated the stale dispatch heading to point to149/150.

Verified19,740r7label files against frozen hashes and6,267button-sidecar hashes;
then19,740current r8labels against retained export evidence and target manifest.
Exactly666labels differ, matching approved replacement IDs; all5,200evaluation
labels and all class-instance multisets remain unchanged. Regeneration reordered
666annotation sequences; the audit was corrected to compare class multisets while
retaining exact file hashes. No source pixels were rewritten or re-decoded.

| PageControl population | Count | Box width as fraction of screenshot |
|---|---:|---:|
| r8manual training, repaired |666|.064–.187|
| r8native KitchenSink training |200|1.000|
| r8native UIKitControls training |700|.872–.878|
| Existing exposed test |600|.102–.187|
| Validation |0|unavailable|

The900native rectangles require a rendered-body/container policy and native
qualification, not an assumption that every wide UIKit control frame is erroneous.
Run013trained on old r7, where all1,566page boxes were wide; r8has not by itself
established a better model. Existing38higher-resolution experiment did not fix
operational page recall and must not be presented as an untried option.

All100test scrollIndicators are2.254–2.879pixels on the short edge at640 input;
1280would geometrically double this, not establish better accuracy. RichContentFeed
500train/100validation examples share this thin geometry. A future matched
scroll-specific resolution test is distinct from the already-run page-control test.

Button-sidecar text is available for2,100UIKit secondary examples; other reviewed
SwiftUI button text is absent, not an empty button. Current source maps confirm
legitimate non-cancel secondary actions. The unused/older UIKitGenerator Cancel
example must not be used to claim the actual r7UIKitControls corpus is mislabeled.
No automatic role remap or OCR-generated ground truth. Per-family class/geometry
and text counts are retained in artifacts/audit.json; r8in artifacts/current-r8.json.

## Verification / evidence

`ios_label_audit149.py --output .../artifacts/audit.json`: exit0,5.975s.
`ios_label_audit149.py --current --output .../artifacts/current-r8.json`: exit0,6.176s.
Frozen/category/label/sidecar integrity and complete support accounting pass.
Original script snapshot retained as artifacts/source-r7-audit.py before extension.
Four focused tests pass: geometry/letterbox scaling, invalid input/path, summary,
real-entrypoint output collision for both modes. Offline Swift build/142native tests
pass, .build/ios149-{build,test}.log; subsequent Python extension does not alter Swift.
No Git writes, model inference, training or TTR dependency. Existing changes preserved.

Next substantial tranche is IOS-NATIVE-PAGE150: qualify native intrinsic geometry,
create96source-separated development examples, repair exact900training members in
a new version if qualified, then preregister one matched candidate. Full contract
in Research/Plans/Run013Evaluation.md; class-wide independent final challenge
remains separately required. No silent evaluation-to-training reuse.
