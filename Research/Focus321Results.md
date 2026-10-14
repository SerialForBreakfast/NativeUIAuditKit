# FOCUS321 — decision margins and frozen score combination

**Decision: reject the candidate.** Whole-frame and detail scores contain conflicting evidence, but this combination does not preserve previous successes.

## Regression results

| Measure | FOCUS313 | FOCUS319 | FOCUS320 | FOCUS321 |
| --- | ---: | ---: | ---: | ---: |
| Native correct / 640 | 598 | 581 | 581 | 520 |
| Native training correct / 548 | 514 | 491 | 497 | 432 |
| Inspected development correct / 40 | 33 | 38 | 32 | 36 |
| Inspected reserved correct / 52 | 51 | 52 | 52 | 52 |
| Replay correct / 668 | 668 | 646 | 665 | 640 |
| Reversed native correct / 640 | 602 | 579 | 582 | 494 |
| Lighting correct / 226 | 226 | 226 | 226 | 226 |
| Left false changes / 226 | 82 | 53 | 78 | 48 |
| Center false changes / 226 | 99 | 136 | 105 | 125 |
| Tiny changes correct / 4 | 0 | 0 | 0 | 0 |
| Placeholder movements correct / 8 | 2 | 8 | 4 | 6 |

Against FOCUS319, the candidate loses 61 native successes and gains 0.
Against FOCUS313, it loses 85 native successes and gains 7.
The native comparison has 120 abstentions and no incorrect firm decisions. This is not complete detection.
Replay loses 28 successes against FOCUS313. Reversed native comparisons lose 112 and gain 4.
The candidate loses previous successes against DTM085 in 11/24 strength and order checks.
All 4 forward and reversed tiny changes remain undetected. Each direction has 2 misses and 2 abstentions.
All 8 identical tiny pairs remain correct.

The report preserves changed case IDs and their data roles. Previously inspected reserved examples do not become new final evidence.

## Question and method

Can different weights for whole-frame and detail scores preserve previous successes while improving focus-change decisions?
The experiment uses FOCUS319's retained image branches. It changes 3 parameters only.
The experiment preserves original views, data roles, training weights, and thresholds.
All evaluation cases are previously inspected checks. They are not untouched final evidence.

The audit uses 1,820 original training views and 240 reviewed authored pairs.
Detail scores oppose incorrect whole-frame scores in 72/80 artwork-only pairs and 40/80 movement pairs.
These counts show conflicting evidence. They do not prove that a single weight can resolve every conflict.

The fitted score is:

```text
score = 0.408567 × whole-frame + 0.438552 × added-detail + 0.246946
```

The 2 coefficients remain positive. Training starts at 1, 1, and 0.
The existing trainer uses 30 epochs, seed 42, batch 16, and learning rate 0.01.
It keeps auxiliary weight 0.25 and thresholds 0.15 and 0.85.
The experiment selects the last checkpoint. It does not select thresholds or checkpoints with evaluation results.

## Training diagnosis

| Training measure | FOCUS319 | FOCUS321 |
| --- | ---: | ---: |
| Original correct decisions / 1,820 | 1,649 | 1,511 |
| Original false changes | 19 | 6 |
| Original missed changes | 12 | 9 |
| Original abstentions | 140 | 294 |
| Authored correct decisions / 240 | 217 | 210 |
| Authored false changes | 14 | 6 |
| Authored abstentions | 9 | 24 |

The lower loss does not establish better decisions.
Both coefficients shrink. The detail coefficient gains about 7% relative influence.
The model makes fewer incorrect firm decisions, but it also abstains more often.
Keep coverage and error counts separate. Do not lower thresholds to conceal lost coverage.

## Efficiency and verification

The cached fit takes 0.64 s for 3,420 updates. Preparation and image evaluation remain separate costs.
The checkpoint preserves all 34 frozen tensors.
Cached and image-based predictions match exactly on 8 retained parity examples.
Checkpoint reload preserves those predictions exactly.
The focused suite passes 49 tests.
The offline Swift build passes. All 14 XCTest tests and 173 serial Swift Testing tests pass.
Swift Testing takes 53.44 s. The build takes 0.30 s.

The experiment uses resident dependencies and 2 CPU threads.
It starts no capture, download, export, or production change.
Raw evidence remains under `reports/work/FOCUS-321/`.

The margin audit takes 89.81 s. Fit through full comparison takes 172.37 s.
The output occupies about 16.4 MB. Observed process memory is about 2.46 GB during evaluation.
These figures are observations, not a peak-memory guarantee.

| Artifact | SHA-256 |
| --- | --- |
| Candidate | `33c30daa7e99cee9a1d0d4925bb2ea97a674d919566d1408b7b58b7cf9a3eeb0` |
| Comparison report | `98a8dacf965128ced07d17e7a4c88db9e76b5107494ac0e51372ca975b0366c1` |
| Input registration | `49591a0b04a7deed8cd7785522139212bce7d2103639b09424c266493bd888cc` |

## Outcomes and next test

The coordinator stores start and result messages but does not confirm forwarding.
The SMB fallback passes exact readback at `nuiak/responses/nuiak-focus321-result-01.json`.
Sillycon-TTR acknowledgment remains unconfirmed. The update needs no new capture or worker assignment.

- Software: focused tests, offline build, and serial tests pass.
- Data: existing training roles remain unchanged. Authored labels do not establish native fidelity.
- Integration: cached scores match image inference. No new Apple conversion or TTR runtime test occurs.
- Model: previous-success checks fail. No model export or promotion occurs.

Next, test whether the 2 frozen scores can separate the conflicting training cases at the required margins.
Use training membership only. Report the conditions that cannot share one combination rule.
If those scores contain sufficient evidence, test 1 loss that preserves decision margins against the unchanged control.
If they do not, identify missing image evidence before another fit.
Keep the same native, tiny-change, nuisance, reverse-order, and previous-success checks.
Do not treat lower loss, more abstentions, or more authored images as the desired improvement.
