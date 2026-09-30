# Make the synthetic focus corpus match the deployed task

## Decision

**Do geometry and contrast qualification next, not another training run.** FDR016
left the two complete Home examples at ranks2and8 and increased real false positives
from1to16. That makes artwork the first target. It does not establish geometry as
the sole cause or prove a different crop will fix the model.

Deliverable of this completed preparation tranche: an exact retained reuse proposal,
a producer-matched geometry contract, and a32-pair diagnostic trial specification.
No model executed, no image modified, and no training membership changed.

## What we can reuse

[reuse-proposal.json](reuse-proposal.json) pins all96 nonduplicate usable members
and their original manifests;384frame/crop files rehashed. The16excluded members
remain explicitly listed:13duplicates and3geometry holds.

| Retained subset | Pairs | Proposed purpose | Limitation |
|---|---:|---|---|
| Native buttons/rows/tabs |32|Maintain control coverage in a future admitted training assembly|Related development sources, not an independent exam|
| Caption-inclusive native artwork |60|Wrapper-context baseline and contrast reference|Not tight Home icon-body geometry|
| Caption-free native artwork |4|First geometry inspection references (numbers33–36)|One flat-artwork recipe; nominal wrapper still does not measure enlarged pixels|

Do not simply append96pairs and claim a production corpus. None is newly admitted
to training. Retained telemetry has no additive artwork_geometry fields; recovering
them would require new measured evidence, not retroactive70%height calculations.
No existing review needs to be redone by the human annotator.

## Geometry contract: preserve roles rather than overwrite boxes

Current production remains makeCrop-v1: incoming detector control box in top-left
pixels,16%per-edge expansion,256×256 resize. No public API/taxonomy change proposed.
The future adapter is local/diagnostic until a separate parity and admission decision.

| Role | Meaning | Consumer action |
|---|---|---|
| Existing element bounds |Measured focusable wrapper, possibly caption-inclusive|Always preserve; legacy route unchanged|
| artwork_layout_view_bounds |Nominal image layout excluding caption|Opt-in experimental crop anchor only; never call it visible-body ground truth|
| Native presentation/body bounds |Enlarged rendered artwork body|Currently unavailable; do not derive it from layout or native focus identity|
| Human/detector body bounds |Per-frame visible control body under the existing annotation convention|Existing real-data reference; detector agreement still needs measurement|

TTR's inspected source proposes optional elements[].artwork_geometry with version1,
source artwork_layout_view_bounds, pixel_bounds and normalized_bounds; explicit
unavailable_reason for not_rendered/clipped/projection_failed, and
presentation_bounds_status=unavailable_native_effect_not_measured. This is an
inspected source contract, **not consumer implementation or live qualification**.
Producer reports76host tests/5wire groups/unsigned compile; no new runtime capture.

The next consumer adapter must preserve these values through intake, verify their
frame/element/native-bracket binding, and generate separately versioned wrapper and
nominal-layout crop manifests through the existing production cropper. Role+source
manifest+element+frame hash+bounds+runtime must enter derived identity. Explicitly
requested but unavailable layout geometry blocks that experimental crop only:
never silently fall back to a wrapper or discard the usable original.

Acceptance cases: old field absent; valid role; unavailable role; nonfinite/outside
bounds; contradictory present/unavailable rectangles; normalized/pixel disagreement;
changed source/frame/member hashes; different pre/post element binding; unknown
version/source; role-specific output identity; unchanged legacy crop pixels.
Use generated offline fixtures and the real CLI, then a producer sample. No guessed
wire examples may be claimed as producer interoperability. Final challenge input
must remain rejected by this development lane.

## One bounded matched diagnostic trial — proposed, not dispatched

**Collection target:8scenes,4tracked targets each,32focused/unfocused pairs.** This
is enough to inspect mechanisms, not a new qualification quota or a production corpus.
Every scene has one observed focus owner. All visible competitors retain native
identities/bounds; dense scenes have more controls but only four common targets are
swept. Reuse native focus and automatic labels; human input only for ambiguity.

| Priority and matched scenes | Change one factor | Question answered |
|---|---|---|
| P0: labeled vs label-free |Caption presence, same assets/layout|Does caption reserve work; how do wrapper/layout crops differ?|
| P0: dark vs bright artwork assignments |Swap luminance between target/competitors, same geometry|Can an unfocused white tile outshine a focused dark tile without corrupting labels?|
| P1: sparse4 vs dense12 |Neighbor density, four common targets and same artwork|Does context capture competitors or truncate the target?|
| P1: smaller vs larger bodies |Card size/aspect within supported geometry, same artwork|Do measurement and crop enclosure remain consistent?|

Freeze recipes, actual rendered parameters, build identities and source ancestry
before dispatch. Use existing approved owned assets/procedural motifs; no external
asset download implied. Avoid coupling brightness with focus state or one tile
position. Matched variants stay in the same development source group, not split
across training and an allegedly independent test. No full factorial or thousands
of pairs until this bounded check answers the questions.

Producer must confirm each contrast is actually supported; unsupported variants
stay unavailable, not substituted silently. Capture both states with native brackets
and per-frame geometry, original PNG hashes and raw telemetry. Preserve failed and
unattempted rows. Respect the existing10GiBproducer reserve and fresh target/ownership
checks; choose an explicit target/time budget in the later capture approval.

Consumer reviews all32pairs in grouped sheets, looking for body enclosure, caption
overlap, selected-but-unfocused contrast, competitor intrusion and exact/near layout
redundancy. Native identity plus geometry checks provide labels; image brightness
or requested remote intent does not. An unavailable enlarged-body measurement is
not a failed native label and must not become invented ground truth.

## Experiment after the evidence, not before

1. Implement/test the local diagnostic adapter against the exact producer contract.
2. Under separate target/capture approval, receive the32-pair matched trial and
   compare wrapper/layout production crops. No model is needed for this check.
3. Choose a single truthful box convention from that evidence; if nominal-layout
   crops still mismatch detector/body boxes, stop that hypothesis. Request measured
   body geometry or pursue a different representation—do not inflate rectangles.
4. Freeze a member-bound admission proposal: keep current363train+9retention and
  453real selection memberships explicit; any additions or replacements are listed,
   deduplicated and grouped. Do not silently relabel the60caption-inclusive pairs.
5. Request one logged experiment with unchanged release guards and comparable
   evaluation. Freeze training configuration only after geometry/admission choice;
   do not allocate FDR017 yet. Prefer testing one primary change rather than mixing
   new loss, new encoder, new thresholds and new data in one unexplained result.

Report the two Home ranks/margins, artwork misses/false positives, complete-frame
wrong/no/multiple decisions, all retention results, and supported per-stratum
metrics. Keep the existing0.85threshold and eligibility rules; zero eligible epochs
means no selected checkpoint. Do not use these repeatedly inspected real screens
as untouched qualification. Deployment still requires export/parity and broader
source-separated real-task evidence under separate assignments.

## Owners and dependency order

- NUIAK can implement the diagnostic consumer against source-pinned fixtures now;
  runtime qualification waits only for a representative producer sample.
- TTR confirms the contrast capabilities and stabilizes caption/measurement output;
  capture waits on storage, explicit target/time scope and human authorization.
- Corpus admission waits on actual crop evidence, not on an improved model.
- Training waits on a frozen admitted corpus and separate run approval.

There is no model→capture→model circular prerequisite. Offline consumer work and
producer preparation can progress in parallel; neither is proof of production readiness.
