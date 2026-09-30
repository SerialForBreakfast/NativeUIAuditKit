# Artwork audit: useful contrasts, but a narrow focus appearance

All150 admitted artwork pairs/300crops audited;559 distinct frame/crop files
decoded and hash-checked. Source metadata binds back to the frozen frame hashes.
No identical focused/unfocused crop pixels within a pair. No labels, crops,
training membership or models changed. `audit.json` is the complete input/pair index;
`audit.py` reproduces the one-off audit against the frozen FDR015 protocol.

## What the count actually represents

| Evidence | Observed support | Limitation |
|---|---:|---|
| Artwork training pairs |150 across27source IDs|Source IDs are not independent families|
| Explicit `native_image` effect |24pairs,16% of artwork|Only4% of total training probability under the existing25%-artwork sampler|
| Explicit artwork content in those24 |3motifs ×4targets ×2backgrounds|Flat, crescent icon, linear gradient; assets arrays empty|
| Native-image layout |24/24 fixed4control row,440×420reported boxes,labels always shown|No native-image dense Home grid or photographic assets in this admitted subset|
| Remaining effect metadata |126unspecified|Do not retroactively label all as custom rings; visual sample predominantly outlines/glows|
| Reported focused/unfocused target area ratio |1.0 for150/150|Fixed geometry does not prove wrong native identity or invalid labels|
| Reported box aspect |75at440/420;75at480/696|Different from the two real Home target boxes, both approximately1.59wide/high|

Five declared related-group values remain: appearance-seed7-all-presets19pairs,
appearance-a2-development32,fixture-procedural-development64,seed:29001 twelve,
retained-fixture-development23. These are not five proven independent renderers;
the known shared fixture ancestry must remain connected for leakage decisions.
All24native-image pairs deliberately place focus on a competitor for the negative
state. That is useful hard-negative evidence, not something to discard wholesale.

## Visual inspection and competing explanations

Seven deterministic sheets cover the first admitted pair from each of27sources;
all27representatives reviewed. This is representative inspection, not a visual
audit of all150pairs. Metadata and byte checks cover all150.

- The21 non-native-image representatives show thin outlines, bright rings or glows.
  Many preserve essentially the same tile body across focus states. “Photos-like”
  is a procedural mountain-and-sun image, not a real Photos/Home app tile.
- All six native-image representatives visibly enlarge/brighten the tile and add
  shadow/glow. This is a counterexample to “our training never contains native
  focus.” But their artwork/layout/label treatment is narrow.
- In the inspected native-image full frame, measured boxes stay fixed while the
  visible tile grows; captions remain visible for both states. Crops retain that
  title/context. The human Home annotations enclose the icon body and the focused
  icon has a newly visible title. This is a crop-target/geometry convention question,
  not permission to automatically tighten boxes or segment shadows.
- The two failed Home targets have area1.579× and1.669× the median competing box
  area in their own frames. Their ranks are2 and8. Relative enlargement exists in
  the annotated frame geometry but is absent from the current crop-only feature
  vector. It is not universally sufficient: the largest-box baseline is only8/13.

Priority hypotheses: (1) appearance/content mismatch is supported by the audited
native subset; (2) fixed synthetic versus per-state real box/context treatment is
a plausible transfer mismatch; (3) independent crop BCE permits content shortcuts
that same-control pair learning could reduce. None is established as the single
cause. We have not fitted a threshold or inferred new ground truth.

## Producer handoff, checked during this audit

Verified SMB metadata hashes for `ttr-next-native100-selection-20260929.json` and
`ttr-canvas-v2-geometry-density-20260929.md`; see `producer-metadata.json`.
The25scene selection lists64 native-image pairs, adding checkerboard, radial
gradient,texture and typography to the three admitted motifs. These are **planned/
producer-reported members**, not64 newly accepted pairs. Neither native100-r2 nor
canvas-v2-native12 has a local receipt in the reviewed artifacts; no archive was
copied or inspected in this retained-data audit.

Producer status observed23:25UTC reports native12 captured and remaining42 stopped
on toolchain probing; an offline repair exists but live acceptance remains pending.
Its minimum72pt repair concerns the three short Library controls, not demonstrated
resolution of the artwork box convention. Canvas-v2 adds density/background
options; source capability is not proof of captured pixels or training benefit.
No new capture is needed to start receipt/QA of the already-published artifacts.

## Recommendation

Do not scale unchanged recipes or ask the human to redraw more Home screens.
Use one same-data **paired-loss head experiment** to test whether learning the
focused-minus-unfocused difference helps, keeping pretrained features and all
guards fixed. [Exact proposal](next-experiment.md). Do not append raw box-size
features yet: these150training pairs have zero recorded within-pair size change,
so they cannot supervise the very enlargement signal we want to learn.

In parallel, next data assignment should receive/QA the existing native12/native100
archives, then answer the box convention and useful-contrast coverage questions
before new collection. This is independent of whether a model passes; neither
team should wait for the other to produce a successful model first.
