# NativeUIAuditKit — Current State

**As of:** 2026-09-22 (local; latest focus experiment 2026-09-22 UTC)
**Audience:** maintainers and agents  
**Open work:** [`Tasks.md`](../Tasks.md)  
**Finished work:** [`CompletedTasks.md`](../CompletedTasks.md)

This page is the living snapshot. If it disagrees with `AGENTS.md` or `README.md`, fix those to match this file.

---

## Shipped

**2026-09-23 FDR-008 completed (experimental, not shipped):**
[Mixed-appearance run](../reports/work/FDR-008/handoff.md) finished30/30 epochs;
epoch3 selected by native-validation loss. At0.85, Fixture training fit improved
75%→100% on172 crops; native validation18/18 and Remotes challenge12/12 retained.
This demonstrates learning on reviewed examples, not unseen Fixture generalization.
The shipped model remains unchanged. Next evaluate retained Home/Photos and new
independent Fixture appearances before export/promotion or further training.

**2026-09-23 development-experiment integration (no new model):**
[FOCUS-DEV-01](../reports/work/FOCUS-DEV-01/handoff.md) freezes 126 training pairs
and nine native-validation pairs through real assembly and trainer dry-run. All
bytes/crop parity/splits passed; launch is blocked only by missing experiment
approval. Production mode correctly rejects the protocol. 63 focused Python tests
and offline Swift checks pass. Next review/authorize the single development run
or revise its sampling balance first (88.89% expected Fixture /11.11% native).
No independent Fixture validation, production admission or training is claimed.

**2026-09-23 retained-data review (no new model):**
[FOCUS-RETAINED-01](../reports/work/FOCUS-RETAINED-01/handoff.md) audited 36 recipes /
138 pairs and all 276 production crops. Visual review yields 86 distinct non-maze
development candidates; four exact pair duplicates and 48 maze pairs are excluded
from the proposed experiment. Seeds 7/19 share pixels and cannot be split between
training and validation. The six missing kitchen-sink recipes remain missing.
38 Python tests and offline Swift checks pass. Next implement the bounded
development-experiment contract, then seek one-run authorization; no new capture,
training, production data admission or model qualification has occurred.

**2026-09-23 mixed-source software (not a model release):**
[OS-FOCUS-04 assembly](../reports/work/OS-FOCUS-04-ASSEMBLY/handoff.md) integrates
49 retained native pairs and2 direct dialog pairs with immutable lineage/splits,
training-only sampling and actual trainer preflight. Old root crops were preserved
and refreshed offline through current production preprocessing, with24 new crops
reviewed.89 focused tests and offline Swift checks pass. Configuration is valid;
full training remains blocked by source/corpus approval, test membership and quotas.
Next qualify diverse retained Fixture development groups and freeze one separately
authorized mixed-appearance experiment. No new capture, training or weights.

**2026-09-23 consumer software:** strict TTR sidecar-v2 intake, development-only
v1.5 production crops and existing baseline/preflight integration are verified by
83 focused Python tests plus offline Swift checks. The peer acknowledged the
kitchen-sink request and reports a repair, but its exact advertised artifact path
is absent locally. No new capture, genuine v2 bundle qualification, or training.
Preserve36 recipes/138 pairs; next obtain the exact repaired artifact and qualify
only the missing boundary/groups. [Handoff](../reports/work/SIM-DATA-02-V2/handoff.md).

**2026-09-23 superseding direct-pilot progress:** authorized separate-copy Fixture
metadata cleanup, existing-signature verification, and exact-simulator installation
succeeded (dylib `46011bb0…`). Repaired media capture passed; retained pilot now
contains 36/42 recipes and 138 pairs. First kitchen-sink recipe stopped with
`no_sample`: source routes it to Components, not the native-probed procedural scene.
Six recipes/108 pairs remain. Focus Maze bottom-row clipping needs explicit review.
No full-pilot admission, baseline, training, or promotion claimed. Preserve partial
evidence and continue only after reviewed producer repair.
[Evidence](../reports/work/TVGEN-SETUP-20260923/handoff.md).

**2026-09-23 00:22Z repair available in source, not runtime:** producer6093663
implements measured-only geometry and sidecar v2. Running Fixture is still the old
binary. The existing repaired candidate fails local strict signature verification
(filesystem detritus), so it was not installed. Need a valid candidate and explicit
Fixture setup authority before the authorized resumed pilot. SMB mount absent;
feedback retained locally. [Evidence](../reports/work/TTR-CHECK-20260923-0022/handoff.md).

**2026-09-22 23:06Z continuation software:** missing-group execution and full-catalog
assembly now integrate with the existing production-crop/baseline entrypoints.
32 Python tests and offline package checks pass; real retained12 recipes/30 pairs
re-audited unchanged. No data admitted or training launched. The22:57Z Fixture check
still finds the unchanged media-header defect. Next is corrected-geometry boundary
qualification, then30 remaining recipes/216 pairs—not more resume scaffolding.
[Evidence](../reports/work/TVGEN-RESUME-02/handoff.md).

**2026-09-22 22:15Z repair check:** Fixture is now natively settled/ready, superseding
the initial zero-sample observation; unchanged dylib still reports inconsistent
media-header geometry. Producer commit3667185 addresses export, not that repair.
Direct pilot awaits geometry and reviewed multi-run completion; it does not depend
on the separate exported-sidecar repair needed by TTR intake. No capture retried.
[Evidence](../reports/work/TTR-CHECK-20260922-2215/handoff.md).

**2026-09-22 21:46Z superseding progress:** retained TTR bundle transferred through
documented read-job IPC (12 files verified); NUA numeric-date compatibility fixed,
but strict normalization rejects producer's omitted resolved theme. Independent
direct dialog capture/crops/inference now works: two development pairs, shipped
model TP2/FP2 on four crops. The42-recipe direct pilot completed12 recipes/30 pairs
before media_shelf header coordinate conflict (1920-based bounds in3840 scene).
Partial run preserved, zero pilot pairs admitted; native reference/postflight healthy.
No training/promotion. [Evidence and exact resume](../reports/work/TTR-SMOKE-20260922-2119/continuation.md).

**2026-09-22 21:25Z integration update:** the local two-element dialog smoke now
completes: two accepted calibration pairs/four PNGs, zero rejections, healthy
postflight and clear ownership. Export fails with `serviceUnavailable` despite
working manifest/receipt IPC; pixel intake and crop qualification remain unperformed.
Reuse completed job697018C6 for export diagnosis, not recapture. Prior dialog
geometry failure is superseded; other families and full training-corpus gates are
not qualified by this smoke. [Evidence](../reports/work/TTR-SMOKE-20260922-2119/handoff.md).

Latest Home evidence: [FOCUS-VISUAL-02](../reports/work/FOCUS-VISUAL-02/handoff.md)
compares six reviewed frames/72 tiles: at0.85 shipped makes2/6 correct unique
selections; FDR-007 FP16/int8 make0/6. Candidates'91.7% tile accuracy is the
all-negative baseline. Box variants expose wrong-focus decisions and int8 drift
up to0.09253 with threshold disagreements. No candidate promotion. Next implement
OS-FOCUS-04 mixed-source assembly/preflight offline, then separately authorized
eligible mixed-appearance acquisition/training. These legacy reviews remain
development-only and cannot train the model.

Earlier regression evidence: [FOCUS-VISUAL-01](../reports/work/FOCUS-VISUAL-01/handoff.md)
compares three models on two reviewed Photos frames without TTR. Shipped recognizes
1/2 visibly focused buttons; FDR-007 FP16/int8 recognize0/2. Four-pixel box variants
expose multiple-focus false positives and int8 probability drift0.04346 (>0.01),
despite unchanged threshold decisions. Preserve old Settings results as scoped;
neither candidate is ready for replacement. The Home follow-up above extends this
finding; do not repeat same-style Settings epochs.

Latest local tranche: [FOCUS-COMPRESS-01](../reports/work/FOCUS-COMPRESS-01/handoff.md)
produced one experimental int8-weight candidate:2,612,925 bytes (48.14% smaller),
zero decision differences from preserved FP16 on12 frozen crops; max drift
0.000000715255. Size gate now passes for this candidate, not the preserved FP16.
Warm CPU inference is essentially unchanged; no broad model gate/promotion claim.
[PER-DATA](../reports/work/PER-DATA/handoff.md) accounts for44 existing screenshots:
39 development-only negative-scene reviews, including2 Photos appearance-focus
labels/four boxes;5 exclusions. No admitted positive chevron/dialog examples or
independent benchmark. Next broaden visual challenge coverage, not same-style
retraining. All shipped artifacts remain unchanged.

Latest export: [FOCUS-EXPORT-01](../reports/work/FOCUS-EXPORT-01/qualification.md)
completed in an approved isolated non-cloud environment (Python3.12/Torch2.7/
coremltools9). Import8.90s, export3.47s, compile1.14s; genuine CPU parity passes
all12 frozen native challenge crops, maximum probability error0.00000357628.
This bypasses old iCloud dataless dependencies without repairing/changing them.
Experimental package5,038,123 bytes passes the legacy5MiB calculation but fails
literal5MB. Exporter now enforces5,000,000 bytes; fresh sizegate export correctly
exits1,70 Python/93 Swift tests pass. Existing challenge has zero near-threshold
cases and only one Settings screen. The assigned compression above supersedes
the proposed export follow-up; broader visual capture remains separate. No production replacement or
automatic retraining. [Follow-up](../reports/work/FOCUS-EXPORT-01/size-and-coverage.md).

Latest independent tranche: [OS-FOCUS-03/04](../reports/work/OS-FOCUS-03/handoff.md)
added3 Apps training pairs and6 Remotes challenge pairs. FDR-007 completed8 epochs
on40 train/9 validation pairs:18/18 validation,12/12 challenge decisions at0.85.
FDR-006 also scores12/12 challenge versus shipped CoreML5/12: no demonstrated
incremental gain. Native Settings acquisition/training works without TTR. Home
remains locally blocked on stable HeadBoard focus observations; zero Home samples
admitted. Next prioritize different focus appearances and export parity, not more
same-style training. No shipped replacement or release/physical-device claim.

Latest learning result: [FOCUS-EXP-01](../reports/work/FOCUS-EXP-01/handoff.md)
completed four native-focus training arms independently of TTR.46 reviewed pairs:
37 training/9 validation, grouped by Settings screen. Warm+production-stretch
achieved18/18 validation decisions at0.85 (shipped CoreML7/18); scratch+stretch
also18/18 but learned later. This is tiny same-app validation, not a final-test or
release gate. No crop-default/model replacement. Next: independent Home/style
challenge data and runtime parity investigation; no automatic training loop.
This supersedes the pre-training bottleneck in the older snapshot below.

Latest native focus development evidence (2026-09-22): independent Settings-root
sweep produced 12 reviewed focused/unfocused pairs with production crops; shipped
classifier at0.85 yielded TP1/FN11/FP3/TN9. [Evidence](../reports/work/OS-FOCUS-02/handoff.md).
Capture is unblocked independently of TTR. Broader independent data partitions,
not another identical sweep, are needed before candidate training. Shipped weights
are unchanged; this is development evidence, not a model gate.

| Artifact | ID | Notes |
|---|---|---|
| iOS 5-class detector | `nativeui-ios-v2.0` | YOLO11n, mAP@0.5 = 0.935 CoreML / 0.968 `.pt`. Latency ~7.5 ms/image. |
| tvOS OS UI detector | `nativeui-tvos-v3.0` | YOLO11n, 25 trained classes, mAP@0.5 = 0.9822. Bundled as `NativeUIModel_tvOS.mlmodelc`. |
| Stage 2 focus classifier | `focus-ring-detector-v1.0` | MobileNetV4-Conv-Small, FDR-001. FP16 4.80 MB. Bundled as `FocusRingDetector.mlmodelc`. Torch test 270/270. Hard-neg n=0. |
| Detection API | `NativeUIDetectionRequest` | YOLO letterbox inference, OCR fusion, audit rules, device inference, optional FocusRing Stage 2. |
| Perception primitives | Frame similarity, change-ROI, text-anchor verify | Track 4, for TVTestRig to consume. |

Phases **0–5b**, **6** (5-class), **6d**, **6-gate (skipped)**, **6b-S / WP1 / E**, **6b-R-2 / R-3**, **6b-FD-01–04**, **7**, **8**, **9-1**, Track 4, extraction checklist: **complete.** See [`CompletedTasks.md`](../CompletedTasks.md).

---

## Not shipped

**2026-09-22 18:30Z updated Fixture:** both binaries changed, source852f341d
matches producer focus-handoff receipt. Local job675C0665 fails earlier reference
geometry: only container measured, both dialog buttons missing, fresh native
reference focus. Neither target transition reached; no completed bundle/intake.
Producer's other-simulator transition proof does not qualify this full capture
path. Postflight healthy/ownershipclear; geometry diagnostic request published
and read back, acknowledgment pending.
[Evidence](../reports/work/TTR-CHECK-20260922-1827/handoff.md).

**2026-09-22 18:08Z TTR smoke:** changed TTR comparator passes reference stage.
Fresh Fixture process has the same dialog-capable code hash. JobE5BCE43B fails
first target handoff: requested dialog_btn_0, actual native reference still focused,
fresh observations and complete geometry, stableMilliseconds0. Neither target
capture nor completed export/intake qualified. Postflight HTTP healthy,8 readiness
checks ready, ownership clear. Producer request published/read back, acknowledgment
pending. [Evidence](../reports/work/TTR-CHECK-20260922-1805/handoff.md).

**2026-09-22 dialog smoke:** native reference focus now verified and settled,
but job661FFE7C fails `telemetry_bracket:identityMismatch` before target capture.
Producer full-scene equality includes changing diagnostic counters/timers; passive
snapshots preserve focus/recipe/geometry while these change. Exact failed bracket
samples were not returned. Zero completed bundle; export/intake blocked. Fresh
postflight HTTP healthy,8 infrastructure checks ready, ownership clear. No retry
or reset. [Evidence/request](../reports/work/TTR-SMOKE-20260922-DIALOG/handoff.md).

**2026-09-22 17:26Z TTR/Fixture:** changed local binaries and matching dialog-repair
source receipt now observed. Eight infrastructure checks ready, local ownership
clear, HTTP healthy. Passive shelf still non_view/unmapped_item (294 samples),
but shelf is explicitly outside the dialog-only candidate scope. Next qualify the
changed two-button dialog through a bounded authorized smoke/export/intake; no
new capture occurred in this read-only check. Do not carry the producer's other-host
cleanup guard onto the locally clear target. [Evidence/status](../reports/work/TTR-CHECK-20260922-NEW/handoff.md).

**2026-09-22 16:29Z TTR/Fixture update:** new local app/companion and persistent simulator
remote interface observed; all eight exact-target infrastructure checks ready,
ownership clear. Installed Fixture bytes remain identical to the prior failing
artifact. Following Fixture relaunch, HTTP health is restored; fresh passive
telemetry (412 samples) still reports native focus non_view/unmapped_item on the
current media_shelf scene. No new capture or two-element smoke. Producer crop repair source matches its receipt;
offline corrected-crop replay is ready, exact parity still unqualified. This is
not a new storage regression or a block on independent native NUA work.
[Fixture follow-up](../reports/work/TTR-CHECK-20260922-1622/fixture-followup.md).

**2026-09-22 parallel acquisition:** direct HTTP/simctl runner, development-only
v1.4 consumer and existing runtime-crop/baseline integration delivered;38 Python
and92 Swift tests pass. Matching installed Fixture launched and reference PNG
captured/visually checked. First focused target fails `non_view/unmapped_item`;
independent TTR job fails the same native-identity prerequisite. Fixture responsive,
ownership clear. Zero eligible pairs;42-recipe pilot and genuine baseline not run.
This supersedes the endpoint-unavailable and screenshot-only bottlenecks below.
[Handoff and producer request](../reports/work/TVGEN/handoff.md).

**2026-09-22 05:49 UTC diagnostic:** updated local TTR responds; exact-target
infrastructure readiness passes and ownership is clear. Repaired companion source
matches the producer receipt, but prior Fixture endpoint8080 refuses connection.
Capture/export/intake were not run; screenshot repair is locally unqualified, not
newly failed. [Diagnostic feedback](../reports/work/SIM-DATA-01-02/readiness-20260922-0548/handoff.md).

**2026-09-22 01:39 UTC smoke:** native reference focus now resolves and settles,
but screenshot output fails Cocoa513/EPERM writing frame.png in TTR's app-managed
capture directory. Zero accepted rows; no export/intake or training. Postflight
Fixture responsive and ownership clear. This supersedes readiness-only status below.
[Failure and producer request](../reports/work/SIM-DATA-01-02/smoke-20260922-0140/handoff.md).

**2026-09-22 01:34 UTC runtime check:** updated TTR/Fixture and repair checkout
fd50a80 are present; all infrastructure readiness checks pass with ownership clear.
Idle Fixture has no native sample yet. A new bounded smoke is ready to be authorized,
but capture/intake and training readiness are not established.
[Evidence](../reports/work/SIM-DATA-01-02/readiness-20260922-0134/handoff.md).

**Offline perception acceptance (2026-09-22):** PER-01 evidence inventory and
PER-02/04/05/06 offline scopes are accepted after integrated review/corrections.
[Acceptance](../reports/work/PERCEPTION-ACCEPTANCE/handoff.md). All 44 supplied
screenshots were visually triaged; no real gold-label benchmark or training corpus
was qualified. Screenshot output access remains the last observed producer blocker,
not the previously resolved native-reference focus failure. No new training or promotion.

| Item | Why |
|---|---|
| 41-class iOS YOLO11m | Run 009 withheld-template holdout mAP@0.5 = **0.586** (DS-G8 ≥ 0.850). In-family val 0.991. |
| FocusRing v1.0 | Need ≥6,000 pairs and non-vacuous `light`/`highContrast` hard-neg (FOCUS-DET-05). |
| macOS detector | Phase 6c not started. |
| Unified iOS+tvOS model | Phase 6b-U not started. Keep separate models until every gate passes. |
| Badge/42-class expansion | Approved later milestone; 41-class release remains first. No enum/map/model change has shipped. |
| ScreenAuditKit contract/CLI | TASK-9-2 / 9-3 live in ScreenAuditKit, not this repo's remaining core path. |

---

## Current bottleneck

**2026-09-22 native OS lane:** approved independent XCTest Settings recording
passed: six directional inputs, seven hash-verified states/four distinct frames,
native focus visually aligned. No TTR/Fixture required. A development replay of
four native rows across four frames found 0/4 focused positives and 4/12 unfocused
false positives at 0.85 through shipped NUIAK preprocessing/model. This is a tiny
single-journey diagnostic, not general accuracy or training readiness. Native OS
admission/Home coverage can progress independently; Fixture repair remains open.
[Evidence](../reports/work/OS-FOCUS-01/live-20260922-0712/handoff.md).

**Parallel path approved, 2026-09-22:** [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md)
defines direct native tvOS Fixture/OS generation independent of TTR capture/export.
Direct software and runtime inventory are now delivered for review; no corpus is
qualified. Both acquisition adapters currently share the Fixture native-focus
identity defect. TTR desktop acquisition remains independent; iOS reconstruction
is unchanged. See [current evidence](../reports/work/TVGEN/handoff.md).

**Legacy FocusRing reuse warning (2026-09-21):** the 1,500-pair crop corpus is
byte-decodable but not requalified. An audit found 84 identical-pixel groups crossing
partitions despite zero shared seeds; all examples are dark and frame-bound label
evidence is absent. Historical 270/270 and empty-hard-negative passes are not clean
qualification evidence. Preserve shipped weights; no automatic replacement follows.
[Audit and corrections](../reports/work/EVIDENCE-AUDIT/handoff.md).

**2026-09-21 FocusRing update:** local simulator runtime/storage readiness passed,
but the clean two-element smoke failed `native_focus_or_geometry_unavailable:
sceneNotSettled`; no eligible pilot exists. Broad simulator collection remains
paused. [Smoke evidence](../reports/work/SIM-DATA-01-02/smoke-20260921/executed-smoke.md).
**2026-09-22 00:35 UTC follow-up:** the newly authorized updated-build smoke also
failed, now narrowed to `unresolved_focus`: both buttons measured, no missing IDs,
36 native samples but no resolved focus. Inline recipe import succeeded after
file import incorrectly surfaced `serviceUnavailable`. Postflight Fixture responds
and ownership is clear; no completed bundle or training data. TTR diagnosis/fix
requested; no automatic retry. [Latest evidence](../reports/work/SIM-DATA-01-02/smoke-20260922-0031/handoff.md).
Offline [launch preparation](Plans/FocusRingLaunchPreparation.md) is delivered for
review: runtime-exact crops, actual CoreML baseline adapter and frozen capture
planning. A tested crop-origin correction changes inference preprocessing, not
shipped weights; historical runtime metrics cannot establish its quality. No
training or promotion occurred. The older operational snapshot below is historical,
not a fresh Office/producer readiness check.

**TASK-6a-10** — full-frame fixture retraining for 41-class iOS. Ingest scripts are written and unit-tested. Coordinator IPC was resolved on 2026-09-18; the later live batch gate is `identity_preflight` / `identityUnavailable` until TVTestRig's adapters attest a shared HarvestIdentity. Office is occupied as of 2026-09-19; an authorized hardware run is a separate prerequisite. See [the recorded evidence](../reports/tvtestrig_feedback_2026-09-18.md). Do not retrain on empty sidecars or the model's own `*_result.json` predictions.

Office-independent work is defined in [ImplementationPlans.md](ImplementationPlans.md); dispatch state lives only in Tasks.md.

**Accepted offline foundation (2026-09-19):** H1 and the NUIAK software scopes of
P1-A, P2-A, P3-A, P4-A, P4-B, P5-A, and FR-A are accepted. This establishes fail-closed
consumer, evaluation, assembly, preflight, and FocusRing-alignment interfaces only.
It does not establish eligible pixels, a genuine producer bundle, live capture behavior,
or a candidate-model gate; those remain separately blocked in `Tasks.md`.

For the explicit iOS five-class → 41-class path, use the
[iOS platform tasks](../Tasks.md#ios-platform-tasks) and
[five-tranche delivery plan](Plans/iOSPlatform.md). Corpus recovery, offline toolchain
acceptance, and eligible synthetic baseline evaluation do not require Office. Live
fixture qualification is a separate input to the planned mixed-data candidate.

The [iteration roadmap](IterationRoadmap.md) separates software acceptance from data/model qualification. H1 producer-contract work, export/selector/preflight software, and recovery assessment are independently dispatchable. TVTestRig has a documented offline bundle-validator lane at inspected revision `586050e`; consumer compatibility remains to be implemented/verified, and passing offline integrity is not trusted capture evidence.

The accepted full backlog is defined as independent revision-4 [worker packets](ImplementationPlans.md),
including later models and separately owned consumer work. [DeliveryDecisions.md](DeliveryDecisions.md)
keeps 41-class first, moves badge to a versioned later model, prioritizes FocusRing then macOS
after DS-G8, and separates software/data/integration/model outcomes. Publishing these plans
does not mark any worker implementation, experiment or quality gate complete.

**Independent corpus blocker — TASK-DATA-01 (updated 2026-09-22 UTC):** All 2,000 historical synthetic test links remain broken, plus 10,543/11,984 training and 2,696/3,056 validation image links; labels and historical Run 009 mAP50=0.585669 remain intact. Missing files do not establish deletion cause. P0-C is executing a separately authorized native-only replacement, not historical recovery. Failed attempts exposed writer/schema drift, native-navigation geometry defects and repeated pixels; evidence is preserved. Corrected-source preflight passes eight native tests and independent validation of 346 sample pairs. The [r5 continuation](../reports/work/P0-C/reconstruction-configuration-r5.md) retains 7,500 verified completed r4 captures with explicit build lineage and collects 9,440 remaining slots toward the unchanged 16,940 target. Full capture/audit remains in progress, not eligible training data yet. `webContent` remains uncovered. [Historical availability evidence](../reports/dataset_availability_2026-09-19.md); [recovery plan](DatasetRecoveryPlan.md); [resumption evidence](../reports/work/P0-C/resumption-20260922.md). Baseline inference, frozen-suite acceptance and training still depend on completed corpus qualification; offline work is independent.

FocusRing v0.1 is independent of that bottleneck and is already bundled.

---

## Train / eval pointers

- Run log: [`ExperimentLog.md`](ExperimentLog.md)
- Doc index: [`README.md`](README.md)
- Fixture ingest format: [`FixtureBatchIngest.md`](FixtureBatchIngest.md)
- Phase streams: [`PhaseMap.md`](PhaseMap.md)
- FocusRing: [`FocusRingDetectorSpec.md`](FocusRingDetectorSpec.md)
- Provenance: [`../PROVENANCE.md`](../PROVENANCE.md)
