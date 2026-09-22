# Perception evidence and integrated acceptance

2026-09-22. Architect review completed against the original offline contracts;
PER-01 inventory/software and PER-02/04/05/06 offline scopes **accepted**.
Base `d3171ec5976e55cf413a7eb782f8c185789d3cf9`; starting working tree clean.
This is an architect review of previously delivered implementations, including local
corrections; it is not independent external peer review or live producer acceptance.

| Outcome | Result |
| --- | --- |
| Software verified | Pass: actual CLI paths, reviewed failure boundaries, 131 focused tests plus standalone ingest checks and package checks |
| Data eligible | Not established: zero newly qualified gold-label cases or training pairs; legacy data remains quarantined |
| Integration qualified | Offline consumer/primitive integration passes; genuine TTR integration remains unqualified |
| Model gate passed | Not assessed; no real-data inference, training, weights, export or promotion |

## PER-01 evidence decision

Fresh [audit](audit.json) exactly matches the previously retained audit, file SHA-256
`f29997b9311a2bec5a03c49265e788a3778fa8238c56e7ce321feb6538f33cf6`.
All 1,500 pairs / 3,000 crops decode, but 84 decoded-pixel groups cross partitions;
all examples are dark and none has the required frame-evidence envelope.
No crop labels were requalified or partitions changed.

All 44 supplied screenshots were visually triaged, with Settings additionally reviewed
at full resolution: 31 Home grid/shelf, five app-switcher, two Photos welcome, and one
each Fixture diagnostic screen, folder, video, loading, account picker and Settings list.
All 29 source sidecars have zero elements; 15 images lack sidecars, and 11 prediction
files are explicitly excluded from truth. File names are not reliable app identity.
The account-picker image is privacy-review quarantined without transcribing identity.
The reported About → Name and Delete Siri History incidents are not in this supplied set.

[Per-member dispositions](visual-review.json) bind every image hash.
[Coverage matrix and intake requirements](evidence-and-gaps.md) freeze supported leads,
missing gold labels, source/journey review, scene/theme and hard-negative requirements.
Quarantine is logical: all original files and historical reports remain untouched.
Contact sheets are local inspection aids under `.build/debug-output/perception-acceptance/`;
they are not dataset examples, gold labels or SMB content.

## Findings repaired before acceptance

1. **PER-02 missing modalities:** `{}` previously looked like successful empty predictions.
   Both actual and oracle payloads now require explicit chevrons/dialog fields; empty
   arrays/null remain valid. New regression exercises both branches.
2. **PER-02 unknown association:** a localized chevron with no row claim counted as a
   wrong-row link. It now has `associationAbstentions`; wrong claimed rows still count
   as errors. Development triage records the gap rather than reporting no measured gap.
3. **PER-01 dimensions:** Python booleans were accepted as integer dimensions. Rejected
   explicitly, tested independently for width and height.
4. **PER-05 helper boundary:** returned regions lacked frame containment/component-count
   validation. Malformed rectangles outside foreground could imply stability. Out-of-frame
   or >128-region replies now fail the sequence and remain in failed-sequence accounting.

Research contract clarifications preceded changes. Production Swift/public APIs, model
artifacts, producer code and protected skills were not changed.

## Per-packet acceptance and integration boundaries

| Packet | Reviewed entrypoints / acceptance evidence | Still not established |
| --- | --- | --- |
| PER-01 | `audit_training_evidence`, perception validator/rubric; all requested members accounted for, actual decode/hash checks, 44 visual dispositions and explicit coverage gaps | Reviewed gold boxes, source/journey assurance, independent benchmark membership |
| PER-02 | `perception_benchmark` + `perception_adapters`: independent observations, actual/oracle isolation, ambiguity, semantic unknown, slice/support/latency/failure reports; 19 tests and actual CLI replay | Shipped/TTR detection baseline on eligible held-out screens; numeric model decision |
| PER-04 | `harvest_focus_pairs` → frame/physical validation → runtime recrop → `physical_focus_readiness` → protocol/score/proposal evaluation; 56 focus tests including 10 physical integration tests | Genuine completed bundle, native callback binding and actual visual alignment; eligible pilot/corpus |
| PER-05 | Actual TransitionTool/FrameSimilarity/ChangeRegionLocalizer boundary; causal history, freshness/cadence/deadline, foreground/full-frame distinction; 16 tests and nine-sequence replay | Calibrated real-journey thresholds, unseen overlay safety, live adapter/navigation performance |
| PER-06 | Actual AnchorTool/TextAnchorVerifier boundary; title/row geometry, changing values/scroll, duplicate/locale/stale/epoch abstention, truth-independent matching; 17 tests and 15-case replay | Registered real references, held-out identity accuracy, producer route/resume integration |

These contracts do **not** form an implicit live controller. Coordinates must stay explicit:
PER-02 uses top-left pixel xywh; PER-04 raw boxes use pixels and production 16%-expanded
256×256 crops; PER-05 ROIs/changes use pixels; PER-06 uses normalized top-left xywh, converted
to Vision coordinates only inside AnchorTool. Producers need a separately reviewed adapter,
not direct interchange of differently named fields or source-kind enums.

All retain unavailable/failed versus successful empty results. PER-02 imported observations
are not executed inference; PER-04 test-only bundles never become physical approval;
PER-05 ready and PER-06 candidate never authorize action. Source claims remain non-attested.
The schemas deliberately separate crop-level, pair-target, frame and journey metrics; do
not pool their scores or treat shared source frames as independent evaluations.

## Verification and reproducibility

Logs: `.build/debug-output/perception-acceptance/`. All final commands exit 0.
Python prefix: `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python`.

| Command suffix | Result / log |
| --- | --- |
| `-m unittest discover -s scripts -p 'test_perception*.py'` | 19 pass / `perception-final.log` |
| `-m unittest discover -s scripts -p 'test_*focus*.py'` | 56 pass / `focus.log` |
| `-m unittest discover -s scripts -p 'test_transition_benchmark.py'` | 16 pass / `transition.log` |
| `-m unittest discover -s scripts -p 'test_identity_benchmark.py'` | 17 pass / `identity-final.log` |
| `-m unittest discover -s scripts -p 'test_evidence_audit.py'` | 14 pass / `audit-tests.log` |
| `-m unittest discover -s scripts -p 'test_harvest_bundle_validation.py'` | 9 pass / `bundles.log` |
| `scripts/test_ingest_fixture_batch.py` | All standalone checks pass / `ingest.log` |
| `reports/work/PERCEPTION-ACCEPTANCE/replay.py` | Three actual CLIs pass / `replay.log` |
| Offline `swift build`, `swift test` | Build passes without warnings; 92 Swift Testing + 14 XCTest pass / `build-host.log`, `swift-test.log` |

Swift uses `--disable-automatic-resolution --manifest-cache local` with project-local
TMPDIR/module/cache/config/security paths. Initial restricted build failed at
`sandbox_apply` (`build.log`); the approved host build/test passed. Host Vision/CoreML
regressions use generated test fixtures only. No capture or trained-model quality result
is inferred from those tests. No downloads, Git writes, system reset or other-repo edits.

Fresh source-bound reports: [PER-02](perception-replay.json),
[PER-05](transition-replay.json), [PER-06](identity-replay.json).
Replays have 1, 9 and 15 synthetic cases/sequences respectively; no live quality claim.
`replay.py` refuses its existing output tree; preserve originals when reproducing in a
new scoped location. Historical reports remain bound to their original implementation.
Final source/helper hash, JSON, Python syntax, link and diff checks are recorded in
`.build/debug-output/perception-acceptance/final-checks.log`.

## Changes, handoff and next action

Changed implementation: perception validator/scorer/triage, transition helper-reply
validation and associated regressions. Added review plan, fresh audit, per-image review,
replay reports and reproducible review scripts. Updated queue, catalog, roadmap,
CurrentState and BP-66; no parent model/data task is closed. P0-C untouched.

The assigned offline review is complete. Remaining real gates require new inputs or
separate execution authority, not another helper. Once TTR is repaired: authorize a
bounded genuine smoke → validate completed-bundle intake/actual crop alignment → authorize
the development pilot and shipped FocusRing baseline. Broader harvest and training remain
separate approvals. While TTR remains blocked, P0-C can continue under its existing owner;
a separate curated manual-annotation assignment could use the Settings/Photos leads,
but cannot reconstruct missing callbacks or independently held-out journeys.

[Shared coordination](coordination.md) publishes only consumer contract corrections and
the intake consequence. No new producer feature is required by these local fixes.
No background work, device lease or training process remains from this tranche.
