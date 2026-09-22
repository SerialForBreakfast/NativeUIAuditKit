# Consumer, maintenance and release packets

**Revision:** 4, 2026-09-19. Read the [common contract](../ImplementationPlans.md#common-execution-contract) and the assigned section. External packets are proposals until assigned in their owning repository with that repository's rules and filesystem authority. This NUA planning task neither edits those repositories nor sends messages. Handoffs from an external worker live in its authorized workspace and are referenced here; do not require cross-boundary writes.

## TV-I1 — Authoritative harvest identity coordination

**Current-contract amendment, 2026-09-22:** this historical proposal predates the
producer's non-attested source-description contract. At dispatch, reconcile the
current H1/producer interface and retire obsolete requirements before implementing.
Do not restore retired attestation or require it for simulator eligibility. Preserve
the distinction between requested target, observed runtime/instance, byte integrity,
native focus binding and approved data use. Descriptive source strings are not
authenticated identity. The current concrete focus repair is TV-FIX, not a replay
of this older lifecycle proposal. Retain TV-I1 only for evidenced remaining lifecycle
gaps under a separately accepted TTR assignment; closure requires source-backed review.

**Parent:** TASK-INTEGRATION-01 (external coordination). **Owner:** TVTestRig. **Inputs:** H1 source snapshot; HarvestIdentity.swift, FixtureHTTPHarvestLab.swift, IPCObservationHarvestCapture.swift and the coordinator/fixture session lifecycle in the producer repository. Current observed production adapters inherit identity accessors returning nil; verify at assignment.
**Scope:** producer lifecycle/HTTP/IPC contracts, adapter implementations, engine regression tests and producer docs; no live capture or weakened production gate.

1. Specify one authority for deviceID/runID/captureGeneration, its creation/expiry and reconnect behavior before adding wire fields. Reuse the actual coordinator device identity/generation; neither IP nor display label establishes identity. Both independently returned adapter identities must refer to the same authorized run.
2. Record exact wire/API changes and a test transcript for lifecycle begin, retrieval, generation change and cancellation. Implement genuine retrieval in both adapters; no caller-provided assertion or copied string masquerades as corroborated identity.
3. Keep requiresIdentity enabled in production; fail before recipe/focus mutation when identity is missing/mismatched. Revalidate across captures/reconnects; cancellation prevents further mutation. Preserve correlated frame provenance and bounded transport behavior.

**Tests/acceptance:** matching pair succeeds; nil/empty/zero generation, wrong device/run, stale generation/reconnect, cancellation and transport failure reject with preserved causes. Assert no capture/recipe/focus mutation before a successful gate. Publish wire changes and supported revisions for H1/P4 compatibility. Hardware qualification remains separate. **Next:** TV-I2 and later P4-L.

## TV-I2 — Reproducible producer compatibility artifacts

**Parent:** TASK-INTEGRATION-01 (external coordination). **Owner:** TVTestRig. **Inputs:** current engine/validator and H1 consumer expectations; no TV-I1 completion required for offline artifacts.
**Scope:** producer regression fixture generation, validator cases and source/version notes; no device access or consumer edits.

Maintain the smallest valid completed offline bundle with stable tiny non-user PNGs and explicitly unverified provenance. Export expected results with source revision/version/contract IDs. Include unknown version, incomplete/aborted receipt, altered bytes, traversal/symlink, malformed image, stale focus, split conflict, missing pair, duplicate artifact and invalid bounds cases. Preserve partial-directory publication semantics and documented bounds/limits.

**Acceptance:** artifacts/results are reproducible without a running app or Office; NUA can consume them under its own offline test workflow; a positive integrity result never asserts training eligibility. A format change ships matching case updates and migration note. **Next:** H1/P4-A compatibility feedback on each revision.

## SA-A — ScreenAuditKit contracts and native rules

**Parent:** TASK-9-2. **Owner:** ScreenAuditKit (currently nested in RA11y-AccessibilityGamification). **Inputs:** NUA NativeUIRecognizing/observations, architecture §12, consumer ScreenAuditContracts/Validation/Rules sources and its repository rules. Does not wait on new 41-class weights.
**Scope:** optional contract types, recognizer injection/evidence merger, rule reporting and deterministic tests. Coordinate package dependency with SA-B; define the smallest buildable shared dependency change in SA-A if required. No real inference required for acceptance.

1. Add optional uiElements with required/forbidden label+optional-region selectors and minConfidence default 0.75. Old contracts decode without the section and retain their old behavior. Validate confidence range, label names and referenced regions; malformed rules fail contract validation.
2. Inject a Sendable NativeUIRecognizing collaborator; no-op is default. Filter observations by confidence first. A required label absent everywhere yields missingUIElement; matching labels only outside the declared region yield uiElementBoundsViolation. A qualifying forbidden match yields unexpectedUIElement. Use deterministic matching/order; a qualifying required instance satisfies an existence rule rather than imposing an unstated count.
3. Map supported observation/audit evidence to missingUIElement (error), unexpectedUIElement/bounds/truncated/clipped/targetTooSmall (warning), inferredOSMismatch (info), honoring existing severity overrides. Do not fabricate findings without supporting evidence; point-based target-size needs reliable scale and platform-appropriate audit evidence.
4. No-op/notRequested skips native constraints; failed/unavailable recognition is an execution failure, not successful empty detections. Preserve existing text/visual rules and report formats compatibly. Sidecar precedence requires a matching image hash as architecture §12 specifies.

**Tests/acceptance:** old/new Codable round trips, default/minimum confidence boundaries, invalid labels/regions/confidence, multiple matches, absent vs outside-region behavior, forbidden match, no-op, failed/unavailable recognizer, severity overrides and unknown scale. Use deterministic fakes, not shipped models, in ordinary unit tests. **Next:** SA-B.

## SA-B — Dependency bridge and native CLI mode

**Parent:** TASK-9-3. **Owner:** ScreenAuditKit. **Inputs:** SA-A injection contract and NUA package/resources. **Scope:** consumer Package.swift/dependency policy, ScreenAuditCLI parser/wiring and tests; no external publishing or training.

Add NUA through the consumer's approved dependency policy; machine-specific paths do not enter library code. Add `--native-ui none|coreml`, default none; reject unknown/missing values using existing CLI argument behavior. Route explicit coreml to the real recognizer; none retains no-op. Missing models or required recognition failure in coreml mode produce a clear error and exit 1. Keep default CLI/report behavior compatible and preserve existing non-native failures.

**Tests/acceptance:** default/none/coreml routing with injected fakes, missing/invalid flag value, unavailable resources, recognition failure, report stability and exit codes. A separately assigned smoke may exercise real models, but unit tests stay offline/deterministic. **Next:** consumer owner release review; no 41-class gate dependency.

## DOC-A — Evidence-based documentation and skill maintenance

**Parent:** TASK-DOC-01. **Owner:** NUA. **Inputs:** K-07/08/10, actual production inference and packaged metadata; skill-creator guidance for skill edits. **Scope:** Research/AGENTS/docs and protected skills only with required filesystem authority; no model resources or training behavior change.

Correct blanket historical scaleFill/eval_map advice so YOLO uses the shipped letterbox path. Clarify prediction-file class counts are diagnostics, never annotation truth. Reconcile FocusRing artifact modelID/versionString with qualification milestone terminology after inspecting metadata. Correct stale phase/section references and route workers to current packets.

**Acceptance:** every correction cites source evidence; no claim of new model qualification; changed links/skill frontmatter validate. If a skill path is protected, complete permitted docs and present the exact patch for the approved edit workflow; do not evade permissions. Do not reread or edit unrelated skill directories. **Next:** updated knowledge references for affected assignments.

## REL-A — Qualified-model release evidence

**Parent:** TASK-DIST-02 (or the selected later model release). **Owner:** NUA. **Inputs:** accepted model-specific quality/export evidence; architecture API and model manifests; provenance/license policy. **Scope:** release documentation/manifests/tests and staged in-project release evidence; no git writes or automatic model replacement.

Prepare exact candidate IDs/hashes, declared taxonomy, input/output/preprocessing metadata, provenance/license records, change notes, reference-report hashes and backward-compatibility results. Check model descriptor/resource names agree. Run required offline package checks and standalone-model-package verification with all outputs/caches confined to project. Inspect proposed release file set for raw weights, datasets and machine-specific paths.

**Acceptance:** gates trace to immutable artifacts and no missing hardware/export evidence is hidden. Existing API compatibility and model loading pass; release inventory contains only intended resources. Later FocusRing/badge/macOS/crop/unified tasks do not block a qualified 41-class release. **Next:** maintainer REL-B.

## REL-B — Maintainer promotion and tagging

**Parent:** TASK-DIST-02. **Owner:** maintainer. **Inputs:** REL-A and selected qualified artifact, reviewed exact destination/recovery plan. **Scope:** explicitly authorized promotion and maintainer git/tag operations; never automatic from plan acceptance.

Verify candidate hash immediately before promotion; preserve the previous recoverable model and manifests. Replace only reviewed resources, rerun loading/compatibility checks, and record released versions/report hashes. Maintainer commits and tags according to project policy. Failed validation retains or restores the verified prior artifact through the approved recovery procedure; no ad-hoc deletion/reset.

**Acceptance:** intended artifact is packaged/loadable, release notes/manifests agree, maintainer records actual tag/version. Do not invent a release version until assigned. **Next:** update CurrentState/CompletedTasks after evidence, not before.

## HIST-A — History-remediation decision package

**Parent:** TASK-DIST-01. **Owner:** NUA architect/maintainer. **Inputs:** existing provenance/redaction records and read-only relevant history. **Scope:** bounded assessment and instructions only; no history rewrite, commit or force-push.

Identify affected refs/artifact categories without reproducing sensitive values in reports. Describe contributor/clone impact, verified recovery backup requirements, remote coordination and exact proposed maintainer procedure. Keep history remediation separate from feature/model release work. Record defer/proceed decision only when given by maintainer.

**Acceptance:** actionable impact/recovery/migration assessment with no sensitive-data amplification or git mutation. A later explicit authorization is required for execution. **Next:** maintainer decision; independent work continues.
