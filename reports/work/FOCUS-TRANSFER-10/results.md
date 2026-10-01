# FOCUS-TRANSFER-10 — reject both changes; change the coverage next

Completed October1,2026. **Neither experiment produced an eligible model. FDR021
and production preprocessing remain unchanged.** The next step is not another
unchanged run or a larger batch of the same poster slot.

## Controlled results

Same1562training controls,315development controls,18retention controls and fixed.85
focus threshold. New runs each completed100updates. The table shows terminal
diagnostics; failed candidates were not selected, exported or promoted.

| Model / change | Focused artwork found /12 | False focus detections /288 negatives | Fully correct focus selections /14 complete screens | Focused buttons /3 |
|---|---:|---:|---:|---:|
| FDR021 retained acceptance baseline | 2 | 3 | 12 | 3 |
| FDR032 matched recent control | 3 | 25 | 12 | 3 |
| FDR033 new examples emphasized10× | 4 | 29 | 11 | 3 |
| FDR034 preserve crop proportions | 7 | 68 | 10 | 0 |

All retain18/18retention controls. The other18development frames lack complete
annotations and are not included in the14-screen selection denominator. This is
development-exposed evaluation, not independent qualification. Every evaluated
checkpoint of both new runs failed the unchanged guards; no threshold search.

### 1. Too little training influence? Tested setting rejected

FDR033 increased the12new controls' aggregate weight from0.695%to6.361%, keeping
both fixture label budgets and every nonfixture weight unchanged. All12remain
confidently learned. VersusFDR032 it corrects one focused home icon but introduces
four false positives; complete-screen selection drops12→11. Insufficient emphasis
at the old level is not a sufficient explanation/fix. This does not prove that
every possible sampling policy fails; it rejects this prespecified change.

### 2. Stretched inputs? Global aspect-fit rejected

The existing Swift cropper reproduced all1895production input pixels exactly.
The experiment changed only its opt-in resize branch: same16%context, same256-square
output, proportional scaling with black padding. Original FDR032weights retained.
Frozen prefix encoding took4.78seconds. See [actual input comparison](artifacts/aspect-comparison.png).

The extra four focused-artwork hits are home-screen icons, **not fixes to the
composite hero/card misses**. The wide NFL false positive was corrected, but the
focused wide Fubo row remained missed. Overall there are7corrected and49regressed
binary decisions versusFDR032, including all3focused buttons becoming misses.
This does not justify a global resize change or a post-hoc per-screen switch.
Aspect-fit preserves proportions, **not absolute enlargement**; tight proportional
crops still normalize away that focus cue.

## Actionable next direction

1. **Keep the working annotation/handoff pipeline.** Its outputs reproduce exactly;
   do not send humans back to redraw the accepted six pairs.
2. **Do not repeat the current partial-backbone recipe on unchanged inputs.** Neither
   more emphasis nor global aspect-fit makes it competitive withFDR021. Do not
   call seven artwork hits a win while false detections rise to68.
3. **Change what TTR generates.** Request native composite image+text containers,
   wide ranked rows and genuinely different home/hero arrangements. Cross bright
   and dark content with both focus states and change focused positions. The current
   48recipes/remaining42cases mainly vary artwork/theme in one standard layout.
4. **Preserve real growth evidence for the next representation test.** Full-frame
   originals, stableIDs, measured per-state body bounds and action-linked pairs
   allow a later before/after model to see enlargement rather than resize it away.
   Do not mix that new representation with a new weighting policy in one test.

TTR has a [concrete capability/coverage request](ttr-feedback.md), published under
`nuiak-20261001-transfer10-coverage`. Request planning/coverage mapping first; this
does not dispatch another capture or cancel its existing42-case assignment.
No new human input is needed to answer that capability request. The gap audit
supports these priorities but does not prove data diversity is the sole remaining
cause; encoder suitability and limited real evaluation remain open limitations.

## Verification and evidence

- FDR033 PID99434,238.196seconds; FDR034 PID99695,208.930seconds. Both hit100updates,
  not the time cap. New encoding+training451.909seconds; artifacts about326MB,
  below1800seconds/2GiB. Rendering separately179.133seconds. No downloads/capture.
- All30retained evaluations (FDR032control and both new runs) replay exactly.
  Identical333evaluation records; emphasis-arm initial predictions identical to
  control; allinitial tail hashes match; tails changed, batch norm did not.
-46focused Python tests pass. Actual CLI accepts both correct protocols and rejects
  six altered contracts: label, weight, evaluation order, runtime, cache and approval.
- Required offline Swift build: zero warnings/errors;134tests passed (14XCTest+
  120Swift Testing). Initial nested-sandbox build denial retained; scoped host build
  succeeded without weakening system permissions.
- No production model, crop default, original annotation or data split changed.

[Metric replay](artifacts/analysis.json), [audit](audit.md), [CLI checks](artifacts/cli-checks/results.json),
[budget](artifacts/output-budget.json), [handoff](handoff.md), [coordination](coordination.md).
Reproduce metrics without model execution:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python reports/work/FOCUS-TRANSFER-10/analyze.py --output reports/work/FOCUS-TRANSFER-10/artifacts/analysis-replay.json
```

The writer refuses overwrites; choose a new output for another replay.
