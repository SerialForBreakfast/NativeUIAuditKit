# Rich reference corpus and route feasibility

Scope: [SYNTH-01/02/05/06 assigned plan](../Plans/2026-10-02-rich-reference-campaign.md).
Local evidence: `.local-work/reference-rich-20261002/`. Producer qualification is
separate from consumer receipt, crop admission, source publication and model benefit.

## Implementation and compatibility

- Opt-in referencePack version2 supplies seeded city, orbit and collage artwork,
  dark/light context, 24/30 catalog items and24 guide rows. Catalog controls use
  native image growth; guide rows use their explicit row-highlight treatment.
  Artwork stays fixed across each pair. Version1 canonical identities and layouts
  remain separate; reference-view parity is not whole-app parity.
- Rich catalog uses eager four/five-column rows and64point viewport margins.
  Measurements still come from rendered native views; margins do not fabricate
  bounds or guarantee a crop for a scrolled-out control.
- Request version11 / `reference-rich-v1` expands the matrix through existing
  campaign CLI/MCP. Exact request bytes, plan hash, seed, styles, backdrop,
  viewport and upstream ancestry are retained. Invalid combinations/budgets fail.
- Rich scene load now waits for a freshly observed, settled neutral scene before
  issuing focus. It checks run/recipe/generation/native verification and sample
  age. A timeout retains the last scene, rather than leaving only a timeout code.
- Rich catalog requires500ms observed native stability. This scoped response to
  a captured late-geometry change does not lower or globally replace settling.

## Checks and acceptance evidence

| Criterion | Evidence / result |
| --- | --- |
| Compatibility, request validation, budgets, negative outcomes, scene-load admission | `campaign-05.xcresult`:61 tests passed,0 failed,2 explicit opt-in skips (generated production matrix, authorized live campaign pilot). Earlier narrower51-test lane passed. Live workflows below cover their assigned runtime scope independently. |
| Fixture model compatibility | `model-check.log` passed; final500ms floor additionally exercised by signed captures. |
| Signed local products | Fixture build03 and TTR candidate04 built successfully; development signature and portable Simulator gates passed. No consumer binary packaged. |
| Review/timing tooling | Reference summary4checks passed: completed/failed separation, member hashes, finite timing and path safety. Skills validation plus10self-tests passed. |
| Actual capture/export/resume | 36/36pairs:12appearance +24transition,72original PNG entries /66unique hashes. Seven exact CLI-plan/MCP-generate/export batches; completed batches resumed without changing retained data. Final runner closed and ownership/readiness clear. |
| Longer forward/reverse route | Actual CLI route record returned observation_unavailable with0recorded transitions. Snapshot sequence1 stayed1through disconnect: no directional input. Starting scene was native-verified neutral, with no focused control. Longer routes, trial qualification, replay and stale-map check were not reached. Developer-only direct HTTP setup was deliberately excluded. |
| Delivery | Data-only archive prepared from the seven original exports, with exact accepted-case index, grouped overlays, crop audit and timings. Final publication receipt is separate; consumer receipt/admission remains pending. |

## Failures preserved and repaired

`pilot-02` exposed missing geometry in lazy catalog rows. Guide pairs remained
accepted; eager catalog rows repaired that producer defect. `catalog-02` then
failed the strict capture bracket when geometry changed late. The observed500ms
native window qualified in `catalog-03`; validators were not weakened.

`remaining-03` completed13pairs then timed out at catalog collage/dark scene setup,
before input. The cleanup scene was neutral, which does not establish the earlier
cause. The new load-admission checkpoint targets the asynchronous scene/focus
publication boundary. Its exact previously failing case passed in
`missing-collage-dark-04`; the original failure is retained, not overwritten.

Host contention deferred several attempts before input. Unrelated processes were
preserved; no Simulator restart, host-service restart, settings change, physical
operation or audible test occurred. Read-only settings showed High Contrast Focus,
Reduce Motion, Hover Text and Enhanced Background Contrast all0.

## Review and limits

Visual inspection of catalog collage/dark and guide orbit/light confirms seeded
surrounding content and visible focus cues; it does not replace measurement audits.
Per-frame solid-body bounds include native growth. Shadows/glows are context, not
segmentation labels. Crop review keeps a common union window plus16percent per side,
explicitly excluding absent/clipped bodies. Originals and sidecars stay unchanged.

Retained timing comparison is descriptive: older guide unchanged/moved cases were
13.20/20.98seconds and catalog13.26/15.14; first rich guide cases12.61/21.76 and
catalog17.91/25.67. More controls, different viewport/content,500ms catalog stability
and host load confound the comparison. No speedup or training improvement claimed.

All reference descendants retain whole upstream renderer ancestry and calibration
intent. Random seeds or art styles do not create independent train/evaluation
families. Consumer acceptance and maintainer Git publication remain outstanding.
Lessons used: N-010 (cleanup/health), N-016 (native route evidence and origin).

## Final corpus and route disposition

| Source campaign | Accepted pairs |
| --- | ---: |
| pilot-02 (guide only) |3|
| catalog-03 |3|
| light-03 |6|
| remaining-03 |13|
| missing-collage-dark-04 |2|
| missing-collage-light-05 |3|
| missing-orbit-06 |6|

All36case identities are unique. Partial campaign receipts retain failed/unattempted
rows, so consumers must use `audit.json`'s accepted index and original receipt state,
not sum every attempted request. Original accepted pairs were not recaptured.
The24transition pairs have96verified scene observations across48capture brackets,
with action/mutation receipts, run/recipe/generation identity and ordered frame times.
Appearance review checked all12pairs, with0rejections and12groups. Transition review
found120measured common crops and72absent/clipped exclusions.66distinct hashes across
72frame entries are expected reusable/unchanged visual states, not72independent images.

Mean retained seconds per appearance/moved-scroll/unchanged-focus-scroll case:
guide6.51/16.88/12.19; catalog11.89/25.73/26.04. These include per-case startup and
cleanup. Host-admission waiting, overall orchestration and export are retained in
separate timing records; neither these means nor the old pilot comparison isolates
renderer throughput. The corpus remains a calibration set, not an evaluated training mix.

The route feasibility result is **not qualified**. The existing campaign intentionally
restores a neutral scene; CLI/MCP route recording has no supported operation to load
a recipe and establish a generation-bound native-navigation origin. The exact failed
record and native scenes are in `route-stingray_catalog-admission01`; its session
closed and postflight can_run was true. Repeating the same neutral-origin probe for
the guide cannot answer a different question. No long-route or stale-map success is
claimed. Resume condition: implement supported origin preparation (identity check,
load readiness, verified focus, independent cleanup), then run both three-down /
three-up routes, repeated trials, batch replay and stale-map/interruption rejection.
This is the assigned feasibility disposition, not completion of broader SYNTH-06.

Recommended next core: SYNTH-06 + NAV-VERIFY-01 origin preparation and end-to-end
scrolling route recipes, together with SYNTH-02 cancellation/resume during those
longer collections. Deliver compact CLI/MCP outcomes and repeatable catalog/guide
routes with current-state checks, crop evidence and bounded cleanup. No new hardware
approval is needed for the standing local Simulator scope. Optional ACC-PERCEPT-01
retained tracking30 OCR/binding agreement is independent and offline; physical
qualification still needs its own scope.
