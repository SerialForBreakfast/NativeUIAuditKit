# Offline focus diagnosis — 2026-09-27

**Recommendation: request specific additional data; do not launch the unchanged
candidate.** Preserve the candidate proposal and shipped artifacts. This is a
development-exposed diagnosis, not independent qualification or causal proof.

## Frozen evidence and reproduction

Authoritative local outputs: [input index v2](input-index-v2.json),
[machine-readable diagnosis](analysis-v2/diagnosis.json),
[complete accounting](analysis-v2/accounting.json),
[95 numbered sheets](analysis-v2/evidence.md), and
[230-pair audit](analysis-v2/candidate-coverage.json).
The initial v1 report is retained but superseded: v2 additionally joins all candidate
geometry and displays matched opposite-state crops on paired failure pages.

Input-index SHA-256 `13424100ecaf90942d9c3128a86948c628c08b2dca86ec4a6e2a1371633eeedf`;
seal `e500bfb32145d93b30bfcff49ba6fc8d4e2632520b43f0a334c6d2371561b064`.
It pins34 metadata/implementation dependencies and2,107 unique image paths, covering
1,248 validation scoring rows and460 candidate/retention crop rows. All image byte
hashes, decoded pixel hashes and crop dimensions pass; zero blocked or excluded files.
All3,744 predictions match exact ordered membership and the frozen protocol seal.
Metadata includes model identities and original runtime/backend versions; no model
artifact was loaded by the diagnostic CLI and no predictions were regenerated.

All published metrics, individual frame decisions and accounting reproduce exactly
using `focus_surface_evaluation.score`. Fixed0.85, original boxes, base variant,
production16%/256 crops. The48 competition frames each contain24 declared candidates.
The96 paired samples represent48 same-control pairs, not96 independent scenes.
Native/oracle boxes isolate classifier behavior; this is not end-to-end detector accuracy.

| Model | Paired TP / FN / FP / TN | Competition TP / FN / FP / TN | Unique / wrong / none / multiple |
|---|---|---|---|
| Shipped |38 /10 /44 /4|38 /10 /988 /116|0 /0 /0 /48|
| FDR-007 |2 /46 /14 /34|2 /46 /299 /805|1 /22 /0 /25|
| FDR-008 |2 /46 /1 /47|2 /46 /23 /1081|1 /22 /24 /1|

Shipped scores were produced by CoreML CPU; candidate scores by PyTorch CPU.
Their original runtime identities remain pinned. These comparisons do not establish
export parity or comparable latency. No runtime timing experiment was performed.

## What the retained scores explain

Distributions below use paired targets only; full min/quartile/mean/max, separate
competition populations, source/control/theme/stratum breakdowns, every paired
difference and every rank/margin are in diagnosis.json.

| Model | Median focused | Median unfocused | Median focused−unfocused | Positive paired differences | Strictly top-ranked true focus |
|---|---:|---:|---:|---:|---:|
| Shipped |0.997070|0.996582|−0.000488|19/48|0/48|
| FDR-007 |0.007631|0.138137|−0.073568|5/48|1/48|
| FDR-008 |0.001621|0.001355|0.00000118|25/48|1/48|

FDR-008 reduces competition false positives299→23 but leaves22 wrong selections
and introduces24 no-focus frames; unique-correct stays1/48. Both candidates miss
all44 non-button focused targets. Dense media16, artwork8, placeholders8 and dock12
are supported diagnostics; actual Photos buttons are unavailable. Both families
are dark-theme; independent-source status remains unknown, not absent pixels.

True-focus rank is an interval for ties, not an alternative selector. Both candidates
have a negative true-focus-versus-best-competitor margin on47/48 frames. Median
margins: shipped−0.002930,007−0.968065,008−0.055307. Shipped top-score ties explain
why nominal rank1 does not imply unique selection. At any scalar threshold, a
strictly higher wrong competitor cannot be excluded while retaining the lower
true target. This rules out a threshold-only unique-selection repair for those47
retained candidate frames; it does not predict performance on new data.

The only unique-correct case for both candidates is `album_grid:synth-6`, detail
action00. All23 FDR-008 competition false positives are detail-action controls.
The Play button remains visually salient while other controls receive native focus.
Do not interpret the apparent94.01% competition accuracy as selector quality: an
always-negative classifier would achieve95.83% with one positive among24 controls.

## Visual review and crop context

Agent reviewer inspected numbered pages019,028,039,045,049,050,052,068,094
(v1 originals; v2 retains the same selection/numbering and original pixels).
These are explicitly **reviewer observations**, not new native labels. The other
pages are reproducible evidence, not a claim that every image was manually reviewed.
Green rectangles are diagnostic bounds overlays, not captured focus cues.

- 039: cinema placeholder has a soft light halo around a dark gray tile. Its
  retained production crop contains the halo, caption bar and portions of neighbors;
  FDR-008 gives the focused target0.00000377. A missing crop alone is not the explanation.
- 028/045: album tile/placeholder has a red outline, while the unfocused red Play
  button remains bright. The target loses to that action control. 049 is the
  counterexample: focusing Play produces the sole correct unique selection.
- 019: an unfocused cinema tile with skyline artwork scores0.99465 on007. It lacks
  the obvious native focused halo seen in039; content/style association is plausible.
- Candidate050/052/068: large simple tiles show thin white borders, sparse repeated
  artwork and prominent captions. Native candidate094 is a wide white focused
  Settings row, visibly stretched in the unchanged square crop. These differ from
  small densely packed validation tiles, soft glows and red accent outlines.

All460 candidate/retention rows have bounds recovered from exact hash-bound source
metadata. Candidate collection-item median box aspect0.690 vs validation1.125;
median original box area5.482% vs0.464% of the frame (~11.8×). Different resolutions
make raw-pixel widths alone misleading. Primary-button median aspect7.273 vs3.832.
These are descriptive corpus differences, not proof that geometry caused the errors.
No crop margin, resize behavior or boxes were changed. Existing460-crop production
parity replay remains authoritative; no additional production crops were needed.

## Ranked hypotheses and discriminating evidence

| Rank / hypothesis | Supporting evidence | Counterexample / limitation | Next observation needed |
|---|---|---|---|
|1. Focus cue fails to transfer across appearance/context|44/44 candidate non-button misses;47/48 negative rank margins; white-border/sparse candidates vs glow/red-outline/dense validation|007/008 recognize the focused Play button; selection effects and only two families prevent causal attribution|Separate-source, matched same-control states covering glow, outline, scaling and dense neighbors; retain native truth and complete competitor geometry|
|2. Persistent salient buttons act as false focus cues|All23 FDR-008 competition FP are detail actions; pages045/049 show bright Play in both states|Cinema action scores often stay below threshold; salience alone is not sufficient|Same action buttons unfocused while each surrounding class is focused, plus focused positives of those same buttons|
|3. Crop context/geometry differs materially from candidate corpus|~11.8× median normalized area gap; aspect differences; neighboring content retained in small-tile crops|Production crop parity is intact; some crop-context overlap exists; no intervention tested|Data spanning small/dense and large/sparse boxes with fixed preprocessing; compare only after separately approved evaluation|
|4.007→008 mainly suppresses scores without reliable focus ordering|299→23 FP, unchanged1 unique,24 no-focus; paired median near zero|25 paired differences positive on008 vs5 on007 suggests some discrimination gain|Balanced matched positives/hard negatives and complete-frame selection on independent sources, not an accuracy-only checkpoint choice|

Hypotheses1–3 can coexist. Candidate proposal is not itself FDR-008's exact training
membership, so auditing it does not establish why FDR-008 learned these scores.
No final-challenge pixels were opened, scored or used to select these observations.
