# HCF334 — the detector finds the control, but focus selection can fail

## Decision

Keep HCF rules as optional review assistance. Do not let the current model override them automatically.
A separate HCF model is not yet justified. First test rules against independent negative and unfamiliar-layout examples.
Use model disagreements to select review cases, not to create training labels.

## Actual execution

The existing production CLI processes all 8 retained images successfully in 1.88 s, including startup.
The data contains 7 unique images from 1 journey. Six frames have saved HCF analysis.
The run uses the shipped tvOS detector at confidence 0.25 and disables OCR.
The focus receipt confirms Core ML execution, complete scoring, and no failed predictions.
Production FocusRing uses its existing thresholds and crops. No model weights or settings change.

Detector digest: `86cc39b1e7d374d760251986d8ace8e2f35535633a82f94c9a611087d3050a79`.
Focus digest: `1fe0de316544d7177c8d99757a9b0b5779aab102a1345c2ac71e5d3ffc5493c2`.
Digest algorithms remain in the raw runtime receipts. They are different contracts and are not interchangeable.

## Comparison with saved rules

| Frame | Captured profile | Model versus rule | Detector overlap with rule | Focused-box overlap |
| --- | --- | --- | ---: | ---: |
| 24 | Default | Agree | 0.738 | 0.738 |
| 30 | High Contrast | Agree | 0.749 | 0.749 |
| 36 | High Contrast | Agree | 0.804 | 0.804 |
| 47 | Default | Model only; rule abstains | Unavailable | Unavailable |
| 32 | High Contrast | Disagree | 0.805 | 0 |
| 34 | High Contrast | Disagree | 0.771 | 0 |

IoU measures overlap between proposals, not precise annotation accuracy.
The detector contains a matching proposal for all 5 rule-supported frames.
The model selects a matching box in only 3 of those frames.
The prior visual review supports the 5 rule identities. This is development evidence, not independent accuracy.

Frame 32 exposes a ranking failure. The rule-matched control receives focus score 0.987, but another control wins.
Frame 34 exposes a scoring failure. The rule-matched control receives focus score 0.00218.
The selected clock-area box receives 0.913. Fresh visual review confirms that the outlined placeholder icon is focused instead.
These failures differ. More detector proposals or a global threshold change alone does not address both.

Requiring rule/model agreement would retain only 3 of the 5 reviewed rule proposals.
Therefore, agreement is useful for sorting review work, but it is not a justified universal acceptance rule.
The model-only Default result is not proof that the model repairs the rule abstention.
No-focus specificity remains unavailable. The retained analysis frames all visibly contain focus.

## Timing and limitations

The first image takes 1060 ms, including model setup. The 7 warm entries take 91–115 ms each.
These timings include production analysis, not only model inference. Hardware scheduling is not observed.
Frame 45 duplicates frame 24. Do not count it as independent support.
The duplicate produces the same selected focus, but some other scores vary slightly. Do not claim bitwise runtime determinism.
No fresh rule inference occurs. Saved rule results and current model results do not establish a matched latency comparison.
The run measures the ordinary shipped FocusRing, not a separately trained HCF model or the transition model.

## Native capture check

The scoped host process check finds Fixture on simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`.
It finds no running TTR desktop app. This does not prove the simulator is ready for a new capture.
Maximum-mini-TTR source remains `d06a64bd8840c5ada053fd90841c56cef2a9dd58`.
Two Xcode user files have local changes. No Git pull or source modification occurs.
Current CLI help does not expose automatic HCF profile switching.
No settings, service, ownership, or runtime state changes occur.

## Verification and next tranche

All 19 focused tests pass, including report failure cases and the existing review CLI and editor tests.
The offline Swift build passes. All 14 XCTest tests and 173 Swift Testing tests pass.
Coordinator stores `nuiak-hcf334-result-01` at cursor 187. Exact-ID readback passes; forwarding and peer acknowledgment remain unconfirmed.
Final attention has no unread messages. No new peer artifact offer arrives through chat.
Raw results remain in `reports/work/HCF-334/`; `comparison-v2.json` records the final diagnostic fields.
The next native tranche needs the TTR desktop app and a supported profile lifecycle with restoration evidence.
Use the existing 48-screen development plan with independent layout groups and verified negative cases.
Prioritize competing highlights and clock/profile badges because this run identifies a concrete selection failure.
Keep independent evaluation separate from these inspected cases. Preserve current production models.
