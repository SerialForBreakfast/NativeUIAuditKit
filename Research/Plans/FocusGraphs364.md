# FOCUS364–365: matched scenes and evidence-guided follow-up

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Status: approved implementation, 2026-10-13.
This plan implements the first bounded graph under [ADR-0027](../ADR-0027-Evidence-Guided-Experiment-Graphs.md).
It uses the existing queue and background runner. It does not create another scheduler.

## Questions and decisions

| Priority | Test | What stays fixed? | What does the result decide? |
| --- | --- | --- | --- |
| P0 | Compare focus movement with dimming and notification changes. | Artwork, layout, target geometry, model weights, crops, and thresholds. | Does a model mistake appearance changes for focus changes? |
| P0 | Check the visible cue in missed movements. | Retained generated images and focus identity. | Should the next experiment improve recognition or handle covered controls? |
| P1 | Repeat the matched comparison on Settings, a dialog, and corner controls. | The same artwork families, renderer, models, and decision rules. | Do failures extend beyond the earlier 4 layouts? |
| P0, blocked | Generate native OS HCF examples. | Existing HCF361 study, approved target, and restoration checks. | Does the actual OS effect support HCF training? |

The last row remains the existing HCF task. Do not create a replacement study or bypass its recovery guard.
research-host-TTR remains at revision `6c85728c605102a9afd38794b08acdd5045b5be4` after an authorized clean pull.
The headless source now defines 7 layouts. The earlier retained recipe supplies only 4 layouts.
FOCUS365 explicitly adds the 3 new layouts after source inspection.

## Graph and execution

The renderer build produces 1 pinned binary.
Each producer makes matched images and a qualification report.
Each comparison requires both verified files and a supported qualification result.
A final job combines counts, case references, and the next decision.
The native evidence review remains separate. Its inconclusive result does not block authored comparisons.

Specifications remain immutable. Graph revisions reference exact specifications and earlier evidence.
The queue accepts only typed condition outcomes: supported or contradicted.
An inconclusive outcome blocks the dependent branch without converting the completed producer into a failed job.
Conditions cannot contain executable expressions or grant new authority.
The queue checks condition evidence again before execution.

The experiment contract uses these limits:

- Run at most 5 jobs per dispatch cycle.
- Permit 800 s and 100 MB for each diagnostic job.
- Permit 1 attempt. Record a successor specification for a corrected producer.
- Use 2 CPU threads for model scoring.
- Do not train, change thresholds, or promote models in this batch.
- Preserve the original crop path and all model files.
- Reuse completed builds and generated inputs instead of repeating successful work.

The initial producer combines 2 artwork families. Shelf and hero outputs exceed their limits.
Revision 2 splits those producers into 1 family per part.
It reuses the completed grid and navigation results. Failed attempts remain available.
Revision 3 adds a visibility check from the resulting failure evidence. It generates no more images.

The canonical graph files are:

- `Research/ResearchSpecs/FOCUS364/graph.json`: initial revision and preserved failed work.
- `Research/ResearchSpecs/FOCUS364-r2/graph-r3.json`: repaired graph and visibility follow-up.
- `Research/ResearchSpecs/FOCUS365/graph.json`: the 3 new layouts and reused renderer build.

## Data and comparisons

Use reviewed artwork from 2 existing training families.
Keep derivatives and reversed pairs in the same family.
These are development diagnostics, not new independent evaluation data.
The reports name 2 artwork groups. They do not establish 2 independent statistical trials.

For each layout and family, render 2 focus targets under 4 conditions:

- Original appearance.
- A dark scrim with alpha 0.35.
- A notification banner.
- A small notification toast.

Test movement in both directions, identical repeats, and appearance changes with fixed focus.
Each family supplies 28 pairs per layout.
FOCUS364 supplies 224 pairs across 4 layouts. FOCUS365 adds 168 pairs across 3 layouts.
The same generated inputs support FOCUS329, gamma348, and movement349 comparisons.
Use the existing thresholds of 0.15 and 0.85. Count abstentions separately.

Authored focus identity describes scene state. It does not prove that pixels visibly reveal that state.
The banner covers both navigation controls in 4 movement cases.
Keep those cases in an interruption test. Do not use them as ordinary visible-focus training failures.
The visibility check reports rectangle coverage and remaining local pixel differences.
Rectangle coverage does not prove complete optical occlusion because the banner uses transparency.

These tests do not measure native HCF, animation timing, real-app generalization, or all visual themes.
Future native experiments require actual OS settings and observed native labels.

## Persisted evidence and acceptance

Each producer retains original images, annotations, exact hashes, generation time, and its source domain.
Each scorer retains case IDs, labels, probabilities, model hashes, timings, counts, and comparison results.
The final report retains gained and lost cases relative to the original model.
No report accepts a model without the separate native and retained regression gates.

Acceptance requires these outcomes:

- A changed input or condition report blocks execution.
- A contradicted condition blocks only its consumer.
- An independent job continues through the actual queue.
- Each generated variant changes pixels without changing target geometry.
- The background runner completes the producer-to-comparison path.
- The dashboard explains the test and its decision in plain language.
- A useful negative result creates a specific next test, not another unrestricted sweep.

## Next decisions

First, review the 3 new layout comparisons.
Next, separate weak visible cues from cues covered by overlays.
If appearance training helps matched visible cases, propose targeted examples with movement-preservation controls.
If controls are covered, test interruption handling and abstention instead of forcing a confident focus answer.
When TTR repairs native observation checks, qualify recovery before resuming the existing HCF capture graph.

Keep bulk expansion on the verified external volume.
These bounded diagnostic parts remain active path-bound queue inputs. Do not move them until consumer migration passes.
Do not repeat these completed comparisons merely to occupy the queue.
