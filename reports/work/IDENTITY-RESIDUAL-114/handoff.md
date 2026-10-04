# IDENTITY-RESIDUAL-114 — baseline-preserving correction

DTM029 improves the newly admitted scrolling cases but fails the retention gate.
No model promoted, exported or substituted in TTR.

| Group | DTM025 confident correct | DTM029 confident correct |
|---|---:|---:|
| Old training |106/108|107/108|
| Related Settings diagnostics |5/5|4/5|
| Region training |0/94|92/94|
| Identical-frame negatives |217/217|217/217|

All217identity probabilities are exactly unchanged, all frozen weights unchanged,
and saved checkpoint replay exact. Region has94/94raw correct but two abstentions
(transition offsets48/49:0.71418/0.81991). Related Settings row25 changes from
0.03511to1.0despite unchanged-focus truth. These are exposed/train/retention results,
not independent generalization or proof that moving content is understood.

## Implementation and evidence

- scripts/focus_identity_residual.py reuses fit_change_head and existing encoded
  inputs;576zero-initialized weights correct frozen DTM025 features. Features are
  cached once for the fit. No alternate cropper, trainer or source-label oracle.
- Protocol:412a44fa2d4f21284419db89cc4c5eadcaa28f48ac3812dd6e3589e56cbf30fe;
  reports/work/IDENTITY-RESIDUAL-114/artifacts/ready/protocol.json.
- NativeUITrainer/focus_ring_runs/identity114-dtm029/result.json is sealed;
  last.pt SHA256:9de87de3a1660554056559553c7ddd1c51d61754d1ef24bb53e412e5dec57209,
  102351bytes. Configuration and parent corpus hashes pinned in protocol.
- PID87624,exit0;600epochs,Adam0.01,seed42,CPU2threads,fixed-last. Fit1.522s;
  total6.322s; no capture or external wait. Single-pair feature construction/scoring
  from already encoded tensors has warm median1.565ms; screenshot decode/resize is
  excluded. This is not cold, end-to-end or CoreML latency.
- Four new behavioral tests plus26relevant regressions pass (30total). Offline
  Swift build and137tests pass; logs .build/identity114-{build,test}.log.
- Actual CLI prepare and execute pass; second execute fails output_collision before
  mutation; checkpoint hash reverified. Tests cover initialization, identity
  cancellation with nonzero weights, frozen fitting/replay and invalid inputs.
- Existing dirty files and older run artifacts preserved. No Git writes.

## Independent outcomes / next tranche

Software verified: passed. Data eligibility: existing training admission retained,
no new role changes. Producer-specific integration: not assessed this tranche.
Model advancement: failed. Production: not qualified.

Next: audit the failed Settings negative and retained native content-motion controls,
compare residual-feature responses against Region changes, and freeze a justified
next candidate plus genuine separate evaluation membership. Do not solve retention
by silently admitting that diagnostic or tuning thresholds. TTR should retain full
before/after frames with native focus identity and motion evidence; no recapture or
new interface is requested. Existing DTM025 remains passive-only.

## Coordination

Verified sillycon.local/SharedStatusFile SMB mount. Published response
nuiak/responses/nuiak-20261004-identity114-retention.yaml and own packet in
nuiak/status.yaml; exact-byte readback and duplicate-key-safe parsing pass. Unrelated
status content retained by semantic hash comparison. Response SHA256:
140a5150bf7e7daa2a65d3ced5937859dcf1d76087f730ce9e0b44d81962cbf4.
Peer acknowledgment remains unverified. Latest peer snapshot08:30:34UTC reports
survey16 retained40frames/39intervals and unchanged-Select repair pending validation;
that report is not independent NUIAK intake or label admission.
