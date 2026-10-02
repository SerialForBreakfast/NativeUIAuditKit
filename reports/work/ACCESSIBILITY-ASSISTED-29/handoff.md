# Accessibility review29 + Settings Swift25

October2,2026. Integrated local deliverables complete; real producer-data slices blocked.

| Outcome | State / evidence |
| --- | --- |
| Software | Optional review importer, actual editor evidence dialog and Swift diagnostic implemented and tested |
| Data eligibility | Existing Settings development data reused; zero qualified real native-artwork pairs in refreshed ledger |
| Integration | Local CLI, grouped editor navigation and Finish review exercised; new TTR profile manifest compatibility awaits producer evidence |
| Model | FDR036 real transfer not run: missing independently identified ordinary artwork reference pairs |

## Delivered

- `scripts/accessibility_review.py`: hash-bound existing review batch plus optional
  evidence -> new `accessibility-review-batch-v1`. The source is unchanged. Seeded
  random selection and all flagged frames, plus paired companions, share one editor
  directory. Positive focus proposals remain unconfirmed; missing/ambiguous/stale,
  wrong-target/profile/viewport, heading and assistive-focus evidence is flagged.
- Actual TTR standalone `AccessibilityPerceptionReport` fields are supported as
  optional retained proposal metadata. `stable` is a producer processing profile,
  not proof OS High Contrast is enabled. Verified settings/correspondence are supplied
  separately; the new consumer evidence manifest is not an existing TTR wire schema.
- Ordinary body boxes are preserved. Annotator's **Accessibility evidence…** action
  shows the associated assisted image and reasons without changing boxes or approval.
  A Markdown review index provides the same links. Existing Finish review/crop QA
  dispatch validates the new sealed batch. Hover Text is optional.
- [Settings ADR](../../../Research/ADR-0018-Settings-Swift-Pixel-Parity.md): Swift
  arithmetic reproduces33correct/0wrong on48scorable controls. Vision tracking drops
  to2correct/46undecided; retain current tracking. Generated14-case comparison also
  favors the current pipeline12exact outcomes versus5. No threshold fitting.

## Producer mismatch and real-data boundary

Published TTR45c84b6 establishes a **geometry mismatch**, not its later exact identity
failure: assisted outline286px versus ordinary body306px, about10px inside each
horizontal edge despiteIoU.930. Hover Text heading stops are another documented
correspondence hazard. Those mechanisms justify separate bounds, profile and identity
checks; they do not establish which caused the later acquisition stop.

The peer snapshot remained19:55:36Z and reported a correspondence stop without its
specific failed action, matched IDs or ordinary/reference export. Source HEAD remained
45c84b6. The exact later root cause and qualified pairs remain unavailable; existing
request `nuiak-20261002-accessibility29-mapping-evidence` is preserved, not duplicated.
Resume with the sanitized failed-boundary report and an explicitly transferable
hash-bound pair bundle. No new capture is inferred from this request.

Refreshed [real audit](real-pair-audit.json):166actions,14timing-ready,7reviewed Settings
endpoint pairs, zero qualified native-artwork reference pairs. The315static representative
controls from Native28 still lack the needed paired identity. This audit covers the
named retained ledger, not every stored image. Real FDR036 testing cannot be replaced
by scoring Settings as though native artwork correspondence were known.

## Use

Run from the project root with resident environments:

```sh
.venv-yolo/bin/python scripts/accessibility_review.py --batch EXISTING_BATCH --evidence EVIDENCE_JSON --output NEW_PROJECT_DIRECTORY
.venv-review/bin/python scripts/human_review_editor.py NEW_PROJECT_DIRECTORY/batch.json --runtime .build/human-review/accessibility29
```

Evidence version is `accessibility-review-evidence-v1`; each record binds `frameID`,
`ordinaryImageSHA256`, `target`, `screen`, `size`, hash references `assistedImage` and
`observation`, optional `perceptionReport`, `profiles.ordinary/assisted` with focusStyle,
verification and receipt reference, correspondence booleans sameControl/sameViewport/
settled/fresh/restored plus candidateCount, actionability, focusChannel, focusedControlID
and status. See generated contract fixtures in `scripts/test_accessibility_review.py`.
Verified evidence produces proposals only; humans resolve flags and confirm ordinary
focus/bounds. Data-role choice and training admission remain separate.

## Verification and execution

- New importer tests including CLI, production crop QA and actual offscreen Qt:10passed;
  existing actual editor interaction regression tests:23passed.
- Existing annotation and Finish review tests:27+13passed; Settings stability7passed;
  new Swift caller tests3passed. Final verification logs are under
  `.build/debug-output/accessibility29/`.
- Offline Swift build passed; host Swift tests134passed (14XCTest+120Swift Testing).
- Swift compile first required typed Vision result casts. First replay hit a missing
  size field, repaired by reading source image dimensions. Restricted Vision replay
  failed creating CVPixelBuffer; scoped host replay passed. Restricted full tests hit
  Apple-managed CoreML cache permissions; scoped host tests passed. Failed logs retained.
- Source/outputs remain local, reviewed originals unchanged. Earlier dirty Native28
  work preserved. This tranche implemented neither training nor model promotion.

## Next substantial tranche

Coordination published to `/Volumes/SharedStatusFile/nuiak/status.yaml`, own
`ACCESSIBILITY-ASSISTED-29` entry at 2026-10-02T20:55:00Z. Duplicate-key validation
and readback passed; unrelated entries and fields verified unchanged. Producer
acknowledgment of the pending requests remains outstanding.

1. Obtain TTR's exact mapping-failure evidence and qualify ordinary profile/reference
   pairing; import one grouped real review batch with High Contrast evidence.
2. After human uncertainty resolution/data-use confirmation, run FDR036 real transfer,
   report artwork misses/false focus and reference availability separately.
3. For independent local work, investigate translation-registration failures with
   retained stress cases before choosing a production Swift tracking strategy. The
   arithmetic port is ready as diagnostic code; the Vision substitution is rejected.
