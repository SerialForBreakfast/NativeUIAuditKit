# Four-frame review receipt and crop QA

## Correction resolved

User explicitly confirmed: “yes. Ghost is focused.” New `ghost-confirmed/revision.json`
preserves parent reference and changes only recorded-598:new-1 from unfocused to
focused, with matching editor snapshot. Original revision and live editor untouched.
`ghost-confirmed-qa` reran production crop QA:79/79, no audit issues, all crop pixels
identical to previous QA. Final counts4focused/75unfocused; one positive per frame.
The prior label clarification below is resolved. Admission draft remains unapproved;
training/source admission and execution decisions remain separate.

## Original receipt

2026-09-30. Explicit revision20260930T234213Z-2517905f received from user.
Source: FOCUS-RETAINED-NEXT-15/review-batch-final/review-revisions/
20260930T234213Z-2517905f/revision/revision.json. Originals unchanged.

Existing continuation CLI completed production crop QA, exit0.79expected,
79completed,79distinct decoded crop pixels; audit issues empty.

| Frame | Focused | Unfocused |
|---|---:|---:|
|598|0|23|
|728|1|18|
|811|1|22|
|895|1|13|

Protected/reserved metadata and existing validation crop hash comparison found no
exact frame/crop overlaps. Original training/development/retention crop comparison
found no exact crop duplicates. This is not an independence claim; source review
and explicit admission remain required. Admission draft remains approved:false.

User is unsure about frame598's all-negative labels and requested the image.
Ghost poster appears enlarged; this is an assistant visual observation, not a
replacement human label. Current sampler requires both label buckets per admitted
frame; preserve all23negatives pending clarification rather than invent a positive.
Other56controls remain available for admission review independently.

Software: unchanged tested tooling. Data: crop QA pass, label clarification pending.
Integration: actual review/crop/audit CLI succeeded. Model: not run.
No TTR action changed; coordination not applicable.
