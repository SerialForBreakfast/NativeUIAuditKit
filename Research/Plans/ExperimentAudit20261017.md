# Experiment priorities after the detector review

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Findings

The catalog contains 96 planned investigations after this audit.
Planning records do not establish executable work.
Before additions, only 7 jobs remained ready, with about 30 s of estimated work.
Short diagnostics cannot provide an overnight workload.

B405-178 compares Run 009 and Run 013 on retained native iOS development images.
Run 013 gains 228 detections and loses 66 previous successes across 6 device and layout groups.
The preservation hypothesis fails. Keep both models and the case-linked losses.

B405-179 measures native tvOS detection on 24 images.
Each control family contains 32 labels.

| Family | Correct class and geometry | Geometry without class matching |
| --- | ---: | ---: |
| Buttons | 9/32 | 12/32 |
| Rows | 15/32 | 17/32 |
| Tabs | 0/32 | 18/32 |

Both proposal coverage and class assignment need repair.
These results do not establish release readiness.
B405-177 remains incomplete. Do not choose another native-control fit before its comparisons finish.

## Implementation order

### Follow-up review

B405-177 completes. With known boxes, native-control training improves selections from 12/48 to 42/48.
Buttons improve from 0/16 to 16/16. Rows improve from 12/16 to 16/16. Tabs improve from 0/16 to 10/16.
Mapped proposals miss all 48 native cases for both models.
Retained known-box and mapped outcomes remain unchanged, including 8 no-focus abstentions.
Raw proposals lose 1 retained tall-control success. The full preservation requirement therefore fails.
Do not promote the candidate. Use its checkpoint for bounded diagnosis rather than repeating training.

B405-185 finds 25 losses among 294 middle-right labels and 23 among 784 middle-left labels.
The top-left slice has 4 losses among only 8 labels. These unequal supports do not establish causal position bias.
B405-186 finds 48 of 66 losses among controls 32–64 px high.
Control size, family, and location remain confounded in these observations.
B405-187 removes 2 unmatched predictions, loses 0 detections, and recovers 0 detections.
Suppression is not the main detector repair.

### New insight batch

B405-188 registers 6 cached comparisons through T42.
Ignore class identity while preserving all original boxes and thresholds.
Compare case-linked losses against the class-aware results on both device sizes.
If losses recover, prioritize class repair. If they persist, prioritize geometry and proposal coverage.
Class-free matching remains a diagnostic upper bound, not a runtime change.

### How the new ideas fit

- Targeted sampling has direct support from the native-control comparison, but its retained raw-box regression still needs diagnosis.
- Equal-budget random versus balanced versus targeted sampling remains the next reusable producer task, PAPER417-SUBSET.
- ConClick-inspired ranking remains conditional. Missing proposals cannot be repaired by changing ranking loss.
- No-focus and unknown-state reporting remains necessary. The 8 retained abstentions do not cover broad native no-focus behavior.
- External iOS evaluation remains blocked on access, licensing, and label compatibility. Do not replace these checks with synthetic evidence.

Next implementation: qualify the detector adapter, build the shared subset producer, and diagnose native proposal coverage.
These changes provide more useful work than repeating successful short diagnostics.
The runner may exhaust the 6 new reports quickly. This batch does not satisfy the overnight-work target.

| Priority | Work | Required output and next decision |
| --- | --- | --- |
| P0 | Finish B405-177 comparisons | Report recovered selections and lost successes before another crop fit. |
| P0 | Qualify ENG405-06 detector training and restoration | Prove a bounded fit and checkpoint restoration. Freeze membership for the measured iOS and tvOS failures. |
| P0 | Build PAPER417-SUBSET | Reuse deterministic group selection for learning curves, profile balance, and equal-budget sampling. |
| P1 | Prepare native content-change and temporal producers | Freeze matched recipes, observed focus, roles, and capture requirements through existing T03/T47 support. |
| P1 | Build PAPER417-STATES | Separate verified no-focus, missed proposals, and unknown observations. Reuse B405-004/B405-058. |
| P2 | Build PAPER417-PAIRS and PAPER417-RANK | Proceed when retained competing-control errors justify ranking beyond proposal repair. |
| P2 | Review PAPER417-IMPORT | Resolve access, licensing, taxonomy, and overlap before external dataset admission. |
| P3 | Larger models and broad architecture changes | Require a measured failure that simpler corrections cannot address. |

PAPER417-SUBSET also supports B405-059, B405-122, B405-124, B405-181, and B405-184.
Do not create separate subset scripts for these questions.
The detector adapter blocks 9 downstream investigations in the dependency review.
T03 data requirements affect 9 records and potentially unblock 21 dependent questions.
These counts describe dependencies, not ready jobs or guaranteed benefits.

## Approved diagnostic batch

Use existing T42 matching with retained inference outputs. Do not rerun inference or training.

| Record | Jobs | Test | Decision |
| --- | ---: | --- | --- |
| B405-185 | 6 | Compare iOS gains and losses by screen position. | Decide whether a position-balanced repair addresses the observed losses. |
| B405-186 | 6 | Compare iOS gains and losses by control geometry. | Separate small-control and poor-box failures before changing training. |
| B405-187 | 3 | Remove overlapping cross-class tvOS proposals. | Keep suppression only if it preserves matched detections. |

Each job uses 800 s and 100 MB limits. The detached runner owns execution.
Fewer unmatched proposals do not automatically mean fewer false positives.
Keep all original results, Standard behavior, and model gates unchanged.

## Queue audit rules

- Count ready duration separately from planned investigations.
- Reuse answered comparisons instead of adding duplicate jobs.
- Treat missing producer recipes as preparation work, not missing templates by default.
- Fix shared producers and adapters before adding more dependent hypotheses.
- Preserve exact blocked requirements and their responsible machine and project.
- Do not use speculative models or repeated fits to occupy idle resources.

This audit changes plans, approvals, and reports only. It does not change runner code or active model inputs.
