# CHANGE-80 — adaptation complete, localization still unqualified

Completed one approved DTM018change-head adaptation plus independent retained-rank
diagnosis. No capture, new data roles, export, promotion, peer edits or Git writes.
44train/5exposed development and all original evidence preserved. No SMB update:
this local result does not change the existing producer source-publication request.

## Controlled result

DTM013initializer; only its existing change submodule updated.600epochs/full44pair
batch,Adam0.0001,seed42,CPU2threads,no augmentation,BCE-with-logits,fixed-last.
Ranker DTM017and every geometry parameter frozen. Not equivalent to DTM013's original
joint/augmented training; this tests supervised change-only adaptation.

| Group | Change correctness before → after | Joint with frozen boxes |
|---|---|---|
| Original32train |32/32→32/32|32/32|
| Added12native train |8/12→12/12|12/12|
| Exposed Settings5 |5/5→5/5|0/5|

All four native misses corrected on training data. No independent final generalization
claim; no abstentions at the existing threshold. Settings box selection remains bad.
All non-change weights bit-identical; saved checkpoint replay exact.

## Ranking companion

Retained DTM017Settings labels/proposals:10endpoints across9unique images. Eight of
nine wrong endpoints select glyph/icon-sized regions whose largest extent is<100px.
No positive candidate in these retained train/development labels occupies that bin.
Most correct proposals now rank2–5, versus previously20–27; one remains22nd. This
supports a size/context-loss hypothesis, not a proved cause or approved hard filter.
Do not discard small controls in production from this limited corpus.

Next comparison should preserve crop bytes and add normalized original box width/
height to the visual ranker. This is a learned input, not a Settings-tuned threshold,
and must be tested against the same44/5membership. Independent small-control coverage
remains necessary before claiming robust transfer.

## Implementation / verification

Existing trainer dispatcher handles transition-change-adaptation. Existing direct
model module owns fit_change_head; existing encoding/model architecture reused.
Preparation builds49paired tensors once; preflight rechecks source references, corpus,
admission, labels/membership, dependencies, checkpoint/control bindings and approval.
Missing approval CLI preflight exit2 as expected; authorized CLI exit0.

21focused Python tests pass1.674s: change80,temporal68,native77,batch79,rank75. Generated
tests check gradient scope, bit-exact geometry, reload parity, bad shapes/ranges/labels/
NaNs. Existing admission/cache regressions retained.134offline Swift tests/build pass;
logs .build/change80-*. git diff --check passes. Actual checkpoint and completion are
under NativeUITrainer/focus_ring_runs/change80-dtm018; raw arrays are ignored.

One-time source/encoding26.260s; fit9.501s,total run10.574s; PID43862,exit0.
Checkpoint SHA25608c0f6feb27035cbc56d9dbd85b45cd8b623348f81583bbdba3b2b62e1192039.
Protocol eadbde625134279aed9f32a581ba75a4d27f78ebd4087da60d2ebb28b3079378.
No corpus pixels/crops were generated again. No architecture sweep or automatic retry.

Software verified; approved development-training eligibility unchanged; local model
integration verified; independent/production model gates not established. Preserve
shipped models. Next substantial tranche: geometry-aware ranking comparison and
small-control coverage audit, while rich24source compatibility proceeds asynchronously.
