# Native SDK action-pair delivery

October 24, 2026. Receiver: Maximum-mini-NUIAK.

The new TTR delivery contains 6 action-linked pairs and 12 screenshot packets.
The archive size and SHA256 match the producer receipt. All packet member hashes pass.
The existing packet consumer accepts all 12 packets without a schema change.

## Newly usable evidence

- All 24 registered element observations include `UIButton` class names and measured screen-pixel bounds.
- Stable element identities, lifetime IDs, and revisions accompany those observations.
- Visibility, enabled state, effective alpha, public labels, and accessibility traits are available.
- Four packets explicitly observe no focused item. Eight packets observe a focused item.
- Requested and delivered action identities match. Simulator, app, process, run, and group checks pass.
- Producer supervisor intervals establish before/action/after ordering. Packet clock identifiers remain independent.

| Requested case | Derived focus outcome | Limitation |
|---|---|---|
| No focus | No focus at both endpoints | One related procedural group |
| Arrival | No focus to focused | Review-only |
| Move | Focused identity changes | Review-only |
| Unchanged | Focused identity stays unchanged | Review-only |
| Content only | Focused identity stays unchanged | Content motion is not independently verified |
| Departure | Focused to no focus | Review-only |

These observations support precise crop placement, registered-box coverage, and focus-state regression tests.
They remove the previous missing-native-no-focus blocker for this sample.
They do not establish complete detector annotations or independent test accuracy.

## Remaining limits

Inventory coverage remains registered elements only. Occlusion, clipped bounds, and complete visible inventory remain unavailable.
Parent links are absent. Registered selection is not a verified native selection label.
All cases share one ancestry group. Preserve the requested test split and review-only admission.
Do not use these packets as training data without separate membership and role qualification.
Source hashes describe an uncommitted delta. Reproducibility from committed source remains unqualified.

## Next experiments

1. Compare optional observer outputs against observed focus across all 6 cases.
2. Compare detector proposals against registered button bounds without treating unmatched predictions as false positives.
3. Use arrival and departure to test abstention and false selection at transitions.
4. Request training-role groups with varied layouts after these consumer comparisons pass.

No new model, capture, or training starts during intake.
Receipt `nuiak-sdk507-receipt-20261024-v1` is stored at coordinator cursor 1364. Delivery acknowledgment remains pending.
The sender owns shared-copy cleanup. Maximum-mini-NUIAK preserves its local archive and extracted evidence.

See [verified intake](../reports/work/SDK507/intake.json) and [transfer receipt](../reports/work/SDK507/receipt.json).
