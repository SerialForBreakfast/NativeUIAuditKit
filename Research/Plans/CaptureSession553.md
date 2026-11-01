# CAPTURE553 — Batched capture plan for MEASURE553 M6

Date: 2026-10-31. Owner: Maximum-mini-NUIAK. Parent: [MEASURE553](Measure553.md).
Source: `backlog_pipeline.py blockers` on 2026-10-31. Rule: launch and capture batching in the local `tvtestrig` skill.
This plan admits no job and starts no capture. Each capture keeps its approval class, target binding, and recipe qualification.

## Summary

37 records wait on TTR or Fixture capture data. They unblock 57 records in total.
They fall into 3 sessions by producer capability. Session A needs no new TTR feature.

| Session | Producer need | Records | Owner of missing capability |
|---|---|---|---|
| A | Existing Fixture recipes, still frames, Simulator | 19 | Maximum-mini-NUIAK prepares recipes |
| B | New Fixture content and action recipes | 13 | Maximum-mini-TTR |
| C | Real apps for the REAL543 pilot | Up to 50 cases | Maximum-mini-NUIAK and maintainer review |

## Session A — still Fixture frames on the existing producer

Prepare all recipes in 1 recipes directory. Use 1 `fixture batch` call for each target and resolution.
Keep training, development, calibration, and audit roles in separate output groups.

| Need | Records |
|---|---|
| Independent no-focus groups | B405-004, B405-057, B405-058, B405-009 |
| Static decorative borders, width and contrast | B405-005, B405-101, B405-102 |
| Non-4K groups with measured bodies | B405-007 |
| Shadow and shading pairs | B405-053, B405-054, B405-052 |
| Bright and identical neighbors | B405-056 |
| Clipped controls with visible bounds | B405-103 |
| Button and row families with new reservations | B405-104 |
| Selected tab versus focused tab | B405-027, B405-194 |
| Stepper values from 3 template families | B405-106 |
| Native coverage receipts | B405-241, B405-240 |

Before the session:

1. Confirm that a qualified recipe exists for each need. If not, name the missing recipe field.
2. Reserve group IDs and data roles. Exclude evaluation groups from training.
3. Register the consumer jobs with dependencies on the capture producers.
4. Estimate the session duration from recorded capture times.

## Session B — needs new TTR Fixture capabilities

Sillycon-TTR or Maximum-mini-TTR must first supply these producer features.
Send 1 combined request, not 1 request for each record.
The request also carries the 8 Session A records that need new Fixture features.
Request: `reports/work/MEASURE553/session-b-request.json`.

| Producer feature | Records |
|---|---|
| Artwork or text exchange with observed unchanged focus | B405-043, B405-062, B405-110 |
| Movement pairs with action receipts and scroll offsets | B405-044, B405-064, B405-112 |
| Timestamped sequences and fixed capture delays | B405-008, B405-065, B405-069 |
| Keyboard recipe with key identities | B405-046 |
| Seeded nested navigation with a route graph | B405-047 |
| Parent selection separate from child focus | B405-045 |
| Identical artwork and labels with stable IDs | B405-066 |

5 records need rights inventories, reserved manifests, or same-build counterparts, not new capture alone.
They are B405-049, B405-109, B405-113, B405-105, and B405-010.

## Session C — REAL543 real-app pilot

Capture the predetermined pilot points for each qualified app in 1 session per app.
Plan all points before the session. Use SDK drafts only for blinded human review.
NewsTV needs the lifecycle disagreement resolved first (REAL550-SDK-STATE).

## Session A capability check — 2026-10-31

Maximum-mini-NUIAK compares each need with the TTR Fixture contracts at TTR revision e4c693c5.
Sources: `Docs/CLI/fixture-appearance-v1.md` and `Docs/Contracts/fixture-composition-v1/capabilities.md` in the TTR checkout.
This check reads documents only. It does not prove rendered qualification.

### Ready on existing Fixture features

| Records | Recipe feature | Target | Check before capture |
|---|---|---|---|
| B405-104 | `native_button` focus and `settings_rows` presentation | Apple TV 4K | Reserve new groups. Keep the 10 native development groups excluded. |
| B405-027 | `tabs` with `selectedIndex`, and `nested_tabs_v1` | Apple TV 4K | Select a tab that differs from the focused tab. Selection is a recipe state, not focus evidence. |
| B405-052, B405-054 | `custom` focus with `shadowOpacity` paired with `native_image` focus | Apple TV 4K | Keep artwork, seed, and layout identical in each pair. |
| B405-053 | `custom` shadow with the fixed 12 pt radius | Apple TV 4K | Shadow extent comes from the declared radius. Native shadow extents stay unmeasured. |
| B405-056 | `bright_unfocused` preset and `canvas.labels` | Apple TV 4K | Preflight must accept duplicate labels. If it rejects them, move identical neighbors to Session B. |
| B405-007 | The same recipes on the "Apple TV 4K (3rd generation) (at 1080p)" device type | Apple TV at 1080p | Use a separate target binding and 1 separate `fixture batch` call. |

These 7 records need 2 tvOS `fixture batch` calls: 1 for each resolution.

### iOS generator, not TTR

B405-106 uses the NUIAK iOS generator through T46 recipes.
The generator has 5 templates that contain steppers, for example `StepperTemplate` and `AccountProfileFormTemplate`.
Before capture, check that the templates vary the minimum, middle, and maximum values and the disabled state.
If they do not, name the missing template field. Do not count 1 family 3 times.

### Moved to the combined Session B request

| Records | Missing Fixture feature |
|---|---|
| B405-004, B405-057, B405-058, B405-009 | A scene with observed no focus. Check first: `scripts/direct_tvos_capture.py` sends Fixture `/focus/set` with `element_id: null` and requires 0 focused elements. The tvOS focus engine focuses a control when 1 is visible. ADR-0051 declared focus is rejected. |
| B405-005, B405-101, B405-102 | A static border on unfocused controls. `custom` borders show only while focused. |
| B405-103 | Clipped controls with measured visible bounds. The Fixture now rejects clipping. |
| B405-194 | Tab-to-content states. `nested_tabs_v1` freezes selection during the focus sweep. |

### Blocked by TTR storage

B405-240 and B405-241 need the 6 `native431` capture receipts.
`native431-recovery` stops with `resourceContended` because Maximum-mini-TTR retains about 35 GiB against a 512 MiB budget.
The offload request is stored at coordinator cursor 887. Maximum-mini-NUIAK does not delete peer evidence.

## Order

1. Session A recipes and consumers. This needs no peer work.
1a. Done, 2026-10-31: Session A captured 74 rows for 7 records. See `reports/work/CAPTURE553/session-a-receipt.json`.
   T59 and T56 consumer jobs are registered in `Research/Experiments/batches/CAPTURE553.json`.
2. The combined Session B producer request to Maximum-mini-TTR. Stored at coordinator cursor 1840 on 2026-10-31.
3. Session C after app qualification and the maintainer decisions in MEASURE553.
