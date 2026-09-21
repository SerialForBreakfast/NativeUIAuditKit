# Authorized simulator smoke — preflight blocked

2026-09-21 23:00Z. User authorized one local bounded smoke; Office excluded.
Recipe: existing `live-smoke/action-dialog.json`, action_dialog, two elements,
high_contrast, regular density, seed 7, step 0. Intended output: two labeled
focused/resting pairs, complete receipt/index, verified export and NUA intake.

## Checks and exact blocker

- GUI PID47684, matching helper under the previously verified DerivedData app.
- Fresh exact-target readiness exit0, 458ms, request
  `D446E29A-0ED8-4D02-B40E-F42A26F1DC57`, 22:59:57Z. All runtime/storage checks
  ready; persisted ownership clear. No storage repair or restart needed.
- Port8080 belongs to Fixture PID37989; executable path binds it to simulator
  `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`.
- `/scene` succeeds, but its raw JSON has **no `focus_observation`** and reports
  `is_settled: true` with the legacy 150ms settle field. Current source requires
  a verified UIKit focus observation to report settled. This is incompatible
  with the observed-focus capture contract, not a missing optional annotation.
- Installed Fixture Debug dylib SHA256:
  `66d279a93fb52a1ac3100201c02e08f17976900349454c2947b9f7b80a8497b4`.
  Local DerivedData Debug-appletvsimulator Fixture dylib has the **same** hash.
  Producer reported updated Fixture hash in its prior handoff was
  `89001eebac3a8faded08d529ea5f523866a61dbf5008fa05b1415e722870677e`;
  no local match was established. Version 1.0/build labels alone are insufficient.
- Current producer engine `validateObservedFocus` rejects missing observation
  as `observed_focus_unavailable_or_mismatched`. Starting the recipe would not
  cure a missing runtime capability. No job or capture was started.

Retained fresh raw reply: `preflight-scene.json`, request
`659F602A-752D-48AF-96D7-29710185DC85`, exit0; stderr retained separately.
Earlier read request `F0B88D1F-26C0-40E4-9984-A95ABEBECD5B` agrees.
No cleanup needed: no resources acquired, no recipe/focus mutation, no export.

## Resume condition

TVTestRig owner supplies a matching source-built Fixture for this Xcode/runtime
and installs/launches it on the exact existing simulator under explicit setup
authority. Do not install the unrelated producer-host artifact blindly. Verify
binary identity and actual `focus_observation` telemetry, then resume the same
two-element smoke through capture, postflight health, export and intake. This
task did not authorize external-repository builds/edits or simulator installation.
No reset, re-pair, signing overhaul or Office fallback is needed.

## Outcomes

Runtime readiness passed; smoke preflight failed compatibility. No genuine data
eligible, capture integration unqualified, model gates not assessed. Existing
offline consumer software remains verified. Do not close SIM-DATA-01 or advance
to broad pilot/harvest merely from the readiness pass.

Published/read back the targeted deployment request
`nuiak-20260921T230053Z-matching-fixture-deployment` in NUA's own shared readiness
packet. YAML validated; peer acknowledgment pending. Local queue and roadmap
updated with integrated pilot/baseline → frozen corpus → one candidate tranches.
`git diff --check` passed. No source implementation changed or tests required.
