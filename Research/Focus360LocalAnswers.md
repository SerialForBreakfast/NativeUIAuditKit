# FOCUS360 — answers from local evidence

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Review: 2026-10-12. Owner: research-host-NUIAK.

## Decision

Do not wait for peers to inspect inputs already present here.
The first useful comparison is a read-only training-conflict diagnosis.
Do not spend a batch on output-score blending for the measured native movement failures.
Keep weight interpolation separate. Its effect cannot be inferred from output interpolation.

## Local answers

| Earlier question | Local answer | Next action |
| --- | --- | --- |
| Which checkpoints share a starting point? | FOCUS329 and both FOCUS358 candidates are local. Both candidates start from the same pinned FOCUS329 checkpoint. | Prepare the gradient diagnostic locally. worker-host-NUIAK residency does not block it. |
| Can we blend compatible checkpoints? | All 3 have 34 matching tensor keys, shapes, and types. All use `edge329-v1` and 2 windows. Only 10 detail/correction tensors change. | Weight blending is structurally feasible. Do not assume it improves decisions. |
| Would output blending recover native movements? | No, on this retained set. All endpoint probabilities are below 0.003, far below the 0.85 change threshold. | Remove this output-blend run from the immediate batch. Preserve the computed result. |
| Do we already have matched native cases? | GENERATION354 retains 50 frames across 5 factors. It supplies movement, content-change, and repeat pairs. | Reuse these cases. Do not ask peers to generate these same conditions again. |
| Do these captures provide the full proposed artwork experiment? | No. Content changes use recipe reloads. Intermediate focus can change. The records do not prove continuous fixed focus during reload. | Use endpoint diagnostics now. Prepare a stricter mutation-based producer locally for the remaining comparison. |
| Is the HCF counterpart question answerable locally? | The intake has 3 metadata records: Standard, HCF, and an unmatched HCF artwork case. The exact artwork recipe is also local. | Prepare the counterpart from that recipe. Preserve the existing remote request, but do not block local preparation on its reply. |
| Can the retained frames measure settling? | They contain screenshot intervals and observed endpoints. Early frames lack verified focus intervals. Sparse samples cannot establish exact settling time. | Use endpoint labels only. Prepare a timed producer instead of inventing temporal labels. |
| Does local TTR support controlled mutations? | Source includes `collect-structural-transitions.rb`, native mutation receipts, ordered capture brackets, and measured scroll offsets. | Adapt the existing producer after target and source checks. Do not build another capture framework. |
| Can we inspect the chat contract locally? | LittleDog's local client defines the structured status envelope. It does not establish the remote recipient map for feedback forwarding. | Stop asking for the whole schema. Keep only the exact forwarding-map question open. |

## Current model results

Both FOCUS358 comparisons are complete, with 24 comparisons per arm.

| Arm | Lost previous successes at 10 epochs | Lost previous successes at 30 epochs | New native movement successes |
| --- | ---: | ---: | ---: |
| Control | 4 | 4 | 0 |
| Position | 20 | 8 | 0 |

Longer position training reduces recorded regressions by 12. Neither arm passes the replacement rule.
These counts can include repeated cases. They do not describe independent real-app accuracy.

## Output-blend screen

The analysis reuses saved probabilities. It performs no inference or training.
It compares FOCUS329 with each FOCUS358 candidate at weights 0.25, 0.5, and 0.75.
Each arm covers 10 native movement rows, 8 distinct image pairs, and 1 related group.

| Arm | Largest endpoint probability | Correct movements at each blend weight |
| --- | ---: | ---: |
| Control | 0.0018608883 | 0 / 10 |
| Position | 0.0025232863 | 0 / 10 |

Every convex probability blend stays between its endpoint scores.
Therefore, no blend weight between 0 and 1 can cross the unchanged 0.85 threshold on these rows.
Changing that threshold would be a different experiment. This review does not change it.

## Verified inputs

| Model | SHA256 |
| --- | --- |
| FOCUS329 | `b8c1314e1edf622bed86cc763d200b6ba18bcddb5b1ae5229108074e55ef6964` |
| FOCUS358 control | `33fed128474ce9b94fa7fc71eb011b33930643049153677e8c4705dc1ea2588b` |
| FOCUS358 position | `f023454388daf842f26d5eef262839d17cd90d4526f81f4ca46be95d7750eeaf` |

The local audit verifies completed output hashes, checkpoint hashes, tensor structure, and all 50 native capture files.
It verifies endpoint focus relationships and screenshot brackets. It does not establish capture-era source matching or real-app transfer.

HCF artwork recipe: `6f08ca8bb215fe01eaa353ecada783e0f9801866bd7a12d0695318acb9c4e99d`.
Path: `reports/work/HCF357/extracted/hcf_card_unmatched/recipe-source-6f08ca8bb215fe01eaa353ecada783e0f9801866bd7a12d0695318acb9c4e99d.json`.
The existing counterpart capture belongs to peer-host-TTR's target. Do not copy that target identity into research-host-TTR jobs.
A local recreation needs its own qualified target, profile observations, and explicit comparison limits.

Inspected research-host-TTR revision: `d06a64bd`, “Temporal Focus Tracking & Catalog Poller”.
The source review finds existing mutation and capture tools. It does not claim the running app contains every inspected change.

## Reproduction

Use `reports/work/FOCUS360/local-review.py` with a new output filename in that same directory.
The script refuses an existing output. It loads local weights with `weights_only=True` on CPU.
The preserved result is `reports/work/FOCUS360/local-review.json`.
Its evidence list records exact report paths and hashes.

No queue specifications, runner settings, training views, or model thresholds change.
The diagnostic passes without new dependencies, downloads, or Swift changes.

## Revised next batch

1. Prepare the gradient-conflict diagnostic from the local retained checkpoint and training membership.
2. Extend the existing producer for matched content/focus changes that avoid recipe reload ambiguity.
3. Prepare the Standard artwork counterpart from the retained recipe, subject to local target qualification.
4. Use the resulting evidence to choose one correction with complete previous-success comparisons.

Ask peers only for remote-only source, runtime, resource, or routing facts that these local checks cannot establish.

## TTR reply received after the local audit

TTR's v1 and v2 contract archives pass size, hash, path, and member checks.
V1 contains 20 members. V2 contains 21 members. No incoming source executes.
TTR confirms the same limitations for joined endpoints, early frames, and unmatched HCF artwork.
Its compact endpoint replaces `recipe` with `recipe_reference`; our consumer still requires the full recipe.
Its current geometry key is `rendered_body_geometry`. It declares no `body_geometry` alias.
Keep the existing full-scene path until an explicit compact adapter passes tests.
The smallest proposed producer extension uses retained `generation354b` case `size-1`, not a new corpus.
The existing HCF357 owner keeps the remote counterpart request. Local preparation does not duplicate that capture.
