# PER-06 screen/row identity benchmark v1

Experimental offline matching of **supplied** OCR/detection observations, not new
OCR inference, route storage, navigation, training or globally stable identity.
IDs are meaningful only inside a registered journey group. Truth is used after
prediction, never to build query labels or select candidates. Reference identities
are explicit registrations, not inferred from the query's expected outcome.

## Implementation decision

Reuse production `TextAnchorVerifier.evaluate` through a package-only `AnchorTool`.
Change only that existing method's access from internal to `package`; no new public
symbol, no behavior change and no duplicate anchor algorithm. The diagnostic tool
accepts independent OCR regions/requirements and emits actual matches/status.
The Python matching/evaluation CLI owns identity policy, not the shipped library.

## Corpus and policy

`identity-benchmark-v1` contains corpusID and 1–128 cases. Each case: id, group
(complete journey/related captures), partition (development/validation/test),
sourceKind (test-only/simulator/physical), sourceReference, labelOrigin
(synthetic-generator/reviewed-human/fixture-callback), reviewReference,
scenario (scroll/changed-value/repeated-label/localization/hidden-row/overlay/
stale/ordinary/ambiguous-screen/missing-anchor), references (1–16), query, truth,
and optional cachedScreenID/cachedEpoch. Reference IDs and row IDs are opaque
journey-local identifiers; query observation IDs cannot serve as logical IDs.

Each reference: screenID, locale, required/optional/forbidden anchor arrays,
titleRegion (unit top-left xywh), snapshot, rowIDs (observation row ID → registered
logical row ID; unique per screen). References are unique by (screenID, locale):
reviewed localized registrations may share the same logical ID, but unknown locales
are never automatically translated. Snapshot: observationID, contextEpoch, locale,
capturedMs, observedMs, status (success/failed/unavailable), texts (≤256), rows
(≤64), overlays (≤16), evidenceKind (test-only/recorded-observations). OCR text:
id, text, confidence, bounds. Row: id, confidence, bounds. Overlay: confidence,
bounds. All boxes unit top-left xywh, finite and contained. Inputs retain original
frame hashes when available. Non-test snapshots require an image object: path,
sha256, width, height. All snapshots bind adapterReference; recorded observations
also bind imageSHA256. Verify PNG bytes, decode, dimensions, no symlink/escape and
≤32MiB/16M pixels. Reported source/reviewer/hash never authenticate provenance.
Failed/unavailable query is distinct from successful empty OCR; neither matches.

Truth: expectedScreenID (registered ID or null for open-set/no match), rows
(every query row ID → expected registered row ID or null). Hidden reference rows
are not query misses: score only observed query rows. A reference's registered ID
can remain expected in an unsupported locale; abstention is then a missed retrieval,
not a fabricated localized success. Different journeys/related variants stay in
one partition; duplicate decoded pixels and identical snapshot content cannot cross
partitions. No claim of unseen-screen/locale generalization without real support.

Separate `identity-policy-v1`: reference, frozenOn (development/validation/test-only),
supportedLocales, confidenceThreshold, labelFraction, minHorizontalOverlap,
maxWidthRatio, minimumRowMatches, minimumScreenScore, minimumMargin, maxAgeMs,
toolTimeoutSeconds. Thresholds are frozen externally on development/validation,
not fit by this evaluator. Test-only thresholds cannot qualify recorded data.
JSON ≤8MiB; names/text/IDs bounded. Helper timeout ≤30sec/case and no retry.

## Matching, in order

1. Reject stale/future queries, unavailable recognition, unsupported locales and
   detected overlays before identity retrieval. Cached epoch mismatch invalidates
   route reuse even if current identity produces a candidate.
2. Filter confidence, scope query title OCR to each registered titleRegion, and
   use actual TextAnchorVerifier required/optional/forbidden matching. Record an
   **anchor-only baseline**: exactly one verified screen is a candidate, otherwise
   unknown. Its case-insensitive substring semantics are unchanged.
3. Conservative matcher additionally requires exact normalized required-title lines
   (Unicode NFC/casefold/whitespace normalization; no translation/transliteration),
   avoiding substring collisions such as General vs General Information.
4. Associate OCR lines with rows only when the line is wholly inside exactly one
   row and its center lies in the configured left labelFraction. Overlapping row
   assignments are unknown; right-side mutable values are not identity anchors.
   This left-label layout assumption must be reviewed per supported locale/layout.
5. Match unique exact normalized row labels plus horizontal overlap/width ratio;
   deliberately ignore vertical position to tolerate scrolling. Duplicate labels
   in reference or query abstain, never use y-position to guess a logical identity.
   Do not manufacture candidates for invisible reference rows.
6. Screen score = uniquely matched rows / observed nonempty query labels. Require
   minimumRowMatches, minimumScreenScore and margin over runner-up. A tie is unknown.
   Missing/ambiguous anchors remain explicit reasons; score is not a probability.

Return candidate/unknown with scoped screenID, per-query row matches/reasons,
evidence, ranked screen scores, observationID/epoch and invalidation reasons.
Do not expose query truth to the helper or matcher. Optional cachedScreenID is
used only AFTER matching to report changed-screen invalidation, not to break ties.

## Evaluation and TTR proposal

Bind corpus/policy/helper/evaluator/primitive hashes. Score anchor-only vs conservative
screen retrieval, false matches, missed matches, abstentions and correct open-set
rejections. Row scores require correct screen and row (component identity is not
global). Report source/scenario/partition/locale slices, unique journey support,
unknown/zero-support rates and actual host/helper latency separately from OCR/capture
and TTR end-to-end latency. No synthetic timing or correctness proves deployment.

TTR consumes a proposal only: group, observationID, contextEpoch, candidate/unknown,
screen/row candidates, source context, policy hash, match evidence and invalidation
reasons (stale/future, overlay, unsupported locale, recognition failure, unknown
screen, changed screen, changed epoch, unresolved rows). Unknown invalidates reuse;
candidate never authorizes Select/backtracking, exempts safety checks or implements
resume logic. Reobserve and let the producer own route/cache policy. No existing
wire format or public NUA API is changed. Producer fake-backed integration and
separately authorized held-out recorded-journey comparison follow review.

## Reproduce software-only evidence

Build `AnchorTool` using the repository's offline Swift workflow; the evaluator
does not build/download implicitly. From package root, choose a new output:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/generate_identity_fixture.py \
  --output .build/debug-output/my-identity-fixture
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/identity_benchmark.py \
  --manifest .build/debug-output/my-identity-fixture/manifest.json \
  --policy .build/debug-output/my-identity-fixture/policy.json \
  --output .build/debug-output/my-identity-fixture/report.json
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python -m unittest discover \
  -s scripts -p 'test_identity_benchmark.py'
```

Default helper `.build/debug/AnchorTool`; `--helper` accepts a project-local binary
and records its hash. Exit0 means all supplied cases evaluated, not a quality pass;
exit1 retains partial results for helper errors/timeouts; exit2 rejects invalid
input/output. Existing outputs are never overwritten. Real source metadata/bytes
do not automatically confer data eligibility; external review remains required.
Replay compares predictions/metrics, excluding variable latency fields. Example:
[final synthetic report](../../reports/work/PER-06/benchmark-final-v2.json).
