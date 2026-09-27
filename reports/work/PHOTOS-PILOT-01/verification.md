# PHOTOS-PILOT-01 verification

2026-09-27. Source base63d2ff4, initially clean working tree. Research decision
recorded before code. No Git mutation, new transfer, device connection, remote input,
capture, model-comparison run, training, model export/promotion or producer edit.

## Executed checks

- Initial24 Photos tests: pass (`focused-tests-01.log`).
- Expanded94 Photos/legacy tests: pass (`integration-tests.log`).
- After filename isolation,95 tests pass in1.996s (`integration-tests-final.log`).
- Final96 tests pass (`integration-tests-final-02.log`), including32 Photos
  tests plus retained-review, native-OS intake, surface-evaluation, appearance
  experiment, legacy visual comparison and runtime batching suites.
- Offline Swift build: pass in5.34s, zero warnings (`swift-build.log`).
- Offline Swift test:14 XCTest+109 Swift Testing pass, zero failures/warnings
  (`swift-test.log`). Existing package tests are not Photos model evaluation.
- Actual import/review CLI tested in subprocesses against generated PNGs and
  source-shaped TTR envelopes. Real production FocusRingTool crop mode produces
  expected256×256 crops; original input hashes remain identical. No model supplied.
- Existing dataset admission, appearance assembly and surface evaluation reject
  the diagnostic version. Actual trainer `--preflight` exits2 with
  unsupported_crop_manifest even after copying the diagnostic file to its expected
  manifest filename. No training run directory created.
- Generated demonstration retained under generated-demo/generated-review; one
  generated pair accepted for software demonstration only. Full-frame control
  overlays and focused/unfocused crop sheet visually inspected: labels, context,
  expanded margins and pair ordering correct. It is not genuine Photos evidence.

## Reproduction

From package root, resident interpreter:
`/Users/josephmccraw/Library/Application Support/NativeUIAuditKit/Environments/focus-export-01/bin/python`.
Python3.12.9/Pillow11.3.0; no environment installation/download. Set
PYTHONDONTWRITEBYTECODE=1, PYTHONPATH to project scripts, and TMPDIR to
`.build/debug-output/focus-launch/tmp`.

Run `-m unittest -v test_photos_focus_pilot test_focus_retained_review
test_native_os_focus_dataset test_focus_surface_evaluation
test_focus_appearance_experiment test_focus_visual_comparison
test_focus_runtime_batching`. The Photos CLI has no subprocess/device/model code;
only its existing crop adapter invokes Swift. Legacy scorer tests use synthetic
probabilities/mocks, not Photos inference.

Swift build/test commands use `--disable-automatic-resolution --manifest-cache local`
with cache/config/security paths under `.build/photos-pilot-check/`. TMPDIR and
Clang/Swift module-cache paths are set there too. Scoped normal-host approval was
used for the existing Swift cropper/compiler and ordinary macOS runtime access;
all explicit artifacts/configurable caches are project-local.

Negative cases cover missing/changed/corrupt inputs, wrong source/session, stale
observation, all-black frame, unknown generation preservation, generation drift,
duplicate observation IDs, path escapes, output collisions/symlinks, reserved-like
frame names, changed review hashes/membership, missing controls/pair frames,
unknown/multiple/conflicting labels, sensitive/unsettled/unconfirmed review,
native conflict, invalid bounds, pair cap, duplicate/contradictory pixels,
missing/failing crop runtime and tampered eligibility.
Final copy verification also fences retained bytes against the declared source
hashes; storage reserve includes the estimated input copy size before output creation.

`git diff --check`, local report-link checks and duplicate-key-rejecting YAML
readback pass. Other packet/top-level status fields are preserved: after excluding
only PHOTOS-PILOT-01, canonical content SHA-256 remains
`7f18463e7b5ec795d85d445b4de28ffdf12ed3964c4a35729013b7aa1b357370`.
Generated JSON/PNG outputs match existing gitignore rules. No test run is left active.

## Live checks not executed

No installed Office helper could be bound on this host: /Applications and user
Applications have no TTR app; normal-host process inventory found no coordinator;
the prior standard development app path is absent. The existing simulator Fixture
extension was left untouched. No runtime help/status invocation, Office capture,
target/ownership qualification, genuine human annotation or cleanup was performed.
The maintainer was asked asynchronously for the current TTR host and availability.

SMB mount inventory returned absent. Shared delivery, readback and peer acknowledgment
are unverified; only local metadata draft exists. See coordination.md.
