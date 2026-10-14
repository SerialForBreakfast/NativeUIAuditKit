# FOCUS349 — movement weighting and real recording review

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Model result

The fixed movement-weighted candidate completes 10 epochs in 542.9 s.
It preserves original training images, crops, primary weights, membership, and thresholds.
The augmented images exactly match FOCUS348 gamma. Only auxiliary class weights change.
The checkpoint passes exact reload comparison.

On the targeted authored gamma test, both candidates produce 26 false changes and 372/464 correct movement decisions.
The new weighting does not recover the lost movement detections.
Across the complete 1,408-pair target comparison, correct decisions fall from 1,107 to 1,085.
Abstentions rise from 242 to 265. Incorrect stable decisions fall from 33 to 32.
These totals include 16 native development cases. Authored movement results remain separate.

On the original 1,408 cases, correct decisions rise from 1,154 to 1,155.
The candidate still loses 39 previous successes on that set.
Both models miss all 8 native corner movements. This failure does not improve.
FOCUS329 remains unchanged. The candidate does not qualify as a replacement.
All 35 comparison jobs finish and report 56 sets.
FOCUS348 gamma loses 56 retained successful decisions. FOCUS349 loses 55.
These totals include related frame orders and disturbance strengths. They are not 55 independent trials.
The complete receipt is `reports/work/FOCUS-349/results.json`.

## Cached branch findings

This review also closes the pending analysis of FOCUS344 jobs 06–10.
It uses retained scores without new inference or training.
The table compares whole-frame scores alone with the existing whole-frame plus detail model.
It does not propose the whole-frame-only model for deployment.

| Cases | Count | Whole-frame correct | Combined correct | Added successes | Lost successes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Authored movement | 464 | 40 | 373 | 333 | 0 |
| Artwork change only | 464 | 392 | 333 | 55 | 114 |
| Identical images | 272 | 272 | 272 | 0 | 0 |
| Matched content changes | 192 | 15 | 27 | 27 | 15 |
| Reversed authored movement | 464 | 40 | 373 | 333 | 0 |

Movement and artwork cases cover 5 source groups. Matched content cases cover 3 groups.
Reversed cases are related to forward cases. They do not add independent support.
Detail information is essential for many movements, but also removes correct artwork decisions.
Neither suppressing detail nor increasing movement weight solves that distinction.
The next useful comparison needs better separation of focus effects from content, not another unchecked scalar weight.

## Office recording

[The Office report](OfficeCapture349.md) describes the verified capture and reusable scripts.
All 121 image files pass exact hashes and decode checks. All images remain private and excluded from Git.
The recording contains 142 commands, 117 reported result frames, and 25 missing results.
The current audit qualifies no command-linked transitions. Fresh before frames are absent, and counter meanings need confirmation.
These limits do not prevent single-frame review or visual-pair analysis.
The queue scores all 21 selected visual pairs with 3 fixed models. The models disagree on 4 pairs.
Full-image inspection identifies 3 visible focus movements and 1 screensaver-to-Home arrival among those disagreements.
The 3 movement cases include adjacent growth, right-edge movement, and small-tab-to-large-row movement.
FOCUS349 reports stable, abstain, and stable respectively. These are useful failure examples, not a qualified accuracy set.
The existing annotation tool has an 8-frame diversity package and an 8-frame priority package.
Two failed priority attempts stay preserved. A tested explicit option permits standalone diagnostic frames without changing default admission.
No training admission occurs. Assistant visual notes remain separate from human-confirmed labels.

## Software checks

The latest focused pass runs 53 tests successfully.
The earlier queue and dashboard pass runs 113 tests successfully.
The offline Swift build passes in 2.68 s.
The first full Swift test attempt stalls in the owned-process cancellation test.
The isolated test then passes. The remaining suite passes without that test.
All 187 tests pass across those 2 checks. Do not describe the first full attempt as successful.
The original failure log and process sample remain under `.build/focus349-swift-*`.
No Swift production code changes in this tranche.

## Queue decision

All 38 jobs finish: 1 training job, 35 matched comparisons, and 2 private recording comparisons.
They use 2,121.2 s of total worker time. The complete tranche takes approximately 52 min against a 45–75 min estimate.
Jobs use the existing detached runner. Each diagnostic has an 800 s and 100 MB limit.
The 43 old blocked jobs remain accounted for. They are not an executable reserve.
Do not add repeated inference to maintain a displayed job count.
The next batch should reuse old model predictions when input and preprocessing hashes match.
This batch still repeats control inference. That remains an avoidable cost for later comparisons.

## Next substantial batch

First, review the 3 visible movement cases and retain explicit unknown labels where required.
Then reproduce their control sizes, positions, and effect styles with local Fixture tools.
Keep the Office images in development and generate separate training examples.
Compare matched growth changes with content changes at equal budgets. Preserve the current model's successful cases.
Qualify the capture build and counter meanings separately. That work does not block visual-pair review.
Use worker-host-NUIAK for longer fixed training only after the local cases and exact inputs are ready.
Do not ask worker-host-NUIAK to duplicate this transfer or the completed score comparisons.
