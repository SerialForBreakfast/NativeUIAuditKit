# STREAM512 — Independent follow-ups

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Verified findings

Reducing detector input from 1280 to 960 pixels improves Standard selection from 10/24 to 23/24 on retained native development observations.
The comparison loses no previous successes and adds no wrong selections. It covers 6 scene groups, without no-focus scenes.
This is a pipeline gain with fixed weights. It is not a model promotion or release qualification.

IOS511 coverage selection gains 18 detections and loses 7 against the prior frozen mixed fit.
It gains 12 and loses 19 against Run013. It gains 16 and loses 26 against original-only frozen training.
Reject replacement. Related observations do not establish independent accuracy.

## Follow-up graphs

1. **tvOS regression:** 16 jobs test no-focus, tall controls, edge clearance, small decoration, and diamond decoration.
   Reuse completed 1280-pixel inference. Compare 960-pixel inference with the same teacher crop models and fixed thresholds.
   The terminal report checks Standard losses, new wrong selections, and no-focus results. HCF stays separate.
2. **iOS additive rehearsal:** 17 jobs include 1 fit, 6 scores, 4 reports, and 6 conditional diagnostics.
   Keep all 128 original training images. Add the same 16 qualified native images.
   All 144 image hashes and 1407 label bounds pass checks. Retained evaluation groups remain excluded.
   Keep Run013 initialization, frozen backbone, seed, preprocessing, and 30 epochs.
   More images increase optimizer updates. This practical comparison does not isolate coverage from exposure.
   Use 1800 s, 2 GiB, and 1 attempt. Compare IOS511, original-only, native-only, and Run013 results.
   Reject any lost retained success. Conditional diagnostics run only after regression.

These are 2 investigations, not 33 independent questions. No new captures or model promotion occur.
Both complete graphs pass admission checks without blockers. Existing templates perform execution and reporting.
No runtime source changes or service restart are needed.
The fit should take roughly 13–16 min, based on earlier 128-image fits near 12 min.
Scoring adds runtime. This tranche does not fill an overnight window.

## SDK prerequisites

Maximum-mini-NUIAK fetches source commit `15de3ecdaa2ccff5f669d04a1d58bf864eafe6dc` through Git.
No TTR working files or running application change. The portable intake audit still needs independent execution.
Sillycon-TTR reports no eligible training exports. SDK505 remains excluded test and calibration data.
Request 1393 narrows the first corpus to registered-control crops and temporal pairs.
Complete screen annotations are unnecessary for qualified control crops. They remain necessary for complete detector labels.
Propose 6 independent training groups and 2 separate development groups for a small pilot.
Cover movement, arrival, departure, background-only change, visible no-focus, and selected-but-unfocused controls.
Require observed state, valid geometry, explicit profile, and separate ancestry. Do not infer unknown labels.
Freshness qualification remains a producer prerequisite. This request does not expand capture budgets.
The coordinator stores the request. Forwarding and producer acceptance remain unconfirmed.

## Evidence

- [tvOS graph](../reports/work/STREAM512/tvos-full-r2.json)
- [iOS graph](../reports/work/STREAM512/ios-full.json)
- [tvOS preflight](../reports/work/STREAM512/tvos-preflight-r2.json)
- [iOS preflight](../reports/work/STREAM512/ios-preflight.json)
- [Prior scope](Stream511IndependentExperiments.md)

Standard, shipped models, original captures, and previous results remain unchanged.

## Preserved preparation failure

The first no-focus control fails because its reference belongs to a different retained no-focus group.
The failed attempt remains available. Three immutable successors correct both no-focus scoring jobs and their terminal report.
All 5 conditions now pass exact baseline and candidate reference-membership checks.
The correction changes no capture, model, threshold, or training specification. Original affected approvals are revoked.

The runner starts the independent iOS fit. Other tvOS conditions continue during the reference repair.
No code changes are needed in this tranche. Full graph validation, input hashes, label bounds, and dependency checks pass.

Final batch snapshot: {'ready': 6, 'complete': 4, 'dependent': 16, 'running': 1, 'conditional': 6}. All current approvals are valid: True.
Recorded preparation after the first graph file: 4.6 min. Initial review is unmeasured; the estimate was 30–60 min.
