# Offline before/after focus diagnostic

This experimental Python tool compares two retained screenshots. It does not drive
TTR, replace FocusRing, label training data, or establish action success. Default
is **disabled**. No new dependencies or service are required.

## Input

Save a project-local JSON request:

```json
{
  "version": 1,
  "before": {"path": "project-relative-before.png", "sha256": "actual-file-sha256"},
  "after": {"path": "project-relative-after.png", "sha256": "actual-file-sha256"},
  "beforeBounds": [200, 200, 160, 60],
  "context": {
    "sameScene": true,
    "settled": true,
    "fresh": true,
    "identityVerified": true
  }
}
```

Bounds are top-left source pixels. Only BEFORE bounds are accepted as the tracking
input. Do not substitute an after truth box or predicted focus label. The context
flags are caller assertions: a screenshot does not prove freshness or settlement.
False flags return unavailable; missing/nonboolean flags reject the request.
Unknown live context must not be filled with true merely to obtain a result.

## Run

From the project root, with the existing native FocusRingTool already built:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/tmp" \
  .venv-yolo/bin/python scripts/focus_transition_verifier.py \
  --request reports/request.json --output reports/new-result.json \
  --enable-experimental --common-support
```

Omit `--enable-experimental` for the disabled path; no screenshot/model is opened.
Omit `--common-support` to reproduce the conservative first alignment method.
The output must not exist. All input/output paths stay in the repository. Images
are hash checked;40million pixels per image maximum. It never downloads weights,
trains, creates controls, or changes the original images/annotations.

## Interpret

- `arrival` / `departure`: visual evidence consistent with gaining/losing focus,
  not proof that an input caused the change.
- `unchanged`: identical pixels in the compared image/window, not initial focus.
- `unknown`: measured but not enough agreement, including illumination warning.
- `unavailable`: tracking, viewport, clipping, context or correspondence failed.

`tracking.afterBounds` retains the before control's width/height and applies only
estimated translation. Optional `beforeCropBounds` / `afterCropBounds` describe
equal visible-support crop requests, **not new control annotations**. Both images
use the existing native cropper. Correspondence uses central texture and can fail
when artwork enlarges, repeats, disappears or changes. Color-only content updates
can be visually indistinguishable from focus highlighting; the current tool can
give false changes on those stress cases even with all flags supplied true.

Every result is `diagnosticOnly:true`, `releaseEligible:false`, `controlIssued:false`.
Do not turn it into an autonomous permission/activation gate. Full-screen candidate
coverage, real input receipts and independent evaluation remain separate requirements.

See [experiment scope](Plans/FocusAlignment12.md),
[common-support follow-up](Plans/FocusAlignment12CommonSupport.md), and
[results](../reports/work/FOCUS-ALIGNMENT-12/results.md).

## Optional whole-scene corroboration

`scripts/focus_scene_transition.py` consumes a version-1 JSON request with:

```json
{
  "version": 1,
  "context": {"sameScene": true, "settled": true, "fresh": true, "completeCoverage": true},
  "controls": [
    {"id": "stable-a", "decision": "departure", "identityVerified": true},
    {"id": "stable-b", "decision": "arrival", "identityVerified": true}
  ]
}
```

Use `--request FILE --output NEW_FILE --enable-experimental`. The default is disabled.
Pass every candidate, not just the two that changed; missing or removed controls
must make completeness/identity false. These flags are caller assertions, not an
implemented live identity provider. Never fill them from guessed correspondence.
Results require exactly one arrival and one departure. Unknown background decisions
are listed; `--require-resolved-background` rejects those too. Unavailable controls
always block a switch. All-unchanged reports no visual change, not initial focus.

This CLI aggregates attributed decisions; it does not run detection or discover
control identities. The existing pixel CLI supplies each decision. There is no
TTR integration or autonomous action. Two opposite content-color changes produce
a false switch through the actual pixel and scene CLIs; agreement is not focus proof.
Retained analysis gives7/12correct transition directions,5abstentions versus11/12
for arrival-only selection. Strict background resolution abstains on all12.
Do not deploy either policy as a replacement for the current model.
