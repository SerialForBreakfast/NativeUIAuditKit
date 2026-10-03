# Corrected transition intake and replay — October 2, 2026

## Outcome

Received and validated the corrected 16-case producer export. All 188 listed files
match their hashes. Duplicate semantic IDs are repaired; clipped controls now have
explicit accounting. Twelve pairs pass capture/settling checks and were scored.
The four actual focus-movement pairs remain blocked by producer readiness evidence.

| Pixel comparison | Correct | Wrong | Abstained | Scorable |
|---|---:|---:|---:|---:|
| Brightness, growth, or combined (each) | 20 | 0 | 8 | 28 |
| Guarded stability | 22 | 0 | 6 | 28 |

Four additional before-controls disappear from eligible visible membership after
scrolling and are unmatched, not correct negatives. All 28 scored states are
unchanged. Guarded results: boundary 12 correct; content-only 8 correct/4 uncertain;
scroll-unchanged 2 correct/2 uncertain/4 unmatched. This provides two extra correct
unchanged decisions, not improved detection of real focus moves. These are four
conditions × two seeds × two content appearances using custom-focus composite cards,
one renderer ancestry—not a native-growth model benchmark or independent evaluation.

## Exact remaining failure

All four `scroll_moved` after endpoints report `observedID=item-2`,
`requestedID=item-1`, `verified=false`, `is_settled=false`,
`reason=focus_mismatch`, `stableMilliseconds=0`. Their before endpoints now validate.
The consumer preserves this evidence and rejects scoring; it does not manufacture
a settled label from the planned action. TTR should clarify/repair action-driven
readiness and provide source commit/push plus corrected evidence under its scope.

## Implementation and verification

- Actual CLI: `scripts/focus_corrected_transition_audit.py --root <received root> --output <fresh path>`.
- Checks campaign/case membership, sidecar equality, PNG digest/dimensions, settled
  native brackets, generation, recipe, simulator/run/action sequence, mutation
  timing/parameters/results, measured body geometry and manifest revalidation.
- Opt-in incomplete-composition contract separates full expected wrappers from
  visible scene controls and explicitly evidenced clipped exclusions. Existing
  harvest callers retain strict default behavior. No raw source is rewritten.
- Pixel predictions use before-image bounds and pixel tracking; native after-state
  and identity are used for grading. Guarded stability is explicitly a cross-domain
  diagnostic, not a declaration that artwork is a Settings screen.
- Final replay: **9.025 seconds**, 32 before-controls; source and runtime pins
  retained in [audit](replay-final/audit.json). Earlier developmental replay retained.
- **101 Python tests passed** (51 focused + 50 harvest regressions), including malformed visibility/duplicate IDs, stale
  focus, mismatched hashes/dimensions, case bindings and action sequences.
- Offline `swift build --skip-update` and `swift test --skip-update` passed:
  **14 XCTest + 120 Swift Testing**. Logs: [Python](python-tests.log),
  [harvest regressions](harvest-regression-tests.log), [build](swift-build.log), [Swift tests](swift-test.log).
- Execution used project-local explicit outputs/caches/temp and scoped host access
  for Swift/Apple framework tests. Resident dependencies only. Original archive
  retained; final outputs remain comfortably inside the assigned diagnostic budget.

## Transfer and coordination

Archive `ttr-controlled-transitions-20261002-r1.tar.gz`: **191,803,968 bytes**,
SHA256 `cd2f42c0a05db7c99ce3408aca9fd7d0a9e8a4cfe7263e471fa98b3256438737`.
Safe extraction: 208 archive members, 197,957,080 expanded bytes.
Receipt verified at 22:28:14 UTC; [local receipt](received/receipt.json).

Published `/Volumes/SharedStatusFile/nuiak/status.yaml`, packet
`NATIVE-TRANSITIONS-34`, at22:40:34UTC; unique-key YAML readback passed and all other
fields preserved. Acknowledged `tvtestrig-20261002-transition22-correction` for
transfer, with partial diagnostic intake stated separately. New request
`nuiak-20261002-transition34-native-readiness` gives the exact four-case failure.
Peer acknowledgment and sender-owned archive cleanup remain unverified.

## Companion and next tranche

DOC-01: reconciled stale seven-frame Settings review dependencies in campaign09,
intake13 and TEMP-FOCUS-02 against actual completed review21 and comparisons22/23/33.
The distinct eight-frame appearance review and source-role decisions remain open.

Next substantial tranche: (1) inspect/receive the already-published rich24 transition
successor and compare which conditions genuinely pass native readiness; (2) qualify
grid-density composition-v4 locally once the source revision is available; (3) use
coverage33's 48-case intent to map supported artwork, wide-button and list-row cases
and build the next changed-data experiment. Source publication/synchronization is
required for the new grid path; exact data admission/training retain their gates.

Independent outcomes: software **passed**; diagnostic data **12 pairs accepted,
4 blocked**; full integration/movement qualification **blocked**; model gate
**not applicable**. Local tranche complete for review; producer repairs stay queued.
