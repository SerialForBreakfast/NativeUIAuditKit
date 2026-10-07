# ADR-0022 — Screen context for focus and navigation

- Date: October 7, 2026
- Status: Proposed; documentation complete, implementation and evaluation pending.
- Owners: NUIAK owns classification and evaluation. TTR owns observations and navigation policy.
- Goal: Test whether screen context improves focus decisions and navigation without increasing confident errors.

## Context

NUIAK currently reports detected elements, visible text, and estimated focus.
Its public observations do not provide a qualified screen-context classifier.
The element taxonomy includes alerts and sheets. Those classes do not establish app identity or OS ownership.
Existing focus rules use row and collection geometry. They do not prove that a screenshot shows Settings or Home.

The current focus experiments show a repeated problem: improvements on one appearance can reduce performance on other appearances.
Screen context could help select an appropriate focus method or identify the active overlay.
This is a hypothesis, not an explanation proven by current results.
A mistaken context decision could instead select the wrong method and increase errors.

## Proposed decision

Evaluate a small, optional screen-context component before changing the main detector or focus model.
Compare it with simple rules and existing TTR observations.
Keep context separate from element classes and focus labels.
Use the existing evidence reports and TTR integration path.
Do not add another controller or require a large language model.

### Separate the meanings

| Field | Meaning | Proposed initial values |
| --- | --- | --- |
| Surface identity | Which surface owns the visible screen? | system Home, system Settings, app, unknown |
| Layout family | How is content arranged? | list, grid, detail, search, playback, mixed, unknown |
| Overlay state | Is an overlay visible? | present, absent, unknown |
| Overlay kind | What kind of overlay appears? | dialog, sheet, menu, keyboard, other, unknown |
| Overlay owner | Which component owns the overlay? | system, app, unknown |
| Active scope | Which region currently receives input? | native-observed region, visually proposed region, unknown |

These fields are separate outputs, not one mutually exclusive screen label.
Settings can remain visible behind a system dialog. An app can contain a Settings-like list.
A detected rectangle does not prove modal behavior, ownership, or the active input region.
If evidence cannot establish identity, report the visual layout and leave identity unknown.
Refine these proposed values against available labels before implementation.

### Evidence contract

Bind each result to the image hash, dimensions, capture time, model version, and preprocessing version.
Record the value, evidence source, uncertainty, and conflicting observations for each field.
Keep model scores separate from calibrated probabilities.
Sources can include pixels, OCR, detected elements, observed navigation history, and TTR native observations.
Missing or stale native observations remain unavailable.

Keep visual predictions separate from native observations in storage and reports.
An expected route or requested app is not an observed screen identity.
Navigation history can provide supporting evidence. A failed action must not silently advance that history.
After a transition, interruption, or observation gap, recheck context rather than reusing an old classification indefinitely.

## Training and data

NUIAK can train screen context when it has trustworthy labels for the specified fields.
Fixture recipes label intended layouts. Runtime observations must confirm actual visible screens and overlays.
A generated Settings-like screen receives a list-layout label, not a system Settings identity label.
Actual Home and Settings identities need native observations or reviewed real screenshots.
Train an OS-ownership output only when the corpus supports that distinction.

Use existing images before making new captures.
For missing reproducible Fixture cases, use local TTR first.
Sillycon TTR supplies only missing capabilities or evidence unavailable locally.
Keep private device images local under the existing restrictions.
Big Dog receives only approved inputs through the verified transfer workflow.

Include the following difficult cases:

- App settings pages that resemble system Settings.
- Media grids that resemble Home.
- Dialogs over lists, grids, and playback.
- App dialogs that resemble system dialogs.
- Partial overlays, dimmed backgrounds, and transition frames.
- Keyboard and search screens with competing focus regions.
- Different themes, languages, accessibility profiles, and supported OS versions.
- Unknown layouts and screenshots with unavailable identity evidence.

Keep related screens, recipes, journeys, assets, and repeated captures in the same data group.
Reserve unfamiliar app and layout families before tuning.
Report OS and accessibility coverage explicitly.
New seeds and artwork do not establish independent evaluation groups.
Do not infer context truth from the focus model being evaluated.

## First experiment

Use one fixed corpus and the same groups for all applicable comparisons.
Inventory label support before setting sample counts or claiming class coverage.
Reuse resident encoders where suitable. Record any new feature extraction before execution.

Compare these alternatives:

1. Existing focus behavior without screen context.
2. A fixed rule using OCR and detected layout.
3. A small learned classifier using visual features.
4. Optional native-assisted context, reported separately from visual-only results.

Freeze the context-to-focus policy before evaluation.
Initially let context recommend a focus method without changing production decisions.
Use reviewed context as a separate diagnostic upper bound for downstream usefulness.
If correct context does not improve focus, stop classifier work for that proposed use.
Do not confuse an upper-bound result with a deployable improvement.

Measure both component quality and downstream outcomes:

- Per-class precision, recall, confusion counts, and support by independent group.
- Confident incorrect identities and missed overlays.
- Unknown results and error among accepted predictions.
- Complete focus decisions with and without predicted context.
- Focus selected behind a modal and incorrect exclusion of valid controls.
- Previous successful cases and unfamiliar layouts.
- Processing time, memory, model size, and end-to-end navigation time.

Use development groups for thresholds. Keep final groups untouched until the comparison is fixed.
Record numeric acceptance limits before a training run, using the current baseline and intended consumer behavior.
Existing release gates still apply. A high pooled context score alone cannot justify deployment.

## TTR use and safety

The first integration runs as an optional observer.
TTR records its native observations beside the NUIAK prediction and identifies disagreements.
Agreement can support route checking. It cannot authorize an input or prove that rendering has settled.
Unknown or conflicting context must not activate a more permissive navigation policy.

After qualification, possible uses include:

- Check that the expected page type appears after navigation.
- Select a tested row, grid, or overlay focus method.
- Restrict focus candidates to a qualified active region.
- Detect interruptions and request another observation.
- Group failure examples and identify missing training coverage.

A broad screen type does not identify an exact page or graph node.
TTR still needs its existing route identity, action verification, and ownership checks.
Context classification does not replace focus detection, control geometry, or temporal change detection.
Do not suppress background candidates solely because an unqualified classifier predicts a modal.

## Delivery sequence and responsibilities

1. NUIAK inventories retained labels and prepares a matched diagnostic with no production behavior change.
2. NUIAK compares rules and one bounded learned candidate when label support permits.
3. NUIAK checks whether predicted context improves focus results without losing previous successes.
4. NUIAK verifies Swift/CoreML behavior if the candidate meets the declared requirements.
5. TTR tests the optional observer on recorded cases before any action-linked integration.

Big Dog can perform assigned feature extraction and training with pinned inputs.
Local TTR provides supported synthetic examples. New producer features remain asynchronous requests to Sillycon TTR.
This document creates no peer assignment and starts no model or capture run.
Keep the current focus improvement cycle as the primary goal.
Select this experiment when context errors explain a measured failure, not merely because classification is possible.

## Consequences and alternatives

Potential gains include better focus-method selection, clearer failure categories, and fewer background selections during overlays.
Costs include new labels, extra inference, confidence calibration, and compounded errors between components.
Native evidence may already solve identity on supported targets. Prefer that baseline where it works.
Rules may suffice for a narrow screen family. A learned classifier needs to show additional value.
A unified full-screen detector remains an alternative, but this proposal does not depend on retraining it.

## Related work

- [Evidence-driven focus qualification](ADR-0021-Evidence-Driven-Focus-Qualification.md).
- [Optional semantic reporting](ADR-0016-Evidence-Bound-Foundation-Model-Semantics.md).
- [Context-aware focus](ADR-0015-Context-Aware-Focus-Detection.md).
- [TTR perception and screen identity](Plans/TTRPerception.md).
- [Focus improvement cycle](Plans/EvidenceDrivenFocusQualification.md#highest-priority--focus-improvement-cycle).
- [Current element observations](../Sources/NativeUIAuditKit/Models/NativeUIElementObservation.swift).
