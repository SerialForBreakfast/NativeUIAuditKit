# Big Dog evaluation tranche — October6

Four archives received with exact size/SHA256; safe extraction bounded to300members,
64MiB expanded,16MiB/member. Counts/bytes: BD25 9/5609671;BD26 7/227202;
BD27 10/1599198;BD28 9/4507888. Source originals retained; no deletion or Git writes.

14 supplied tests pass (4+4+3+3). Tests use project-local copies of pinned resident
fixtures and import-root rebinding, not altered worker source. No production code
changed, so no redundant Swift suite. Source reviewed before execution.
BD27 independently regenerated1152pixels/state/three-frame truth/difference rows
and reconciled72metric rows. BD28 exact512selection and12representative choices
reproduced from returned metadata/descriptors; this does not reverify source pixels.

## Results and decisions

- BD25:262category rows and ranked atlas reproduced from621cached cases. Six
  supported categories; no padding to ten. Unmatched FP affects583cases, below-
  threshold geometric candidates528, no operating overlap417, localization366,
  duplicate FP298, missing same-class proposals111. Categories/models overlap;
  these are not summable independent errors. Representative selection should spread
  across images rather than return three boxes from one image.
- BD26: counts distinguish1758unique source IDs in034 and249in035 from repeated
  exposure. Existing report's three lowest-support classes:webContent/actionSheet/
  alert. This is coverage only, not a final acquisition priority or model quality
  threshold. Reproduced negative/fractional class ID and NaN-center acceptance in
  audit(); helper needs strict validation and actual-label pin checks. Existing
  report not invalidated without evidence those inputs occurred in real data.
- BD27: at.005, whole-frame false-stable48/48tiny-motion windows; tile0/48. On
  small irrelevant background animation whole-frame false-unstable0/72, tile72/72.
  This is a sensitivity/relevance tradeoff, not a deployable threshold decision.
- BD28:512sample descriptors/12distinct representatives and5256metadata records
  returned. Proxies are not semantic labels or rights approval. Original512pixels
  were not re-transferred/redecoded locally; source and tests reviewed, not full
  independent asset measurement. Portable paths and remaining negative tests requested.

## Model and next action

Published/read back `nuiak/responses/nuiak-20261006-bigdog-review221.json`,
5148bytes, SHA256 `9c882ea8254e115205e1a9fad7646456a164a59528ae045a4be472fee921b696`.
Peer acknowledgment is separate and not yet observed. No sender files deleted.

035 has no published start/checkpoint at this review; latest219-specific message
remains validation_membership preflight failure. Explicit binding approval already
published; follow-up references the same assignment, not a new GPU experiment.
Without returned candidate bytes, model evaluation is concretely blocked, not failed.

The [review/receipt](../../coordination/bigdog-review221.json) gives exact fixes,
<=2CPUhours/128MiB, independent of035, and TTR-facing implications. Do not launch
another blind candidate while this approved retention hypothesis awaits execution.

Software:14tests pass; reusable-helper repairs pending. Data roles unchanged.
Integration: bounded transfers verified, native runtime not tested. Model gates:
not assessed. Next substantial tranche: independently accept035 source/accounting
and score2400retained frames; combine native/ROI/full-frame retention with coverage
and failure atlas; select one evidence-backed data or training intervention, retaining
shipped models and all evaluation boundaries.
