# EXT-CAP-01 consumer acceptance checklist

2026-09-27. Reviewed the user-provided EXT-CAP-01 plan and the actual
`scripts/photos_focus_pilot.py` implementation / existing
[CLI contract](../PHOTOS-PILOT-01/cli-contract.md). This is a semantic mapping,
**not a wire schema or qualified adapter**. No new transport is implemented.

Shared producer revision1 was also read on2026-09-28 at~02:25Z:
`tvtestrig/ttr-external-capture-plan-20260928T012443Z.md`,15,547bytes,
SHA256 `113ee8fb44cf1f2a85ec6f2e2956eb65ae1208b7617a280d2cba8710951a4cf0`.
Its response acknowledges the original request but asks for consumer compatibility.
**Conflict:** revision1 still proposes10min/two frames and a `maximumFrames` consent
field. The newer user-provided plan specifies30min default, duration-only approval,
no frame-count permission limit, persistent trust and restart-invalidated grants.
Reconcile the shared plan to those newer decisions before implementing consent.
Storage/backpressure and the bounded Photos pilot remain independent limits.
The shared descriptor specifies artifact/operation/observation IDs,byteCount,SHA,
width/height and an opaque `provenanceReference`; it does not define the referenced
observation/session schema or verified receipt. An opaque reference is not enough
to bind importer fields. No transport/bootstrap compatibility pass is claimed.

## Producer → consumer contract

| Evidence | Specified by EXT-CAP-01 proposal | Existing importer needs | Remaining responsibility |
|---|---|---|---|
| Original image |Immutable pixels, artifactID,SHA-256,bytes,dimensions; resumable verified delivery|Original up-oriented PNG≤32MiB; local relative path and hash; decoded size matches observation|TTR specify versioned descriptor, MIME/orientation and byte identity; client deliver atomically into recipient-approved local storage; NUIAK reverify|
| Observation |Observation identity and provenance; freshness/readiness and capture recheck|Successful schemaVersion1 `observe capture` envelope with `data.observation._0`, id,providerID,sourceDeviceID,dimensions,mimeType,orientation,outputWritten,freshness,capturedAt|Plan does not specify this envelope or an equivalent new schema. Deliver raw observation bytes and a representative receipt; do not synthesize a legacy successful response|
| Time |Monotonic grant expiry; captured provenance unspecified at field level|Captured wallClock seconds since2001 plus monotonic nanoseconds; freshness age≤1000ms, confidence exact/estimated|Specify epochs/units, clock domain, session/restart semantics and per-artifact timestamp binding; no Unix/2001 guessing|
| Target/source/session |Exact target/source mapping,owner,session,generation checked at capture|Capture index targetID,sourceDeviceID,sessionID,operator,sourceBindingReference; session status `data.status._0`, selectedDeviceID,sessionID,connected,idle,queue0|Readiness alone is not atomic image binding. Specify how each operation/artifact binds client/grant/session/target/source/generation, and deliver compatible session evidence or assign explicit consumer version update|
| Geometry |Dimensions; native Photos telemetry may be absent|Per-frame original-image top-left pixel control bounds after review; focused/unfocused/unknown|TTR must not invent native boxes/labels. Human confirms bounds for each state; preserve real native geometry separately with coordinate convention if present|
| Labels/review |Human labels separate from native; diagnostics until admission|Named reviewer,time,reference,image hash,Photos/content/settled confirmation; same reviewed control across two states|NUIAK proposes numbered overlays; human explicitly confirms. Ambiguity/conflict blocks examples. Approval to capture is not approval of labels|
| Verified receipt |Client auto-retrieves,hash-verifies; compact descriptor/local receipt; ACK|Original image and metadata files available under project root before import|Specify receipt version,recipient identity,operation/request digest,artifact list,byte/hash verification status,metadata hashes and commit/ACK semantics; never expose credentials or require producer container paths|
| Recovery/cleanup |Dedup client/opID/request digest; query unknown outcomes; separate finish stages; owner-only cleanup|Preserve partial/duplicate evidence and complete disposition accounting|Specify whether pending downloads/ACK/finish remain available after grant expiry/revocation/restart. No fresh capture from a retry. An unknown cleanup state does not establish target availability|

TTR's no-frame-count-limit **permission grant** is compatible with the Photos
pilot's consumer limits:≤60 frames,≤20 pair attempts,≤3states,≤45min capture and
2GB storage reserve. These are separate layers. The30min default grant may expire
before a45min pilot; choose an appropriate duration in the human approval or obtain
an explicit extension. Never silently extend a grant or silently truncate imports.
The2GiB producer spool is also separate from consumer free-space reserve.

## Responsibility checklist

**TTR producer/client owns:** authenticated pairing and human grant; exact target
and resource ownership; atomic capture provenance; original-byte transport;
bounded persistent operation/receipt state; query/resume without recapture; explicit
finish/cleanup outcomes. Deliver matched app/helper/client/protocol build identities,
versioned schema and an example descriptor + observation + session + verified receipt.
The planned packaged client must work through the actual NUIAK agent integration,
not only a standalone terminal demo. No terminal relay/manual SMB happy path.

**NUIAK owns:** recipient path policy and independent byte/hash checks; explicit
mapping from an inspected producer schema to local import requirements; existing
import/review CLI; numbered evidence, duplicate/missing accounting; per-frame review
record; production-crop QA and development-only manifest. Keep all raw originals and
raw producer metadata immutable. No source observation becomes native truth merely
because transport authenticated its sender.

**Human owns:** fingerprint check and grant (client,target,duration,recipient),
non-sensitive Photos navigation, exclusive-use confirmation, per-frame bounds/states
and content review. No agent remote-button inputs in this workflow.

## Acceptance path and gates

1. **Verified local delivery.** Hash/size match, exact expected artifact list,
   correct recipient and target/source/session binding. Safe relative local paths,
   no symlink/traversal, no credentials. Existing captures remain pending receipt.
2. **Inspected schema mapping.** Exact producer schema and representative receipt
   are prerequisites to a separately assigned adapter. If TTR retains the current
   envelopes, construct the existing capture index from their actual values. If it
   changes them, version and test the mapping; do not fabricate old session evidence.
3. **Existing import CLI.** `photos_focus_pilot.py import --input <local-index>
   --output <fresh-project-diagnostic-root>` preserves raw bytes, produces numbered
   frames and a review template. Check counts/dispositions, not just process exit0.
4. **Human confirmation.** Numbered frame IDs and image hashes; original-coordinate
   bounds separately for each focus state; known state or unknown; visible competitors;
   reviewer/time/reference. Genuine native disagreement blocks that example.
5. **Existing review CLI.** `photos_focus_pilot.py review --intake <intake.json>
   --review <confirmed-review.json> --output <fresh-project-crop-root>` uses production
   makeCrop16%/256 with existing item/pixel limits. Review overlay/crop sheets.
6. **Diagnostic manifest only.** Complete accepted/rejected/blocked/duplicate counts;
   partition development,trainingEligible=false,independentEvaluationEligible=false,
   modelGatePassed=not_assessed. Capture success and label review do not pass training
   or independent-source gates. No final-challenge conversion of exposed screens.

Adapter tests later should cover actual schema/version drift, wrong binding,
truncated/chunk-reordered/hash-mismatched transfer, lost ACK/duplicate operation,
expiry/restart pending delivery, importer membership preservation and existing
negative dispositions. Reuse the completed importer tests rather than reimplementing
an annotation app or duplicating its full test suite now.

Two-host Simulator transport success is necessary but not physical Photos acceptance.
Final qualification must use the actual consumer → Sillycon build → bounded Office
Photos receipt → import/review/crop/cleanup chain under separate authorization.
Measure the proposed60s cold/15s returning/2s warm-p95 targets as distinct stages;
do not claim them from source code, offline tests or the earlier manual capture.

## Current disposition

Two Office frames are operator-confirmed to show different focus states, but their
original bytes/metadata have not been admitted here: **pending consumer receipt;
zero admitted Photos pairs**. This tranche requests neither recapture nor transfer.
EXT-CAP-01's wire schema/example and live compatibility remain unverified. The
precise next producer consequence is to include the versioned metadata/receipt
contract above with its development handoff; then assign the consumer adapter.
Independent-source review can proceed without this transport or Photos telemetry.
