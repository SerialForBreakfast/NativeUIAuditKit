# Accessibility and tracking30 — diagnostic tranche

October2,2026. Local diagnosis complete; real-model scoring awaits candidate-use
confirmation and a qualified reference context. Existing dirty Native28/review29
changes preserved. No model weights changed.

| Outcome | State | Evidence |
|---|---|---|
| Software verified | Passed | Actual diagnostic CLIs, production crops,10new Python tests,20related Python/Qt tests, offline build/134Swift tests |
| Data eligible | Blocked for clean transfer | No new qualified real-artwork reference pairs; two historical Home candidates have neighboring controls in their crop |
| Integration qualified | Blocked | Consumer manifest agreement/private producer review pixels remain pending |
| Model gate | Not assessed | FDR036 was not loaded; oracle geometry results are not model scores |

## Producer diagnosis resolved

Received [exact sanitized TTR report](received/tvtestrig-nav-verify-acc-map-20261002-r1.md):
13,271bytes, SHA2560830baabd5f6faf664ee7795418869b333803f451774aa16b7d686c5c7b2e874.
The later stop was Hover Text navigating to Accessibility/VISION headings where an
ordinary remembered sequence expected controls. Independently, the matched Home
Settings icon's manually referenced body changes306×183ordinary→253×151assisted.
Transferring the assisted rectangle yields0.580IoU and approximately+33/−36px
horizontal edge errors. These are producer measurements with±2pxedge uncertainty,
not consumer-measured or human-approved boxes. This is distinct from the earlier
10pxoutline inset observation. Original settings were restored per producer report.

Decision: assisted text/focus can support identity review; ordinary pixels need
their own boxes. Existing importer's heading, profile, identity and no-geometry-transfer
guards pass their actual CLI/editor regression tests. TTR acknowledged P0/P1/P2
planning and the consumer adapter; exact binding-manifest agreement remains open.
Raw42-frame physical audit was not delivered, so a genuine High Contrast-assisted
annotator batch cannot be manufactured from this prose report.

## Tracking failure isolated

Five retained same-screen pairs,50controls,48scorable. Same fixed rules, production
cropper and before-sized windows. Two page-change pairs remain excluded.

| Alignment | Correct | Wrong | Abstained /48 |
|---|---:|---:|---:|
| Existing OpenCV (retained baseline) |33|0|15|
| Saved Vision replay |2|0|46|
| Rounded Vision displacement |2|0|46|
| Reviewed-center diagnostic oracle |36|0|12|

Vision's48scorable controls split into15tracking-unavailable, one wrong row,
30pixel-rule abstentions and two correct unchanged. Median center error3.11source
pixels over33review-corresponded tracks; maximum69.50. The wrong row is visible in
the [grouped local crop review](retained-verified/review.md). Reviewed-center rescues
both real switches but consumes human after-geometry; it is not a deployable method
or model improvement. OpenCV is already close to this particular diagnostic result.
Twelve unchanged controls remain uncertain even with reviewed centers: alignment
alone is not the entire problem, and human boxes have their own precision limits.

[Final retained report](retained-verified/result.json),6.13s, pins source/policy/runtime.
[Fourteen generated cases](stress-verified/result.json),0.57s: raw5exact, rounded5,
oracle13; zero wrong decisive calls in any arm. Neighbor-only remains uncertain;
duplicate identity stays withheld from the oracle. Thresholds stayed fixed.
Recommendation: retain OpenCV correspondence and Swift arithmetic, reject rounding
as a fix. A native tracker replacement must meet precise translation and ambiguity
tests before TTR integration. See [ADR0018](../../../Research/ADR-0018-Settings-Swift-Pixel-Parity.md).

## Existing-image opportunity, with an important limitation

Fresh [action-ledger audit](real-pair-audit.json):166actions,14timing-ready,
seven reviewed Settings endpoint pairs,46reviewed image hashes, zero qualified
native-artwork action-linked references. This does not exhaust arbitrary still pairs.

A separate inspection of those reviewed stills found Home frame001/002: Photos
focused versus Music focused. Their existing labels/boxes can be reused unchanged.
[Two candidates and four production crops](home-reference-review/review.md) are
prepared together by `prepare_real_focus_references.py`, bound to the immutable
reviewed source. No redraw is requested. Pair identity/data-use confirmation was
asked asynchronously and is pending at handoff.

The fixed20%reference context includes the changing neighbor: Photos reference has
8.51%window area occupied by focused Music; Music reference has10.27%occupied by
focused Photos. Additional static neighbors are separately listed. Therefore these
are potential difficult-case development diagnostics, not clean-context qualification
for the existing advisory gate. No cropping change, masking, fabricated capture-time
receipt or relaxed eligibility was used. Their data roles and training membership
remain unchanged. A clean generalization claim still needs suitable ordinary pairs.

## Verification

All explicit outputs are project-local. Final code checks:

- `test_settings_tracking_diagnosis.py`:8passed, including generated native crops,
  frozen oracle size, ambiguity, source-tamper rejection and grouped gallery coverage.
- `test_real_focus_references.py`:2passed; real CLI produced four256×256crops and
  explicitly rejected clean-context eligibility for both candidates.
- Existing Settings stability7, Swift arithmetic caller3, actual review CLI/Qt10passed.
- Offline `swift build --disable-sandbox --skip-update` passed; full host
  `swift test --disable-sandbox --skip-update` passed134tests (14XCTest+120Swift Testing).
  Scoped host permission covers existing Apple-managed CoreML cache; explicit logs,
  TMPDIR and module cache stay under `.build/debug-output/tracking30/`.
- Initial generated-stress read rejected its legacy envelope's missing common flags;
  exact version/seal compatibility was added locally, leaving normal intake strict.
  Earlier output/logs preserved; `retained-verified` and `stress-verified` are final.

## Coordination and next substantial tranche

Receipt published/read back in `/Volumes/SharedStatusFile/nuiak/status.yaml`, own
`ACCESSIBILITY-TRACKING-30` entry; unrelated entries verified unchanged. Sender owns
cleanup. Producer acknowledged earlier requests; receipt acknowledgment/cleanup and
consumer binding agreement remain separate.
Final publication21:38:08UTC validated/read back; the binding-agreement request
names the actual consumer fields and asks for sanitized producer contract alignment.

1. Resolve use of the two existing Home pairs as an explicitly context-confounded
   development challenge, then run frozen FDR036 and report all four scores/crops.
2. Build a broader reference-candidate inventory from reviewed stills, grouping by
   screen/session and rejecting changed artwork, scroll/profile changes and crop
   contamination before requesting one consolidated human review. This is a promising
   alternative to new capture, not already-qualified evidence.
3. Port translation/ambiguity matching to a native diagnostic only with parity and
   generated-scroll/content-change checks; keep current tracking until it matches.
4. Import a genuine producer profile-bound review bundle once available; review
   uncertain identity/geometry together, then qualify clean real transfer.

The approved local tracking investigation and producer failure diagnosis are complete.
The remaining real evaluation has a human data-use boundary and a clean-context
evidence gap. No background execution is left running by this handoff.
