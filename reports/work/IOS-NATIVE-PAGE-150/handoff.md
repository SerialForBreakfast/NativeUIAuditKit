# IOS-NATIVE-PAGE150 — geometry hypothesis rejected; corpus unchanged

Software:7focused Python checks plus142offline package checks pass. Native test
build and exact Simulator execution exit0. New opt-in test captures all36cases
in6.866seconds; automated membership/hash/dimensions/ink containment pass.
Representative light render inspected. No production annotation changes.

Runtime: Xcode27.0/27A266a, iPhone17Pro iOS26.5 exactUUID
F3EF9DB8-0B0F-4757-B653-D1628269F6FF. Project-local build/logs/xcresult under
`.build/native-page150` and this report's artifacts. Normal platform storage scoped
in execution approval. Target initially shutdown; Xcode launched test and target
returned to shutdown. Post-test get_app_container returned shutdown error405;
retrieved only the exact operation-owned path printed by the successful test, not
a guessed prior container. No reboot/service reset/cleanup or unrelated simulator.

36probes:3/5/7pages,first/middle/last,light/dark,375/430point canvas. Public sizes
73/108.33/143.67×25.67pt; visible ink43.33/78.67/113.67×7.67pt. All ink lies
within measured frames, but substantial blank padding remains. Intrinsic frames
fail the tight-visual-body policy. No hardcoded subtraction introduced. Background
threshold measurement is limited to isolated flat probes, not a production labeler.

Evidence: `artifacts/native-capture/receipt.json`, `artifacts/geometry-audit.json`,
`artifacts/geometry.xcresult`; code`native_page150_audit.py` and opt-in
`NativePageGeometry150Test`. Existing corpus/666repairs unchanged.
Data:development-probe only. Integration:36native renders established; annotation
strategy not qualified. Model gates:not assessed. No inference/training on probes;
900regeneration and96new composition milestones remain incomplete, not accepted.

Next: qualify control-local rendered-alpha bounds, including native backing,
against composed pixels and interaction/background styles. Reuse capture pipeline
and public APIs; no private subview geometry or universal dot-margin formula.
Then integrate SwiftUI/UIKit annotation entrypoints and capture the planned corpus.

## Follow-up alpha qualification

72native captures completed in16.606s; bytes and dimensions audited in
`artifacts/alpha-audit.json`. Disabled automatic controls pass36/36 visual-bound
checks. Interactive prominent controls fail36/36: isolated transparent rendering
omits the composed backing material (up to15.333pt edge error). The helper remains
development-only and is not used by production annotation. No900image rewrite or
96composition milestone claimed. Next qualify explicit style-aware geometry;
do not generalize alpha bounds to materials without composed-image evidence.

RESIDUAL154companion reuses all72pixels: a style-specific proposal passes72/72
within0.5pt (`artifacts/style154-assessment.json`). Disabled automatic uses alpha;
interactive prominent uses public intrinsic frame. Recorded earlier3xpublic sizes
were reused, so2xequivalence is still inferred. No production integration. Next
batch should combine actual frame/style telemetry with96real compositions rather
than repeat isolated captures; unqualified styles fail admission individually.
