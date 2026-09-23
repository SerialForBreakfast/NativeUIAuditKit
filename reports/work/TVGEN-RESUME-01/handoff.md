# TVGEN continuation — retained-pilot audit and resume preparation

2026-09-22 21:54 UTC. Scope: NUA-owned direct runner diagnostics and read-only
resumption planning; changed-build check and shared coordination. No new capture,
producer edits, installation, training or promotion.

## Outcomes

| Outcome | Result |
|---|---|
| Software verified | 20 direct-runner tests; offline build;14 XCTest +93 Swift Testing tests pass |
| Data eligible | No new eligibility; failed pilot remains immutable/ineligible; prior two-pair direct smoke remains development-only |
| Integration qualified | New planner audits genuine retained evidence; live pilot still blocked by unchanged producer geometry/sidecar gaps |
| Model gates | Not assessed; no inference/training in this tranche |

## Implemented and integrated

Existing `scripts/direct_tvos_capture.py` now exposes `--resume-plan FAILED_RECEIPT
--output NEW_JSON`. It shares runtime, source-plan, scene interval, PNG hash/decode,
sidecar, target membership, taxonomy, count and health validation with completed
capture validation. Planning requires a fully validated ordered prefix; an incomplete
last recipe or bad evidence rejects the plan, rather than skipping or repairing it.
It never calls the simulator, changes source bytes/state, manufactures a completed
receipt or produces an executable subset catalog. Full capture admission still
rejects failed state. Execution/merge remains a separately reviewed contract.

`resume-plan.json` was produced through the actual CLI against the retained failed
pilot. It verifies12 recipes/30 pairs and enumerates30 remaining recipes/216 pairs,
starting zero-based catalogIndex12 (media_shelf/light/seed7). Full membership remains
42 recipes/246 pairs. Source receipt SHA256:
`7e419d25e299cbdf0e7b3993729c0acf4fd71ee13e0c7896b49bb5cd76f77ff2`.
`retained-evidence-check.json` confirms source unchanged and specific failed predicate.

Settling failures now preserve the last rejection reason, including the element ID
for coordinate conflicts. The original bounded settling window remains; no retries
of mutation or weakened geometry checks. Offline replay names
`coordinate_conflict: header_shelf`, rather than implying missing native focus.

## Verification

- `python -m unittest discover -s scripts -p test_direct_tvos_capture.py`: exit0,
  20 tests in1.072s. Includes actual plan CLI, deterministic output, output collision,
  source immutability, corruption, bad sidecars, symlinks, wrong membership/health/count,
  partial recipe, and exact timeout predicate. Existing crop/baseline entrypoint tests
  remain test-only evidence, not new genuine inference.
- Actual read-only `--resume-plan` against retained pilot: exit0,30 verified/216 remaining.
- Approved offline `swift build`: exit0,2.16s; `swift test`: exit0,14 XCTest and93 Swift
  Testing tests. Project-local tmp/cache/config/security paths; automatic resolution
  disabled. Logs adjacent. No final warnings/errors. Scoped diff check passes.
- Prior dirty files and iOS worker artifacts preserved; own changes confined to
  runner/tests, canonical plan, queue, lesson and handoff/status.

## Concrete live blockers

Fresh passive check: running Fixture dylib still
`9bd3859b9f71e6255bba0a3d64cfdd31cad323a67d70416826330c1414fa70f0`.
HTTP scene still reports media header coordinates in1920x1080 while scene dimensions
are3840x2160. No changed-build evidence, so no replay of the failed capture.
No producer acknowledgment yet for resolved-scene or header-coordinate requests.

TTR acknowledged the export request and identified its shipped
`Skills/tvtestrig/references/export-fixture-job.rb`. Read its source; it uses the same
bounded manifest/read route already successful here, with exclusive staging/publication.
Prefer the producer-maintained tool on future transfers after matching local skill
availability. No redundant transfer performed; that script is source-inspected,
not newly runtime-qualified here. Direct `export-job` diagnostic repair remains TTR-owned.

## Exact next tranche after producer repair

1. Verify changed Fixture build and passive media-header consistency; reconcile the
   source-defined target plan. Repair source evidence, never double/drop header boxes
   at consumer. Receive supported resolved-scene sidecar contract for TTR intake.
2. Define/review multi-run completion evidence retaining original and new build/instance
   identities plus every catalog slot. Current resume plan is intentionally not runnable;
   do not pass it to `--execute` or claim the partial prefix is an admitted corpus.
3. Under continuing pilot authority, run the missing groups into new outputs only,
   then validate complete42-recipe membership, visual geometry, development crops and
   shipped baseline. Existing failed artifacts stay failed. Capture remains blocked
   until producer geometry is repaired; no automatic polling/retry is installed.
4. Only after full pilot acceptance prepare scale/candidate authorization. No quotas
   or training gate lowered. Existing unrelated offline work remains independent.
