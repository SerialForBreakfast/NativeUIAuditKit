# SDK513 — Reusable SDK preparation

October 24, 2026. Owner: Maximum-mini-NUIAK.

## Delivered

1. Verify SDK version 1 and 2 action pairs through pinned TTR source.
2. Prepare registered-control crops through the production FocusRing helper.
3. Prepare temporal rows for arrival, departure, movement, unchanged focus, and no-focus.

The compiler creates intake, crop, and temporal jobs from one request.
Each job preserves source identities and existing data roles.
Missing crop metadata does not block valid temporal observations.
The crop output connects to existing T06 training through `crop_training_description`.
Temporal rows work with the existing temporal pixel preprocessor.
These connections do not start training or promote models.

## Verification

The focused suite passes 24 tests in 14.695 s.
Two software campaigns execute the same adapters through isolated queues.
Negative tests cover changed labels, excluded groups, duplicate membership, unknown focus, and leakage between roles.
Tests verify production crop dimensions and the temporal input shape.
The offline Swift build passes. All 177 Swift tests pass across 25 suites.
Software-generated packets prove adapter behavior. They do not prove native model accuracy.

## Retained qualification

The background runner completes all 3 jobs. Their output receipts verify:

- `sdk513-retained-r2-intake`
- `sdk513-retained-r2-crops`
- `sdk513-retained-r2-temporal`

The graph reuses 6 retained action pairs. It does not repeat captures.
The intake preflight finds 16 visible control observations.
The transitions include arrival, departure, movement, unchanged focus, and no-focus.
All retained rows stay review-only. No training data is admitted.
Each job has an 800 s ceiling and a 100 MB output ceiling.
These ceilings are limits, not runtime forecasts. This graph is not an overnight workload.
The detached runner executes this graph without a restart. No model training occurs.

## Limits and next work

Sillycon-TTR source `eb7397d9e0204a9e5b9fcfb98e240e38108d6cbc` supplies the pair verifier.
Its standalone intake audit fails under the installed Ruby 2.6.10.
`training-intake.rb` calls `Hash.filter_map`, which this Ruby version does not support.
Pair verification works. The new NUIAK adapters do not call the failing audit.
Coordinator message 1397 records this failure. Storage does not confirm forwarding.

Sillycon-TTR still needs independent layouts, timestamped profile observations, and matching-host freshness evidence.
The selected-but-unfocused stimulus remains unavailable in the reported calibration scene.
The proposed 6 training layouts and 2 development layouts are not implemented or approved as a new capture batch.
Cross transition classes with layouts to avoid confounding the outcome with the layout.

Partial registered controls do not prove complete detector annotations.
Registration metadata does not prove observed selection state.
An expected background change does not prove independently observed background motion.
HCF crop preparation requires observed HCF appearance. Standard does not require HCF.
Explicit within-family development permits shared app ancestry while preserving group and pixel separation.
Such development does not establish cross-application accuracy.

Next, qualify eligible producer data and bind matched crop training plus temporal comparisons to complete regression reports.
Preserve Standard, shipped models, excluded evaluation groups, and previous successes.

Local execution receipts remain under `reports/work/SDK513/`.
