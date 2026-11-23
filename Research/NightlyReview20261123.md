# Nightly review · November 23, 2026

Window November 17 07:48:34.487 UTC to November 23 20:06:42.525 UTC. Starts at the previous successful report cutoff. Four overlapping runner attempts are recorded by ID. All results are provisional. [Ledger](../reports/work/NIGHTLY-20261123/window.json)

## What improved

Adding a focused detector class improves correct Kanopy focus picks from 1/18 with D1 plus shipped FocusRing to 10/18 at seed 371 and 9/18 at seed 372 on one development recording, with five and seven wrong picks respectively and limited independent coverage. Both seeds abstain on all three explicit no-focus screens across Kanopy and AX-dev. Seed 372 passed final authorization, its export hashes verified, and the existing scorer produced all three reports during this review. [Paired focus results](../reports/work/TRAIN666/h3-arm-f/README.md)

Full-scale D1 improves localization recall from 404/460 to 458/460 and 454/460 on dev42; Kanopy and AX-dev also improve in the recorded matched comparison. Seed 371 remains diagnostic after a source-authorization failure. H1 has no release-qualified result. [H1](../reports/work/TRAIN666/h1-scoring/README.md)

## What we learned

TTR acknowledged both Settings and Pavilion readbacks in message 2302. No repeat trial is required. Six Settings states and both corruption checks remain calibration evidence. TTR also reports new QA lifecycle/map fixes and requests owner coordination for local QA and second-Mac release preparation; these are peer reports awaiting their own qualified readback. [Messages](../reports/work/NIGHTLY-20261123/messages.json)

## What regressed

Focus-class seeds score 20/36 and 24/36 on dev42 versus 29/36 and 28/36 for the existing comparative selector. AX-dev is 21/34 and 24/34 versus 29/34 and 26/34 with the development-tuned nested filter. Selector refitting failed to improve consistently. The H1 report retains superseded NewsTV no-focus counts; use label v3, where six states are unknown. No iOS improvement measured. [Selector](../reports/work/TRAIN666/h3-arm-s/README.md)

## What runs next and what each test decides

Registered B405-298 through the catalog as preparation under H3. Reconcile fresh reviewed real-app references, native no-focus evidence and independent layout groups before qualification. Compare both frozen focus-class seeds with S0/S0n at existing thresholds to decide whether Kanopy gains transfer and how many correct picks are lost elsewhere. Seed-372 decode diagnostic remains pending. No jobs released, admitted or continued. [Catalog](Experiments/backlog405.json)

## Queue health

0 ready, 0 running, 351 dependency-blocked, 13 otherwise blocked, 8 awaiting approval, 128 exhausted, 29 unselected. Ready duration zero; dependent duration unestimated. Runner live and waiting. Window execution includes 3 complete attempts and 1 failed: 25 h 14 min completed, 1 h 59 min failed, 129 h 5 min idle, with non-overlapping intervals. All four belong to TRAIN666. Local QA work is separately recorded and outside this runner occupancy calculation. [Queue](../reports/work/NIGHTLY-20261123/queue.json)

## Blockers and approvals

No set passes the scorer's independent-layout requirements. Only three explicit no-focus screens support this comparison. No new model acceptance or fit approval. QA preparation requests do not expand model-training authority.

## Priority changes and reasons

Prioritize fresh H3 qualification and benchmark balance over more crop tuning. H2 stays pending the H1 decision. iOS, HCF and Watch Later fits stay paused. Updated completed H3 execution/scoring tasks and TTR acknowledgement. No new off-plan work admitted.
