# Perception/intake completion — 2026-09-22

Assigned to the architect by the maintainer: complete PER-02/PER-04 offline
corrections and review FOCUS-LAUNCH/EVIDENCE-AUDIT. Prior worker turns are complete;
existing implementations and unrelated dirty operational reports are preserved.
No live capture, real-data inference, training, producer edits or promotion.

## Frozen implementation decisions

- Extend the existing perception CLI with an optional independent observation
  input and deterministic geometry/OCR relation baseline. Observations contain
  proposed rows, chevrons, dialogs, button focus scores and OCR text, never truth
  labels. Associate ambiguous boxes to unknown; use a reviewed small English
  destructive phrase set, never guess informational from absence of keywords.
  Oracle-box component evaluation may replace geometry/element roles, never semantics or
  focus. Report that component separately from actual proposals.
- Preserve imported prediction support but label it externally supplied, not
  observed model execution. Bind report to manifest, predictions, observations,
  evaluator, settings and declared adapter artifacts. Missing shipped/TTR results
  remain unavailable. No model recommendation from asserted source strings.
- Report source/partition/theme/control/locale/focus-treatment slices and
  journey-group support. Exact deterministic group-bootstrap uncertainty is
  diagnostic only. Missing support yields null metrics. Measured imported timing
  requires scope, machine, OS and warm/cold designation; fake timing stays test-only.
- Extend current completed-bundle extraction to physicalFixture using explicit
  NUA review evidence bound to receipt/index bytes, with preserved source context.
  It uses the shared frame validator and existing v1.2 → production v1.3 recrop
  path, not a competing crop engine. Physical review declares device/run/capture
  context; it is not cryptographic attestation or training approval.
  Frame-bound physical native observations must positively resolve one focused
  target/reference, be at most150ms old and stable for at least150ms. This is an
  explicit NUA review envelope, not a producer-wire change; missing fields cannot
  be fabricated. Check normalized/pixel geometry against actual image dimensions.
- The physical readiness CLI admits the shared byte-backed crop contract in
  addition to legacy inspection-only metadata. Optional baseline preparation and
  score ingestion call existing FocusRing protocol functions; no implicit inference.
  Separate oracle-crop results from absent proposed-box results. Missing hard-negative
  support is reported unavailable for diagnostic pilot scoring, never a gate pass.
- Strengthen shared duplicate isolation with decoded RGB pixel hashes, since
  different PNG encodings must not evade the demonstrated leakage check.

## Completion

Exercise the real CLI paths on explicit generated test-only physical and simulator
fixtures, then adversarial source/hash/callback/geometry/leakage/abstention tests,
offline Swift build/test, focused existing suites, and evidence-backed handoff.
Keep four outcomes separate. Software review can finish; genuine integration and
model quality cannot. Next data step remains producer fix → authorized smoke →
qualified development pilot, not immediate full training.
