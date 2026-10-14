# FOCUS327: a useful TTR feedback cycle

## What Maximum-mini-NUIAK can verify

The available Maximum-mini-TTR checkout remains at `d06a64bd8840c5ada053fd90841c56cef2a9dd58`.
The earlier [source review](TTR318Review.md) covers its tracking, catalog polling, and archive reuse.
This checkout does not establish the newer chat updates reported by the maintainer.
The coordinator returns no unread messages. The visible history through cursor 160 contains NUIAK messages, not new TTR replies.
Request `nuiak-focus327-start-and-routing-01` asks BigDog-Coordinator to identify and forward those replies.
The server stores that request at cursor 161. It reports `provider_delivered: false`.
The completed result is stored at cursor 162 with the same delivery limit.
The SMB fallback publishes `nuiak/responses/nuiak-focus327-result-01.json` and passes size, hash, and readback checks.
Peer acknowledgment remains unconfirmed.

The SMB status dates from October 8. Its EVS offer already has a verified receiver receipt and completed shared-copy cleanup.
Do not download that completed transfer again. Do not treat the old status as evidence of current worker availability.

## Use existing capabilities first

| Capability | Useful contribution | Required limit |
| --- | --- | --- |
| Headless authored rendering | Draw known layouts without launching a Simulator | The available script uses fixed positions and effects; confirm new parameters before use |
| Native Fixture capture | Measure actual effects and verify whether synthetic training helps | Use observed focus and capture checks, not requested focus alone |
| Retained sequence replay | Compare old and new models on identical frames | Preserve group membership, frame order, model hashes, and preprocessing |
| Optional model loading | Test a qualified candidate without changing the bundled model | Discovery does not approve a model or give navigation authority |
| Verified archive reuse | Avoid repeated transfer and image generation | Verify exact bytes and keep originals until receipt checks pass |

## Proposed complete cycle

1. Maximum-mini-NUIAK reports a reproducible error category with exact cases, scores, decisions, and thresholds.
2. TTR checks whether its existing renderer can vary the suspected cause independently.
3. Maximum-mini-NUIAK freezes training groups and keeps different native groups for evaluation.
4. TTR generates a bounded batch with unchanged comparison cases and explicit negative examples.
5. Maximum-mini-NUIAK checks labels and images, then trains 1 matched candidate.
6. BigDog-NUIAK can score the same fixed package when a complete approved assignment exists.
7. Maximum-mini-NUIAK returns gained cases, lost cases, false changes, abstentions, and the next measured gap.

Reuse existing manifests, trainers, reports, and transfers. Do not add another service or duplicate benchmark.
Use compact metadata for routine cases. Retain image access for failures and a small review sample of claimed successes.
Model agreement prioritizes review. It does not prove correct labels.

## The current evaluation gap

The retained native set contains 548 training pairs, 40 development pairs, and 52 reserved pairs.
All 40 development pairs have unchanged focus. They span 10 groups.
The 52 reserved pairs include 34 focus changes and 18 unchanged pairs. They span only 2 groups.
Those reserved examples have already informed earlier investigations. They are not untouched final evidence.
The separate tiny-control check supplies only 4 forward focus changes and their reversed versions.
Reversing a pair does not create independent evidence.

Prioritize verified focus changes across different native layouts, control types, positions, and effects.
Pair those cases with unchanged-focus content changes and animations. Report each condition separately.
TTR's observed focus records can fill this gap. High model scores and authored geometry cannot replace those records.
Keep existing groups unchanged. Assign new groups before training or review changes their role.

## How this avoids another volume-only experiment

FOCUS327 keeps the images fixed and tests whether detail filters can learn the required distinction.
If training fit improves but native results fail, target the difference between authored and native effects.
If training fit remains poor, inspect the selected regions and representation before requesting more images.
If native results improve but previous successes regress, identify the conflicting groups before another fit.
Any proposed TTR change needs human approval. Existing approved features can support already approved work without another infrastructure project.
