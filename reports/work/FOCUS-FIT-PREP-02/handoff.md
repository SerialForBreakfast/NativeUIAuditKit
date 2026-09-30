# FOCUS-FIT-PREP-02 — preparation and artwork comparison complete

2026-09-30; owner Codex; base1bb4590. No implementation changes or model execution.

| Outcome | Evidence |
|---|---|
| Software | Existing intake/crop paths execute successfully;37focused tests pass. New full-corpus trainer mode is proposed, not implemented. |
| Data | Two archives and96declared members verified;4calibration pairs accepted for diagnostic intake only. Existing928training members reverified, no admission changes. |
| Integration | All64TTRreference PNGs match local production bytes/pixels;8artwork plus8wrapper target crops render and replay. Producer audit has incorrect clamp flags. |
| Model | Not run; FDR019 findings unchanged, no release or training approval inferred. |

## Full-corpus preparation

[Canonical proposal](../../../Research/Plans/FocusFullCorpusFitPreparation.md)
defines one schedule, exact source/class loss mass, full-training diagnostics and
unchanged development checkpoint guards. `full-corpus-proposal.json` freezes928IDs
and weights,315development/18retention, source references and seal
`ef8001be1109177728ecd35ec8fd473bee31a6bf61782c08737070eb84a44537`.
Model-free source/crop checks pass. Native loss mass0.4positive/0.4negative; human
0.1/0.1.26same-label exact-pixel duplicate groups contain65training members; no exact
train/development pixel overlap. Duplicate IDs are not independent support.

Proposal is ready for approval, not launch-ready software. Next implementation:
versioned full-corpus weighted-fit adapter in the existing trainer, tested then actual
preflight. A training assignment must explicitly approve that sealed schedule; no
automatic run, sweep, download or candidate promotion follows this handoff.

## Artifact receipt and native intake

Existing `synth05_receive.receive` ran with only these two named entries.45GiB local
free,5GBreserve enforced, bounded extraction into fresh ignored storage; no producer
source executed or peer file deleted. Original archive bytes retained.

| Archive | Bytes | SHA256 | Members |
|---|---:|---|---|
|ttr-artwork-qualified-four-pairs-20260930-r1.tar.gz|11636989|36938427efb849e61861b1cc79a12483008c3c5511bbd0efad6023e3709acd87|27declared payload files verified|
|ttr-retained-crop-audit-20260930-r1.tar.gz|1623999|abd26c20e2d9bd5dc39837232b0123638f83587d70b02e5a2699dc29f07f8755|69declared payload files verified|

Actual `ttr_focus_manifest.py --test-only` accepts4pairs, complete4target recipe
coverage. Native bracket/metadata checks and image hashes pass; outputs remain
test-only development diagnostics. Actual `focus_geometry_diagnostic.derive` renders
and replays8nominal-artwork crops and8wrapper crops:0blocked/0failed. This resolves
the prior absent artwork geometry boundary for this delivery, not all recipes.

## Crop parity and findings

All64reference crops independently rendered with `focus_runtime.invoke` using bounded
item/decoded-pixel batches and no model. Original source/metadata and reference hashes
verified before comparison.64/64byte parity,64/64RGBApixel parity; runtime identities
and every comparison in `crop-parity.json`. Production16%expansion/256square retained.

The32unique crop contact-sheet views were inspected: focused card bodies visibly
enlarge/change highlight; neighbors appear as thin slivers. Nominal wrapper/artwork
bounds coincide in this label-free sample, so it does not test caption separation.
Native shadow/glow containment cannot be established from nominal layout bounds.
No model scoring was performed; neighboring content's effect on predictions is unknown.

**Producer reporting defect:** all64`image_edge_clamped` fields are true, yet all
expanded windows are inside3840×2160images. Independent out-of-image checks yield0.
Differences from algebraic expansion are at most3.41e-13pixels. `audit.swift` line45
uses exact CGRect inequality after intersection, confusing rounding with clipping.
Request geometric boundary tests or documented tolerance and a versioned correction;
preserve original evidence. Pixel parity is unaffected; no recapture needed.

## Verification and coordination

- Archive copy/extraction,96member validation,4pair intake, both geometry roles,
 64crop comparison and full-corpus input/loss accounting all completed with exit0.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-review/bin/python -m unittest
 test_focus_geometry_diagnostic test_harvest_derived_views`:37tests pass in1.703s.
- No implementation changed; prior offline Swift build/123tests remain recorded in
 FOCUS-FIT-01, not rerun or represented as new evidence.
- Exact receipts and crop finding published to `nuiak/status.yaml` packet
 FOCUS-FIT-PREP-02 on verified SharedStatusFile; see `coordination.md`. Peer
 acknowledgment and sender cleanup are separate, still pending at handoff.

All assigned preparation/receipt/comparison work complete. Remaining60pair capture
requires separate runtime scope; new calibration data is not training-admitted.
No background process or device lease remains from this tranche.
