# HCF374 — Repeated images and useful capture diversity

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Current evidence

research-host-NUIAK checks the first 5 completed HCF371 admission reports.
They contain 2,000 frames and 2,000 distinct decoded pixel identities.
This check uses verified admission hashes and image dimensions. It does not decode the original images again.
These frames represent 250 scene groups, with 4 focus positions and 2 profiles per scene.
They are not 2,000 independent scenes.

Similar-looking screens are expected within matched comparisons. This does not prove that the remaining corpus has sufficient diversity.
The crop trainer samples HCF crops only. Repeated unfocused crops could increase their influence even when full frames differ.
The detector already uses same-volume hard links for its input images. Those links do not create another image payload.

## Decisions

- Keep each capture event, time, input, focus observation, profile receipt, and body geometry.
- Treat identical bytes, identical decoded pixels, and similar content as different measurements.
- Use decoded pixel identity with dimensions and a declared color conversion.
- Use Vision similarity to find review candidates. Do not use it as focus truth or a deletion rule.
- Preserve tiny focus changes, Standard/HCF pairs, temporal repeats, and intentional identical neighbors.
- Report distinct payloads, scene groups, capture events, and training samples separately.
- Reject conflicting labels and cross-role exact overlap before accepting model evidence.
- Do not move inspected examples into a final audit.

[Apple's feature-print example](https://developer.apple.com/documentation/vision/analyzing-image-similarity-with-feature-print) supplies the similarity mechanism.
Our existing Swift probe records the Vision revision, crop mode, OS, hashes, and distances.
No universal threshold follows from that API. The queued test reports fixed thresholds without choosing one.

## Queued tests

All 4 jobs use the existing background runner. Each permits 800 s and 100 MB.
The active capture, original study specifications, and training membership remain unchanged.

| Test | What will it decide? | Inputs |
| --- | --- | --- |
| First 2,000 frames | Are repeated pixels already present? Do labels conflict? | 5 completed admission reports |
| Complete corpus | Do exact pixels cross roles or repeat across scene groups? | Completed HCF371 catalog |
| Vision similarity | Can a similarity filter accidentally remove real focus movement or HCF differences? | 3 development scenes, 24 frames, 50 comparisons |
| Original crops | Do repeated HCF crops overweight training or leak into evaluation? | Completed original production crops |

The Vision controls include identical frames, focus movements, profile changes, and different scenes.
The crop report checks decoded pixels, labels, roles, and multiplicity. It also reports HCF-only membership.
These are diagnostics, not new dependency gates on immutable training jobs.
Any conflict prevents acceptance of affected model evidence. A corrected experiment requires a new specification.

## Required TTR behavior

research-host-TTR and peer-host-TTR should qualify these behaviors against their current fix.
This request does not ask either worker to replace the running app.

1. Identify each capture event separately from its image payload.
2. Record file hashes and canonical pixel hashes with dimensions and color handling.
3. Reuse a verified payload for exact duplicates where the storage contract permits it.
4. Preserve every event record and its observed focus, geometry, profile, and timestamps.
5. Record the requested recipe, seed, applied values, and observed scene identity.
6. Report unchanged requested factors instead of counting them as new coverage.
7. Use Vision candidates with native focus and local pixel evidence before suppressing redundant collection.
8. Preserve settling repeats and paired experiment endpoints even when images match.
9. Detect repeated navigation states with observed identity and route context. Do not reuse stale focus from a similarity match.
10. Bound repeated no-progress navigation. Return an explicit partial result instead of silently completing coverage.
11. Report bytes written, payload reuse, duplicate counts, scene counts, and exclusion reasons per shard.
12. Support resume without recapture when verified events already satisfy the frozen plan.

Test the fix with exact repeats, re-encoded images, small focus moves, profile differences, animation, and repeated artwork.
Check conflicting labels and interrupted payload publication. A missing payload reference fails validation.
Keep failed evidence. Remove only verified redundant copies under the existing retention policy.

## Training response

First measure repetition within actual loader membership, not only the exported corpus.
If repeated crops dominate, compare group-balanced or duplicate-weighted sampling against the unchanged control at equal updates.
Do not silently remove intentional negatives or change class balance.
Measure target gains and previous successes lost. Keep development and final-audit groups unchanged.

Storage reuse and training weighting are separate changes. Saving bytes alone does not correct repeated influence during training.
No images are deleted or relabeled in this tranche. No model improvement is claimed.

## Verification and handoff

The background runner completes the first audit. It confirms 0 exact duplicate groups among the first 2,000 admitted frames.
The other 3 audits remain queued behind capture or their required producer outputs.
The seventh capture part runs at the final check. The app and runner remain unchanged.

The focused suite passes 89 tests, including 7 new duplicate tests.
The first test command names a missing test module. The corrected command passes the full selected suite.
The Xcode build fails on resource-fork signing metadata. No signing settings or files are changed to bypass it.
The native Swift build succeeds. All 173 Swift Testing tests and 14 XCTest checks pass.
Logs remain in `.build/hcf374-swift-tests.log` and `.build/hcf374-swift-native-tests.log`.

The coordinator stores the compact corrected status envelope at cursor 559.
Earlier envelopes enter review because their formats are invalid. The correction explicitly supersedes those reviews.
The final status summary contains 1,463 UTF-8 bytes, within the coordinator's 2,000-byte limit.
Forwarding and TTR acceptance remain separate, unconfirmed states.
The request also repeats the exact FOCUS372 receipt location for sender-owned cleanup.

Next, use the crop and Vision findings to select a matched sampling correction, if needed.
Qualify TTR's payload reuse against the preserved event records after capture releases the target.
The tranche takes about 20 min against the initial 25–40 min estimate. Background capture and audits continue separately.
