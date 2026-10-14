# FOCUS309: context and enlarged detail

## Decision

Do not promote either model. The candidate improves training fit but fails the intended correction.
It still misses every tiny-control focus change. It increases false changes from center distractions.
Keep the previous models and all evaluation roles unchanged.

## Matched experiment

Maximum-mini-NUIAK completes 2 serial runs from DTM085.
Both use the same 1,820 training entries, labels, weights, seed 42, and thresholds 0.15/0.85.
Each run uses 30 epochs, batch 16, learning rate 0.0001, and 2 CPU threads.
Each run completes 3,420 updates. The existing trainer keeps geometry weights unchanged.

The control adds a second full-frame branch.
The candidate adds a 32 × 32 window selected from local image differences.
Both frames use the same window. Both models keep full-frame context and have 339,932 parameters.
The added correction starts at zero. Initial scores match DTM085 within 0.000001.
Saved checkpoints match each live model on the pinned sanity inputs.

The local window comes from the encoded 192 × 128 frame.
The runner stretches that square window to 192 × 128. It does not recover original-image detail.
The correction adds separate contributions from context and detail. It does not use a learned multiplicative gate.
These limits prevent a general conclusion about every context/detail architecture.

## Results

The table shows correct decisions. Abstentions do not count as correct decisions.

| Cases | DTM085 | Matched control | Context and detail |
| --- | ---: | ---: | ---: |
| Native training groups, 548 | 505 | 528 | 539 |
| Native development groups, 40 | 33 | 33 | 33 |
| Reserved native groups, 52 | 51 | 51 | 51 |
| Retained native total, 640 | 589 | 612 | 623 |
| Retained replay, 668 | 667 | 668 | 668 |
| Reversed native pairs, 640 | 582 | 603 | 617 |
| Reversed replay, 668 | 666 | 665 | 666 |
| Global lighting changes, 226 | 226 | 226 | 226 |
| Left distractions, 226 | 144 | 139 | 142 |
| Center distractions, 226 | 80 | 84 | 77 |
| Tiny native changes, 4 | 0 | 0 | 0 |
| Reversed tiny changes, 4 | 0 | 0 | 0 |
| Unchanged tiny comparisons, 8 | 8 | 8 | 8 |

All 34 additional native successes against DTM085 come from training groups.
Reserved performance does not improve. These reserved cases have prior inspection; they are not a new final audit.
Native false changes rise from 2 to 3. Center false changes rise from 121 to 134.
The candidate loses 9 previously correct center decisions while gaining 6.
It also loses 2 left-distraction decisions and 1 reversed native decision against DTM085.
The report includes case IDs and comparisons against DTM078, DTM081, DTM083, DTM085, and the matched control.
The candidate regresses against at least 1 registered reference in 13 of 24 disturbance-strength and direction checks.
Repeated strengths and reversed pairs do not count as independent trials.

## What the added correction does

Removing only the added correction reduces correct native decisions from 623 to 591.
That same removal improves center-distraction decisions from 77 to 92.
Global lighting remains correct on all 226 cases in both checks.
The added correction changes tiny-control confidence but fixes no tiny-control decisions.
The largest forward tiny-change probability is 0.000158, far below the unchanged 0.85 change threshold.

This result supports a narrow conclusion: the added branch learns useful training patterns and harmful distraction patterns.
It does not establish that a different fusion design or original-resolution detail cannot help.
Do not repeat the same fit with more epochs or select a threshold from these 4 native pairs.

## Cost and verification

Both fits and their regression checks complete in 820.40 s, including shared preparation.
The control fit takes 270.83 s. The candidate fit takes 323.99 s.
Checkpoints and initial results use 3,039,956 bytes before the final comparison report.
The separate report uses cached historical predictions and adds one correction-removal check.

Warm CPU time per pair is approximately 0.00200 s for DTM085 and 0.00554 s for the candidate.
The candidate adds 24,049 parameters, about 7.6%, but takes about 2.77 times the measured CPU time.
Timing uses batches of 8 and 5 warm measurements. It is not Core ML latency or an isolated hardware benchmark.

- All 32 focused Python tests pass.
- The actual training, scoring, saved-model loading, and reporting entrypoints pass.
- The duplicate-output CLI check rejects the existing destination before training.
- The native offline Swift build passes.
- All 173 serial Swift tests pass in 55.06 s.

The first build attempts fail on cache access and nested sandbox setup.
The approved retry uses project-local caches and temporary files. It needs no service or signing changes.

## Next substantial experiment

Keep P04 open for the unresolved tiny-control failure.
First measure control-size coverage in the exact current training schedule, including replacement images.
Distinguish missing body measurements from small measured controls.
Then prepare aligned views from original images, with aspect ratio preserved and the full frame retained.
Keep encoded enlargement as the matched control. Use training groups only for any new scale variants.
Include content-only, lighting, and non-focus growth negatives at the same sizes.
Keep the tiny native development cases and previous reserved groups outside training.
Compare 1 fixed candidate with the same regression checks before any broader collection.
This work can use retained original images while TTR repairs the headless renderer.

## Evidence and outcomes

Local evidence is under `reports/work/FOCUS-309/`.
The registration pins membership, initialization, source, settings, labels, and weights.
The comparison hash is `b74c3208bfcad660e40b18c5768d6656616c7d8370120a6bf9ce6b818a84da31`.
The completion hash is `d6359ac130373e79d98f10e49a4ac6b2ee68ce916429f819f4737e885675a971`.

- Software verification passes.
- Existing data roles remain unchanged.
- Retained input compatibility passes. No new live TTR integration occurs.
- Model acceptance fails. No model export or promotion occurs.

The coordinator stores `nuiak-focus309-context-result-01` at cursor 137. The status check confirms storage, not forwarding.
The same result passes readback at `nuiak/responses/nuiak-focus309-context-result-01.json` on the verified SMB share.
Sillycon-TTR acknowledgment remains pending. No new peer assignment occurs.
