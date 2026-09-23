# FDR-008 retained Home/Photos diagnostic tranche

| Outcome | Result |
|---|---|
| Software verified | Existing scoring/crop path reused;9 focused tests and offline Swift build/test pass. |
| Data eligible | Eight frames/76 reviewer boxes, visual-only development evidence. Not training data or independent holdout. |
| Integration qualified | Real production crop helper and Torch CPU checkpoint comparison. Shipped CoreML reference reused after hash/protocol checks. No TTR operation. |
| Model gate passed | No. Candidate still fails these appearance cases; no promotion/export. |

## Findings, fixed0.85 threshold

| Surface | Shipped correct unique | FDR-007 correct unique | FDR-008 correct unique |
|---|---:|---:|---:|
| Home,6 frames |2/6|0/6|0/6|
| Photos,2 frames |1/2|0/2|0/2|

FDR-008 Home outcomes:4 no-focus,1 wrong-focus,1 multiple-focus abstention.
Five of66 negative tiles become false positives, versus zero for FDR-007; neither
candidate detects any of six true Home focus tiles. Home tile accuracy falls
91.67%→84.72%; the old91.67% was itself the all-negative baseline, not useful
navigation. Photos retains two misses and no false positives. Lowering to0.5 does
not resolve this: Home TP1/FP6 and Photos TP0 for FDR-008.

Across36 correlated non-base Home frame/variant decisions, FDR-008 yields0 correct,
2 wrong,16 no-focus,18 multiple; FDR-007 yields1/6/23/6 respectively. Photos'
12 perturbed decisions improve1→4 correct, but base still0/2. Do not choose the
variant with the best post-hoc result or infer robust improvement from those four.
All seven variants/thresholds were frozen previously, not tuned here.

## Interpretation and ranked next work

1. Fixture learning did not transfer to retained Home/Photos appearance decisions.
   Native Settings retention and100% Fixture training fit are insufficient evidence
   for usable general focus detection. Keep the shipped fallback unchanged.
2. Prioritize colorful/bright negative tiles, dock/neighbor context and Photos-like
   button focus treatments with observed labels. New Home false positives make
   negative appearance support as important as adding more positive crops.
3. Box sensitivity remains material. Train-only jitter may warrant a later controlled
   experiment, but changing crop margins or thresholds on these failures is not
   qualification. Keep production16% expansion/256px behavior intact.
4. Gather independent appearance groups before another run; distinct seeds alone
   already failed independence. [APPEAR-A/B contracts](../../../Research/Plans/FocusAppearanceAcquisition.md)
   specify capability audit, bounded ground-truth pilot, split freeze, evaluation
   and one future proposal with separate operation authority.

These are empirical coverage findings, not proof of a particular causal mechanism.
Home/Photos host/journey provenance remains unknown, even for filenames containing
Office. Sources are known development failures, not untouched evaluation; exact
frame/crop pixel non-overlap with training does not prove semantic independence.

## Evidence and verification

`protocol.json` pins existing protocols/reference reports, both checkpoint hashes,
mixed-training protocol and runtime before inference. `compare.py` validates old
source reviews, model/runtime identities and original frame bytes; generates all
532 crops through production helper; checks exact decoded crop/frame isolation;
then evaluates both checkpoints on identical membership (1064 Torch predictions).
No cropper, trainer or public library API changed. Shipped scores are checked against
the frozen old protocol and rescored with the existing scorer, not rerun needlessly.
No new images displayed; all source/base crop reviews already exist.

Per-element scores, confusion, abstention and sensitivity: `photos.json`, `home.json`,
`report.json`. Actual comparison completed exit0 in34.65s. Torch timings are host
diagnostics, not device/navigation latency or CoreML parity. Focused tests0.19s,
Swift build0.72s/tests3.60s;14 XCTest/93 Swift Testing pass. `verification.json`
contains exact commands and exit codes. No capture, training, export or promotion.

Base revision7c09e211c0aeecc98cece78a50af7ff74b8c8973. Changes are this report/runner,
the acquisition contracts and targeted queue/research updates; existing artifacts
and weights preserved. No Git writes. No running processes remain. SMB is not
applicable: no producer capability gap is yet source-verified or needs peer action.

Next dispatch APPEAR-A's offline capability audit; request explicit exact-simulator
authority for its bounded pilot after the supported matrix is known. No TTR wait is
required for capability planning or supported independent-Fixture capture. Do not
promise unsupported Home label binding. Whole assigned comparison/plan tranche is
complete for review. Worker-execution kept evidence/authority separate; model-workflow
kept preprocessing, model identities and shipped assets stable.
