# TTR updates: useful features and limits

Maximum-mini-NUIAK reviews Maximum-mini-TTR source `d06a64bd` after `538a1119`.
This is source review, not live qualification. No TTR script runs during this review.
The maintainer requires human approval before worker suggestions become new assignments.

## Useful changes

| Feature | Benefit | Current limit |
| --- | --- | --- |
| Temporal focus tracking | Records model boxes and scores across several target states | Does not independently prove correct focus or settled rendering |
| Saved archive reuse | Avoids another download when exact archive bytes remain available | Cache success does not approve a model or replace installer checks |
| Catalog polling | Finds offers and reports catalog checks | Self-computed hashes do not establish an approved publisher or production status |

## Temporal tracking

`Scripts/track-temporal-focus.swift` uses a fixed Simulator UUID and localhost port 8080.
It sets target focus directly through HTTP. The recorded directional commands do not represent executed D-pad navigation.
The script waits 0.6 s after setting focus. It does not check observed settled state across the capture interval.
HTTP callbacks discard errors and status codes. Semaphore waits have no explicit operation timeout.
The script selects the highest-scoring model focus box and records its center.
It does not compare that selected box against an independently observed target box.
The final success text claims zero focus loss. Model predictions alone cannot verify that claim.

Proposed task TTR318-A: qualify a bounded sequence recorder, not model-driven navigation.
Inputs: exact target, endpoint ownership, model hashes, recipe hash, and a fixed sequence.
Record actual actions, observed focus IDs, source images, timestamps, model outputs, and independent result checks.
Fail on HTTP errors, stale frames, target mismatch, or incomplete hops. Keep unknown states explicit.
Acceptance: one complete sequence plus mismatch and timeout tests. No prediction becomes a training label.
Owner proposal: Sillycon-TTR owns producer changes; Maximum-mini-NUIAK owns retained replay and evaluation.
Status: awaiting human approval. No device operation starts from this proposal.

## Catalog polling

`Scripts/poll-model-catalog.rb` computes each discovered catalog's hash and passes it as the trusted hash.
This verifies self-consistency, not agreement with a separately approved hash.
The receipt sets `approved_production_catalog_available` when any catalog check succeeds.
That field overstates approval. Discovery, integrity, compatibility, license review, and production approval remain separate.
The scan reads only the 3 newest response files. Unrelated responses can hide a relevant unresolved model response.
The script catches file errors, but it does not establish a bounded, immutable handoff transaction.

Proposed task TTR318-B: separate discovery from approval and test bounded scans.
Inputs: a human-approved catalog hash, named offers, explicit scan directory, and one-shot mode.
Test valid, changed, oversized, stale, unapproved, and unrelated-newer files. Reject links outside the allowed directory.
Acceptance: unapproved catalogs never receive production approval in a receipt. Discovery never activates a model.
Owner proposal: Sillycon-TTR. Maximum-mini-NUIAK supplies approved catalog identities through the existing release workflow.
Status: awaiting human approval. Do not start a persistent poller as part of FOCUS313.

## Archive reuse

`OptionalModelPipeline.swift` adds a cache keyed by SHA-256.
The source checks file type, length, hash, links, cancellation, and exclusive destinations.
It preserves installer checks and does not automatically select the model.
The TTR report records offline synthetic tests. It explicitly excludes actual installation and macOS 14 execution qualification.
Keep those limits. Reuse this capability during an already approved installation test when that test reaches this stage.
No separate cache implementation is needed in NUIAK.

## Priority and current work

Finish approved FOCUS313 first. Its retained inputs do not need these TTR features.
Propose TTR318-B before trusting poller approval fields. Propose TTR318-A before treating trajectories as labeled training evidence.
Keep headless effect requests under FOCUS314. This commit does not change the reviewed headless renderer.
Do not start extra training from these feature announcements.
