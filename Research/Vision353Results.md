# VISION353 — first executable batches

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Delivery

research-host-NUIAK prepares and runs 10 immutable jobs through the existing dashboard.
The jobs use 32 settled frames from DATASET351 and its 24 labeled endpoint pairs.
They exclude 8 unsettled early frames. All related scenes remain in 1 development group.
No new capture, training, threshold selection, or model replacement occurs.

The jobs use the existing `vision_annotation_probe.swift` with opt-in feature-print and OCR settings.
The old default request remains available. Each new specification pins its compiled executable, source, images, and labels.
The two executables remain separate. Later probe changes do not replace the first executable.
Each comparison depends on completed producers and checked output hashes.
Each job retains its raw Vision receipt, request settings, OS version, and result.

## Findings

| Test | Measured result | Meaning |
| --- | --- | --- |
| Revision 2, scale fit, cutoff 0.1 | 2/8 movements missed; 8/16 negative pairs flagged | All 8 content changes trigger alarms. Repeated frames do not. |
| Revision 2, center crop, cutoff 0.1 | 2/8 movements missed; 8/16 negative pairs flagged | Center cropping does not fix the semantic confusion here. Individual distances differ. |
| Revision 2, cutoff 0.5, either crop | 8/8 movements missed; 0/16 negatives flagged | Suppressing nuisance changes also suppresses the desired signal. |
| Revision 1, scale fit | Distance magnitudes differ substantially from revision 2 | Do not reuse a distance cutoff across revisions without evaluation. |
| Rectangle proposals | 8/128 body observations covered at IoU 0.5; 0/128 at IoU 0.75 | This configuration supplies poor body coverage. Counts include repeated related frames. |
| Accurate OCR, correction on | Identical text lists in 23/24 pairs | Text recognition often remains stable while focus changes. |
| Accurate OCR, correction off | Identical text lists in 23/24 pairs | Disabling correction does not improve this stability count. |
| Fast OCR, correction on | Identical text lists in 24/24 pairs | Agreement alone does not establish correct transcription. |
| Accurate OCR, smaller text limit | Identical text lists in 23/24 pairs | More permissive size filtering does not improve this count. |

No OCR pair has empty results at both endpoints in these 4 configurations.
The report does not claim OCR accuracy because reviewed text labels are unavailable.
Rectangle coverage permits proposal reuse. It is not one-to-one detection accuracy or focus-selection accuracy.
Raw observations preserve text, bounds, confidence, request revision, and timing for further review.

The frozen similarity cutoffs are 0, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1, and 2.
The report preserves every cutoff. It selects none for deployment.
All 3 retained focus models miss the same 8 movements and correctly reject the 16 negative pairs.
Vision similarity provides change evidence, but these results do not justify replacing semantic focus detection with it.

## Limits and decisions

- Preserve the existing models and their crops.
- Do not let unchanged OCR text establish unchanged focus.
- Keep feature-print revision and crop settings in cache identities.
- Do not treat these rectangle proposals as complete control boxes.
- Keep text recognition, body localization, and semantic focus decisions separate.
- Do not claim real-app transfer from this single related Fixture family.
- Keep unsupported archetypes, themes, and HCF modes unavailable.

The next justified work is a regional similarity comparison and improved proposal coverage, using the same original frames.
For tracking and settling, prepare ordered qualified sequences before starting those tests.
For OCR accuracy and merging, obtain reviewed text and control associations before scoring correctness.
For temperature scaling, require valid logits and separately reserved calibration groups.
These are missing execution prerequisites, not reasons to repeat the completed batch.

## Verification and time

Native smoke checks verify supported revisions 1 and 2, zero self-distance, and rejection of changed image hashes.
The focused suite passes 109 tests. The first sandbox run cannot bind test sockets; the scoped host run passes.
The offline native Swift build passes. Swift Testing passes 173 tests; XCTest passes 14 tests.
The standalone probes compile with the resident Swift toolchain. No dependency installation occurs.

The 10 jobs use 45.8 s of total worker time. The host test suite takes 28.24 s.
Swift Testing takes 51.93 s. These times exclude implementation and queue preparation.
The initial estimate is 30–60 min for preparation and checks; no training run is part of that estimate.

Evidence: `reports/work/research-queue/jobs/vision353-*/attempts/1/`.
Specifications: `Research/ResearchSpecs/VISION353/`.
Native checks and build logs: `.build/vision353/`.
The runner executes both batches without chat supervision. It waits when no eligible jobs remain.

The coordinator stores the findings at cursor 390 and confirms the request ID on readback.
Forwarding and recipient acknowledgment for these findings remain pending.
peer-host-TTR acknowledges the earlier DATASET351 and GENERATION352 reports at cursor 389.
Its source publication is now available. Its HCF pilot still needs a native folder grant and qualified capture.
