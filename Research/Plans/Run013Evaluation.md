# IOS-R013-EVAL — approved local evaluation tranche

Assigned by maintainer 2026-09-27; owner: current NUIAK evaluation worker.
Parent: TASK-6a-11. This is evaluation, comparison and documentation only.

Freeze Run013 epoch-91 best.pt and r7 manifest/YOLO exports, category map,
runtime and evaluator source identities. Audit every member through source
manifest, PNG decoding, byte/pixel hashes, sidecar-to-YOLO correspondence and
split/family checks. Preserve all source data and prior reports.

The 2,000 original r6 test members are a withheld-family diagnostic; the 400
addon test members share all four families with training and are within-family
diagnostics. Report each separately, plus a supplemental combined score.
homeIndicator, unknown and webContent lack test support. Historical testing and
failure-driven development mean the reused r6 cases are not an untouched final
release challenge. No DS-G8 pass can follow from this tranche's partial coverage.

Reuse eval_phase6a.export_predictions and prediction-artifact-v1, explicitly
binding checkpoint and manifest. Settings remain 640, confidence0.001, NMS0.7,
max300, MPS, no augmentation. Reuse compatible Run009 retained predictions on
the exact r6 subset; otherwise perform one explicit Run009 evaluation of that
subset. Recompute both sides using the existing all-point interpolated AP
implementation in eval_ios_r6_baseline; label it custom VOC-style AP, not official
Ultralytics/COCO AP. Report AP50/70/90/50:95 and P/R, misses/FP at confidence0.25,
IoU0.5; include per-family support and geometry results. No threshold tuning.

Only additive local driver/tests and minimal existing-evaluator changes are
needed; no public API, taxonomy or sidecar schema changes. Reports, frozen
manifests, logs and source hashes go to reports/work/IOS-R013-EVAL; configured
caches/temp stay in-project. Missing/corrupt inputs stop inference; failed
prediction rows prevent metric qualification without silently reducing membership.
Known family overlap is reported, not repaired by moving source data.
Explicit input manifests may include optional imageSHA256/labelSHA256 fields;
when present the loader rejects changed bytes before inference. Legacy manifests
without these additive pins remain readable. All source splits receive normalized
label validation. MPS availability and inference elapsed time are recorded locally.

Acceptance: complete2,400-member accounting; separately reported populations;
strict compatible baseline comparison; per-class/family errors and coverage;
focused offline tests plus offline Swift build/test; concise handoff with four
outcomes, all acceptance evidence, exact limitations and prioritized next assignment.
Research/CurrentState, ExperimentLog and Tasks are updated. Local iOS findings
need no SMB publication unless they change TTR's next action. No training,
export, promotion, device capture or new worker is authorized.
