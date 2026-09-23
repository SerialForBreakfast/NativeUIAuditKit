# APPEAR-C — catalog qualified; independent appearance evaluation still blocked

| Outcome | Result |
|---|---|
| Software verified |9 v2 +14 harvest tests pass; Swift build passes. Full Swift tests blocked/fail in restricted Vision/CoreML execution; not a full software acceptance |
| Data eligible |12 reviewed pairs admitted v1.5 development-only;8 distinct decoded pairs, not12 independent examples |
| Integration qualified |Three exact-target catalog jobs → bundled chunk export → strict v2 validation → production crops pass |
| Model gate passed |Not assessed; no inference, training, export or promotion |

## Completed scope

Frozen contract: [APPEAR-C](../../../Research/Plans/CatalogAppearanceQualification.md).
Local target9026ECA9, Fixture5b697fb4, appPID42670/FixturePID43156; source checkout
4acf1dee. Source and installed identities are separately recorded, not claimed
reproducible-build equivalence. Normal simulator/app-managed storage included;
explicit outputs remain in NUIAK. No Office, button activation, settings changes,
restart, installation, producer edit, recapture or Git write.

| Recipe, seed307/regular | Job | Expected/captured/accepted/rejected pairs |
|---|---|---|
| kitchen_sink/light |20FDBC1C-8062-4C51-9C73-3CC7452F0FEE|4/4/4/0|
| kitchen_sink/dark |E62EB535-C42B-45E9-BD91-689F32A33FE7|4/4/4/0|
| kitchen_sink/high_contrast |5F7E6524-9F37-4CCA-A35C-AD3A4511F2D3|4/4/4/0|

Each recipe:5 reference/focus states,8 actual measured control annotations,
4 native focus targets,33 explicit placeholder exclusions. All54 exported files
independently size/hash verified; strict v2 freshness/recipe/geometry/hash checks
pass. All15 state overlays and24 production crops visually reviewed. No missing
target or clipped target; real controls rather than catalog cells are measured.
Member hashes, recipe hashes, job receipts and manifests are retained in per-theme
prepare/status/export/inspection/intake files. All jobs terminal within10 minutes.
Final postflight same Fixture instance, settled/ready, ownershipclear. No owned
operation remains. Fixture left on last high_contrast catalog, not restored.

Raw: `dataset/tvos_captures/appear-c-{light,dark,high_contrast}`.
Crops: `dataset/focus_ring/appear-c-{light,dark,high_contrast}`.
Three v1.5 manifests are hashed in reservation.json. They stay development-only
by consumer contract; all catalog variants reserved together, unavailable for
training and not automatically reclassified as holdout. Sillycon's old4-pair
artifact remains separate; local capture does not claim to have received it.

## Independence and coverage decision

reservation.json verifies old source bytes/decoded pixels against APPEAR-B and
protected Remotes references:434 old samples versus24 new crop samples, zero
exact frame/crop overlaps. All high_contrast crops equal their dark counterparts:
8 duplicate sample groups,16 distinct crops/8 distinct pairs. Retain originals,
do not double-count. Source has `.preferredColorScheme(theme == .light ? .light : .dark)`
and no highContrast branch in the procedural renderer/builder. This proves this
catalog's missing visible contrast variation, not every producer screen's behavior.

One common layout/rendering/focus-treatment family cannot provide two unrelated
groups per stratum per partition. No model predictions were computed; the reserved
data have not been consumed for model selection. Zero pixel overlap alone is not
proof of semantic independence. No validation/final groups approved.

| Required APPEAR-B stratum | Current evidence | Remaining requirement |
|---|---|---|
| Dense dark media/thin outlines |Old development media uses fixed blue/purple gradient|New artwork/layout families with observed labels|
| Bright unfocused artwork |Catalog bright focused buttons; static image SF Symbol|Actual varied bright artwork and verified non-focus|
| Gray/blank artwork placeholders |33 excluded taxonomy-label placeholders|Real rendered placeholder visual family, not fake class labels|
| Dock/neighbor focus |Catalog grid; no dock renderer|Independent dock/grid context with focus callback binding|
| Photos-like primary/secondary |Native catalog buttons, one treatment/layout|Distinct qualified families for validation and final challenge|

Top Shelf's solid/gradient/checker controls do not add artwork to these in-app
controls or label Home targets. No Top Shelf mutation or Home capture was implied.
No authorized local operation can create absent producer renderer families; request
producer-owned changes, not more seeds/copies of this catalog. Final independent
evaluation remains blocked, not silently reduced to8 pairs from one family.

## Targeted NUIAK fix and verification

Light bundle originally passed sidecar integrity but extraction rejected existing
`destructiveButton` as unsupported. Added only that existing taxonomy case to
FOCUSABLE; research amendment preceded code. Real CLI regression verifies two
production crops remain test-only; noninteractive `label` still rejected. All
native observation and v2 safety gates retained. Captured bytes reused unchanged.

- v2 suite9 tests,0.736s,exit0; harvest suite14 tests,0.085s,exit0.
- Actual three manifest/crop CLI invocations exit0,4 pairs each.
- Swift build exits0,7.82s. Full Swift tests exit1:15 Swift Testing issues;
  CoreML E5RT tries user Library/Caches outside the approved project boundary,
  and Vision feature-print tests fail CVPixelBufferPool(-6662). No permission
  weakening, HOME spoofing or external cache-write escalation performed.
  These checks remain incomplete; do not report all tests green. A separately
  approved platform-cache/test runtime or compliant cache routing is the resume
  condition for full-suite verification, not another TTR rebuild.
- diff whitespace check required at final handoff. Old evidence and source
  memberships preserved. No experiment log entry because no training run.

## Next tranche / exact blockers

Producer: qualify explicit independent in-app artwork/layout/focus-style presets,
rendered high-contrast distinction, resolved preset IDs/hashes and native labels.
Begin with one representative positive/negative pair per distinct family, not
another large harvest. NUIAK then reserves entire families before capture,
validates them and establishes independent validation plus untouched final groups.
Existing APPEAR-B1 offline adapter work remains unblocked in parallel.

This tranche completed the locally supported catalog capture/intake and readiness
assessment. The requested independent appearance qualification is incomplete due
to missing families, and full software verification has a separate test-runtime
blocker. TTR/fixture skills preserved labels/cleanup; worker guidance prevented
counting duplicates or parser success as model readiness. Shared status publication
and acknowledgment tracked in coordination.md.
