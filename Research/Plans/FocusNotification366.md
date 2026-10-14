# FOCUS366 — learn notification changes without losing movement

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. The background runner executes this graph.

## Question

Can fresh notification examples reduce false changes while preserving dimmed-corner movement and previous successes?

The 392 inspected pairs stay in development. They do not enter training or the preservation loss.
The exact corner case is `artwork-s1-focus_maze-005`.

## Frozen comparison

- Generate 252 pairs across 3 authored layouts and 3 reviewed artwork families.
- Use artwork families 2, 3, and 4. Earlier training already uses these families.
- Change rendered text for Settings and dialogs. Artwork changes alone do not change those screens.
- Use Settings rows 1 and 4. Keep corner movements in the maze.
- Include dimming, banners, toast messages, movements, and identical frames.
- Reject exact RGB matches with development images before training.
- Reject training controls covered by notifications.
- Keep authored labels separate from native observations. Do not claim new independent families or native HCF evidence.

The renderer is a NUIAK copy of the pinned TTR source. Fixed text changes leave geometry and focus effects unchanged.
The TTR checkout stays unchanged. Native capture remains blocked by the recorded HCF restoration check.

## Matched training

Both runs start from FOCUS329. Both use 10 epochs, seed 42, and 2 CPU threads.
Each run has 1800 s and 2 GiB limits. Each diagnostic has 800 s and 100 MB limits.

Keep all 1820 original views and their original detail crops unchanged.
Keep all 1200 retained auxiliary views. Add 252 extra slots to both runs.
The correction uses fresh pairs. The control fills those slots with label-matched retained pairs.
Both runs use the same label schedule and loss settings. Every auxiliary row appears during training.
Only detail filters and correction layers change. Whole-frame weights stay fixed.
Preservation loss uses training examples only. It does not guarantee preserved decisions; comparisons enforce that requirement.

## Graph and decision

Compile 3 renderers → generate 9 shards → admit fresh data → train 2 runs → compare → decide.

Each run receives 24 retained comparisons and 4 comparisons covering the 392 inspected pairs.
Reports retain probabilities, labels, input hashes, counts, timings, and case identifiers.
The final decision requires all 56 comparisons.
An additional report preserves earlier correct decisions from gamma348 and movement349 on the 392 development pairs.
The graph has 81 jobs. These jobs form 1 matched study, not 81 separate model hypotheses.

A correction passes this development check only when:

- It has fewer false changes than the matched control on the 392 pairs.
- It has more correct decisions than the matched control on those pairs.
- It preserves the exact dimmed-corner movement at the unchanged 0.85 threshold.
- It loses no FOCUS329 successes across the full retained suite.

Thresholds remain 0.15 and 0.85. Missing results block the decision.
No automatic promotion occurs. Native transfer remains a separate qualification requirement.
Repeated and related cases do not count as independent evidence.

## Execution and storage

Use the existing queue and its approved-additions mechanism. Do not restart stopped work or retry failed runs automatically.
Keep bounded active outputs in their existing queue paths. Preserve original captures and shipped models.
Check free space before dispatch. Move inactive bulk outputs only through verified storage procedures.
The maximum reserved graph output is reported in `Research/ResearchSpecs/FOCUS366/graph-r2.json`.

## Next decision

If the correction passes, measure native transfer before proposing a replacement.
If false changes improve but movement declines, inspect paired margins and the changed detail features.
If both runs behave alike, test whether the new examples reach the selected detail regions before expanding volume.
