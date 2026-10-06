# Native page-control coverage —144-case pilot completed

Implemented an opt-in native capture path and frozen catalog with independently
varied background style and interaction. New account-summary/document-stack
layouts avoid copying155development compositions. Existing generator paths unchanged.

Exact target F3EF9DB8-0B0F-4757-B653-D1628269F6FF, iOS26.5, iPhone17Pro,
verified booted with scoped CoreSimulator access. Restricted inventory initially
failed; approved read-only inventory succeeded without restart/service repair.
Built with existing unsigned native-test configuration and project-local DerivedData.
Source/binary pins and full launch command: `artifacts/execution01/launch.json`.
Native test passed in approximately242seconds. Host limit720s, native limit600s,
new pixel budget512MiB. No retries, Office, training or TTR dependency.

## Evidence

- Catalog144recipes/18connected groups: SHA256
  `b5f6bb7411bb79863b1424c4b77e0131ecbee744aafae8b059324e14d7176609`.
- Completed144/144cases;577files copied into `artifacts/capture01`, each size/content
  independently hash-compared against freshly resolved simulator-container originals.
- Receipt SHA256 `c9b4c65a35ed05f89df1c1946b03bb33d46d6cfaef8819d3e56f94df7daad213`.
- Audit SHA256 `efdb1e2fd9e9422fd664f6ece285f826bcc0a037f4c5296ade8d2773aed299f0`.
-96unique visible rasters;48duplicate sets, zero cross-group duplicates. Duplicates
  preserved, not counted as distinct training evidence.
- Ordinary bodies23pixels high in all72cases; prominent bodies77pixels in all72.
  Interaction states are independently recorded; this directly fills the diagnosed
  geometric coverage gap, not proof of a detector improvement.
- Visible/hidden bytes, dimensions, requested/resolved style, annotation/body agreement
  and all element pixel extents checked. Representative prominent light image018
  visually inspected: native capsule present; no general visual review claimed.

Software:24focused Python tests passed, native test build/execution passed, offline
Swift build passed and132tests/17suites passed in4.413s. Diff check passed.
New code: `scripts/page_style210.py`, `scripts/audit_style210.py`, corresponding
tests, and opt-in210test/controller in KitchenSinkValidationTest.swift.

Data remains **training-candidate**. Full visual/ancestry review and deterministic
duplicate disposition still required before admission. No final evaluation data
was changed; no automatic admission from requested role or successful capture.
Model gates unassessed. Original container outputs preserved; no cleanup or backups
claimed. SMB not applicable to this independent local iOS acquisition.

Next substantial tranche: finish96-image admission and all-class annotation review,
then register one matched data-only detector comparison with old/new retention gates.
In parallel, review Big Dog's executable benchmark when delivered and reconcile TTR's
native focus geometry/source blocker; FocusRing remains the tvOS priority.

## Superseding admission review

`admit_style210.py` accepted96unique training images, preserving48duplicate aliases
only after exact annotation-geometry/group equality. All18groups are forbidden from
future final evaluation. Compared shape-prefixed pixel hashes with sealed20004-member
173corpus and raw RGB hashes with the pinned155development audit; no overlap.
Missing family fields in173derived rows resolve through their existing parent groups;
unknown parents fail closed. No training/development role was changed in old data.

Independent full-frame visible/hidden difference bounds agree within1pixel with all
144page-control annotations. This verifies rendered extent, not just repeated
metadata. Representative native images018and125 inspected and generator source
reviewed. The scope is simple native-style coverage, not unseen-app fidelity.

Admission SHA256 `c2df5d0b1f99b6945faf4f46d611371614c8dc05d3bbbe5063ac754c9e261f97`.
Raw artifacts unchanged. Tests now25Python passing, plus offline Swift build and
full serial test suite (`.build/style210-admission-test.log`). No model run yet.
Next: existing-exporter integration, matched optimizer-exposure control/treatment
registration and training; retain development/final scores separately. Big Dog has
not delivered executable runner source at this turn's initial check.

## Export integration completed

`export_style210.py` reuses `export_coco.py` and `checked_export_labels`:96images,
480annotations, unchanged41class map. Every emitted label checked against native
annotation; pixels unchanged; val/test directories empty. Export membership SHA256
`a82c4a4bc3678feb4def2afd5d30f8059c9ca09a69d90cadb3e235d41a6098c0`.
No training launched.25focused Python tests pass; required offline build and full
serial suite recorded in `.build/style210-export-{build,test}.log`.

Next preparation must reuse ROI196's crop writer/label transforms, not train a
full-frame versus ROI mixture accidentally. Match optimizer-update exposure across
control and treatment, preserve retained evaluation inputs, and register exact
initialization/configuration before launch. This is executable data, not a claim
that the77pixel failure is fixed.
# ROI preparation continuation

Evaluation coverage corrected before candidate results: refinement alone misses the
motivating ROI197extra-proposal failure. `evaluate_style210_extra.py` now reuses
the frozen existing proposal/merge/scoring contract for each fixed-last checkpoint.
Exact135fit/37page/413combined crop inputs revalidated; no membership/threshold
change. Historical negative screen is explicitly not a pass for new candidates.
Training-incomplete and output-collision guards tested;11focused tests passed.
Required integrated Swift build/test passed (132tests/17suites); logs
`.build/style210-evaluation-{build,test}.log`. Candidate inference still awaits
terminal training; do not claim evaluation complete from entrypoint verification.

After each training arm terminates successfully, execute its existing refinement
infer/report modes and `scripts/evaluate_style210_extra.py <arm>`; compare both
paths' matched results and all existing gates. Do not start inference on the MPS
device concurrently with training. Source87c5143is still absent from the local TTR
Git object store, so native focus semantic qualification is genuinely pending.

Matched execution registered as027/028. New wrapper `scripts/train_style210.py`
uses existing roi196 trainer/roi194 evaluation; no independent trainer. Both prepared
protocols freeze1509slots/189batches,10epochs and optimizer schedule. Control027is
live PID36156/session92840; do not restart while handle remains live. Treatment028
awaits control terminal evidence and then executes serially under existing approval.
Retain MPS nondeterminism warning. No terminal/model-quality result yet. Next resume:
poll92840, inspect completion.json, then train treatment and evaluate both unchanged
retained corpora with fixed-last checkpoints. Explicit outputs remain project-local;
42GiBfree launch space satisfied existing8GiBguard and2GiBper-arm output budget.

Existing cropper produced336unique new crops from96parents.48jitter windows clipped
the page target and were excluded explicitly;96other jitter variants collapsed to
already planned windows at edges. Original1173ROI196crops and all non-fit evaluation
members revalidated. Sealed `artifacts/roi04/comparison.json` contains equal1509-slot
arms: original1173once plus336balanced old repeats(control) or336new crops(treatment).
No training launched or new model result. Evaluation memberships remain unchanged.

Failed roi01/02/03 evidence retained: relative-manifest requirement, clipped jitter,
then six-decimal intermediate serialization made identical translated crop pixels
carry center labels differing0.000276pixels. New inputs reuse export_coco conversion
on native annotations with15decimal intermediate precision and verify agreement with
original six-decimal exports. Strict crop duplicate/label checks remain unchanged;
no original pixels, labels or crop geometry were overwritten.

Offline build passed. Restricted Swift tests failed CoreML sandbox model loading;
same unchanged suite with scoped host access passed132tests/17suites in3.983seconds.
Logs `.build/style210-roi-build.log`, `style210-roi-test.log` and
`style210-roi-test-host.log` preserve both outcomes. Focused Python results below.

Seven focused Python tests passed in0.007seconds. Read-only post-seal verification
reloaded336crops and checked96parents,48rejections,equal1509slots and unchanged
evaluation plans. ComparisonSHA256:
`ef5592873f5c2f17acc557d8b7114e2cb8d2b1f8e1c23c051adcad54633db3f1`.
