# Supplemental human review — production crop QA

Input: coverage-supplement-01/review-revisions/20260929T191036Z-583a5cf2/revision/revision.json.
Human revision records8 reviewed frames and155 reviewed controls. Frozen revision,
snapshot, image and batch bindings passed the existing audit; originals unchanged.

## Outcomes

- Software verified: pass. Existing crop CLI produced155/155 crops through production
  FocusRingClassifier.makeCrop,16% expansion,256×256, bounded16-item/80Mpixel groups.
  No model argument was supplied. Audit command exited0; no structural issues.
- Data eligible: diagnostic-only.155 distinct decoded crops;6 focused and149
  unfocused annotations. Candidate completeness remains unknown for all8 frames.
  Two zero-focused frames require targeted label confirmation; not a whole-corpus
  semantic-label pass or complete-frame selection qualification.
- Integration qualified: local revision-to-production-crop path passed; no TTR
  runtime/device qualification performed.
- Model gate: not assessed. No inference, training, export or admission.

## Narrow follow-up — no redraw requested

| Editor frame | ID | Human annotation | Agent visual observation, not ground truth |
|---|---|---|---|
|3|recorded-742|19 unfocused,0 focused|Control6 Watch Now has a prominent outline; confirm whether focused|
|5|recorded-653|21 unfocused,0 focused|Control1 Lioness card is enlarged; confirm whether focused|

Zero focus is not automatically invalid, so the structural audit correctly does
not rewrite these states. Confirm actual state; if either flag was omitted, update
that control in the existing editor and Finish review into a new immutable revision.
Preserve this revision and QA evidence. No need to redraw or repeat all8 frames.

Support:80 collectionItem,54 listRow,14 label,4 primaryButton,3 imageView.
These155 controls are not155 pairs and do not add independent source families.
Seven frames are Paramount+; broad app/overlay/player coverage remains incomplete.

Reports: crops/crop-qa.json, audit/audit.json, audit/review.html and numbered context
and crop sheets. Runtime/source/helper hashes are pinned in crop-qa.json.
Commands: human_annotation_review.py crop-qa BATCH OUTPUT --revision REVISION;
human_review_audit.py REVISION CROP-QA OUTPUT; both exited0.
No source code changed; full Swift rebuild/tests unnecessary for existing-tool data QA.
Coordination not applicable: this local review result changes no TTR action.
