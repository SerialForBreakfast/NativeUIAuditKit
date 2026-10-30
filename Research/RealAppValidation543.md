# REAL543 — Independent real-app validation

Owner: Maximum-mini-NUIAK. Date: 2026-10-29.

Real-app accuracy is not independently established. Dataset mAP is not the percentage of screenshots understood.
This benchmark measures a selected test population. It does not estimate accuracy across all deployed applications.

## Implemented software

`scripts/real_app_benchmark543.py` provides reference review, immutable freeze, scoring, candidate comparison, and queue compilation.
It reuses existing file pins, queue execution, box validation, and historical AP code.
Two isolated campaigns execute the same adapter without another script.
Software fixtures do not qualify an application, model, human reviewer, or consumer runtime.

The evaluator reports per-class recall and precision, missed controls, unmatched detections, class errors, and localization errors.
It reports correct focus, wrong selection, abstention, unknown references, no-focus false selections, execution failures, and latency.
Every application has a separate report. The focus summary weights supported applications equally.
Uncertainty resamples whole flows within applications with a fixed seed and 2,000 draws.
Few applications limit generalization. Related screenshots are not independent samples.

Official COCOeval provides AP50, AP75, and AP50–95 on complete, successful screens.
Historical all-point interpolated AP uses identical eligible inputs for a separate cross-check.
Different interpolation and matching rules can produce different values. Review differences before interpreting them as defects.
Failed inference remains in overall outcome and recall denominators. Reports identify the smaller AP scope.
Partial annotations cannot establish false-positive rates. Unknown classes and visibility remain unresolved.

## Accuracy claim inventory

| Location and score | Model and input scope | Evaluator and settings | Evidence role and correction |
| --- | --- | --- | --- |
| README, ModelStatus500: 0.935 / 0.968 | iOS v2.0, 5 classes, 1,394 generated validation images | Historical CoreML / PyTorch AP50; export NMS IoU 0.30, floor 0.001 | Generated-screen validation. Not independent real-app accuracy. |
| README: 0.934 | iOS 5-class withheld generated templates | Historical AP50; exact evaluator settings need source receipt recovery | Generated-screen development. Do not infer real-app performance. |
| README: 0.756 | Historical Create ML, same generated validation corpus | Historical AP50 | Generated-screen validation. Preserve the comparison. |
| README, ModelStatus500: 0.9822, P/R 0.983, AP50–95 0.944 | tvOS v3.0, 25 classes; training uses 5,000 synthetic screens | Historical trainer validation; operating threshold not supplied in the headline | Trainer validation. Not real-app qualification. |
| README, ModelStatus500, ModelPromotion536: Run013 0.6322 versus Run009 0.5549 | 2,000 withheld generated screens, 13 supported classes | Custom all-point AP50; prediction floor 0.001; count metrics use confidence 0.25 and IoU 0.50 | Inspected development evidence. Preserve historical Run009 0.586 as a different comparison. |
| ModelStatus500: 86/236 native occurrences | Retained native stress cases and pinned detector comparison | Located annotated controls; see original comparison for model pins | Development evidence. Related observations do not establish broad accuracy. |
| ModelStatus500: 270/270 crops | Shipped FocusRing crop classifier; no hard negatives in this set | Supplied-box crop classification | Development evidence. Not full-screen selection or no-focus qualification. |
| ModelStatus500: 9 and 8 recoveries on 408 pairs | Temporal candidates, seeds 42 and 44 | Retained paired comparison | Development evidence. Not independent tracking qualification. |
| README: 23 captures, 586 detections, “zero false positives” | Historical physical Apple TV observations | Retained report has 29 entries; complete reference labels are absent | Counts remain historical. The zero-false-positive claim is unsupported. |
| README: about 7.5 ms | Direct CoreML inference on historical iPhone configuration | Excludes Vision and end-to-end consumer overhead | Runtime observation. Not consumer latency or accuracy. |
| Dashboard counts | Execution states and job outcomes | Queue accounting | Not model accuracy. The dashboard now states this explicitly. |

The README no longer attributes the backend AP difference to quantization without evidence.
Sidecar and pixel-only descriptions no longer claim an unmeasured accuracy ranking.
Promotion thresholds are requirements, not achieved scores.
Historical experiment records remain intact.

Sources: [ExperimentLog](ExperimentLog.md), [ModelStatus500](ModelStatus500.md), [ModelPromotion536](ModelPromotion536.md).
The retained `reports/work/IOS-R013-EVAL/metrics.md` identifies the matched custom evaluator.
The retained `reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.md` reports 4/7 correct focus outcomes.
That report lacks complete annotations for false positives and remains development evidence.

## Execution sequence and current gates

1. Freeze the production baseline and protocol before viewing predictions.
2. Reuse SDK539-APPS to qualify independent source-built applications.
3. Predetermine 10 pilot screenshots per application, up to 50 total.
4. Export SDK draft labels for blinded human review.
5. Score the pilot through the actual Standard consumer path.
6. Repair evaluation defects before freezing the additional 200 cases.
7. Run the shipped baseline before any predeclared candidate.
8. Convert confirmed model failures into separate development tasks.

Current gate: no verified five-application qualification inventory is attached to REAL543.
Fixture and NavigationConsumer do not count as independent applications.
The existing human-reviewed screenshots lack this plan's independent application and flow qualification.
They can test import compatibility, but cannot become fresh qualification evidence.

Current gate: the actual Standard consumer needs a loaded-model receipt in the benchmark format.
On-disk model files and optional HCF observer receipts do not prove the loaded Standard configuration.
The benchmark requires model hashes, preprocessing, taxonomy, runtime revision, screenshot identity, and inference outcomes.
No production baseline is frozen until this evidence passes.

Current gate: the maintainer or a designated reviewer must accept blinded reference labels.
The software exports drafts. It does not mark SDK observations as human review.
No real-app accuracy number is produced by the software tests.

## Frozen protocol

Keep tvOS Standard, iOS, HCF, supplied-box focus, and temporal evaluations separate.
Do not train, tune thresholds, replace models, or promote models within REAL543.
Keep SDK labels outside inference inputs. SDK-assisted prediction requires a separate experiment.

The pilot has up to 50 cases, with up to 10 per qualified application.
If fewer applications qualify, report the smaller pilot and its actual scope.
The qualification set has 200 additional cases across 5 applications.
Each application supplies 8 distinct flows with 5 predetermined capture points per flow.
Exclude pilot flows, training groups, duplicate pixels, and related sequences.
Record missing and rejected cases with reasons. Failed execution does not remove a case.

Select lists, grids, overlays, scrolling, control sizes, and genuine no-focus states where available.
Audit source ancestry, training exposure, controlled content, and SDK observation correctness before selection.
The reviewer checks all visible controls, including controls absent from SDK registration.
Keep class uncertainty, focus uncertainty, visibility, clipping, and occlusion explicit.
Native class names alone do not establish semantic labels.

After results inform a model change, those cases become development evidence.
Use fresh cases for subsequent independent qualification.
Simulator results describe Simulator behavior. Physical-device qualification remains separate.

## Internal data interface

Use `real-app-benchmark-v1` manifests. File references contain project-relative `path` and `sha256` values.
The manifest contains `platform`, `profile`, `phase`, `trainingEligible:false`, `classes`, `baseline`, `apps`, `exclusions`, and `cases`.
Optional `candidates` contain configurations declared before freeze.

Each configuration declares screenshot-only input, upright top-left pixel coordinates, confidence, and matching IoU 0.50.
Pin the detector, focus model, preprocessing, taxonomy, runtime receipt, and 40-character TTR revision.
The runtime receipt uses `real-app-runtime-v1` and `observedLoaded:true`.
It binds `detectorSHA256`, `focusSHA256`, `preprocessingSHA256`, `taxonomySHA256`, `ttrRevision`, and `inputMode`.
A producer supplies this receipt from observed runtime state. Do not create it from assumed filenames.

Each application records identity, ancestry, source revision, exposure audit, and a qualification receipt.
Each case records application, flow, group, planned status, dimensions, image hash, decoded pixel hash, SDK evidence, and labels.
Labels record object identity, class or null, visible box, visibility, provenance, and observed focus state.
Labels also record reviewer identity, blinded review, accepted status, and complete-coverage status.

The freeze pins the manifest and evaluator. The pixel manifest omits labels and SDK evidence.
Prediction files bind the freeze and configuration hash.
Each case binds image and decoded pixel hashes, runtime receipt, status, latency, detections, and selected focus box.
Failed cases contain an error and no fabricated predictions.
Optional crop records bind the crop hash, source image hash, and source box.

## Commands and queue integration

Run commands from the verified USB checkout with `PYTHONPATH=scripts` and `.venv-yolo/bin/python -B`.
Use new output paths. Existing freeze and report files are immutable.

```sh
python -B scripts/real_app_benchmark543.py review manifest.json --output reports/work/REAL543/review
python -B scripts/real_app_benchmark543.py freeze reviewed-manifest.json --output reports/work/REAL543/freeze.json
python -B scripts/real_app_benchmark543.py report report-request.json --output reports/work/REAL543/report.json
python -B scripts/real_app_benchmark543.py compile report-request.json --output reports/work/REAL543/report-spec.json
```

A report request contains `id`, `freeze`, and `predictions` file references.
Submit and approve the generated specification through existing queue interfaces.
The detached runner executes reports within 800 s and 100 MB.
Compilation validates retained inputs. It does not launch model inference or capture.
The caller uses `compare(baseline_report, candidate_report)` for recovered controls, lost controls, and focus outcome changes.
Candidate reports require the same frozen membership and a predeclared configuration.

## Remaining deliverables

- REAL543-RUNTIME: connect actual Standard replay receipts to this report contract and prove one retained screenshot.
- REAL543-APPS: attach SDK539 qualification receipts and predetermined pilot flows.
- REAL543-REVIEW: obtain blinded human labels and completeness decisions.
- REAL543-PILOT: execute the pilot and fix evaluation defects.
- REAL543-QUALIFY: freeze and evaluate the additional 200 screens.
- REAL543-FOLLOWUP: rank failures by frequency, consumer harm, and affected applications.
- REAL543-TEMPORAL: define a separate movement, dismissal, settling, and background benchmark after the static baseline.

No application capture, model replacement, or live benchmark execution occurred during software qualification.

## Verification and handoff

The focused suite passes 38 tests. Dashboard descriptions pass 7 tests.
The offline Swift build passes. Serial Swift tests pass 177 tests across 25 suites.
The first build failed because a retained module cache contained the parked checkout path.
A new project-local cache resolves that failure without deleting the original cache.

The approved dependency is pycocotools 2.0.11. Its version is recorded in the evaluator identity.
Freeze also pins evaluator helpers, NumPy, and Pillow versions.
COCO scores use predictions returned by the consumer. Its confidence floor can limit the available precision-recall curve.
Do not compare these values with raw trainer outputs without matching prediction retention rules.

BigDog-Coordinator stored request `nuiak-real543-standard-runtime-contract-20261029-v1` at cursor 1756.
Forwarding and Sillycon-TTR acceptance are not confirmed.
TTR source already exposes detector digest and focus execution fields in `NUIAKVisualAdapter`.
The request asks for the supported replay mapping and missing final-selection, timing, and input identity fields.
It does not request new capture, training, or model changes.

The tested dashboard notice is active. The restart preserves PIPELINE538 priority and resumes the existing approved queue.
No real benchmark jobs were admitted with placeholder inputs.
Private test logs remain under `reports/work/REAL543`.

## SDK539 application intake

Swiftfin source is retained at revision `10629aba15fce88be7ca663eb1fcd77c609cc66b`.
The source license is MPL-2.0. This does not license unrelated media content.
The source declares tvOS and iOS targets. Simulator builds and SDK integration remain unqualified.
The maintainer approves resolution of its 42 pinned packages into project-local storage.
No App Store binary is used. No upstream pull request is permitted by its contributor instructions.

Pilot flow proposals are recorded before model predictions: server selection, sign-in, home shelves, library grid, and item detail.
Other proposals cover search, filters, playback controls, dismissal, and in-app preferences.
These are proposals, not captured or qualified cases. Controlled content and genuine no-focus coverage require separate verification.
Source intake does not establish training exclusion, ancestry independence, or label correctness.

Source reference: [Swiftfin repository](https://github.com/jellyfin/Swiftfin/tree/10629aba15fce88be7ca663eb1fcd77c609cc66b).
The private intake receipt records the package lock hash and missing qualification steps.

The live dashboard health check passes after activation. A separate full-page fetch exceeds 30 s while the queue snapshot builds.
The rendered notice passes its software test. Live page verification remains incomplete.

Compiled CoreML directories use a pinned `compiled-model-reference-v1` descriptor.
It contains a project-relative `root` and the existing `compiled-tree-sha256-v1` digest as `compiledSHA256`.
The evaluator verifies every model file and includes those files in queue inputs.
The runtime receipt binds the compiled tree digest, not the descriptor file hash.

NewsTV source revision `95aa870210a5db57b84317353ed9999ad8bcb81d` passes a tvOS Simulator build.
The original project references `/Volumes/Data/xcode/NewsTV/NewsTV/NovaAPIServer.swift`.
The local project now uses `NewsTV/NovaAPIServer.swift` relative to its source root.
Swift property-list APIs preserve project objects. Serialization changes the project format to XML.
No upstream contribution, installation, launch, or capture occurred.
Source reference: [NewsTV](https://github.com/kochj23/NewsTV/tree/95aa870210a5db57b84317353ed9999ad8bcb81d).

WeatherFeels source revision `d96361e2e3aa440498bcd3cbc3a0eaca4cd4a2db` is retained.
It requires XcodeGen to generate its project. The approved project-local XcodeGen build now passes and generates the project.
Source reference: [WeatherFeels](https://github.com/hollandcloud/weatherfeels/tree/d96361e2e3aa440498bcd3cbc3a0eaca4cd4a2db).

The inspected TTRDiagnostics README explicitly excludes unregistered controls, occlusion, and complete SwiftUI hierarchy from automatic observations.
Human review remains necessary for complete visible coverage and unresolved occlusion.
The benchmark keeps these unknowns explicit instead of assuming SDK completeness.

Swiftfin resolves all 42 pinned packages successfully. Its build stops at Xcode's approval gate for CasePathsMacros and StatefulMacrosMacros.
The maintainer subsequently approves execution of those macros. No global trust setting changes.
WeatherFeels reaches Metal compilation. Xcode reports `cannot execute tool metal due to missing Metal Toolchain`.
No system toolchain download is started. Its source and shaders remain unchanged.
XcodeGen source revision `783a19e863ff906e042d061aa0a1d569d3c52ffa` builds in project-local storage.

Current independent-app count is **0 fully qualified** and **2 Simulator build passes**.
The candidates are NewsTV, Swiftfin, and WeatherFeels. Two additional independent applications remain unselected.
Do not report five-app coverage. SDK runtime verification and blinded labels remain required for every candidate.

Recorded implementation and build checks span 23:18–23:53 UTC, about 35 min.
The initial estimate is 60–120 min. Earlier audit time is not included in that recorded interval.
The full benchmark remains incomplete at the stated runtime, application, and human-review gates.

## Swiftfin macro qualification — 2026-10-30 UTC

Swiftfin now passes its tvOS Simulator source build with the approved pinned macros.
The first retry incorrectly forced compiler plugins to use the Simulator SDK.
Removing the global SDK override lets macros target macOS while the app targets tvOS Simulator.
The source checkout remains unchanged. The build receipt records the executable hash and bundle identity.
SwiftFormat is absent. Its script prints an error, but Xcode completes the build with exit status 0.
No app installation, launch, SDK runtime qualification, or capture occurred.
NewsTV and Swiftfin have source build passes. Neither counts as a fully qualified benchmark application yet.


## NewsTV SDK trial — 2026-10-29

Maximum-mini-NUIAK builds NewsTV with controlled article content and explicit SDK hooks.
The reproducible integration is in `scripts/sdk539/newstv/`.
A private source snapshot preserves the SDK revision, local modifications, license, and file hashes.
A clean published SDK revision remains required for portable consumer qualification.

The approved Simulator trial installs and launches the source-built app.
TTR authenticates the app and returns 23 unique control IDs with finite, positive rectangles in window points.
These include 6 article buttons, 10 category tabs, and 7 main tabs.
The app preserves unknown focus. The SDK reports interruption on all 3 delayed observations.
This trial does not verify pixel alignment, clipping, occlusion, complete annotations, or native focus.
The observations remain review-only. No benchmark screenshots or model predictions were produced.
The trial terminates NewsTV successfully. It does not restart TTR or the background runner.

The first launch failed with file redirection. Console streaming permits launch.
Explicit flushing makes startup receipts visible. TTR requires enrollment inside its selected project workspace.
Live `sdk snapshot` requires the default page limit. A limit of 100 is valid for elements, not snapshot.
All failed attempts remain recorded. Private enrollment files remain outside public documents.

Ten pilot cases are predetermined across 3 NewsTV flows. All remain planned and unreviewed.
They do not establish independent application coverage or 10 independent samples.
Private evidence: `reports/work/REAL543/newstv-sdk-trial-receipt.json` and `newstv-pilot-cases.json`.

## Confirmed TTR consumer gap

Sillycon-TTR's source-map reply confirms that retained Fixture replay does not accept arbitrary independent-app images.
The saved-image UI uses the pixel-only consumer but omits parts of the required export.
REAL543 needs a supported standalone replay with complete model provenance and request-to-durable-result timing.
Maximum-mini-NUIAK sent that exact contract through BigDog-Coordinator. The follow-up is stored; acceptance is not confirmed.
No SDK truth or receipt comparison decision may become a model prediction.


Sillycon-TTR subsequently proposed `aatv visual replay` and `visual.replay` MCP support.
At the proposal stage, implementation was pending. Maximum-mini-NUIAK returned selection, hash, timing, and failure-test requirements.
Its RGBA8 pixel hash must remain distinct from the benchmark's RGB hash.
Its request-to-result-durable timing excludes completion receipt writing and IPC return. Reports must state that boundary.
Unavailable preprocessing, taxonomy, and crop identities remain explicit qualification gaps.


## Follow-up: scene readiness and timing — 2026-10-29

A bounded metadata trial compares 3 direct observations after startup.
SwiftUI reports `inactive`. UIApplication reports state 1. UIWindowScene reports state 1.
The window is visible and key. A native focus system exists, but its focused item is nil.
All observations agree. The interruption flag is correct; its cause remains unresolved.
A successful launch and authenticated SDK connection do not establish foreground readiness.
Do not classify this inactive scene as a verified no-focus screen.
The trial takes 9.42 s. Cleanup passes. It captures no screenshots and sends no remote inputs.
Evidence: `reports/work/REAL543/news-scene-diagnostic/`.

Sillycon-TTR accepts the proposed replay contract for its next core task.
At this checkpoint, the wrapper was pending. Maximum-mini-NUIAK sent scene findings and 6 improvement requests through BigDog-Coordinator.
The new request is stored. Its forwarding and acceptance remain unconfirmed.
See [the error report](TTRIntegrationErrors543.md).

The benchmark reports `end-to-end-consumer` and `request-to-result-durable` timings separately.
The latter excludes completion-receipt writing and IPC return. It cannot populate the end-to-end latency headline.
Missing timing requires an explicit reason. It remains missing rather than becoming zero.
Valid accuracy evidence can still be scored when timing is missing. All model and reference identity checks remain required.
All 45 benchmark tests pass, including 7 new timing checks. The instrumented NewsTV Simulator build passes.


## Source delivery and independent preparation — latest checkpoint

Sillycon-TTR confirms that its current interface cannot activate an arbitrary application.
NewsTV needs a supported activation path before another readiness trial.
Do not use Settings activation or treat inactive focus as known no-focus.

Sillycon-TTR reports a completed pixel-only replay implementation and 95 checks.
This is producer-reported evidence. Source remains unpublished and consumer qualification remains pending.
The producer has not run actual model inference in that tranche.
Unknown preprocessing, taxonomy, crop, and source provenance still block a complete baseline freeze.
Maximum-mini-NUIAK requests Git delivery and preserves separate timing and pixel-hash definitions.
The follow-up is stored at coordinator cursor 1785. Forwarding is not yet confirmed.

Photo Guessing Game passes its pinned tvOS Simulator build without new dependencies.
It remains uninstalled and unqualified for the benchmark.
Three source builds pass across four identified candidates. Zero applications satisfy all benchmark gates.
See [application preparation](RealAppApplications543.md).

## REAL550 runtime intake — October 30

Published TTR source e8bbdd4 now builds and runs standalone pixel replay.
The earlier unpublished-source blocker is resolved.
Three retained Fixture screenshots produce hash-verified exports and partial provider results.
The `audit-replay` CLI checks export integrity without granting benchmark eligibility.
Runtime provenance and independent reviewed references remain required before freeze and scoring.
See [REAL550](Real550ConsumerReplay.md) for measured failures and the rejected policy shortcut.
