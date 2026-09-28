# Local human annotation and data review — implementation plan

Revision1,2026-09-28. Planning deliverable; implementation not started or authorized
by this document. Tasks.md owns packet state/assignment. Focus is the first use
case; support existing UI-element labels without changing public taxonomy or Swift APIs.

## Outcome and design

**Capture a batch → inspect/correct locally → validate → explicitly admit an immutable
dataset revision.** No chat between individual annotations or remote inputs.

Two complementary lanes:

- **Annotation:** self-hosted CVAT for drawing/correcting control boxes, class and
  focus attributes, keyboard-driven object review and human decisions.
- **Audit/triage:** local FiftyOne for frame/pair browsing, overlaying retained
  predictions, source/class/failure filters and reproducible review queues.

Use the existing FiftyOne–CVAT integration rather than another annotation app.
NUIAK owns provenance, coordinate conversion, review/admission validation and crop
QA. Files in immutable versioned bundles are authoritative; tool databases are
working copies. Preserve original labels, suggestions and reviewed labels separately.

Official references checked2026-09-28:
[FiftyOne CVAT integration](https://docs.voxel51.com/integrations/cvat.html),
[CVAT local installation](https://docs.cvat.ai/docs/administration/community/basics/installation/),
[CVAT manual review](https://docs.cvat.ai/docs/qa-analytics/manual-qa/).
The integration supports a self-hosted endpoint and scalar label attributes;
complex provenance stays in NUIAK sidecars. CVAT UI restrictions must not be relied
on to protect IDs: enforce identity and permitted changes on reimport. Verify
chosen community-edition/version features during setup; no enterprise dependency.

## Existing evidence and reuse

- `reports/work/FOCUS-HUMAN-OFFICE-01/`:8 retained1920×1080 PNGs, raw inline receipts,
  session snapshots and final timeline with9 inputs. Home, Photos Welcome and
  Settings. Both Photos button focus states exist; missing intermediate route
  images remain explicit. No new capture required to start review.
- `scripts/photos_focus_pilot.py` and `scripts/test_photos_focus_pilot.py`: working
  diagnostic import/review, original hash binding, dispositions and production crops.
- `scripts/focus_runtime.py`, existing FocusRingTool/FocusRingClassifier crop path:
 16% expansion,256×256, existing item/pixel limits. Reuse, do not implement a Python
  approximation of training crops.
- `scripts/focus_retained_review.py`, `scripts/audit_training_evidence.py` and current
  contract validators: inspect/reuse compatible logic without loosening their gates.

**Concrete adapter gap:** the Photos importer checks `outputWritten == true`, limits
observation JSON to2MiB and requires `photosConfirmed`. Current captures have
`outputWritten:false` because bytes arrived inline, and some base64 receipts exceed
that JSON limit; Home/Settings are not Photos. Preserve raw receipts and validate
decoded byte identity through a separate bounded inline adapter/versioned generic
review record. Never flip original fields, raise all limits blindly, or claim every
frame is Photos. Preserve existing Photos CLI semantics and its rejection tests.

## Tranche map

| Tranche / packet | Deliverable | Dependency | Engineering estimate |
| --- | --- | --- | --- |
| 1 / HUMAN-REVIEW-01 | Usable local annotation round trip on8 retained images | Approved local setup/storage scope | 1–3 days |
| 2 / HUMAN-REVIEW-02 | Defect audit, sampling and prioritized review queues | Tranche1 contracts/working round trip | 2–3 days |
| 3 / HUMAN-REVIEW-03 | Automatic TTR bundle → review-batch integration | Tranche1 + exact producer schema/sample; live proof needs recorder readiness | 1–2 days after interface available |
| 4 / HUMAN-REVIEW-04 | Human-label admission policy and gated dataset preparation | Tranches1–2 + explicit role-policy approval; not dependent on live TTR | 1–2 days |

Rough total5–10 engineering days, excluding producer recorder work and dependency
installation/compatibility issues. First usable editor is Tranche1, not the end of
the project. Budget an initial30–45minute human review session; measure actual
time/object and correction rates before estimating larger audits. Estimates are not
commitments or a requirement to spend the full time.

## HUMAN-REVIEW-01 — local setup and real annotation round trip

Proposed owner: NUIAK review-tool worker, assigned separately. Implement end to end,
not just install tools or produce a schema stub.

1. **HR1.1 Runtime/storage preflight.** Inventory Python/package compatibility,
   available Docker runtime, ARM64 image support, ports, memory and disk; pin tested
   tool versions and image digests. `docker` executable exists locally, but daemon/
   image compatibility is unverified; about40GiB disk free was observed during
   planning. Preserve existing training environments. Dedicated ignored review env,
   database, caches, media, logs and temp files stay project-local.
2. **HR1.2 Local service lifecycle.** Reproducible explicit start/status/stop commands;
   loopback-only host endpoints, scoped container networking and local credentials.
   No cloud annotation backend, public listener, external image upload, automatic
   model download, background login service or dependency on TTR being open. Check
   telemetry/update traffic and document/disable optional egress. Declare Docker VM,
   image-store or OS-owned writes outside the repository and obtain a scoped
   exception before installation/start if unavoidable; do not relocate HOME or
   silently use default external database/volume locations. No sudo/install today.
3. **HR1.3 Verified import.** Freeze input index/hashes, retain all8 originals and
   receipts; implement the inline/mixed-screen adapter described above. Preserve
   Foundation/monotonic timestamps, event mappings, source/session IDs and missing
   sequence frames. All membership accounted for, idempotent repeat imports, no
   overwrite or inference from remote-button intent. Use generated adversarial
   fixtures for software tests rather than depending on ignored live artifacts.
4. **HR1.4 Actual review interface.** Load a numbered frame list and paired controls;
   full-frame context remains available. Show each control's box, stable local ID,
   existing class, focus state and review status. Permit precise box edits and
   keyboard iteration, flag/reject/unknown decisions and an explicit batch review
   completion action. Human confirms focused/unfocused/unknown plus per-frame
   bounds; clicking Save alone does not prove every object was inspected. No
   required hand editing JSON. CVAT tasks must be reachable from the review queue.
5. **HR1.5 Round trip and crop QA.** Use existing predictions only when their image/
   model/preprocessing binding is verified; otherwise no predictions, or explicitly
   labeled agent/manual box proposals. Do not silently run a detector. Correct an
   actual box and focus attribute, export, reimport into a NEW reviewed revision,
   validate IDs/coordinates and generate crops with the production helper. Preserve
   fractional coordinates; conversion must not move an unchanged box by more than
   one original pixel (round-trip engineering tolerance, not model quality gate).
6. **HR1.6 Operator handoff.** Review both Photos controls across frames004/005;
   keep repeated Home/boundary frames as contextual evidence, not new independent
   sources. Complete the real browser edit/reimport path with the user and retain
   review provenance; without a human session, software can be review-ready but
   data remains pending. Exported diagnostic records stay rejected by current
   training/evaluation admission. Provide one-page Start/Review/Finish instructions.

Acceptance: all8 images displayed/accounted for or a precise diagnosed exclusion;
changed and unchanged annotations round-trip without silent ID/geometry loss;
unknown/unreviewed examples blocked from accepted labels; original bytes unchanged;
real production crops verified. Service restart preserves review progress, stop
releases only owned processes, and no media leaves approved local storage/services.
Minimum negative tests: changed hash, missing/corrupt image, swapped image ID,
unconfirmed focus, conflicting native/human evidence, invalid/NaN/out-of-bounds
geometry, metadata edits, repeated import, unsupported version and interrupted export.

## HUMAN-REVIEW-02 — audit defects and prioritize review

1. **HR2.1 Deterministic validators.** Reuse existing integrity and crop checks;
   report missing media, hash mismatch, invalid boxes/classes, duplicate identity,
   contradictory labels, missing pair members and source/role leakage. Validate
   per-frame boxes rather than copy geometry across focus scaling. Distinguish
   crop pixel duplicates, full-frame duplicates and perceptual near-duplicates;
   approximate similarity flags never automatically delete frames or labels.
2. **HR2.2 Focus-aware completeness.** Track complete/partial/unknown candidate
   coverage, unknown/no-focus states and human/native disagreements separately.
   A partial annotation set cannot establish unique-focus selection. Missing
   labels are not negative examples. Original source/task membership stays fixed.
3. **HR2.3 Two review queues.** Reproducible source/stratum-aware random sample
   (seed, denominator and selection IDs retained) plus targeted defects/disagreements.
   Browse both in FiftyOne; send correction tasks to CVAT and return to the same
   sample IDs. Keep random-audit results separate from targeted-review statistics.
4. **HR2.4 Measured data feedback.** Report coverage by source/app/control/appearance,
   label issue types, corrected boxes, ambiguity, reviewer time and pair dispositions.
   Link each issue to the image/control/review revision and a proposed Fixture recipe
   or real-source collection assignment. Missing attributes stay unknown. New model
   inference/embeddings require a separate assignment; retained scores may be reused.
5. **HR2.5 Scope and verification.** Start with8 real frames plus isolated known-bad
   fixtures; then an explicitly chosen development corpus, not a whole-repository
   scan or protected challenge. Inject each supported defect and verify the actual
   CLI→queue→correction→revalidation flow. Preserve label changes as revisions.

Acceptance: deterministic seeded membership; every injected hard defect caught or
unsupported behavior explicitly blocked; soft heuristics labeled as such; every
sample disposed without silent dropping; corrected examples leave issue queue only
after revalidation. Audit report does not claim broad model accuracy or independent
sample confidence from correlated templates. No fixed review percentage is a gate:
initial real examples receive explicit review, later sampling policy uses measured
defects/source diversity and separate approval.

## HUMAN-REVIEW-03 — connect the automatic recorder to review

1. **HR3.1 Bind real producer schema.** Obtain exact TTR recorder interface, versioned
   receipt and representative finalized bundle from the separate
   [action-linked recorder work](TTRActionLinkedCapture.md). Validate named files,
   hashes, paths, size bounds and ownership; no guessed transport or new MCP server.
2. **HR3.2 One consumer ingest.** After an explicit delivery/import action, build
   a review batch automatically: event/frame ordering, candidate pairs, no-op and
   overlap/gap labels, and optional OCR tied to exact images. Incomplete trajectories
   remain incomplete; event IDs alone cannot manufacture intervening images.
3. **HR3.3 Reuse lanes.** Same review/validator path for local and remote TTR bundles;
   no silent host failover, remote transport requirement for local work or automatic
   live device operation. Idempotent receipt prevents duplicate batches; annotation
   progress survives reimport/restart. Batch launch does not imply a background watcher.
4. **HR3.4 Qualification.** Offline representative bundle tests first; later one
   separately approved Start→human navigation→Stop→verified import→batch review
   trial, with zero per-button chat. Report producer capture, delivery, consumer
   import and annotation outcomes independently. Software development on an accepted
   schema/sample does not wait for full hardware qualification.

Acceptance: all recorded inputs accounted for with image mappings or typed gaps;
no silent frame reduction; interrupted delivery cannot appear complete; replayed
receipt creates no duplicates; human can correct imported controls without editing
metadata files. Producer readiness blocks only actual interface/live acceptance,
not Tranches1–2 or retained-data review.

## HUMAN-REVIEW-04 — explicit human-label admission and dataset candidate

1. **HR4.1 Policy decision before gate code.** Propose separately versioned criteria
   for human-reviewed training candidates and development regression examples, label
   provenance, disputed/unknown exclusion, source grouping and reviewer acceptance.
   Maintainer must approve that policy explicitly before implementation changes any
   admission path. Existing diagnostic manifests remain ineligible; do not toggle
   their flags or pretend labels came from native telemetry.
2. **HR4.2 Immutable candidate construction.** After approval, create new references
   to original/review/crop hashes plus the exact admission decision. Preserve existing
   train/retention/selection memberships, use source/journey-group split constraints
   and run cross-role pixel/source checks. Existing exposed8 screens can be assigned
   approved development uses, never untouched challenge status. Different sessions
   of the same layout do not create independent source groups. Keep unknown lineage
   disjoint from independently qualified evidence.
3. **HR4.3 Preflight, not training.** Verify actual assembly/admission entrypoints
   accept only the new approved lane and reject legacy diagnostics, tampered reviews,
   absent approvals, source leakage and incompatible manifests. Prepare a candidate
   dataset/coverage report and exact remaining data assignment. No trainer run,
   export, promotion, qualification-threshold change or new model run ID.

Acceptance: policy recorded before code, one valid admitted fixture and realistic
rejected cases exercised through caller integration; actual human examples admitted
only where review/policy permit. Approved dataset snapshot and rollback references
are reviewable; ability to train is not authority to train, and missing independent
coverage still blocks full qualification.

## Cross-tranche implementation contract

- Suggested new entrypoint: `scripts/human_annotation_review.py`, with explicit
  import, send-for-review, receive-review, validate and export operations; names
  finalized in research before coding. Lifecycle commands may be a small separate
  script/config. Do not turn this into a custom annotation application.
- Proposed schemas under Research/schemas are local versioned contracts; no changes
  to native-journey schema or library taxonomy. Stable frame/control/review IDs and
  hashes bind every operation; external app object IDs are mapped, not authoritative.
- Put installed runtime/workspaces under an ignored project-local review tree;
  outputs in `reports/work/HUMAN-REVIEW-0N/` and existing ignored data paths. Pin
  manifests/config/templates, not media, databases, secrets or containers in git.
- Before code, perform AGENTS.md's mandatory research reading and record architectural
  decisions. Preserve other active worker files. Run focused adapter/UI round-trip
  tests plus existing Photos/intake regressions; run offline `swift build` and
  `swift test` at each integrated code handoff. Package tests require neither Docker
  nor services/network; separate local service/UI acceptance is explicitly reported.
- Each handoff maps criteria to evidence and reports software, data eligibility,
  integration and model gate separately. Planning doesn't pass those gates.
- Sharing: this plan creates no new TTR requirement beyond the published recorder
  contract, so no SMB publication needed now. Publish a schema incompatibility or
  actionable acceptance finding when it changes the producer's next action.

## Recommended first assignment

Assign **HUMAN-REVIEW-01 in full**, including approved dependency/setup preflight,
actual editor use, export/reimport, negative tests, production crop integration and
operator handoff on the8 retained images. Approve exact local dependency/service
installation and any unavoidable outside-project runtime storage explicitly before
those actions; missing permission blocks that portion, not offline adapter work.
Run TTR recorder implementation as a separately owned parallel lane. Do not wait
for better models, recapture Photos or require all four tranches before useful review.
