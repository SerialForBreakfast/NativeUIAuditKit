# Corpus readiness decision — 2026-10-01

Decision: retained baseline is auditable and reusable for development; **new
production-corpus readiness is NO-GO**. Run approval alone would only repeat the
baseline. Do not request it as the solution to missing coverage.

## Coverage matrix

Counts are focused/unfocused crops, not independent examples or pair counts.
Source: `delivery/inventory.json`; repeat verification is in
`readiness-recheck-20261001/`. No model was run for this decision.

| Family | Training crops | Development crops | Interpretation / next evidence |
| --- | ---: | ---: | --- |
| Buttons | 150 / 155 | 3 / 3 | Present; broaden shape, resting fill and competitors. |
| Artwork | 159 / 249 | 12 / 181 | Present but FDR021 finds only 2/12 focused development examples. Prioritize structural/context variation, not more duplicates. |
| Rows | 38 / 115 | 7 / 64 | Present; accessories, widths and neighboring-row contrasts needed. |
| Explicit tab labels | 0 / 0 | 3 / 21 | Label-stratum absence, not complete visual absence: exact producer-sidecar joins identify 12 tab/nested-tab pairs currently labeled primaryButton. Do not relabel them silently. |
| Keyboard | 0 / 0 | 0 / 0 | Absent; native export capability unqualified, not proven impossible. Supported families need not wait for this lane. |
| Other | 60 / 60 | 2 / 19 | Mixed/unmapped controls, not a demonstrated uniform family. |
| Selected-but-unfocused parent | Unknown | Unknown | Need explicit selected state, native focus and hierarchy together. Negative labels alone cannot establish this case. |
| Appearance hard negatives | Unknown | Unknown | Need recipe-linked light/high-contrast and control/content evidence. Ordinary negatives are not automatically hard negatives. |

Retention remains 9/9 crops in the existing other stratum. Preserve it; it does not
provide per-family retention coverage. Development source IDs are absent from these
normalized rows, which means this audit cannot certify independent source ancestry;
it does not mean original source evidence never existed. No cross-role relationships
detected is not proof of independence.

## Existing production scene gate comparison

| Scene | Retained native pairs | Existing minimum | Count shortfall |
| --- | ---: | ---: | ---: |
| gridMatrix | 218 | 2,000 | 1,782 |
| mediaShelf | 75 | 1,500 | 1,425 |
| settingsList | 22 | 1,000 | 978 |
| actionDialog | 20 | 500 | 480 |
| heroCarousel | 20 | 500 | 480 |
| focusMaze | 0 | 500 | 500 |

These six buckets contain 355 pairs. Another 40 pairs have scene names
settings/general (25), settings/root (12), settings/apps (3); preserve those names,
do not count them as settingsList without a reviewed mapping. The arithmetic
shortfall is 5,645 in the six buckets, **not an instruction to capture that many**:
lineage, themes, hard negatives and physical transfer also remain requirements.
196 human static crops are not 196 pairs. Count/diversity gates are unchanged.

## Acceptance path and ownership

1. **NUIAK coverage contract — supplied.** Use collection-contract.json and this
   matrix. Freeze original train/development/retention memberships and matched24's
   validation purpose. No unreviewed numeric AX-role conversion.
2. **TTR source/layout manifest — missing.** Return exact new recipe membership,
   renderer/component ancestry, assets and supported native fields, with selected
   parent/keyboard capability limits. Existing seeds or new names are not ancestry.
   Extend request `nuiak-20261001-corpus-source-layout-contract`; do not create a
   second transport or wait for Hover Text/braille.
3. **NUIAK source reservation — pending that manifest.** Review related groups and
   assign intended roles before generation. Unknown independence stays diagnostic;
   retain existing semantic holds. First supported-family batch is not blocked on
   unrelated keyboard support, but cannot claim full coverage.
4. **Bounded capture/intake — not dispatched.** Bind exact target/runtime, eligible
   recipes, target count, duration, retained-byte limit and free-space floor. Then
   use existing capture/export and receipt paths; no per-control human prompts.
5. **Final production assembly/preflight — pending new eligible data.** Every member
   needs observed focus/geometry correlation, image/hash and crop checks, explicit
   disposition and split review. Review recipe sheets plus exceptions. Keep proposed
   counts distinct from accepted counts. Only then prepare a changed-data experiment.

The 32 native-button/row/tab pairs in TTR's geometry matrix do not need artwork-body
recapture. Twelve native-image pairs need measured artwork only for body-specific
uses. Neither statement removes existing admission holds. Do not recapture retained
successes or use the matched24 validation campaign to fill training quotas.

## Finish boundary

The audit/readiness decision can be handed off now; the full FOCUS-CORPUS-03
production assembly criterion remains blocked, not completed by this document.
No new qualifying source/layout manifest or response to the corpus/semantic request
was identified in the latest shared snapshot (producer updated 00:41:51Z).
That snapshot is stale and establishes neither current device availability nor a
new producer delivery. Resume when TTR supplies the named manifest/schema evidence;
no further human rectangle annotation is currently requested.
