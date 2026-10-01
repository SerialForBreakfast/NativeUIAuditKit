# Focus growth 02 — input preparation and weighting repair

Assigned October 1, 2026; owner Codex. Implement the approved growth-analysis
follow-up locally. No production preprocessing, labels, split or model changes.

1. Add an explicit `baseline-fixture-budget-v1` assembly weighting policy. Keep
   legacy behavior for existing sealed inputs. Preserve every non-fixture weight;
   redistribute only baseline fixture mass, separately by label, across old and
   added fixture controls equally. This deliberately changes within-fixture
   sampling, not OS/human budgets. Empty additions must be exact identity.
2. Prepare experimental local+scene+geometry inputs from sealed retained protocols.
   Reuse verified production crops; resize the whole scene to one aspect-preserving
   768x432 letterboxed viewport. Rasterize candidate masks in that common viewport
   and expose normalized current bounds, never focus/native callback/oracle size.
   Explicitly account for unavailable original geometry instead of inventing it.
3. Test actual pixels, geometry, clipping, global resize invariance, malformed
   bounds, hashes, forbidden roles and deterministic candidate mapping. Run the
   builder on retained admitted data and report usable/blocked membership.

The artifact format is diagnostic-only. A scene/mask is not an encoded feature and
cannot be fed to the current 576-feature head silently. New architecture, encoding,
training budgets and CoreML parity require the subsequent controlled experiment.
Prepare evidence for that decision; do not spend a run confounding weighting with
new representation. Existing fixed threshold and all selection gates remain.

Cached-feature reuse: the experiment accepts an explicit `reweightPolicy` while
retaining the original assembly and encoding receipt. The encoded protocol's
recorded runtime remains historical; current trainer code is pinned separately.
All other encoding-contract fields still match exactly. Reweighting does not grant
a run approval and does not require re-encoding identical inputs.
