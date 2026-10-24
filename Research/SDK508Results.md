# SDK508: native SDK model comparisons

Maximum-mini-NUIAK completes 4 queue jobs on October 24, 2026. The detached runner executes all model comparisons.
Output hashes verify for both campaigns, their combined report, and the temporal comparison.
Standard, shipped models, thresholds, and original captures remain unchanged.

## Evidence and limits

The delivered SDK data contains 6 pairs, 12 endpoints, 5 unique images, and 1 related group.
Eight endpoints have observed focus. Four have observed no-focus.
The SDK registers 24 control observations. Sixteen remain visible and enabled.
No-focus endpoints hide both registered controls. Empty known-box inputs therefore provide only a trivial abstention check.
The producer requests a test split. All inputs remain review-only and excluded from training.
HCF mode is unknown. These results do not qualify HCF behavior or independent model accuracy.
The content-only pair lacks verified content motion. Complete inventory, clipping, and occlusion remain unavailable.

## Results

| Comparison | Result | Decision |
| --- | --- | --- |
| Known boxes, HCF crop | 0/8 focused endpoints correct; 6 wrong selections and 2 misses | Diagnose crop behavior before further proposal changes |
| Known boxes, mixed crop | 0/8 focused endpoints correct; 8 misses | Do not promote |
| Scoped proposals, frozen fallback | 3/4 no-focus endpoints produce false selections | Preserve these negative cases |
| Combined proposals, frozen fallback | 1/4 false selections; 3 recovered abstentions but 1 lost abstention | Reject this union policy |
| Combined proposals, mixed crop | 4/4 no-focus abstentions; 0/8 focused endpoints correct | Abstention improves; focus selection does not |
| Temporal baseline and candidates 42/44 | Each gets 5/6 pairs correct; each misses departure | No candidate improvement |

Aggregate counts hide a regression. The combined fallback loses the previously correct departure endpoint, `case-5-after`.
Its other gains do not justify that loss. No model or observer policy changes follow.
Temporal detection identifies movement and arrival on this slice. It does not identify the destination control.

## Reusable execution

`scripts/sdk_campaign508.py` validates pairs, runs 4 proposal arms, and scores both crop models with frozen fallback behavior.
Two disjoint campaigns use this adapter through configuration alone: `sdk508-absence` and `sdk508-movement`.
`scripts/sdk_report508.py` waits for verified dependencies and emits case-linked decisions automatically.
`scripts/sdk_temporal508.py` compares the baseline and 2 frozen temporal candidates on the same pairs.
`scripts/compile_sdk508.py` compiles multiple request files and their combined report. It does not submit or approve jobs.

Use the existing request shape to pin inputs, models, crop tool, and pair membership.
Compile with `--output` pointing to a new project directory and `--report-id` naming a unique report.
Use existing queue admission after compilation. Do not change submitted specifications.

## TTR runtime qualification

The supported source preflight accepts the running Developer Tool application for device preflight.
The retained campaign application fails with `candidate_process_missing_or_ambiguous` because that exact application is not running.
This does not prove a sandbox defect. Do not substitute helpers or change campaign identities silently.
The remaining session work needs a deliberate matching-runtime handoff. No capture repeats or application restarts occur here.

## Next correction

1. Inspect retained crop scores and rendered geometry against observed SDK focus. Separate missing visual context from score calibration.
2. Request separate training groups with observed focus, explicit visual profile, and departure states. Keep these test inputs excluded.
3. Compare unchanged initialization against one justified training correction. Include all previous success and no-focus checks.
4. Qualify complete inventory before using SDK boxes as complete detector annotations.

This tranche supplies a working comparison path. It does not supply an overnight training workload or a model improvement.
Private receipts remain under `reports/work/SDK508` and the 4 queue attempt directories.
