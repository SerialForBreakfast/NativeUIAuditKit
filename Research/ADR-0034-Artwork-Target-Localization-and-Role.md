# ADR-0034 — Locate artwork controls and audit their native roles

Proposed on 2026-11-13. Owner: Maximum-mini-NUIAK. Partner for contract changes: Sillycon-TTR. This proposal defines a development diagnostic. Joe reviews any headline metric or model promotion.

## Two consumer questions

A navigation agent needs the intended visible target. Count a well-placed button or cell box as a target candidate. A neighboring card, a decorative poster, or a duplicate detection can still invalidate the result. Localization alone supplies no evidence about current focus, enabled state, modal ownership or successful activation.

An auditor needs the native owner of the visible body. Keep the exact role, construction, applied style and evidence source. A NewsTV custom-styled SwiftUI button, a native card-styled SwiftUI button and a collection cell can share the same artwork. Contract v1 projects these examples to button, cell and cell respectively. With insufficient evidence, record “exact role unknown”. Preserve reviewed target geometry independently. [Frozen construction contract](Contracts/tvos-framework-projection-v1.md)

## Alternatives

| Option | Utility | Decision |
|---|---|---|
| Exact v1 roles for both uses | Preserves framework distinctions. Can count a well-localized target as a navigation miss. | Retain for exact-role audits and historical comparison. |
| Derived button-or-cell category | Answers the target-location question with existing predictions. Duplicate and decorative detections remain measurable. | Proposed first choice for evaluation. Keep existing model outputs and public APIs. |
| Learned parent category | Could recover targets missed by both leaf predictions. Requires independent parent labels and a demonstrated localization deficit. | Defer pending evidence that grouping cannot solve the deficit. |
| Appearance-based v1.1 projection | Could give visually identical controls the same visual role. Preserve construction as a separate observed attribute. | Require an operational pixel rule, matched counterexamples, Sillycon-TTR agreement and a new versioned table. Preserve v1 labels and results. |

## Frozen decision rules

Use detector confidence 0.25 and source-pixel box IoU of at least 0.50. Merge only button and cell predictions. Match in descending confidence, with original prediction order for ties. Match each prediction to at most one unmatched eligible reference and each reference at most once. Attribute a match to the actual overlapping target. Count a second prediction on a matched target as an unmatched duplicate. Report decorative false targets only when independent review identifies decorative content and covers the screen. Keep unresolved status explicit.

Require at least 30 layout-distinct ordinary-app screens across at least 3 apps for release-facing decisions. Count one screen per related scene sequence. Report per-app and equal-app results. Require at least 90% equal-app shared recall and precision and at least 80% recall in every app. Missing completeness, class support or independence leaves the decision open.

| Shared localization | Exact role separable | Action |
|---|---|---|
| Strong | Yes | Consider exact-role training for a named audit use case. Keep shared navigation scoring. |
| Strong | No | Stop this exact-role fit. Use observed framework facts for audits and evaluate a v1.1 visual rule. |
| Weak | Yes | Test a localization correction first. Measure exact-role retention alongside it. |
| Weak | No | Improve shared target detection. Report ambiguous exact roles as unknown. |

Insufficient coverage or an inconclusive separability test selects no decision-table cell. Activation is outside this experiment.

## Native cue experiment

Maximum-mini-TTR checks the installed Fixture first. Request missing recipes through BigDog-Coordinator. Compare a custom-styled SwiftUI Button, a native .card Button and a UICollectionViewCell with identical artwork. Change one focus lift or scale cue at a time. Fix text, bounds before focus, neighboring content and focus route. Include disabled controls and decorative artwork. Do not infer framework construction or focus from screenshots.

Record actual focus, owner, visible bounds, clean settled frames and native timestamps. Check bounds through the normal loader. Keep linked assets, related layouts and repeated states in one partition. Freeze the held-out groups before inspecting their outcomes.

For the proposed scale rule, measure focused-to-unfocused painted width and height ratios in source pixels, then verify both changes survive production resizing. Predict cell only if both ratios exceed 1.00 with at least 2 detector-input pixels of expansion on both axes. Use the median of two stable samples per state. Record unavailable boundaries as abstentions, counted as failures in the denominator. Apply only to paired temporal observations. A passing temporal result does not qualify static screenshot classification. For a static fit, test a separately frozen single-frame cue on held-out screenshots first. Report focused and unfocused results separately.

At the decoded production input, hash dimensions and RGB bytes. Equal hashes establish pixel identity. Flag near-identical opposing-role pairs when at least 99% of corresponding pixels differ by at most 2 in every channel. Check the control ROI separately so unchanged background cannot hide a real local cue. Keep ambiguous pairs diagnostic-only unless independent measurements establish a surviving cue.

Require at least 30 independent matched layout groups in the held-out cue assessment. Compute binary balanced accuracy with each group weighted equally and each binary class equally within its component recall. Bootstrap whole groups 10,000 times with seed 619. Require balanced accuracy at least 75% and a 95% lower bound above 50% in the claimed state. Reuse of one asset family does not establish independent groups.

## Explicit hold on training

D1 stays paused. Before seeking Joe's exact-job approval, require T2.5d membership, independently reviewed real-app references and the separability gate. For a proposed 10-role T107 trial, preflight the exact initializer, verified head transfer or replacement, replay labels, seed support and immutable memberships. No legacy generator membership is strict 10-role evidence by default.

Use matched control and treatment at 100 epochs for seeds 371 and 372. Pin fixed final selection, initialization and all execution settings within a seed. Four fits would take approximately 32.5 h serial before export at the recorded probe rate. Where authorized, each guard is 12 h and 2 GiB. Record fresh cost estimates and proposed job IDs before requesting approval.

Both treatments must exceed their paired control by at least 10 percentage points in equal-app exact-role recall and exceed the absolute control-to-control difference. Retain all 11 specified TVCatalog button targets, 30 retained Fixture button appearances and previously correct true-cell targets. Require no added false buttons on completely reviewed screens. Report all losses across other roles, shared localization and per-flow NewsTV results. Reserve fresh qualification flows. [Active gates and training policy](../Tasks.md)
