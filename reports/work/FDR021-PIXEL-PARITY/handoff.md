# FDR021 pixel-buffer repair — complete for review

| Outcome | Result |
|---|---|
| Software verified |PASS:12Python tests;112Swift tests; offline build, no warnings. |
| Data eligible |Unchanged development/retention role;333/333frozen crops preserved. No new admission or independence claim. |
| Integration qualified |PASS for local production CPU path; NOT RUN for TTR build/device/ANE. |
| Model gate passed |Not a release qualification; existing coverage/generalization gaps remain. Shipped model unchanged. |

## Implemented end to end

Candidate metadata `inputPixelContract=png-straight-rgb-v1` selects exact saved-PNG
straight RGB handling inside the actual FocusRingClassifier. Missing metadata
retains the legacy path; unknown metadata fails preprocessing. No public API or
taxonomy changes. No disk roundtrip: ImageIO encode/decode is memory-only. Byte
copy initializes BGRA alpha/padding without blending, preserving orientation.

Production FocusRingTool exposes final-input RGB hashes alongside predictions.
Exporter supports explicit metadata and binds it in parity identity checks.
Fresh complete FP32 encoder+head package is3,788,293bytes (5,000,000byte gate PASS).
No weights trained or changed. Original failed export artifacts remain untouched.

## Acceptance evidence

| Criterion | Evidence |
|---|---|
| Frozen original pixels/labels/model |Same sealed trace/head/encoder/protocol referenced in export report; original inputs rehashed. |
| Actual caller integration |FocusRingClassifier.classify uses metadata-selected inputPixelBuffer; FocusRingTool invokes classifier, not a Python-only workaround. |
| Exact preprocessing |parity.json:333/333production crop hashes AND333/333model-input RGB hashes match frozen PNG/PIL reference. |
| Complete scoring |333CPU predictions; maximum probability error0.0000340920, mean0.0000014878, tolerance0.01; zero flips at0.5/0.70/0.85. |
| Transparent/opaque regression |Generated alpha0/1/127/254/255 in straight and premultiplied layouts, repeated calls, opaque legacy equivalence, orientation and unknown contract rejection. |
| Artifact rejection |Python tests cover metadata mismatch/missing input contract, receipt/hash/protocol mismatch, size, membership and invalid scores. |
| Required checks |python-tests.log:12pass; swift-build.log:pass; swift-test.log:112pass; focused-swift.log:3tests including5parameterized cases pass. |
| Handoff/status |Tasks, CurrentState, architecture, experiment history, lessons and shared coordination updated. Consumer request published/read back; acknowledgment pending. |

## Reproduction and timing

Bounded stages in `launch.py`: export, compile, parity. Commands, exact interpreter,
PID, UTCstart, timeout flag and elapsed times are in each stage-execution.json.
Export4.557s, compile0.133s, complete production parity22.585s; exits0, no timeouts.
The existing resident Torch2.7/coremltools9lane consumed the original Torch2.13trace.
CPU-only/macOS26.4.1/arm64.22batches, median model load14.737ms. Full verification
time includes hash checks, crop passes, image serialization and process startup;
it is NOT end-user inference latency. Device/ANE/performance gates not assessed.

`artifact-index.json` records package/compiled/source/runtime identities. Baseline
Git revision2b0d3da3c1aa2fb648cff9275cecc2b9c16ca2b2; working tree already contained
earlier review/training/export work. Unrelated edits preserved; no Git writes.

## Next owner/action

[TTR consumer checklist](ttr-consumer.md) describes the exact local artifacts,
metadata, hashing and the missing experimental loader/build proof. The old build
cannot safely consume the candidate merely by copying weights. TTR must identify
its opt-in path; standard NUA public request/session has no custom-model override.
No other-repository edits, artifact transfer or device operations performed.
No more human annotation or retraining required for this repair. Local authorized
tranche complete; next boundary is actual TTR adoption/observer qualification, not
an invented claim that passing local parity means deployed. No processes left running.
