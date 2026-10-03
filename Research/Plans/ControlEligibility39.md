# Local control eligibility and corpus preparation — tranche39

Maintainer continuation of local38. TTR update stays deferred.

1. Retained-score-only comparison on the same46development screens. Preserve known
   YOLO semantic exclusions. Fixed candidate refinement: a new rectangle must have
   IoU>=.50 with an existing focusable YOLO body and must not contain centers of two
   non-overlapping eligible bodies. Preserve eligible original bodies. This tests
   conservative refinement, not discovery of controls YOLO completely misses.
   Compare fixed union, role-preserving union and supported refinement; no threshold
   search or new inference. Report exact7complete outcomes, missing targets, ties,
   role and source-group support. All46frames have already informed development;
   grouping cannot make them an untouched evaluation set.
2. Audit retained Run013 pageControl labels by source family/split, size and padding,
   then compare38predicted geometry to whole-dot-group truth. Read generator source
   to distinguish native UIPageControl containers from visible SwiftUI dot groups.
   Identify executable corrections without relabeling existing evidence or tuning
   against withheld families. Verify selected source images/labels and retain hashes.
3. Assemble a full-screen preparation manifest from existing native26membership,
   preserving train/evaluation group assignments and original source provenance.
   Inspect actual full-frame observed focus and completeness, storage and runner
   compatibility. A draft is not admission: explicitly report any missing rights,
   full-frame completeness or execution compatibility instead of claiming readiness.
   Metadata stays project-local; USB originals are read-only.

Audit finding: MediaCardGrid and ProgressActivity measure their pageControl after
maxWidth expansion (666training frames), unlike the tight dot group in evaluation.
Repair these two source modifiers: fix intrinsic dot size, capture, then align the
container. Preserve old labels; new rendering requires a separately scoped iOS
generator run. Static guards/Swift parsing verify source structure, not rendered QA.

Bounded offline tranche: no model execution/capture, <=2GiB outputs; use cached
predictions. Implement reusable replay/preparation checks with focused tests and
offline Swift build/test. Produce a single evidence-backed handoff and next actions.
