# Office FocusRing: smoke, qualified data, one candidate

Revision 2, 2026-09-21. Highest available dispatch priority. [Tasks.md](../../Tasks.md)
is the sole ownership/status queue. Preserve active workers and simulator evidence;
simulator execution is paused until explicit user release of that restriction.
This plan authorizes publication of one smoke request, not broader capture or training.
Use the [worker workflow](../WorkerWorkflow.md) and mandatory pre-code reading.

## TVTestRig build, signing, and fixture-job preflight

Use the TVTestRig skill package installed at
`.agents/skills/tvtestrig/` as the operational authority for the producer
interface. An installed signed TVTestRig app is the normal path: use its matching
bundled helper and do not request a development team, source rebuild, or re-signing
as generic recovery. A source build is only appropriate when explicitly requested
or when resolving a diagnosed signing setup failure.

For an explicit source build, TVTestRig's checkout must select the maintainer's
Apple Team with `Scripts/configure-signing.rb`; its ignored
`TVTestRig/Config/LocalSigning.xcconfig` is the only local signing input. Do not
edit the tracked Xcode target team setting, guess a Team ID, alter credentials, or
reuse active DerivedData. Build in a fresh project-local work directory with a
verified locked package cache, perform TVTestRig's post-build signature check, and
launch only with separate authorization and no conflicting running owner.

The first helper check is the running app's exact copied help command. If it aborts
with exit 134 under an agent sandbox, retain stdout, stderr, exit status, and build
identity, then request one identical help-only invocation in normal host execution.
Do not treat that abort as evidence of an Office, pairing, or package failure; do
not rebuild, re-pair, modify sandboxing, or replay a device command. A successful
help check permits only separately authorized read-only readiness checks.

For the independent staging gate, current TVTestRig builds use
`fixture prepare --recipe FILE` to transfer a recipe over IPC and return
`storageReady` plus a job ID. NUIAK must not write into TVTestRig's container or
change `HOME`. After separate capture authority and fresh coordination, the producer
may run that prepared job; only a completed job may be exported to a new, writable,
non-symlink destination and then passed to P4-L validation. Partial export folders
are never ingested. These mechanics do not grant capture, navigation, or training
authority.

## P4-L — Bounded physical smoke and NUIAK intake

**Producer owner:** Sillycon TVTestRig agent after acknowledgment in its own queue.
**NUA owner:** architect for request; intake worker assigned after bytes arrive.
**Inputs:** current physical app/helper/Fixture, fresh Office readiness, supported
producer format and accepted consumer validation. Source descriptions are not attestation.

1. Publish the NUA-owned request for one Office smoke. It overrides the earlier Office
   release only for this operation. Require actual target/endpoint verification and fresh
   control/capture checks; pairing or HTTP responsiveness alone cannot prove capture works.
2. Use the existing live-smoke action-dialog recipe: two elements, high_contrast,
   regular density, seed 7, step 0. Do not run the whole recipe directory.
3. TTR creates one new project-local output destination. Limit the operation to ten
   minutes from preflight start; arrange owned cancellation and cleanup, preserve
   ambiguous/partial output, and stop on failed preflight. No automatic retry or repair.
4. Report recipe, producer/build and receipt/index hashes, expected/captured/accepted/
   rejected counts, bundle location, completion validation and post-cleanup Fixture health.
   Release only this operation's resources; do not take over unrelated sessions.
5. Keep original bytes on TTR. Confirm a separate transfer route; default is maintainer
   copy into gitignored `dataset/tvos_captures/office/<bundle-id>/`. Verify ignore rules
   and source/destination hashes. No images, labels or weights on the status share.
6. NUA checks every indexed member, schema/version/path/hash/image/annotation, dimensions,
   per-frame boxes/focus labels, split and source context. Inspect both elements visually;
   verify 16% expansion and 256×256 extraction through actual consumer entrypoints.

**Acceptance:** completed genuine bundle, limited revision-specific P4-L compatibility
and image/annotation alignment report. Separate integrity, source assurance and data-use
eligibility; parser success cannot approve training. No full-corpus/model gate passes.
**Failure cases:** wrong target, capture unavailable, partial receipt, corrupt/altered
bytes, unsupported versions, stale focus, geometry mismatch and unhealthy teardown.
**Blocker/resume:** peer acknowledgment, fresh readiness, completed bundle or confirmed
transfer; exact missing input recorded, no remote shell workaround.
**Evidence:** `reports/work/OFFICE-FOCUS-SMOKE/` coordination and P4-L intake report.
**Next:** FR-B development pilot after separately authorized harvest.

## FR-B — Physical visual-focus development pilot and corpus

**Inputs:** accepted P4-L intake, reviewed physical consumer behavior, pinned recipes,
explicit Office harvest window/authority. **Scope:** fixture-only capture and validation,
development baseline inference only when assigned. No simulator or semantic alignment work.

Before capture, reconcile the accepted ADR-0007 separation: the visual corpus does not
require the VoiceOver alignment matrix. Existing matrix validator/tests remain supported
for a separately assigned semantic dataset; present alignment metadata must still validate.
Unknown VoiceOver state stays unknown. This changes no visual quality or hard-negative gate.
Reuse reviewed grouping/crop improvements only with physical-source regression coverage;
do not relabel Office as simulator data or reopen accepted software wholesale.

1. Freeze 36 development recipes: six required scene families × light/dark/high_contrast
   × seeds 101/102, with exact source-supported configuration/element limits and hashes.
   The smoke, pilot and related variants/content are development-only; exclude them from
   final validation/test membership. Report unsupported targets instead of silently dropping.
2. Qualify pilot capture and benchmark the actual shipped FocusRing artifact by hash.
   Report per-scene/theme/control accuracy, FPR/FNR, precision/recall at 0.85 and
   hard-negative support; failed inference is not an unfocused prediction.
   Record crop-parity evidence and targeted training coverage before scale-up.
3. Freeze a versioned scale catalog and deterministic 80/10/10 recipe-group partitions
   before capture. Record split algorithm/seed and exact membership. Keep all related
   pairs, seed variants and duplicate content together; no post-capture split moves.
4. After scale-capture authorization, use resumable batches ≤100 recipes with unique
   destinations, explicit timeouts and postflight health checks. Validate every completed
   batch before accepting counts. Resume only missing groups after inspecting cleanup.
5. Require ≥6,000 distinct pairs: gridMatrix ≥2,000, mediaShelf ≥1,500, settingsList
   ≥1,000, actionDialog/heroCarousel/focusMaze ≥500 each. Light and highContrast each
   ≥20% of actual gridMatrix and mediaShelf totals. Require ≥100 held-out hard negatives,
   all four light/highContrast × imageView/collectionItem combinations populated.
   Counts require verified unfocused labels, not caller flags or duplicate crop inflation.
6. Freeze raw/derived membership, hashes, fixture-label provenance, crop lineage,
   rejection reports, retention owner and recovery evidence. Report remaining deficits;
   do not lower quotas or fabricate labels. Stop when Office is reclaimed or state uncertain.

**Acceptance:** valid leakage-free corpus, complete quotas, reproducible development
baseline, untouched final evaluation groups and physical-use eligibility evidence.
**Tests:** physical-source fixtures, repeated seeds within/across splits, frame-specific
geometry, duplicate pairs/content, missing labels, prediction-derived labels, false source
claims, empty hard-negative strata, output collisions and invalid/partial batches.
Code extensions require focused tests plus repository-required offline build/test checks.
**Next:** FR-C only after corpus acceptance and explicit training assignment.

## FR-C — One candidate, export, then application comparison

Use the existing [FR-C contract](ModelsAndHardware.md#fr-c--focusring-candidate-and-export-qualification).
Log before launch, pin local initialization and fresh run state, use isolated outputs:
vendored MobileNetV4, 30 epochs, batch 64, LR 3e-4, HFlip-only first candidate.
No downloads, automatic retraining or production-resource overwrite. Select checkpoint
using validation only; compare candidate and shipped model on identical untouched test data.

Retain all six gates: accuracy ≥99%, unfocused FPR ≤0.5%, focused FNR ≤1%,
precision/recall at 0.85 each ≥0.98, non-vacuous hard-negative FPR ≤0.5%.
Report each required hard-negative stratum. Trace-export FP16 CoreML, verify score/
decision parity and ≤5 MB package. Failure produces diagnosis and separately reviewed next work.

After candidate acceptance, separately authorize a TTR-owned bounded Office comparison:
freeze identical frames/candidate proposals and reachable start/goal scenarios before runs,
explicit model selection with artifact hash, unchanged settings and fixed action/time limits.
Report focus-selection accuracy, wrong/no-focus decisions, target-reaching rate, action
counts, latency, support and invalid trials. Telemetry grades outcomes, never supplies
model decisions. Separate classifier-only results from detector/proposal/navigation failures.
Verify healthy cleanup and peer intake. No model promotion follows automatically.

## Handoff and boundaries

Every stage reports software verified, data eligible, integration qualified and model gate
passed separately, with commands, exit codes, artifact hashes, scope and next action.
Keep success/rejected/invalid trials distinct. No public API changes are assumed.
Status share contains only coordination; publication/readback is not peer acknowledgment.
No SSH, service resets, Settings mapping, VoiceOver dataset expansion or simulator execution.
