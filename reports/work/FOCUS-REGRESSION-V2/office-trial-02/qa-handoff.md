# Trial02 production crop QA and diagnostic audit

## Outcomes

- Software: circle-only normal focus indicators implemented;11 actual Qt tests and
  offline Swift build/test pass. Hover details, pinning and warning symbols retained.
- Data:8 reviewed frames/82 controls;82/82 production crops,82 distinct crop pixels.
  Diagnostic-only, no training admission. Raw screenshots/revision unchanged.
- Integration: actual CLI crop→audit→review-sheet workflow completed. Production
  16%-expanded256×256 crops use bounded item/pixel batches and pinned runtime receipt.
- Model gate: unassessed. No inference, training, export or promotion.

## Evidence and findings

Input: review-batch/review-revisions/20260928T225131Z-056fc495/revision/revision.json.
Outputs: qa-20260928/crops/crop-qa.json and qa-20260928/audit/audit.json (sealed
hash-bound reports); qa-20260928/audit/review.html and per-frame context/crop sheets.
CLI crop and audit commands exited0. Both reports retain exact source references.
The separate human completeness receipt covers all8; the generic audit's
candidateCoverage=unknown does not consume that separate receipt or replace it.

Support:8 focused/74 unfocused;49 listRow,1 imageView,14 label,18 focus:tabItem.
Four named screen contexts, one source session. No hard audit issues, no exact crop
duplicates. One near-frame heuristic warning: recorded-676/687. Visual inspection
of both context sheets shows Games→Apps focus change, not redundant observations.
Retain both, grouped as related development evidence, not independent sources.

Sampled visual QA: both above tab contexts and recorded-319 crop sheet inspected.
Static headings/help text appear among label annotations. Keep these annotations;
they may be background negatives, but do not treat them as confirmed focusable
candidates. The single imageView's focusability also needs explicit interpretation.
Square-resized wide rows show the expected production aspect distortion, not a
reason to alter human geometry or silently change preprocessing.

## Next assignment

Prepare a versioned development-evaluation admission proposal binding this revision,
completeness receipt and focus-role schema. Separate interactive candidates from
static background negatives; preserve all source annotations. Reconcile prior
operator concern about unsettled App Store frames with the later settled attestation
before admitting them as settled-focus benchmark data. Do not infer settled state
from blank content alone. Reserve this whole correlated session for development;
it must not become training or untouched challenge evidence without a new decision.
No more bulk annotation requested now. Role-aware model evaluation remains separately
approved work; prior evaluator intentionally rejects role-bearing revisions.

Local UI refinement loads on next editor restart; current window is not interrupted.
Coordination not applicable: no change to TTR's next action.
