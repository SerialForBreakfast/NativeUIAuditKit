# Localization55: controlled candidate and metadata companion

October3,2026. Scope complete; DTM002 is **not usable**. No weights promoted,
new capture, export, split change or automatic follow-up experiment.

## Outcome

Same24Fixture train/5Settings development pairs as DTM001,30epochs/90updates,
same six-channel96×64CNN, seed42, Adam0.001,batch8,CPU2threads,fixed-last. Only
box MSE changed to unit-weight mean GIoU loss plus coordinate L1; BCE unchanged.

| Metric | DTM001 | DTM002 |
|---|---:|---:|
| Train raw change |24/24|24/24|
| Train both endpoint IoU≥0.5 |2/24|0/24|
| Train before/after mean IoU |0.4023/0.3954|0.2705/0.2643|
| Settings raw change |2/5|5/5|
| Settings both endpoint IoU≥0.5 |0/5|0/5|
| Settings decisions / abstentions |3/2|0/5|
| Settings confident joint success |0/5|0/5|

No invalid decoded boxes, but localization fails. Train normalized width errors
increased0.0708/0.0851→0.2835/0.2473. Settings mean IoU increased slightly to
0.0555/0.0666, far below0.5. Loss1.91144→1.22733 is not comparable with MSE loss.
The hypothesis is not supported at this fixed budget. Five exposed development
pairs cannot establish generalization; raw classification gains are not safe decisions.

Existing96×64encoding leaves Settings focus boxes only3.45–4.12pixels tall;
Fixture heights span4.05–20.5pixels. This suggests a spatial-resolution/representation
diagnostic, not proof that resolution alone caused failure. Do not tune thresholds
to salvage this checkpoint. Full scene/no-focus detection remains untested.

## Acceptance evidence

- Software:68Python tests pass3.226s, covering legacy MSE, identical/disjoint GIoU,
  nonzero finite gradients, closed configuration rejection, per-endpoint failures,
  geometry, admission, corruption, collisions, actual legacy prediction CLI and
  generated-fixture optimization. Logs `.build/direct55-python-tests.log`.
- Real trainer preflight exit0 with no blockers; execution exit0/tool session90861,
  16.814s including input revalidation/fit/scoring. OS PID not recorded.
- Checkpoint evaluation exit0: all5saved development predictions match reload;
  new and legacy prediction CLI outputs match their retained reports. Initial
  malformed empty request was rejected before inference; corrected request then
  passed. Failure retained in `.build/direct55-prediction.log`, success in
  `.build/direct55-prediction-verified.log` and `direct55-legacy-prediction.log`.
- Warm20sample CPU median4.269ms,p954.477ms; load519.1ms, first measured pair19.20ms.
  Resize/forward/box decode included; PNG load excluded, not process-cold latency.
- Offline Swift build4.12s plus test build2.43s pass;14XCTest+120SwiftTesting tests.
  Logs `.build/direct55-swift-{build,test}.log`. Scoped compiler sandbox escalation,
  existing local caches, no dependency downloads or device use.
- Read-only metadata companion: resource modelID`focus-ring-detector-v1.0`,
  versionString`1.0.0`, RGB256×256, thresholds0.85/0.70,isUpdatable0. README,
  loader comments and spec distinguish artifact identity from historicalv0.1
  qualification; TASK-DOC-01 metadata checkbox closed. No resource bytes changed.

## Pins and preservation

Local ignored `protocol.json`, `approval.json`, `checkpoint-evaluation.json` and
prediction files are retained under this directory. Original54admission reused:
corpus`9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.
Protocol identity`832c544cc449e88b4132c3452132b4f7c0da179dbf9a19abc8fffa5c623d08e5`.
Run`NativeUITrainer/focus_ring_runs/direct55-dtm002`,625,188bytes (2GiB cap).
5.1GiB free before execution. No external wait/capture time; no SMB publication.

- Checkpoint SHA256`1b0a81413f79912da5e84ea824ff564642e4b14060f9618eae2bf3510172d463`.
- Result SHA256`644e1dec702f8f2768769d73c1455778fa40af959eb52d82f257483bee5edc8b`.
- Evaluation SHA256`a04f341fb03d310c922596b7c8a14d7c611d322c88a753861fe1ed9b23bfefe3`.
- Metadata SHA256`cf847ab2dd843c692cd2073530606d74ecd3efd6274544261eb61a76fa6682ab`.

Sources changed: direct learner loss/config handling, existing evaluator endpoint
diagnostics, new localization tests, canonical plan/queue/snapshots/log and metadata
docs/comments. Preserved prior uncommitted54implementation/reports/docs, original
source pixels, DTM001checkpoint and reports. No Git writes.

Software verified: yes. Data eligible: exact admitted development experiment only.
Integration: local trainer/evaluator/prediction verified; no new TTR/live evidence.
Model gates: not passed/not production assessed. Shared coordination: not applicable;
this local candidate does not change the peer's next action. Existing cleanup request
remains untouched and its status has not been freshly diagnosed here.

## Next substantial tranche

1. Pin a spatial localization representation and bounded tiny-subset memorization
   diagnostic to distinguish optimization/representation failure from transfer.
2. Only if fit succeeds, compare on the unchanged24/5roles with fixed metrics;
   include changed/unchanged, invalid-box and confident joint outcomes.
3. Independently audit deconfounded coverage (no-scroll switch, scroll without
   switch, textured backgrounds) and prepare exact additional label needs.

New representation/run settings need explicit tranche scope before execution.
No physical-device access, live retry, new data admission or model promotion implied.
