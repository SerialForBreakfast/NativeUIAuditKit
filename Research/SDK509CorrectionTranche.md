# SDK509: native crop and departure corrections

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

SDK508 shows crop failures even with measured boxes. Its temporal models miss focus departure.
This tranche tests inference corrections before requesting more training.
Standard, shipped models, thresholds, and original pixels stay unchanged.

## Matched comparisons

1. Compare the production crop against 1.5 times wider context and aspect-preserving resizing. Test each intervention separately.
2. Use the same crop comparison on 8 retained Fixture endpoints. Preserve their calibration roles.
3. Compare forward temporal scores against the maximum of forward and reverse scores on 6 native pairs.
4. Repeat that temporal comparison on 408 retained pairs for the baseline and candidates 42 and 44.
5. Join results automatically. Reject corrections with lost successes or new wrong outcomes.

The crop comparison keeps the original proposal boxes for selection scoring. Wider context changes only the pixels supplied to the classifier.
The native inputs remain review-only with their requested test split. The retained temporal manifest keeps its original roles.
Repeated images and related endpoints do not become independent evidence.

Each diagnostic has an 800 s limit and a 100 MB output limit. No training or capture starts directly.
The existing background runner executes the jobs. The combined report depends on all comparisons.

## Reuse

`scripts/sdk_diagnostics509.py` compiles multiple request configurations and their report with one command.
Use `--output` for a new project directory. Use `--report-id` for the unique combined report.
The native and retained crop campaigns share one implementation. All temporal campaigns share another function in the same adapter.
The compiler does not submit jobs. Existing queue admission records exact specifications and authority separately.

## Producer requirements from these failures

- Supply an explicit visual profile for each group. Unknown HCF mode cannot qualify HCF behavior.
- Keep observed focus identity and screen-pixel geometry aligned with the screenshot.
- Separate layout bounds from presentation bounds and visible clipped bounds when available.
- Record focus effect availability and settlement. Preferred focus is not observed focus.
- Use different training groups for button appearance, content changes, arrival, and departure.
- Declare inventory coverage and exclusions before using screenshots for detector training.
- Keep observed no-focus separate from unknown telemetry and unregistered focused controls.
- Preserve source revisions and sample implementation hashes. Supply source changes through Git.

These are dataset requirements, not authority for new producer execution.
The current test group stays excluded from training.

## Initial execution failures

Both first crop attempts fail because wider context extends outside the image boundary.
Their specifications and failed attempts stay preserved. The repair needs explicit clipping without changing proposal geometry.
Temporal comparisons remain independent of that repair.

The first Swift build fails because a module cache contains the old checkout path.
A separate scratch directory uses resident dependencies and preserves the experiment's pinned helper.

## Verified first results

All 6 corrected comparisons and their combined report complete. Output receipts remain in the queue.
The crop adapter verifies original crop hashes and scores before comparing changes.
Wider context recovers no native focus selections. Aspect-preserving crops introduce 6 new wrong native selections with the mixed model.
Aspect-preserving crops recover 1 retained Fixture endpoint with mixed and fallback scoring. These are 2 scores on the same endpoint.
That narrow gain does not qualify a replacement or repair the native failures.

Temporal maximum scoring recovers no native cases. All 3 models still miss departure.
Across 408 retained pairs, the baseline loses 4 successes and seed 42 loses 2 successes.
Seed 44 gains none and loses none. Reject maximum scoring as a departure correction.

Pixel measurements show a large background-color change before the missed departure.
The paired content-change case has unchanged observed focus. Its outside-control mean absolute channel difference is 112.86 on a 0–255 scale.
This verifies changed pixels, not continuous background motion.
One bounded follow-up compares grayscale inputs against verified RGB scores for native pairs and seed-44 regression cases.
The original image reader verifies hashes before conversion. Conversion happens in memory for both full-frame and detail inputs.
This follow-up uses the same models and thresholds. It cannot promote a model or change original data roles.

## Color comparison outcome

The native color comparison completes. Grayscale recovers departure for all 3 models.
Each model then classifies the unchanged-focus background change as a focus change.
These are the same 2 cases across 3 models, not 6 independent observations.
The seed-44 regression comparison gains 9 cases and loses 39 across 408 retained pairs. Fourteen outcomes become newly wrong.
The automatic report rejects grayscale for all 3 models. Preserve RGB preprocessing and deployed behavior.

The useful next training question is separation of departure from background-only change across controlled visual profiles.
Use separate training groups with both conditions. Keep the inspected SDK test group excluded.
Pair background variation across changed-focus and unchanged-focus examples. Do not let background color predict the label.
Require the original retained comparison and explicit arrival, departure, movement, and no-focus results with each fit.
This is a data requirement. The current SDK delivery does not contain eligible training groups.

## Completion

Ten jobs complete across crop context, temporal order, color sensitivity, and automatic reports.
Two failed crop attempts remain preserved. Their completed replacements permit safe removal from the active blocker view.
No captures repeat. No training or model promotion occurs. The background runner remains available.
TTR capability request 1370 is stored through BigDog-Coordinator. Forwarding and producer acceptance remain unconfirmed.
Completed findings are stored at cursor 1372. The runner remains enabled and waits for eligible approved work at handoff.
Successful execution totals 150.5 s. These diagnostics are not an overnight workload.
The measured implementation interval is 9.3 min from adapter creation to receipt verification; earlier inspection time is not instrumented.
The initial estimate is 45–75 min. No precise total-turn duration is claimed.

## Software verification

The separate offline Swift build passes. All 177 Swift tests pass.
The first build failure remains recorded. The experiment's pinned helper remains unchanged.
Focused tests cover source receipts, context clipping, regression classification, duplicate dependencies, and restoration of the grayscale reader.
All 25 focused Python tests pass. The final code diff check passes.
Failed crop attempts remain preserved. Dashboard replacement links hide them only after their successors complete.
