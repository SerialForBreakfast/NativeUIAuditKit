# Model status and recovery — October 24, 2026

Real-app accuracy is not independently established. Dataset scores do not measure the percentage of screenshots understood.
See [REAL543](RealAppValidation543.md) for the independent benchmark and historical metric audit.

Owner: Maximum-mini-NUIAK.
All 26 MATCHED499 jobs complete. Their output hashes match their execution receipts.
No new model qualifies for promotion. Standard and the optional HCF observer remain unchanged.

## Model status

| Model | Evidence and scope | Problem | Next priority |
|---|---|---|---|
| Shipped iOS `nativeui-ios-v2.0`, 5 classes | Historical Core ML mAP50 0.935; PyTorch 0.968. These are generated-screen validation results. | These scores do not establish coverage across new native classes. | Preserve this release. Evaluate broader native coverage separately. |
| Experimental iOS Run013, 13 supported classes | Matched withheld generated-family custom mAP50 0.6322 versus Run009 0.5549. | Native adaptation still loses retained detections. The 41-class release gate remains closed. | Repair training coverage and localization before another fit. |
| Frozen iOS adaptations | Mixed data detects 1,829/2,030 labeled occurrences, versus 1,848 for frozen original-only training. It gains 13 and loses 32. | Class-agnostic matching still loses boxes. Class naming alone does not explain the regression. | Identify lost classes and geometry. Require complete training-only labels and matched retention checks. |
| Shipped tvOS `nativeui-tvos-v3.0`, 25 classes | Historical synthetic-screen validation mAP50 0.9822. Current native stress comparisons detect 86/236 labeled occurrences. | This general detector loses 56 scoped-detector successes and gains 28. Historical accuracy does not describe these native cases. | Diagnose body coverage and crop geometry. Do not replace the scoped proposal source wholesale. |
| Scoped tvOS DETECTOR422 | Detects 114/236 labels in the matched class-agnostic comparison. Supports 10/24 correct Standard focus selections. | Missing or malformed boxes still prevent correct focus selection. | Use matched geometry reports to select a targeted proposal correction. |
| Shipped FocusRing crop classifier | Historical 270/270 development crops; that set contains no hard negatives. | Crop accuracy does not establish full-screen accuracy or safe abstention. | Preserve the release. Evaluate proposal errors, decorative controls, and no-focus cases separately. |
| Standard experimental crop models | Both tested crop models select correctly on 24/24 supplied-box native observations. | With general-detector boxes, the newer crop model selects 3/24 correctly and makes 12 wrong selections. | Fix the proposal path before further crop training. Teacher preservation also fails retained consumer negatives. |
| Optional HCF/mixed observer | Retained TTR parity covers 38 observations and 264 crop hashes. Maximum score difference is below 0.000003. | Independent app coverage remains unqualified. Mixed crops include false positives and content sensitivity. | Keep observer use optional and navigation disabled. Qualify independent apps, moving backgrounds, and no-focus behavior. |
| Temporal focus candidates | Historical seeds 42 and 44 recover 9 and 8 cases without losses on 408 retained development pairs. | Related pairs do not establish independent accuracy. Native moving-background and absence coverage remains incomplete. | Obtain observed before/after labels and explicit no-focus semantics before promotion. |

The 2,030 iOS labels span 6 related conditions. They are not 2,030 independent examples.
The native focus comparison contains 24 observations across 6 recorded groups.
The supplied boxes are diagnostic inputs. They are not the full-screen proposal path.

## Decisions from current results

1. Reject general-detector replacement for the current Standard focus path.
   With the same newer crop model, correct selections fall from 10/24 to 3/24. Wrong selections rise from 2 to 12.
2. Keep iOS mixed freezing rejected. Its localization losses persist without class matching.
3. Do not repeat the same training configuration. First identify a correction supported by specific lost cases.
4. Keep the lower-confidence coverage result as development evidence only.
   COVERAGE498 recovers 14 iOS labels and 6 tvOS labels without lost class-correct detections.
   Incomplete annotations prevent precision claims.

## Recovery and session comparison

Retained recovery completes with verified cleanup. Session 1 captures and exports all 4 cases before import fails.
The corrected importer accepts additive artwork presentation and composed navigation metadata.
It still checks element identity, generation, observed focus, geometry, and the producer recipe.
All 41 focused tests pass. Isolated queue import validates 8 retained images without another capture.
The failed isolated attempt remains available. Its strict report comparison rejected an added export path.
The correction excludes only that transport field from report equality.

The approved dashboard restart loads the correction. The background runner resumes.
The retained import job completes through the background runner. Three remaining session successors and the combined report are registered.
The 3 capture successors remain unapproved because Maximum-mini-TTR refuses the readiness connection.
Both the pinned helper and the running source-built app's helper report service unavailability.
No TTR source changes, workspace switches, app restarts, or repeated captures occur.

The report uses TTR campaign elapsed time for all 4 arms.
The retained first session lacks caller-total timing. Do not claim export throughput from campaign timing.

## Next useful batch

Six approved T61 jobs compare retained general and scoped proposals for buttons, rows, and tabs.
They measure missing bodies, ambiguous matches, center offsets, size ratios, and score changes.
They require no new capture or inference. These are short diagnostics, not overnight training.
Their decision is whether the next correction needs body proposals or crop geometry.
At handoff, 1 geometry job completes and 5 remain pending. The runner reports continuous mode without an error.
The 3 capture successors and their report cannot execute while readiness and approvals remain unresolved.
No useful overnight training duration is claimed for this batch.

The measured import and activation segment takes approximately 10 min, from 12:12 to 12:22 PDT.
The earlier review start is not recorded reliably. The initial estimate was 20–35 min for the whole tranche.

Highest priorities:

1. Restore the approved Maximum-mini-TTR endpoint and verify ownership. Release the remaining sessions only after readiness passes.
2. Select a case-supported Standard proposal correction from the 6 geometry reports.
3. Qualify complete training-only detector labels. Prepare matched training only after the correction and membership are explicit.
4. Continue iOS localization and retention repair independently from TTR capture recovery.
5. Qualify the optional HCF observer across independent apps and temporal negatives.

Sillycon-TTR supplies the artwork schema through BigDog-Coordinator.
Its newer SDK recovery results remain peer evidence. Dynamic readiness remains unqualified, and later repairs are uncommitted.
The compatibility result and endpoint blocker are stored with BigDog-Coordinator. Forwarding is not yet confirmed.

## Evidence

- [MATCHED499 experiment definitions](Matched499DetectorAndFocus.md)
- [HCF observer evidence](HCF490Results.md)
- [Verified result list](../reports/work/IMPORT500/matched-results-verified.json)
- [Focused tests](../reports/work/IMPORT500/tests.log)
- [Isolated import result](../reports/work/IMPORT500/isolated-queue-r2/jobs/adr493-session-1-import-r5/attempts/1/result.json)
- [Session admission](../reports/work/IMPORT500/session-admission.json)
- [Independent geometry admission](../reports/work/IMPORT500/geometry-admission.json)
