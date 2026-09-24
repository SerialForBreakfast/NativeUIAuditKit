# FOCUS-RECEIPT-01 — executed focus provenance

2026-09-23 source assessment and implementation contract. Parent: TTR report-only
visual verification. Tasks.md owns assignment/status. This records the additive
public API implemented at baseline7588a92 because the older consumer cannot recover
the information from observations alone. The contract below preserves its original
acceptance scope; this planning audit makes no further API change.

## Pre-implementation verified boundary

NUIAK HEAD b3f054657ff8163ae4631163dac4c75666a9cf75 plus local working changes.
NativeUIDetailedDetectionResult exposes observations, modality health and timings,
not which focus resolver ran. NativeUIDetectionRequest.performDetailed selects
FocusRing when enabled and load succeeds, otherwise the heuristic. The loader uses
try? and collapses missing model/load failure into nil. ML resolution skips invalid
crops/prediction errors with guard/try?. Health is available if some result is focused,
otherwise empty; it does not enumerate scoring failures. Both resolver branches
write focusScore/focusConfidence. Their presence or range cannot identify the backend.

FocusRing's focusScore is probability; focusConfidence is a separate model output
or distance-from0.5 fallback. Heuristic values have different meanings. Neither
should be treated as a universal calibrated probability. Existing0.85 FocusRing
threshold applies to probability, not indiscriminately to focusConfidence.

Local packaged tvOS manifest SHA256:
`470d9b76f495ec8783ea5301d2a7743d01a500e31529e7a54065923a09eb208c`.
Local FocusRing weight.bin SHA256:
`da22327015b7b8a58c43b64f7dd7e7a3abc962d0db8dae944e8eee9143d32027`.
These identify inspected disk resources, not the model executed by a particular
request. The weight hash alone is not a complete compiled-package identity.

Mandatory YOLO resource/manifest accessors still contain fatalError paths; a consumer
preflight can avoid known missing inputs, but is not a universal guarantee against
later corruption/resource races. Optional FocusRing load itself returns nil on absence
and throws on load errors, which request-level try? currently suppresses.

## Safe interpretation for TTR's older package pin

Keep `focus_backend=unknown` for the pinned/current public detailed API. Bundled
resource hashes, configuration intent and actual scorer execution are separate facts.
Report native agreement as uncertain when model provenance or complete scoring is
unknown; do not count heuristic/partial outputs as model agreement. No action veto,
control permission or training label follows from report-only verification.
This closes the question of what can truthfully be inferred today, not the feature gap.

## Implementation contract

**Inputs:** request/session implementations, FocusRingClassifier, model resource
loader, existing result Codable API and TTR's c25fa8fa adapter/receipt contract.
**Authority:** NUIAK source/tests/docs only. No TTR edits, model change, runtime
capture, training, promotion or packaging mutation.

1. Add optional versioned focus execution evidence to detailed results, with a default
   nil initializer argument and backward-compatible old-result decoding. Public types
   must be documented, Sendable and Codable; do not expose CoreML objects or local paths.
2. Record selected backend (CoreML/heuristic/not-requested/unavailable), fallback reason
   (disabled/missing/load-failed where observed), attempted/succeeded/failed counts,
   completeness and exact selection-policy version/thresholds. Distinguish choosing
   a backend from completing any inference. All-failed must not become empty success.
3. Per observation ID, record non-focusable skip, crop rejection, prediction failure,
   successful scoring, and decision/abstention. Keep raw probability separate from
   confidence and heuristic score. Nonfinite/out-of-range model output fails scoring.
   Unknown future roles remain explicit unsupported candidates, not fabricated negatives.
4. Bind a model content identity at the actual loader boundary and carry it through
   preloaded/session caches. A descriptor/name or package manifest hash is insufficient.
   Define a deterministic compiled-resource tree digest and verify load-bound bytes;
   custom/preloaded models without such evidence report identity unavailable, never
   substitute the bundled artifact identity. Avoid per-frame tree hashing.
5. Preserve observation results/selection policy for currently successful paths.
   Separate receipt instrumentation from any proposed change to failure/fallback or
   winner-selection behavior. A change in legacy failure semantics needs its own
   documented compatibility decision and tests, not an incidental refactor.
6. Expose recoverable model resource validation at the appropriate boundary so TTR
   need not depend solely on guessed Bundle paths before a fatal accessor. Preserve
   mandatory detector failure (never silently return empty detections). Keep this
   packaging/error-handling change separately reviewable from receipt wiring.
7. Publish an exact consumer migration example and software evidence. TTR's adapter
   remains its own assignment; pin a new package revision only after maintainer commits.

## Deterministic tests and acceptance

Wire clarification: version1 explicitly serializes attempted, successful and failed
prediction counts plus modelScoringComplete. These are derived from dispositions,
not caller assertions; decoding rejects inconsistent totals, unsupported versions,
duplicate observation IDs and invalid probability/disposition combinations. Old
outer results without a receipt still decode. Completeness means all supported
model candidates scored, not that any focus decision or model quality gate passed.

Inject a narrow internal scorer/loader boundary so unit tests do not require genuine
model execution for every case. Test classifier enabled/disabled, missing/corrupt model,
mixed scoring successes, all failures, invalid crop, nonfinite output, unsupported role,
no candidates, ambiguity, ties and non-tvOS. Every input observation must be accounted
for exactly once. Ensure receipt counts match dispositions and not merely final winners.

Test old Codable result decoding, new roundtrips, session preloading/cache provenance,
custom unknown-identity models, model-byte changes and path redaction. Frozen-success
fixtures prove instrumentation preserves existing decisions. Use existing model smoke
tests once at integrated verification, plus required offline build/tests.

Acceptance requires the real performDetailed/session paths, not only a new struct or
fake-backed helper; TTR can distinguish full CoreML scoring from fallback/partial
execution and identify when artifact identity is unavailable. Live TTR integration,
model accuracy and navigation qualification remain separately reported.

## Handoff and next action

Return changed files, exact API/receipt revision, compatibility matrix and tests,
model-identity algorithm and all unproven cases. Publish only the consumer consequence
to SMB. Implementation evidence is in [the migration and handoff](../../reports/work/FOCUS-RECEIPT-01/handoff.md).
The peer's older package pin remains without the receipt until it adopts a
maintainer-published revision; committed NUIAK software alone is not peer adoption.
The remaining source-pinned adoption work is [TTR-PROVIDER-01](QueueCompletion.md#ttr-provider-01).
