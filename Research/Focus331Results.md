# FOCUS331 — image-only boundary regions

## Decision

Reject both crop-replacement rules before training. Neither passes the fixed coverage and purity requirements.
Boundary ranking helps 13 of 15 measurable groups. It harms both artwork-change families.
This finding supports keeping existing image evidence while testing added boundary evidence. It does not support replacing the existing crops.
No candidate starts. Current models, labels, thresholds, data roles, and source images remain unchanged.

## Fixed comparison

The audit checks all 548 native-derived training pairs from 17 groups.
It verifies source hashes, metadata, observed focus identities, measured bodies, and encoded pixel agreement.
Only training images enter rule selection. Measured bodies serve only as diagnostic references.
The selector smooths each frame with a 5 × 5 mean filter. It measures differences between per-frame gradient magnitudes.
It ranks legal 32 × 32 windows. It selects at most 2 nonoverlapping windows, matching the existing maximum crop budget.
An empty edge signal retains the original windows. An unchanged image remains an unchanged image.

The boundary rule selects both windows from edge changes.
The retained-first rule preserves the original first window and selects the second window from edge changes.
Both rules use pixels only. Neither uses detector boxes, focus labels, or control measurements.

| Mean measurement | Original | Boundary | Retained first |
| --- | ---: | ---: | ---: |
| Boundary coverage, 485 nonzero cases | 54.47% | 59.02% | 49.32% |
| Boundary fraction inside crops, 470 supported cases | 30.93% | 27.41% | 28.06% |
| Boundary coverage, 279 content cases | 44.49% | 38.39% | 35.85% |
| Boundary fraction inside crops, 279 content cases | 22.96% | 16.09% | 17.96% |

Boundary coverage improves overall, but the difficult content cases get worse. The selected crops also include more non-boundary change.
The registered requirement needs coverage to improve by 0.02 on both subsets. Purity cannot fall by more than 0.02.
Neither rule passes. The report preserves the requirements instead of changing them after the result.

## Family and label checks

Boundary ranking improves mean coverage in all 12 recipe groups and the style-first group.
Both content families lose coverage. The 2 other style groups have no boundary change, so their coverage remains unavailable.
These are related training groups, not independent deployment trials.

On 210 content cases with changed focus, mean coverage falls from 42.29% to 36.27% with boundary ranking.
On 69 content cases without changed focus, mean coverage falls from 51.19% to 44.83%.
Thus, the failure does not depend only on mixing changed and unchanged labels in one summary.
These percentages describe retained image evidence, not model accuracy.

## Verification and limits

The audit takes 98.70 s. It makes no detector calls and starts no training.
The focused suite passes 44 tests. Tests cover reversal, batch agreement, fixed budgets, clipping limits, fallback, and existing cropper integration.
Existing tests also cover altered image hashes, missing geometry, conflicting observations, and source crop parity.
The offline Swift build, 14 XCTest tests, and 173 serial Swift Testing tests pass.
The handoff records coordinator receipts separately from peer acknowledgment.
Result `nuiak-focus331-result-01` passes exact-ID readback at cursor 179. Forwarding and TTR acknowledgment remain unconfirmed.
Raw measurements and exact input hashes remain in ignored FOCUS-331 output.

- Software: the selector and complete audit execute successfully.
- Data: existing training roles remain unchanged. Native-derived data does not establish real-app performance.
- Integration: no new TTR runtime or capture test occurs.
- Model: no candidate starts; no model is promoted.

## Next substantial tranche

FOCUS332 should preserve both original crops and add boundary crops as separate inputs.
This changes the detail budget from 2 crops to 4 crops. Do not describe it as an equal-cost comparison.
Use the retained FOCUS327 checkpoint as the unchanged control. Keep its whole-frame and existing detail decisions available.
Initialize the added correction to 0. Verify exact initial agreement with the control.
Train only the added branch for 1 fixed 30-epoch run on the same eligible membership and weights.
Keep raw channels, original-resolution extraction, thresholds, and all evaluation exclusions.
Measure memory, latency, correct decisions, false changes, missed changes, abstentions, and every lost previous success.
Require useful native gains without regression before replacement. Report inspected evaluation separately from untouched final evaluation.
This proposal tests whether complementary image evidence helps. It does not assume that better boundary coverage means better model accuracy.
The added crop budget and branch form a new proposed experiment. No additional run starts here.
