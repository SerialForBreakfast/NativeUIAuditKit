# Faster evidence-driven iteration

Established 2026-09-22 from the maintainer's workflow review. This refines verification
cadence, not acceptance gates or execution authority. Tasks.md remains the only queue.

## Diagnosis from observed work

| Observed friction | Evidence | Change |
|---|---|---|
| Readiness checked a different writer from the failing capture path | [Latest local smoke](../reports/work/SIM-DATA-01-02/smoke-20260922-0140/handoff.md): storageReady, then screenshot EPERM | Producer repair evidence must exercise the actual adapter/writer; NUA then tests the complete export/intake boundary once |
| Repeated discoveries at serial handoffs | Same smoke: native focus repaired, screenshot still failed | Ask for one small completed artifact and stage-level results, not only a new build or green unit tests |
| Conflicting Office-first and simulator-first dispatch guidance | Tasks/catalog headers versus accepted ADR-0008 | Keep simulator-first sequencing explicit; Office is later transfer validation |
| Small diversity probes missed finite visual space | [P0-C r4/r5 diagnoses](../reports/work/P0-C/resumption-20260922.md) | Check affected family's requested capacity; retain successful qualified output instead of rendering it twice |
| Different seeds and sidecar values concealed identical pixels | BP-61 and P0-C status-axis probe | Verify rendered effects, decoded duplicates and metadata together |
| Old blocked summaries outlive producer progress | SMB producer NUIAK-SCREENSHOT-WRITER reports a real PNG at 04:55Z, while NUA summary still requests repair | Separate producer-reported repair from locally verified integration; reconcile at handoff, not via repeated unchanged polling |

The records establish these failure modes, not a measured percentage of time lost to
testing. Actual defects were caught. Removing validation would conceal them; moving
the right checks earlier and reusing unchanged evidence is the optimization.

## Verification cadence

| Change / boundary | Required feedback |
|---|---|
| Prose-only edit | Content, links and diff review; no package build or simulator |
| Local code iteration | Smallest behavioral regression covering the changed mechanism and its failure path |
| Schema, crop geometry, split rules, writer or shared interface | Affected callers plus realistic positive/negative contract tests before scale |
| Integrated code handoff | Focused checks plus required offline swift build/test once on the final relevant source state |
| Capture repair | Exact authorized target and fresh ownership/endpoint checks; one changed-candidate smoke through capture/export/intake and cleanup |
| Corpus freeze / model qualification | Full membership, integrity, leakage, label-source and applicable model gates; no sampling substitution |

Do not run the full package suite after every helper, prose change or status update.
Do not omit it at a code handoff. Record command, result, duration, source/artifact
identity and relevant inputs. Reuse evidence only when the behavior's source,
dependencies, configuration and inputs remain unchanged; explain the dependency
scope. Changed shared schema/crop/runtime boundaries invalidate their dependents.
Runtime identity/ownership/health is ephemeral and must be checked fresh for operations.
No cache is trusted merely because a filename or source revision matches.

For large generation, audit early real outputs, check new batches incrementally,
retain verified complete prefixes with lineage, then perform one full final audit.
Use requested-scale validation for demonstrated finite-variation risks, not a second
full-corpus rehearsal for every edit. Changed-family qualification output can become
corpus membership if it meets the same frozen contract. Preservation copies remain
necessary before destructive app reset; efficiency is not permission to skip recovery.

## Producer–consumer repair loop

1. NUA sends one reproducible failure with request/job IDs, exact artifact/toolchain
   context, expected result and all already-observed downstream gaps. Keep one primary
   blocker, but do not hide known failures to force another handoff.
2. TTR owns its repair under its own assignment. Request a receipt for the actual
   failed boundary and, where authorized, a minimal complete bundle/export with hashes,
   counts and postflight health. Use existing jobs/export/diagnostics interfaces.
   A host-local screenshot is valuable partial evidence, not completed NUA integration.
3. NUA checks candidate identity and the relevant delta, then performs the authorized
   end-to-end smoke/intake. Do not redo signing/discovery repairs without new evidence.
   A failed smoke returns typed stage/cause and retained diagnostics; no unchanged retry.
4. Pass unlocks the already-assigned next stage. New capture scale or training still
   requires its explicit authority; ask for a complete bounded tranche at dispatch,
   not another confirmation between steps already included in it.

Maintain one concise current result, next owner and exact resume condition in shared
status. Readback is publication, acknowledgment is receipt, an artifact is evidence.
Expired status is historical—not proof a repair is absent or a device is available.
Independent local work continues; do not invent extra offline helpers when existing
software is accepted and the only remaining need is a genuine artifact.

## Synthetic visual coverage goal

Long-term goal: systematically cover every controllable visible state relevant to
supported screens. Track each axis as implemented-and-visually-verified, planned,
unsupported, or intentionally fixed, with rationale. Do not claim exhaustive coverage.

Start with controls/focus/geometry and observed model failures; then themes, contrast,
enabled/selected/loading/error states, text lengths/localization, scrolling/clipping,
density/type size, and chrome (clock, cellular/Wi-Fi, charge/charging). Record actual
rendered effects, label implications and supported renderer/runtime—not metadata alone.
Battery health is not an ordinary status-bar appearance label.

Use deterministic independent schedules to avoid accidental clock/battery/theme
correlations; use targeted boundary and pairwise combinations rather than the entire
Cartesian product. Retain physically plausible combinations and explicitly labeled
intentional defects. Group related variants in one split; protect final evaluation
groups from failure-driven tuning. Report coverage gaps separately from milestone
requirements: exhaustive visual variation does not block today's valid baseline.

## Check whether the loop improves

For the next three actual repair/capture iterations, record timestamps and time spent
in focused tests, full tests, capture/intake, peer wait and approval wait; record
unchanged checks repeated, handoffs to first eligible bundle, and accepted unique
pairs per capture minute. Add these fields to existing handoffs, not a new dashboard.
Compare observed timings before setting budgets. No automatic monitor is installed.
