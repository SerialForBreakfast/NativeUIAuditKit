# Approved static-human comparison — 2026-09-30

Owner Codex, HUMAN-STATIC-ADMISSION. Maintainer: “Lets try that experiment.”
This authorizes the inventory proposal's whole-session role amendment, implementation,
preflight and two bounded training arms, not export/promotion or further experiments.

Freeze the existing395 native/Fixture pairs, nine retention pairs, inventory and
exact138 eligible supplement members. Move the entire eight-frame supplement session
and all descendants out of development selection; its17 excluded controls stay excluded.
Keep315 human selection crops and the other47 exclusions. Preserve original artifacts
and protected challenge reservations. New versioned admission records retain human
label provenance; no fake native observations, pair IDs or transition labels.

Both arms use the pinned ImageNet MobileNetV3-small frozen encoder/BN, fresh577parameter
linear head, AdamW0.0003, seed42,30epochs,1,800seconds per arm. Production256stretch,
16% crop context, ImageNet normalization and0.85threshold stay fixed. Reuse encoder,
paired loss, evaluator and trainer entrypoints; explicit new protocol dispatch.
Frozen features may be computed once for the union and reused with exact ID/hash order.

At each epoch draw395 genuine pairs with the existing appearance-balanced distribution
and identical seeded schedule. Partition138 auxiliary slots among the same13 updates;
A draws baseline crops, B visits each human crop exactly once. Each human frame has
equal aggregate auxiliary weight. Each update's main loss is scaled by its pair share
of the epoch and its auxiliary loss by the sum of slot weights, both scaled by13;
this gives exact aggregate80/20 coefficient mass without oversampling positives.
Identical update/forward counts, slot weights and initial head; human labels receive
BCE only. No gradients through the encoder. Maximum30presentations/human crop.

Selection retains the original absolute guards (retention18/18, realTP>3/FP<=9,
per-stratum floors, at least2 unique correct frames and no wrong/multiple). Apply
the separately approved Photos completeness amendment:14supported frames, not13.
Recompute balanced loss weights on315members. These conservative absolute floors
are not retuned to make the smaller corpus pass. Minimum balanced development BCE
among eligible epochs, earliest tie; no eligible epoch means no best.pt. Historical
453-member scores receive no numeric delta. Compare both arms on common completed
epoch budgets; truncated or failed execution stays explicit.

Acceptance: exact member/source/image/crop verification and scoped reservation
amendment; real trainer preflight; matched schedule/initialization evidence; negative
tests for membership, protected leakage, labels and stale approval; legacy tests and
offline Swift checks; complete predictions, family/stratum/frame deltas; status and
handoff with software/data/integration/model outcomes. No independent-transfer claim:
remaining development data is one connected group, already repeatedly inspected.
