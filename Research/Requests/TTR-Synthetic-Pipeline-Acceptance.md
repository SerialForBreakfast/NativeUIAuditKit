# Synthetic pipeline — producer/consumer acceptance addendum

2026-09-30 PDT. Proposed contract clarification, not implementation or live proof.
Parent request: `nuiak-20261001-semantic-export-fixture-v1`.
This extends that request; it does not create a second capture system or assignment.
TTR must acknowledge supported/missing items and exact wire examples before both
sides can call the contract agreed. Existing receipt and ownership rules still apply.

## Outcome and ownership

One bounded approved campaign should generate varied UI, record measured annotations,
deliver immutable evidence, pass automated consumer QA and prepare an eligible
training assembly without chat per press or human drawing per rectangle.

| Boundary | TTR / Fixture owns | NUIAK owns | Acceptance evidence |
| --- | --- | --- | --- |
| Plan | Supported recipe/renderer/asset ancestry and capabilities | Coverage priorities and source-group role reservation | Exact accepted plan; unsupported requests explicit |
| Render / traverse | Measured geometry, native focus and scene inventory; input receipts | Required geometry/focus semantics | Frame correlation and actual visible variation, not requested values |
| Job lifecycle | Bounded capture, progress, cancellation, recovery and export | Submission/resume bookkeeping within approved scope | Repeated submission/reconnect does not duplicate work |
| Bundle | Originals, native records, manifest and final artifact descriptors | Safe receive, hash checks and receiver receipt | Complete immutable package resolves every reference |
| Annotation / crops | Producer findings and field provenance | Normalization, optional proposals, production crops, exception review | Every member disposition accounted; no guessed focus |
| Corpus / training | No consumer admission or training trigger | Split isolation, admission, feature cache, approved run, evaluation | Frozen assembly and exact approved run contract |
| Feedback | Fix producer defects and version corrected exports | Return precise defects or coverage requests | Same evidence identities; no blanket recapture |

## Operational additions to the original request

These specify behavior, not invented CLI names or JSON fields. Reuse existing job,
artifact, CLI/MCP and app-owned access contracts wherever they already satisfy them.

1. **Machine-readable preflight.** Describe supported schema/recipe versions,
   native field availability and geometry roles, scene capabilities, target/runtime
   and permissions. Validate the plan before dispatch. Return actionable unsupported
   or setup-required reasons, estimated capture/storage scope and effective limits.
   Capability availability is not live focus/capture qualification.
2. **Plan identity and replay-safe submission.** Accept a consumer correlation key
   tied to the exact plan/target. Repeated submission returns the existing job or a
   clear conflict, never silently starts another capture. Changed content requires
   a new identity. Consumer reservations are echoed, not invented by the producer.
3. **Explicit lifecycle.** Map existing states to queued/running/partial/completed/
   cancelled/failed with a durable job ID, progress, reason codes and remaining
   targets. CLI/MCP reconnect can query an existing job without replaying inputs.
   Define exactly which operations are safe to retry. Resume only uncompleted work
   when evidence/target generations permit; ambiguous actions are not auto-replayed.
4. **Budgets and cancellation.** Enforce count/time/retained-byte/free-space limits
   and ownership loss. Cancel stops further dispatch, preserves completed evidence
   and publishes a partial manifest with explicit unattempted targets. Recovery must
   not depend on silently resetting a device, deleting originals or renewing a lease.
5. **Complete export boundary.** Advertise an artifact only after finalization;
   include schema/build identities, exact filenames/sizes/hashes, member count,
   total expanded bytes, manifest and all referenced images/native evidence.
   No producer-machine absolute paths required by the consumer. Publish a precise
   completed/partial/failed export result. Partial bundles may support diagnostics
   but must never masquerade as a complete campaign.
6. **Export independent of capture.** A failed transfer can retry the same retained
   immutable export without another UI traversal. Local TTR and remote TTR supply
   equivalent bundle semantics; storage paths/transport endpoints are deployment
   details, not different annotation contracts. Existing verified handoff is enough;
   external disk/SMB replacement work is not a prerequisite.
7. **Correction lineage.** Corrected annotations or metadata get a new bundle
   identity with superseded member references and reason. Preserve original bytes.
   NUIAK must invalidate dependent crops/features/assemblies when their inputs change;
   a receipt for old bytes cannot acknowledge the new bundle.
8. **Structured feedback.** NUIAK returns receipt separately from semantic acceptance,
   with bundle/recipe/frame/control IDs, error category, expected versus observed
   condition, affected counts and disposition. TTR distinguishes fix/re-export from
   new-render-required and unsupported. No raw private content in shared status.

## Annotation completeness and scale

Keep required distinctions from the original request: actual native input focus,
assistive focus and selected state; measured wrapper/body/label geometry; layout
and capture intervals; stable local identity; clipping/occlusion; complete versus
partial inventory. Include unfocused visible competitors, not only the active item.
Non-focusable/decorative elements need an explicit exclusion classification where
known. Unknown focusability stays unknown; it does not become a negative label.

Document multi-focus scope and zero-focus/transition cases; do not force exactly one
positive onto a broken/ambiguous frame. Controls partially outside the viewport
retain unclipped and visible geometry when available, with a documented inclusion
policy. Geometry is not OCR glyph bounds. No semantic/OCR inputs enter visual-only
model evaluation by accident.

Recipe provenance includes actual component/layout ancestry, OS/build/locale,
font/dynamic-text configuration and asset identity. Assets need a permitted-use
record for corpus use; availability or synthetic composition is not a license.
Requested seeds are reproducibility inputs, not independent sources or a guarantee
of identical pixels across OS changes. Treat renderer/OS changes as new review
boundaries, not reuse of old recipe QA without checking.

Review burden: recipe-level sheets for new/changed designs, stratified batch sampling
and exception review. NUIAK measures reviewed frames/minutes and defect categories;
there is no blanket promise of zero human QA. Never require manually tracing every
native key or control after its producer instrumentation is qualified.

## Concrete first delivery and tests

**Before a new build:** TTR sends the versioned schema plus representative valid,
partial and invalid example bundles, capability mapping, command/result examples
from the real interface, field meanings/units, compatibility policy and owner/order.
Examples can use retained approved evidence; offline generated examples must say so.
Consumer adapter development can proceed once this contract is agreed, without
waiting for runtime qualification. No executable commands are inferred from prose.

**First runtime proof:** supported artwork, buttons, rows and selected-parent tabs
through the same export/import path, plus keyboard support or an explicit gap.
Exact target, recipes, counts and budgets are bound before dispatch. Hover Text,
braille, arbitrary third-party AX and a huge corpus are not prerequisites.

| Test | Producer evidence | Consumer check |
| --- | --- | --- |
| Valid settled pair / full scene | Native brackets, measured geometry, original frames and competitors | Import, labels, complete accounting and production crop parity |
| Missing field / partial tree / stale generation | Explicit incomplete reason, no fabricated field | Diagnostic/quarantine disposition; no silent training admission |
| Selected parent, duplicate label, no-op | IDs, independent selection/focus and action receipt | Correct joins, no label-string matching or intent-derived focus |
| Malformed geometry / changed bytes | Invalid example or versioned correction | Reject unsafe bounds, hash mismatch, dangling IDs/references |
| Disconnect / repeated submission / export failure | Durable job and immutable completed members | Resume without duplicate capture or duplicate admission |
| Cancellation / disk or time limit | Terminal partial accounting | Accepted + rejected + excluded + blocked + unattempted reconcile |
| Unsafe archive / unsupported schema | Compatibility examples | Reject traversal, links, duplicate paths, oversized expansion and unsupported required semantics |
| Renderer/OS change | New provenance/version and compatibility result | Recheck recipe QA and invalidate stale derived artifacts |

Producer software tests, live compatibility, consumer acceptance, data eligibility
and model quality are separate results. A test bundle does not establish live proof.

## Automation boundary

TTR delivers evidence, not an instruction to train. NUIAK can automate ingestion,
checks, review preparation and assembly within approved scope. Unattended encoding/
training requires an explicit policy bound to data roles, validated versions,
run/model configuration, budgets and stop conditions; current run-approval rules
remain until the maintainer approves such a policy. Delivery never silently grants
training, model promotion or navigation authority. This request installs no monitor.

## Requested response — reply against the parent request

For each item provide existing / planned / unsupported, implementation owner,
evidence/interface reference and expected delivery order. First return:

1. Exact schema and valid/partial/invalid samples; identify required versus optional
   fields and legacy compatibility. Provide now if possible, before the build.
2. Existing job/submit/status/cancel/resume/export operations and replay semantics.
3. Bundle finalization/receipt/correction contract, portability and resource bounds.
4. Source/layout/asset ancestry for a new training campaign, preserving matched24.
5. Remaining supported-family blockers; keep optional keyboard/Hover Text gaps separate.

Local work can continue while the build is pending: SYN-04 coverage planner and
reservation/duplicate audit; offline existing-format intake/recovery tests; then
native admitted-corpus assembly/feature-cache integration preparation. No speculative
TTR wire adapter, training or fresh device activity is included in this audit.
