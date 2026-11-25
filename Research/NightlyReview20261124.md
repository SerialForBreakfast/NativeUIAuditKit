# Nightly review · November 24, 2026

Window: November 23 20:06:42.525–November 24 07:47:02.458 UTC, after the last successful review. Partial readiness/coordination audit; results provisional. [Window and attempt ledger](../reports/work/NIGHTLY-20261124/window.json).

## What improved

**No verified model improvement this review period.** Current TTR source was built and its running identity verified. The canonical host lane passed 79 tests; live snapshots and two saved frame hashes survived explicit history restoration after reopen. These are engineering checks, not model acceptance. [Qualification](../reports/work/TRAIN666/fresh-flow-b405-298/current-ttr-qualification.md).

## What we learned

A local prompt-scoring wrapper omitted class names. Correcting it on identical cached boxes makes S0/S0n select the human-approved Allow control across all four candidate sets. The original comparative abstention is invalid; this is a scoring correction on one layout, not a model gain. The earlier multi-app scorer supplied class names. Both direct-focus seeds still rank passive dialog text above Allow. Training has 1,211 dialog rows but no dialog no-focus rows and no horizontal pair among its 75 two-button dialogs. [Trace](../reports/work/TRAIN666/fresh-flow-b405-298/capture-fix/trace-v2/README.md).

## What regressed

No new matched model regression measured. Reference correction: use **two** uncontested Kanopy no-focus retention screens; Settings Balance is disputed and six NewsTV states are unknown. The prior nightly three-case no-focus claim cannot be carried forward unchanged. Capture failures: two NewsTV AX query timeouts, an acknowledged Select with identical before/after pixels, and WeatherStar launch timeout. No failed frame admitted. One familiar native-focused NewsTV draft remains pending review; zero newly qualified independent layouts.

## What runs next and what each test decides

B405-298 remains H3 preparation. First resolve native accessibility/activation responsiveness using retained failures; then capture populated distinct layouts and freeze human references. Paired F371/F372 and S0/S0n on identical reviewed screens decide transfer, wrong picks, abstentions and recoveries/losses. Keep no-focus separate. Horizontal dialog focus swaps and passive text are the next corpus priorities under the existing full-scale plan, not a new small fit. Catalog requirements now reflect the cleared prompt and actual capture blocker.

## Queue health

Runner health: live, waiting, no active job. Full readiness API timed out after 60 s; current ready/dependent/blocked counts and useful ready duration are **unverified**, not inferred from yesterday. Previous snapshot: 0 ready, 351 dependency-blocked, 13 otherwise blocked; historical only. No attempts overlap this window: 0 completed execution, 0 failed execution, **11 h 40 min 20 s idle** in non-overlapping runner wall time. Local capture/build activity is separate. No jobs released, admitted or continued by this review; no new off-plan attempts observed. Last fit ended November 23 08:26 UTC. [Health and limitations](../reports/work/NIGHTLY-20261124/limitations.json).

## Blockers and approvals

Thirty-layout benchmark gate remains unmet; review packet :6300 has one pending familiar layout. No new approval is needed for scoped capture diagnosis. TTR feedback was published via approved SMB fallback; recipient acknowledgment remains unverified. Coordinator replies could not be refreshed; stale share status is not current evidence. D1-371 remains diagnostic after final authorization failure; no restart budget added.

## Priority changes and reasons

Prioritize capture responsiveness and real-app breadth over more local scoring or crop tuning: they unblock H1/H3 decisions. H2 waits on H1; iOS, HCF and Watch Later stay paused. Preserve the live runner; do not restart it to repair reporting. No filler jobs or new hypothesis.
