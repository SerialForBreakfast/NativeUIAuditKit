# Before/after focus: result and decision

October1,2026. **Keep the paired representation for further work; do not deploy
this rule or train another model on these results alone.** FDR021 stays unchanged.

## What works

The same image window before/after preserves visible enlargement. Independently
resizing each control can erase it. On six directional Home-screen contrasts,
fixed-window growth identifies6/6arrivals; independently resized crops identify0/6.
These reuse four captures/two focused icons in three pairs: not six independent
trials. Their existing whole-screen ineligibility remains unchanged.

Across513accepted native training pairs, fixed-window growth identifies63arrivals,
versus13with independent resizing;450abstentions remain. These are training examples,
not held-out evidence. Composite artwork does not always have a simple outer edge.

## Matched screen comparison

Six pairs/nine distinct frames satisfy existing completeness and full geometry
matching: Accessibility, Settings, Settings Apps and three tab pairs. Reversing
them gives12directions, **not12independent observations**. FDR021 transition baseline
requires both endpoint scores confident (>=.85or<=.15); this is not its standalone
screenshot accuracy.

| Method | Correct new target /12 | Abstained | Wrong target |
|---|---:|---:|---:|
| FDR021 confident before/after scores | 7 | 5 | 0 |
| Frozen common-window growth | 0 | 12 | 0 |
| Frozen brightness+growth | 6 | 6 | 0 |
| Separate clipping follow-up, unchanged thresholds | 12 | 0 | 0 |

The frozen rule rejected Settings rows because16%extra context reaches beyond the
screen edge. The separately documented follow-up allows brightness in identically
clamped windows but still blocks edge-growth for clipped margins. No threshold
tuning; original results preserved. This is a narrower availability fix, not new
approval for clipped control bodies, motion or uncertain correspondence.

Across all454real-control contrasts, follow-up combined signals give27/27arrivals,
24/27departures (3abstentions), no false changes on400unchanged controls
(396abstentions/4identical-pixel confirmations). This includes incomplete screen
contexts, repeated screens and partially mismatched VoiceOver rows: **descriptive
totals, not deployment accuracy**. Retention exposes a failure:8/9arrivals and9/9
departures versusFDR021's9/9each. That fails the replacement bar.

## Why it fails

Accessibility Shortcut scrolls upward161source pixels. The fixed before-window then
looks at dark background rather than the now-highlighted row and calls a departure.
Stable control identity is insufficient: paired windows need translation alignment
or explicit movement rejection, without scaling away enlargement.

![Scroll defeats a fixed window](artifacts/audit/retention-failure.png)

VoiceOver removes a row: position matching pairs some different labels at similar
locations (7/10matched). Whole-frame scoring correctly rejects that partial match;
even complete-count geometry matching remains an assumption, not an identity service.
All18real frame pairs were visually inspected. No action causality was established.

Controlled stress tests also produce false changes from uniform lighting, artwork
replacement and translation. Externally supplied invalid-context flags stop them,
but no visual context/motion detector was implemented. Supplied flags are not safety
qualification. The native captioned-card example also shows why a universal brightening
rule fails: focus enlargement changes how much bright artwork fits in the window.

## Scope and verification

-513native training pairs,9retention pairs,227real-control contrasts across18frame
  pairs; forward/reverse/identical controls total2,996cases.281exclusions:
  196without cross-frame identity,85groups missing a focus state.
-1,702unique native crops,84.22seconds rendering; first replay6.07seconds.
  Original1562training/333evaluation membership and labels unchanged.
-All2,996primary decisions and summaries replay exactly.23Python tests,7actualCLI
  tamper rejections (seal,policy,label,geometry,context,duplicate,anchor), offline
  Swift build and134Swift tests pass. No compiler warnings observed.
-Approximately98MiB at audit time, under2GiB. Four fixed/normalized example panels
  plus the scroll failure inspected. No GPU training, export, promotion or new capture.

## Next substantial tranche

Implement translation-only alignment or abstention; preserve scale. Recover or
reject the161pxscroll counterexample. Stress against disappearing rows, moving
artwork, lighting-only changes and unchanged focus, and compare wrong changes and
abstention against the retained baseline. Only then integrate an optional diagnostic
transition verifier. Genuine navigation qualification still needs reviewed action-linked
endpoints. Another neural fit now would not resolve this demonstrated movement gap.

TTR: retain full-resolution paired frames, stable IDs, per-frame enlarged bounds,
viewport/scroll offsets or explicit unavailability, action/capture brackets and
no-op/content-only/scroll cases. Existing structural-coverage request remains active;
no new capture dispatched or accepted images requested again.

Evidence: [primary](artifacts/evaluation-final/result.json),
[audit/follow-up](artifacts/audit/audit.json), [inventory](artifacts/inventory/inventory.json),
[plan](../../../Research/Plans/FocusPaired11.md),
[follow-up scope](../../../Research/Plans/FocusPaired11Clipping.md).
