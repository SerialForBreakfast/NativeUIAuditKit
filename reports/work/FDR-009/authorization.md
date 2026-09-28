# FDR-009 authorization and execution boundary

Maintainer answered **yes** to: one development-only experiment selecting checkpoints
on the existing nine retention pairs while preserving their accuracy floor, maximum
30 epochs/30 minutes, no export/promotion/qualification claim. The prior
[decision](../SIM-FOCUS-DEV-01/selection-decision.md) specifies the concrete policy.
This authorizes the current worker to finish integration, preflight and one run
without further generic training approval. It does not authorize a retry.

Frozen membership:273 training pairs (546 crops),9 retention pairs (18 crops).
Train sources are40 native pairs plus233 Fixture pairs. No new random split or
independent-family claim. The52 new additions include two repeated focused crop
pixels with different matched negatives; support counts preserve this distinction.
FDR-007 warm weights, fresh AdamW,50/50 logical-source sampling,30epochs,batch64,
lr0.0003,seed42,no augmentation,production16%/256 stretch. Threshold0.85.
Eligibility requires18/18 retained classifications; minimum retention BCE selects
among eligible epochs, earliest tie. No eligible epoch means no selected checkpoint.

`focus-retention-experiment-v1` is a new development policy. The original immutable
full appearance extension and its ten unmet coverage blockers remain unchanged.
ProtocolSHA256 `9c525a6f1f6698417a2a4af299e13b97459b53cbf3002511cd12f93821f3423f`;
`approval.json` binds that exact protocol, arm and output. `frozen-index.json` records
runtime/code/data/model identities. Changes invalidate preflight, not silently repin.

Execution uses the resident focus-export-01 Python3.12.9/torch2.7.0 environment and
MPS if available, with actual backend recorded. Configured caches/temp/logs/checkpoints
stay in-project. No downloads, dependency edits, installs, device operation or other
repository edits. Fresh optimizer, not interrupted-run resume. Launcher allows one
child with a conservative1,800-second total-process deadline including preflight;
the trainer separately checks a1,800-second internal compute cap. On deadline only
the owned child is terminated, evidence is retained and no automatic retry occurs.

Expected deliverable: software checks, actual training/preflight receipts, selected
checkpoint or explicit no-selection/failure evidence, verified retention metrics,
four separate outcome statements and updated local status. A post-run48-frame
transfer diagnostic is the next separately assigned evaluation, not included in
the approval. No protected challenge scoring, CoreML export or model promotion.

Coordination: not applicable. This local model run does not change TTR's existing
nine-control diagnosis or EXT-CAP assignment, so no SMB access/publication is needed.
