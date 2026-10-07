# INTAKE225 — candidate and producer evidence reconciliation

Four archives copied from verified SMB, size/SHA256 verified before and after bounded
extraction. Exact receipts: artifacts/receipts.json. No incoming code run, checkpoint
deserialized, capture, new training or Git writes. Approximately426MB expanded.

Published/read back `nuiak/intake225.json`,2731bytes,SHA256
`6818cf0ff8dd4f64aca2c464779cf5e0eef7c645a380458e622a70f923d8819d`.
Peer acknowledgment/cleanup pending. Both peers have exact archive receipt identities.

## Run035

Checkpoint SHA256 `4b28997ba8ab65be589787b23079a480f6b533c061a553827a2553b13af17bca`.
Returned trainer/wrapper match configuration hashes. Existing check_epochs verifies
10epochs,4400batches,275updates, order and finite losses. Configuration matches
recorded manifest;1758slots/249unique sources;11diagnostics of512images.
Five prediction artifacts total621cases, all size/hash/model pins match; all per-class
TP/FP/FN sums reconcile to report totals. This is artifact/accounting acceptance,
not independent inference or rematching. Worker-reported26.62s evaluation.

Versus034, returned native validation24images:TP401→408,FP19→4,FN7→0.
Native diagnostic12images:TP168→197,FP19→1,FN36→7.
ROI fit135images:TP234→0;page37images:30→0;combined413images:331→8,
FP1013→1116,FN1193→1516. Severe retention loss prevents replacement recommendation.
Do not call these focus-classifier gains:035 is the UI detector experiment.
Independent2400full-frame evaluation remains the next experiment acceptance step;
the ROI result cannot answer that different question. No automatic training loop.

## TTR repair09 and failures08

repair09:251members/305354850expanded bytes;62PNG decode;12indices,
115indexed artifacts byte/hash verified. Seven v4 pairs pass existing schema4
structural inspector. Five v3 pairs pass existing full bundle validator.
failures08:83members/75282810expanded bytes;15PNG decode;3indices,
29indexed artifacts verified. Two v4 structurally reviewed;one v3 bundle passes.
Do not turn structural acceptance into label accuracy: the producer explicitly
preserves diagnostic/failed trials. Repair09 includes one diagnostic tab trial.
Version4 path checks frame hashes/dimensions, observed-focus brackets and body
geometry; capture-era source semantics/pixel review/crop parity still gate admission.
Producer reports32tab edges within0.667pixels; not independently rerun here.

Local diagnostic review01 used relative paths and was rejected by the inspector's
absolute-path guard. Corrected review02 preserves that attempt; review03 dispatches
version3 to its existing validator. No weakening or source change was required.

## Outcomes and next substantial tranche

Software: reused existing reviewed validators, accounting checks pass. Data:
no new admission. Integration: transfers verified, live runtime not exercised.
Model: not promoted, full-frame gate unassessed. Existing training and dirty changes
preserved; no source-code change requiring another Swift build.

Next: run035 independent2400frame retention with pinned shipped comparison; review
repair09's capture-era source/body evidence and representative overlays, preserve
diagnostic exclusions; reconcile EVIDENCE223 worker responses into one frozen205/206
campaign. No need to recapture transferred material. Sender owns shared-copy cleanup
after exact receipt. TTR offload request does not authorize changing its local disk.
