# SYNTH05 native-label and crop review

2026-09-29, current NUIAK Fixture consumer worker. Agent visual review, not human
annotation or model prediction. All 50 numbered pairs on 13 sheets in
`qa-final/review-sheets/` inspected. Final sheet hashes are identical to the first
reviewed `qa/review-sheets/` output; final inventory binds exact original and crop
hashes, IDs and per-frame measured bounds. All 100 production crops have visible
target content, usable context and focus differences consistent with native labels.
No ambiguous or rejected pair observed. Raw originals preserved.

Rows 1–4: native button analogs. 5–20: flat/icon/linear/radial artwork. 21–24:
Settings-row analogs. 25–28: selected-tab analogs. 29–32: checkerboard with mixed
sizes. 33–36: generated imported-owned asset. 37–42: nested selected-parent/child
controls, including the last two pairs on sheet11. 43–46: texture;47–50: typography.

Browse deliberately stays selected while another control has native focus.
Its unfocused crop remains bright; the focused crop adds elevation/expansion.
This is not a double-focus labeling error. Native focus is exactly one per frame;
selection is separately represented by `isSelected`, and nested child linkage by
`parent_element_id`. The six nested pairs preserve the selected parent across all
24 bracket snapshots. This is a useful hard negative, not proof of system-tab parity.
The visible "Selected" subtitle is a synthetic convention and potential shortcut;
future corpus variation must not make it the sole cue distinguishing these states.

All backgrounds are dark and largely empty. Repeated motifs/colors and identical
sweep states limit effective diversity. Imported-owned is a 32×24 generated asset,
not licensed photographic coverage. Wide buttons/rows stretch strongly in the
unchanged 16%-expanded 256×256 production cropper; observed distortion is expected
preprocessing, not a newly introduced crop bug or proven cause of model failure.

Accepted for development diagnostics only. No training approval, independent-source
qualification, final-challenge inspection, model scoring or directional-transition
claim. Automatic UIKit observations supply labels; no new human annotation needed.
