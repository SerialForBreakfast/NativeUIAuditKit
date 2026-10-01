# FDR023 authorization — October 1, 2026

Maintainer: “Why do you need approval for this? I approve it, but maybe we should
loosen this rule/”. This accepts the preceding exact request for one cached-feature
weight-control comparison, up to 1,000 updates / 300 training seconds, no encoding,
retry, export or promotion. Outer process cap: 600 seconds including input checks.

Protocol: 438ceeeeb1eeb6c0627f49da19a01febafb62e5559d0b6c85a51718d23fb2767
at reports/work/FOCUS-GROWTH-02/artifacts/reweighted-protocol/protocol.json.
Arm: native-body-full-fit. Output: NativeUITrainer/focus_ring_runs/fdr023-weight-continuity.
1,550 training controls; unchanged 315 development + 18 retention; seed 42;
fresh linear head, existing frozen cached features, AdamW lr .01 / decay .01,
full batch, fixed .85 evaluation and existing guarded checkpoint selection.

Approval-rule relaxation is a proposal, not blanket permission inferred from
“maybe”. This record authorizes this single run only.
