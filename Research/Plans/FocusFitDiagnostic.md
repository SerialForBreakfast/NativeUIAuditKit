# FOCUS-FIT-01 — establish whether the existing representation can learn

Owner Codex. Maintainer approved “ok. Go ahead” after the small balanced-set diagnostic
proposal. One diagnostic run, not a production candidate or hyperparameter sweep.

Use only FDR017/018-admitted training members:16native/Fixture pairs (four from each
buttons/tabs/artwork/rows stratum), plus8focused human controls and8unfocused human
controls, one of each per approved supplement frame. Choose deterministically by
ID/hash and label/role, never model scores. Human controls remain static labels, not
fabricated pairs. Reject duplicate/conflicting crop pixels and development overlap.
Freeze exact membership before loading features.48examples,24per label. Existing
315development and18retention members stay out of optimization. No challenge access.

Reuse the verified FDR017 feature cache, receipt, source protocol and production crop
hashes, preserving order and ImageNet normalization. No encoder inference or training.
Fresh577parameter linear head seed42; existing trainer's AdamW/BCE path, full batch48,
lr0.01, weight_decay0.01, no sampling/augmentation/pair auxiliary loss. Maximum1000
updates (epochs over this deliberately tiny set),300s model budget/600s external cap.
This is a fit stress test, not a comparable improvement run against30epoch protocols.
MPS required in the actual launch process. No downloads or environment changes.

Record initial and every-update training loss/predictions and gradient/parameter
changes. Stop after five consecutive training observations with all48positives>=0.85
or negatives<=0.15 (according to label) and mean BCE<=0.05, or at the budget limit.
Also report0.5training classification separately, not an alternate release policy.
These are diagnostic fit criteria, not qualification threshold changes. Evaluate
the fixed development/retention set initially, every50updates and terminally with
the unchanged0.85 implementation and14-frame policy. Development scores cannot
influence stopping, sample selection, optimizer or learning rate. No best.pt.

Interpretation: fit success falsifies “this frozen feature/head setup cannot even
learn these examples”; poor development then demonstrates failure to transfer for
this bounded setup, not its unique cause. Failed fit is inconclusive between
representation, labels and optimization until separately diagnosed. Good rank alone
does not establish calibrated scores. No new run follows automatically.

Verify cache/hash/order/labels, balanced/disjoint membership, corrupt inputs,
training-only stop, saved-prediction replay and legacy behavior. Required offline
Swift build/test. Log FDR019 before execution; handoff with four outcome categories
and one evidence-backed next step. TTR capture/crop delivery is not a dependency.

Also score retained FDR017/018 terminal heads on their original cached training
features within this diagnosis (no optimizer/new run). Report native training and
human auxiliary separately: the latter was not trained inFDR017. Replay saved
development predictions to verify head/cache correspondence. This checks prior
training underfit without a second learning experiment or threshold adjustment.
