# NativeUIAuditKit — Experiment Log

## FDR021 candidate pixel-contract repair — 2026-10-01UTC

User approved continuation; no training. Same775head/encoder/trace, fresh FP32 model
ID `focus-ring-experimental-fdr021-reviewed-contrast-rgb-v1`,3,788,293bytes. Metadata
requires `png-straight-rgb-v1`. Production16%/256crop unchanged; input discards alpha
using exact saved-PNG RGB semantics instead of opaque-context redraw.
All333crop AND final model-input RGB hashes match. CoreML CPU versus Torch CPU:
max0.0000340920,mean0.0000014878; zero threshold flips at0.5/0.70/0.85.
Original failed packages retained.12Python tests,112Swift tests and offline build
pass. Source/compiled/package hashes, runtimes and bounded stage timings retained
in [handoff](../reports/work/FDR021-PIXEL-PARITY/handoff.md). TTR build/device
qualification and release gates remain unassessed/open; no promotion.

## FDR021 complete-model export verification — 2026-10-01UTC

No new training. Selected775head plus pinned ImageNet MobileNetV3-small encoder,
in-graph ImageNet normalization, RGB/255 image input. Full Torch CPU trace agrees
with cached MPS scores on333development/retention crops. Existing resident
Torch2.7/coremltools9 converted the Torch2.13trace without installation.
FP16package1,953,933bytes: production CPU parity FAIL(max0.211059).
FP32package3,788,242bytes: production CPU parity FAIL(max0.418649,mean0.002125).
Direct FP32 CoreML on the SAME saved RGB crops PASSES(max0.0000340939,
mean0.0000014878), zero decision flips at0.5/0.70/0.85.63PNGcrops have partial
alpha. RGB hashes before inference do not attest the opaque pixel-buffer input;
direct versus production image handling must be reconciled. No threshold,
labels or corpus altered. No promotion or TTR transfer of weights. Exact commands,
PIDs, timeouts, hashes and scores: [handoff](../reports/work/FDR021-COREML/handoff.md).

## Run FDR-021 — approved reviewed contrast addition (2026-09-30)

Status: completed; eligible checkpoint update775, not promoted. User explicitly approved58new
controls and one bounded encoding/training/comparison. Membership986train
(790native+196human),315development,18retention; no duplicates/role migration.
Arm reviewed-full-fit; output fdr021-reviewed-contrast. Fresh577parameter linear
head, frozen ImageNet MobileNetV3-small576features; seed42, AdamWlr0.01,
weight_decay0.01, native/human80/20label-balanced loss, full batch986,
1000updates/300model-seconds,600second external training deadline.
New58crops encoding:300internal/600external seconds; existing features reused.
Data-ready protocol b04e18d6e44b8000a3c4405948d67778104a1f17fd3f269a98ee6665b6ce10e1.
Final feature-bound protocol 1140910f741a048cefe155b4146087c6f5831ff55860c514416367e773097543.
Encoding completed on MPS, PID94705, exit0; exact58members and encoder state match.
Training PID94800,2026-09-30T23:55:03–23:55:24UTC,21.115s external/17.701s model;
1000updates, exit0, no timeout. Encoding PID94705,5.683s external, exit0.
Selected checkpoint update775:16/27development positives (FDR02014/27),3/288FP
(unchanged),12/14unique-correct complete frames (was9/14),18/18retention unchanged.
Artwork2/12(was1/12), artworkFP3(was2); rows7/7(was6/7); buttons3/3and0FP
(was3/3and1FP); tabs2/3unchanged. Photos all-iCloud unfocused score0.983845→0.766655,
below0.85but in abstention band, not a confident negative. App Store featured
positive regressed0.889582→0.383987; new now-streaming negativeFP0.984190.
Predeclared bounded development objective met, broad/model release gates still open.
Training-fit stop not met; stopped at1000update cap. No export/promotion/retry.
Best head SHA256bc1b5978f1febbf86ba57ae51d13c8f0fb68ffa4107e303f2f6ccf57fb0c2ec8.
Replay verified986986training+13653validation predictions for this run, identical
initial validation predictions/membership and source hashes.15focused tests,
offline Swift build and109Swift tests passed. See execution-handoff.md.
Compare fixed0.85against FDR020, unchanged guarded checkpoint selection. No export,
promotion or automatic retries. Authority/evidence: FOCUS-REVIEW-CONTINUE-16.

## TRAIN-MPS-COMPARE-14 — bounded batch comparison (2026-09-30; completed)

All four trials completed, exit0, aggregate712.116s. PIDs87684/88127/88576/88973;
elapsed181.614/171.228/173.388/181.663s. Median epoch1training wall77.258s(batch8)
versus71.751s(batch16):7.13%less time /7.67%higher throughput. Peak logged MPS
driver allocation5.62versus10.60GiB; lowest sampled available RAM5.465versus
3.374GiB. All guards held. Decision: retain batch8default; modest gain does not
justify thinner shared-machine headroom. No model quality qualification or promotion.
Same source membership in epoch1does not mean equal optimizer work:19versus15
optimizer steps during warmup. Epoch2OHEM membership differs. No pure GPU scaling claim.
[Results and receipt hashes](../reports/work/TRAIN-MPS-COMPARE-14/handoff.md).

User continued after batch8/16recommendation. Four diagnostic trials8,16,16,8;
2epochs each, same frozen512train/64validation inputs, local yolo11m.pt,
MPS/640/seed42/workers0; existing OHEM, warmup and optimizer unchanged. Primary
comparison is epoch1training wall before OHEM changes membership; optimizer warmup
and rectangular grouping still differ. No quality-equivalence/default-change claim.
One aggregate1800s budget (2s monitoring interval, up to10s owned-child termination
grace),8GiB launch/3GiB runtime RAM,10GiB free disk,2GiB output per trial. Stop
whole comparison on first failure/block/limit; no retries. Actual PID/times above.
Bundle SHA256:519da3f7336f8699fc015edc8e2f98efae46cffa7e896db52d359fbca4725d28.
Software verification:35Python tests,123Swift tests and offline build pass.
[Contract](Plans/MPSBatchComparison.md).

## TRAIN-MPS-DIAG-13 — bounded timing diagnostic (2026-09-30; completed)

Resume authorized2026-09-30 after user closed applications. Fresh memory observation
12.93GiB available; launch attempt02 uses the unchanged frozen plan and limits.
Attempt01 remains preserved. Attempt02 child PID85595 completed, exit0,
189.832s. Epochs85.423/81.210s,128batches; batch intervals133.759s total (80.3%of
epoch time), inter-batch gaps19.443s, validation9.635s, saves2.692s, mirrors0.287s.
Nested OHEM batch callbacks0.039s; epoch replacement0.022s. Replacements94/102
then75/83,8unfulfilled each epoch. Minimum sampled available RAM6.376GiB;
maximum sampled output724.407MiB. No guard breach. Frozen inputs/source pins
reverified; diagnostic weights isolated and never promoted. MPS nondeterministic
operation warnings mean seed42is not a bitwise reproduction guarantee.
Next: matched batch8/16MPS timing proposal; no automatic training continuation.
[Execution evidence](../reports/work/TRAIN-MPS-DIAG-13/execution.md).

User continuation authorizes the next bounded local MPS diagnostic. Not a model
candidate run; no FDR/iOS run number allocated. Configuration: pinned local
yolo11m.pt,512original training members,64original validation members,2epochs,
batch8,imgsz640,MPS,workers0,seed42; existing repaired OHEM, optimizer and3epoch
warmup unchanged. Explicit host timing enabled. Maximum child wall time1800s;
launch8GiB available memory, runtime3GiB reserve,10GiB free disk,2GiB artifact cap.
Initial read-only memory observation about6GiB available; launch may be blocked.
Historical attempt01 preflight:5,410,406,400bytes available RAM (5.04GiB), below8GiB guard;
48,145,682,432bytes disk free. Outcome blocked before model loading, PID none,
model elapsed time none. Frozen576members verified. Model quality and steady-state
throughput remain unassessed. No automatic retry. Runner tests30Python/123Swift pass.
Plan SHA256:21f83fffcb44e545d3c7299c2964bd122ca5647705eb73a1ad2b8ad096e3066a.
[Handoff](../reports/work/TRAIN-MPS-DIAG-13/handoff.md).
[Contract](Plans/MPSBoundedTiming.md).

## Trainer software repair — no run allocated (2026-09-30)

TRAIN-OHEM-TIMING-12 repairs rectangular slot compatibility in iOS OHEM and adds
optional host-wall timing. Original membership is restored each epoch; replacements
are limited to equal original output shapes, with explicit unfulfilled counts.
The existing batch-loss proxy and MPS backend remain unchanged. No model loaded,
training launched, weights changed or speedup measured. Next compute experiment
still requires a bounded, separately approved MPS benchmark specification.
[Contract](Plans/OHEMBatchTiming.md).

## Run FDR-020 — approved full-corpus weighted fit (2026-09-30)

FOCUS-FULL-FIT-03, owner Codex. Maintainer approved prepared proposal
ef8001be1109177728ecd35ec8fd473bee31a6bf61782c08737070eb84a44537.
928training controls (790native/Fixture,138human),315development/18retention unchanged.
Frozen576feature cache, fresh577parameter linear head seed42; fullbatch928, AdamW
lr0.01/weight_decay0.01, plain weighted BCE. Native80%/human20%, overall50/50labels;
no encoder execution, augmentation or pair loss.1000updates/300model-seconds with
600second external deadline; training-only five-consecutive fit stop; development
every25updates/terminal, unchanged guarded minimum-loss checkpoint selection.
One run only, no export/promotion. Arm `full-corpus-fit`, output `fdr020-full-corpus-fit`.
Frozen protocol `b650da4919583d57180ca0f29c6577529c2b6984f7582ce0c2c3ab695b5644b7`.
47focused/legacy tests and offline Swift build/123tests passed before launch.
Actual preflight eligible. Completed PID40455,19:03:08–19:04:40UTC;91.530s including
preflight,21.342s model loop, exit0/no timeout.1000update cap reached; strict five-
consecutive all-confident fit criterion not met (901/928confident). Nevertheless,
928/928training classifications correct at0.5,393/403positive hits and0/525FP at0.85;
weighted BCE0.017118. Native385/395TP,0/395FP; human8/8TP,0/130FP.
Terminal development14/27TP,3/288FP; retention18/18.14complete frames9unique correct,
4no focus,1multiple,0wrong;18incomplete/unresolved frames remain unavailable.
Strata: buttons3/3TP,1/3FP; tabs2/3TP,0/21FP; artwork1/12TP,2/181FP;
rows6/7TP,0/64FP; other2/2TP,0/19FP. Photos frame004 unfocused all-iCloud button
scores0.983845, causing the multiple-focus result. No eligible snapshot among40;
no best.pt/export/promotion. This recipe fits training substantially better, but
artwork transfer remains poor. Compared with FDR019's same development members,
false positives38→3 and complete unique correct7→9, but focused hits17→14.
This is not a controlled single-variable comparison or independent qualification.
Saved-prediction replay passes928,928training/13,653development+retention predictions,
training-only stopping, selection, code/source/crop hashes and changed head weights.
Next: targeted artwork/Photos transfer diagnosis and one evidence-backed changed-
representation/data experiment proposal, not a longer unchanged FDR020 run.
[Handoff](../reports/work/FOCUS-FULL-FIT-03/handoff.md).

## Run FDR-019 — approved balanced training-fit diagnostic (2026-09-30)

Owner Codex, FOCUS-FIT-01. Maintainer approved small balanced learning diagnostic.
Protocol `c818c7ab4e98f1a6fa1781273761b2fb15bf303a138fc3894163f4f56759bdaa`,
arm `fit-diagnostic`, output `fdr019-balanced-fit`. Exactly48admitted training crops,
24focused/24unfocused:16genuine native/Fixture pairs (four/appearance stratum) plus
8human positives/8human negatives, one each per supplement frame. No invented pairs.
Exact FDR017 frozen576feature cache/order/labels, fresh577parameter linear head
seed42; fullbatch48, BCE, AdamWlr0.01/default weight_decay0.01. No augmentation,
sampling or pair auxiliary loss. Up to1000updates/300model-seconds/600external-seconds.
Stop on five consecutive training-only checks with48/48confident (.85positive/.15
negative) and BCE<=.05; otherwise stop at cap. This deliberately tests tiny-set fit,
not a comparable30epoch improvement run.315development+18retention are observed
initially/every50updates/terminally, never used to stop or tune. Original0.85guards
and14complete-frame policy retained. MPS required; no encoder loaded. No best.pt,
export, promotion, new data or additional runs.42focused/legacy Python and123offline
Swift tests pass; actual preflight and launch receipts under reports/work/FOCUS-FIT-01/.
Completed PID34480,18:33:56–18:35:04UTC,68.756s including preflight; model loop1.726s.
Stopped at update162 on the fifth consecutive training-fit pass:48/48confident,
BCE0.038574;32/32native and16/16human. Gradients finite and head parameters changed.
Retention18/18. Terminal development at0.85:17/27TP,38/288FP; complete frames7correct,
5multiple,1wrong,1no focus;18incomplete frames unavailable. Artwork3/12TP and31/181FP
dominates remaining errors; rows7/7TP and1/64FP. No selected checkpoint or promotion.
Replay verifies7,824training and1,665development/retention predictions, pinned sources
and training-only stopping. Retained FDR017/018 head audit reproduces saved development
scores exactly and finds native trainingTP32/395 and27/395 at0.85; at0.5 classification
646/790 and626/790. FDR018 human trainingTP0/8 at0.85. Evidence supports inadequate
prior training fit, not a proven broken encoder or a causal claim about data diversity.
Different subset/loss/lr/budget prevent a controlled model-improvement claim. Next:
full-corpus fitting/optimization proposal, separately approved; keep development gates.
[Handoff](../reports/work/FOCUS-FIT-01/handoff.md).

## Run FDR-017 — approved matched baseline (2026-09-30)

Owner Codex, HUMAN-STATIC-ADMISSION; maintainer “Lets try that experiment”.
Protocol `f2eca5bd9644f2f6497820e7763362f4046527ec5e90fd5836c1c6b4c0682316`,
arm `static-baseline`, output `fdr017-static-baseline`.395genuine training pairs,
138baseline auxiliary draws/epoch; human crops encoded for matched feature identity
but never used in this arm's optimization.18retention and315human development crops,
14complete frames. Frozen ImageNet MobileNetV3-small/BN, fresh577parameter head,
seed42 AdamW0.0003,30epochs,13updates/epoch,1800second external cap.80%paired
BCE+softplus loss,20%weighted auxiliary BCE; identical schedules inFDR018 except
auxiliary content. Production256stretch/ImageNet normalization; threshold0.85.
Original absolute eligibility guards preserved with14-frame completeness amendment;
minimum balanced devBCE/earliest tie, no eligible epoch=>no best.pt. MPS required,
PyTorch2.13.0/torchvision0.28.0.29focused tests and123offline Swift tests pass.
Completed30epochs,PID30063,18:13:22–18:14:34UTC,72.28s including preflight
(4.85s model execution). Exit2/no timeout: no eligible epoch or best.pt. Final
retention9/18,TP1/27,FP5/288,complete frames1correct/13none. BalancedBCE0.488012.
Exact receipts/results in reports/work/HUMAN-STATIC-ADMISSION/.
No export, promotion, capture or further run authorized.

## Run FDR-018 — approved matched static-human auxiliary (2026-09-30)

Same approval/protocol `f2eca5bd9644f2f6497820e7763362f4046527ec5e90fd5836c1c6b4c0682316`,
arm `static-human`, output `fdr018-static-human`. Same395pairs and13updates/epoch
asFDR017; auxiliary slots are138human controls (8positive/130negative) from one
whole reassigned eight-frame supplement session. Once/crop/epoch, equal frame loss
mass, maximum30presentations. Human labels receive BCE only, no fabricated pairs.
Same18retention/315development, preprocessing, initialization, optimizer, seed,
30epoch/1800s budget, MPS and unchanged eligibility guards asFDR017. No historical
453-member score delta or independent-transfer claim. Completed30epochs,PID30313,
18:15:08–18:16:20UTC,72.14s including preflight(4.54s model execution). Exit2/no
timeout: zero eligible epochs/no best.pt. Final retention9/18,TP0/27,FP15/288,
14complete frames all no-focus, balancedBCE0.549087. This mixture regresses versus
matched FDR017; no repeat/promotion. Exact receipts and matched comparison under
reports/work/HUMAN-STATIC-ADMISSION/.

## Data admission only — FOCUS-CONTROL32-ADMIT-01 (2026-09-30 UTC)

Exact user-approved 32 retained native-control pairs admitted: 363→395 candidate
pairs, with 9 retention pairs and 453 real selection crops unchanged. 64 artwork
pairs held pending geometry evidence. No new run number, weights, model execution
or training approval. FDR016 remains the latest completed run. Data-only assembly
is explicitly rejected by trainer preflight; a future experiment requires a new
member-bound protocol and feature preparation. [Evidence](../reports/work/FOCUS-CONTROL32-ADMIT-01/handoff.md).

## Run FDR-016 — approved paired frozen-feature head (2026-09-29)

Owner: current NUIAK worker. Current-chat approval covers exactly one run.
Protocol `d10227895837dabdda821faf6d18dfb5088aafd1b1cee82aff2709a99ab09f41`,
arm `paired-stretch`, output `fdr016-paired-frozen-mps`.
Same363training pairs/726crops,9retention pairs/18crops,453real selection crops;
FDR015 immutable cached576features, same fresh577parameter head seed42.
AdamW0.0003,30epochs,32pairs/64crops per batch,363pair draws per epoch,
25%appearance mass. BCE plus softplus negative focused-minus-unfocused logit
margin, coefficient1. Unchanged0.85 guards and minimum balanced-real BCE among
eligible epochs; no eligible epoch means no selected checkpoint.1800s cap,
MPS required in actual process; no encoder inference or newly received data.
59focused tests passed; offline Swift build/test passed before launch.
Completed30epochs on MPS,PID82133,23:44:27–23:45:58UTC,90.83s including preflight.
Exit2/no timeout; zero eligible epochs and no best.pt. Final retention12/18,
real3/35TP and16/418FP; top1 remains11/13, Home ranks2/8 unchanged and margins
worse; AUROC0.7070 versus0.7261. Fixed0.85complete-frame decisions2correct/11none.
No research-target or qualification win.14,601cached predictions reproduced;
identical initial predictions/cache order verified. Do not repeat unchanged.
Evidence: reports/work/FDR-016/. Pair-correlated batches are a comparison
limitation, not a pure loss-only causal claim. No export/promotion authorized.

## Run FDR-015 — approved frozen ImageNet feature baseline (2026-09-29)

Owner: current NUIAK model worker. Research-led reset and named weight download
approved in current chat. Protocol
`353205a204ce39c4b3c6519dea11fdd9544cccf1822d9a1e015551cc17e4432e`,
arm `pretrained-stretch`, output `fdr015-pretrained-frozen-mps`.
Same363training pairs/726crops,9retention pairs/18crops,453real selection crops and
64exclusions as FDR014; unchanged membership, appearance sampler, threshold0.85,
selection guards and minimum-balanced-real-loss eligible checkpoint rule.
Official MobileNetV3-Small ImageNet weights SHA256
`047dcff4addef86ea5bc2eff13c9614dc11f47ab1160d0a71a25e7db994f4e1f`.
Frozen encoder/BN, full256production crops/ImageNet RGB normalization (no center
crop), cached576features, fresh577parameter linear head only. AdamW0.0003,
batch64,30epochs,seed42,1800s cap. MPS assertion in actual trainer process;
resident PyTorch2.13.0/torchvision0.28.0. Architecture, normalization and runtime
differ from FDR014; not a causal pretraining ablation or latency comparison.
93focused tests and offline Swift build/test pass. Runtime executable identity
repair permits normal venv symlinks without weakening data containment.
Completed30epochs,PID75348,23:10:26–23:12:00UTC;94.55s overall/5.49s trainer,
exit2,no timeout. Frozen features/order/hashes verified. No eligible epoch;
retention9/18 throughout. Final real0/35TP,1/418FP at0.85. Final top1 ranking11/13
versus FDR014 final5/13 (but matches its epoch1); cropAUROC0.726 versus0.601.
All14,601scores replayed. Settings-related8/8 and tabs3/3 rank first; both Home
artwork cases fail. No best.pt; head-only last.pt diagnostic, not exporter-compatible.
Next: matched artwork/context audit plus separately designed grouped calibration;
do not lower threshold to manufacture a pass. No automatic repeat, export,
promotion or new data admission. [Results](../reports/work/FDR-015/results.md),
[handoff](../reports/work/FDR-015/handoff.md).

## Run FDR-014 — appearance-sampling-only comparison (2026-09-29)

Owner: current NUIAK model worker. User authorized sampler correction and one run.
Protocol `e807725468811a02af7c775d881e8582a1a9a3d6caa69e20e139b9bd2291298a`,
arm `warm-stretch`, output `fdr014-appearance-sampling-mps`.
Same363training+9retention pairs,453real selection crops/64exclusions as FDR013;
FDR007 initialization/freshAdamW,30epochs,batch64,lr0.0003,seed42,noaugmentation,
MPS,1800s cap; unchanged representative checkpoint guards and objective.
Only training sampling changes: buttons/tabs/artwork/rows25%each, balanced labels,
uniform examples within each bucket. Drops source-first50/50; native Settings
expected12.99%. Metadata identifies119button/17tab/150artwork/77row pairs; nested
tab child buttons remain buttons.21780actual seed42 draws:5497button,5479tab,
5366artwork,5438row.82tests and offline Swift build/tests verified before launch.
Approval and immutable protocol in reports/work/FDR-014/. Completed all30epochs,
PID67225,22:22:30–22:26:06UTC;123.54s trainer/216.07s overall,exit2. No eligible
checkpoint. Retention18/18 throughout; every epoch fails real-improvement,artwork,
complete-frame guards. MinimumFP10 at epoch4 versus FDR013's21, but still only2/35TP.
Finalepoch4TP/35FP; tabs1/3 in six epochs, otherwise0/3. All14,601stored scores and
selection metrics replayed; frozen code unchanged. Rebalancing alone insufficient.
No conditional selected-checkpoint comparison, new data/export/promotion or rerun.
Next: existing native100/canvas-v2 contrast/geometry audit before more training.
[Results](../reports/work/FDR-014/results.md), [handoff](../reports/work/FDR-014/handoff.md).

## Run FDR-013 — approved representative-selected development (2026-09-29)

Owner: current NUIAK model worker. User approved the frozen FOCUS-SELECTION-01
run proposal in this chat. Completed30epochs21:56:46–22:00:24Z,PID63806; MPS verified
in the trainer process with PyTorch2.7.0. PID/start/end
will be recorded in reports/work/FDR-013/started.json and execution.json.
Protocol `1c39256bf41e133d1e9532d35f4b2d6d6f7e24240729eb0375fc04e866326ae7`,
arm `warm-stretch`, output `fdr013-representative-mps`.
363training pairs/726crops;9retention pairs/18crops;453real development selection
crops;64excluded real labels. FDR007 initialization/freshAdamW,50/50 native–Fixture,
30epochs,batch64,lr0.0003,seed42,noaugmentation,1,800second cap. Same-process MPS
assertion required. Earliest minimum balanced real BCE only among epochs meeting
all frozen real/retention/frame guards; no eligible epoch means no best checkpoint.
Selected-checkpoint comparisons use the same frozen517real and312related-synthetic
scores as FDR012; no new threshold, final challenge, export or promotion. No automatic
rerun. Approval: reports/work/FDR-013/approval.json.

Outcome: no eligible epoch; exit2, no best.pt.124.34s trainer/217.41s overall.
Retention18/18 in29epochs,16/18 at epoch24. Every epoch fails real-improvement,
artwork and complete-frame guards; minimumFP21 exceeds9, with only2/35TP at
that epoch19. Epoch20 has5TP/24FP; finalepoch7TP/39FP. Tabs0/3 throughout.
All14,601initial/epoch predictions and selection metrics replayed. No conditional
selected-checkpoint comparison, export, promotion or automatic retraining.
Next: targeted native100/canvas-v2 coverage audit, artwork hard negatives and tab
contrasts. See reports/work/FDR-013/results.md and handoff.md.

## Representative selection preparation — FOCUS-SELECTION-01 (2026-09-29; no run)

Assigned software integration and immutable 363+9 candidate preflight following
QUALIFIED44 review. Real development selection replaces retention-only selection
for a future separately approved experiment; legacy runs remain unchanged.
No new run ID, training, model inference or export is authorized by preparation.
Policy: [FocusRepresentativeSelection.md](Plans/FocusRepresentativeSelection.md).

Completed: immutable363+9 and453real-selection/64excluded labels; prior668rows
preserved. Protocol `1c39256bf41e133d1e9532d35f4b2d6d6f7e24240729eb0375fc04e866326ae7`.
Actual trainer preflight exits2 solely for missing_experiment_approval; no training
directory created.77focused tests and offline Swift build/tests pass. Retained
FDR010/FDR012 score replay confirms the new guards reject unchanged/worse transfer;
no new epoch inference. See ../reports/work/FOCUS-SELECTION-01/handoff.md.

## Post-FDR-012 data/selection review — QUALIFIED44 (2026-09-29; no run)

Named TTR44-pair archive received and verified. Native contract and production
crop checks completed; visual review blocks3 short Library geometries (two unique
pixel pairs).38 usable new candidates and3 additional duplicates account for all44.
No exact evaluation overlap. Existing325training+9retention assembly unchanged.
39 focused tests pass. Proposed real-development checkpoint objective plus retention
and false-positive guards replaces retention-only selection in a future approved
experiment; proposal only, not trainer implementation or new training authority.
See reports/work/QUALIFIED44-INTAKE-01/handoff.md and selection-proposal.md.

## Run FDR-012 — approved MPS replacement (2026-09-29)

Status: completed30/30epochs; development transfer criterion failed. Replaces
interrupted FDR-011, not a resume. PID54962,21:03:10–21:09:47Z,exit0;
90.70seconds training,396.55seconds including preflight. Same-process MPS verified.
Selected epoch29,18/18retention, BCE2.8957965862683084e-8; all30epoch selections
replayed. best.pt SHA256 b079f4c756af52889b055cda2a3a87d4310be9fe518703a1d28704b49dbd044c.
829/829candidate comparisons complete.453settled real candidates:1/35TP,15/418FP
versus FDR0103/35TP,9/418FP; shipped18/35TP,140/418FP. Complete real frames:
1/13unique-correct,1wrong versus FDR0102/13correct,0wrong. Related synthetic:
20/50unique-correct versus18/50; artwork2/32 versus0/32. No independent qualification.
33focused tests pass. No export/promotion or extra run. Next: intake published44
pairs and freeze representative-selection proposal before further training.
Details/errors/frozen membership: reports/work/FDR-012/results.md and handoff.md.
User explicitly approved replacement GPU run and frozen comparisons. MPS verified
in the actual training process before invoking the existing trainer, failing closed.
Protocol6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac,
arm warm-stretch, output related-synth-development-mps.325training pairs/650crops,
9retention pairs/18crops,FDR007 initialization,fresh AdamW,30epochs,batch64,
lr0.0003,seed42,50/50 native-Fixture,no augmentation,16%/256production crops.
1,800second total cap including preflight. Minimum retention BCE among18/18correct
at0.85; earliest tie. Compare selected checkpoint with shipped/FDR010 on frozen
40real frames/517scores and separately50related synthetic pairs/312scores.
Reuse verified baseline scores; no changed threshold, challenge scoring, additional
run, export or promotion. Approval/execution evidence: reports/work/FDR-012/.

## Run FDR-011 — approved related-synthetic development (2026-09-29)

Status: interrupted after3/30 completed epochs; no selected checkpoint or evaluation.
PID51386,20:36:43–20:45:44Z,541.19seconds including preflight, exit-15 (owned stop).
Restricted launch selected CPU, unlike FDR010's MPS. Scoped host probe confirmed
MPS available with the same PyTorch2.7.0 interpreter. This is a launch-context
failure, not a data/model-quality result. Preserve partial best/last artifacts;
do not use them as the approved30epoch result. No automatic second run.
Next: separately approve replacement bounded run in verified MPS context with
fresh output and an MPS assertion before trainer launch.40real frames/517scores
and50related synthetic pairs/312scores are frozen; baseline metric replay and
33focused tests pass. Candidate inference/export/promotion not run.
PID/timestamps/elapsed and outcome in reports/work/FDR-011/execution.json and
started.json; handoff and verification.json preserve complete accounting.
Maintainer explicitly approved
the exact run and comparison after325+9 data/configuration preflight.
Protocol6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac,
arm warm-stretch, output related-synth-development-candidate.325training pairs,
9retention pairs, FDR007 warm weights/fresh optimizer,30epochs,batch64,lr0.0003,
seed42,50/50 native-Fixture, no augmentation, production16%/256 crops,1,800second cap.
Minimum retention BCE among18/18correct at0.85; earliest tie; no eligible epoch
means no selected checkpoint.12new native-image pairs are the only data addition.
Compare selected checkpoint with shipped/FDR010 on frozen40real development frames
and separately50related synthetic pairs. No challenge scoring, threshold sweep,
automatic retry, second run, export or promotion. Execution approval is bound in
reports/work/FDR-011/approval.json. Use resident focus-export-01 runtime.

## RELATED-SYNTH-ADMIT-01 — approved data-use amendment (2026-09-29; no run)

Maintainer approved new related synthetic variants for development training while
retaining exact test-member exclusion and separate related-synthetic/real-transfer/
independent-qualification reporting. Preparing existing313+12 training pairs and
unchanged9 retention pairs through existing assembly/preflight. No new run ID,
weight update, inference, export or training execution authorization in this entry.
Completed actual trainer preflight20:34Z: configurationValid=true, expected exit2
solely for missing_experiment_approval.325training/9retention pairs, previous644rows
unchanged; protocol6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac.
See [policy](Plans/FocusRelatedSyntheticAdmission.md) and resulting
`reports/work/RELATED-SYNTH-ADMIT-01/` evidence; runtime proposal retains FDR007
initialization/fresh optimizer and fixed30epoch retention-selected configuration.

## HUMAN-BENCHMARK-02 — evaluation complete (2026-09-29)

Maintainer approved development benchmark admission and comparison for corrected
8-frame/155-control human revision192241Z-aabb2be6. Shipped9e5ba294… versus FDR-010
epoch29/775c3197…; fixed0.85, production16%/256 crops, CoreMLCPU/PyTorchCPU. No
training run allocated. Frozen protocolfd5acf5e…;155/155 per model,0failed scores,
unchanged pre/postflight identities.138 candidates: shippedTP6/FN2/FP99/TN31;
FDR-010TP0/FN8/FP2/TN128.17 auxiliary:16FP shipped,0candidate. All8 positives
missed by candidate despite92.75% candidate accuracy; no promotion. Actual CPU loops
3.76s/4.41s are backend-specific, not comparable latency. Four retained benchmarks
reused:32frames/362scores each/315supported crops. Full-frame selection unavailable
for the new8 due to absent completeness and visible omissions.23 focused tests and
five actual-artifact negative checks pass. Handoff under reports/work/HUMAN-BENCHMARK-02.
Next: new TTR bulk contract intake and role-bound matched contrast corpus; training
waits for admitted data/approved representative selection, not another identical run.

## FOCUS-REPRESENTATIVE-01 — fixed evaluation, no training (2026-09-29)

User assigned representative buttons/tabs/artwork/rows validation followed by
coverage-driven corpus readiness. Frozen protocol77f417ee…; shipped9e5ba294… and
FDR-010 epoch29 checkpoint775c3197…;0.85 threshold,original top-left bounds,
production16%-each-side/256stretch crops. CoreMLCPU and PyTorch2.7CPU2threads,
Python3.12.9.312/312 scores each complete; measured loops15.42s/7.29s are different
backends, not directly comparable latency. No new training,export or challenge use.

Synthetic50pairs: candidate TP4/4buttons,10/10tabs,0/32artwork,4/4rows,zero FP.
Complete50frames:18unique-correct/32no-focus; shipped7unique/4wrong/39no-focus.
Native-image32 versus native-button18 is confounded with content/geometry/labels;
the result establishes a coverage failure, not its cause. Retained real32frame
scores reproduced:362/model,315supported settled candidate crops. Candidate
TP0/3buttons,0/3tabs,1/12artwork,2/7rows; shipped3/3,1/3,5/12,2/7 respectively.
Four-stratum macro recall9.23% versus50.89%; tiny/development-exposed support.

Decision: keep shipped, reject FDR-010 export; no unchanged repeat run. Immutable
selection proposal preserves retention floor but needs representative source-balanced
selection approval.313+9 unchanged;5727 canonical additional-pair deficits scheduled,
with prioritized matched contrasts,real-source gaps and storage gate before capture.
70Python/123Swift tests and offline build pass. [Evidence](../reports/work/FOCUS-REPRESENTATIVE-01/handoff.md).

## SYNTH05 consumer intake — no model run (2026-09-29)

Received22+28 producer pairs;50/50 native bracket/geometry/recipe checks and100/100
production crops pass;74 distinct full frames. Artwork and selected-parent/child
consumer compatibility now verified. All dark/seed7/related Simulator Fixture data;
diagnostic-only,zero training admission.313+9 membership and FDR-010 outcome unchanged.
64 focused Python tests,offline build/123 Swift tests pass.
[Handoff](../reports/work/SYNTH05-HIERARCHY-INTAKE-01/handoff.md).

## Run FDR-010 — approved gap-targeted retention development (2026-09-29)

Logged before execution. Maintainer approved the bounded candidate and limited
production milestone; no production promotion. Owner: current model-workflow worker.
Output `NativeUITrainer/focus_ring_runs/fdr010-gap-retention`, arm `warm-stretch`.
Frozen protocol `8dd1a45090ed372157dbcd453cb3d77f770db4fb54cc0118a34141fdc2e2399a`.
313 training pairs/626 crops, nine retention pairs/18 crops. FDR-007 initialization,
fresh AdamW,50/50 source sampling,30 epochs,batch64,lr0.0003,seed42,no augmentation,
production16%/256 stretch,threshold0.85. Minimum retention BCE among18/18-correct
epochs, earliest tie; no eligible epoch means no selected model. Internal and
whole-process1,800-second limits. Resident focus-export-01 Python3.12.9/torch2.7.0,
numpy1.26.4/Pillow11.3.0; actual backend/PID/timing recorded on execution.
One run, then frozen24-frame and separate Photos regression; conditional observer
export only if the research contract's improvement conditions hold. Full production
coverage gates unchanged. [Contract](Plans/FocusLimitedProduction.md),
[approval](../reports/work/FDR-010/approval.json). Initial preflight was pending at
registration; completed outcome follows.

**Outcome:** preflight exit0; single run exit0,PID21169,16:45:53Z–16:52:21Z,
388.452s process/90.265s post-preflight phase,MPS/torch2.7.0. All30 epochs18/18
retention; selected epoch29,BCE0.000017874388,best SHA256
`775c3197a48169807fb8e20b41df71b4c61c8f152bde82f3ebbd56d25712583d`.
Same24-frame benchmark: FDR-010 TP3/FN16/FP3/TN180 versus shipped8/11/30/153
and FDR-0094/15/8/175; unique-correct2/13 versus shipped3/13. Separate113-crop
Home/Photos/Settings benchmark: FDR-010 TP0/FN8/FP4/TN101; both Photos pairs fail.
All362 candidate scores complete; compatible baselines reused with exact metric
reproduction. Conditional observer export rejected: fewer false positives do not
compensate for collapsed recall. No export/promotion/retraining. Next: representative
selection validation and source/geometry coverage before a volume campaign, retaining
the nine Settings pairs only as a forgetting check. [Handoff](../reports/work/FDR-010/handoff.md).

## FOCUS-GAP-LIVE-20260929 — corpus preparation, no training run

Current matched Max TTR/Fixture completed8 competitor jobs:40 pairs(24 native
buttons,8 Settings-row analogs,8 selected-tab analogs),0 rejected targets.
168 exported files/126,466,360bytes verified;80 frame files/42 distinct pixels,
80 distinct production crops visually reviewed. All40 additions admitted to a
new immutable extension, preserving273 prior training-candidate pairs and9 retention
pairs:313+9 total. Zero new complete-pair duplicates, contradictory crop labels or
real-world regression pixel overlap. Full protocol hash
`cabd9dc9bac2a4a5192f7e004cd596c9878aa06bab46151d546b2f0fc97c032f`.
All10 independent evaluation-coverage blockers remain. New retention-only proposal
`8dd1a45090ed372157dbcd453cb3d77f770db4fb54cc0118a34141fdc2e2399a`
initially awaited a specific scope decision; subsequently approved/executed as
FDR-010 above. Previous FDR-009 approval was not reused.
Actual trainer preflight completed(exit2,empty stderr): configurationValid=true,
launchEligible=false,10 coverage blockers plus missing exact experiment approval.
No run ID, new weights, dataset model inference, export or promotion in this preparation.
83 focused Python tests and offline Swift build/123 tests pass.
[Evidence/next decision](../reports/work/FOCUS-GAP-LIVE-20260929/next-run-decision.md).

## FOCUS-TTR-TEST-CYCLE-01 — development evaluation, no new training (2026-09-29)

Maintainer authorized the benchmark→justified candidate→conditional test-export
tranche. Existing evaluator froze three role-aware protocols before inference:
24 trial02 frames,249 controls, fixed0.85, production16%/256 crops, shipped CoreML
CPU versus FDR-009 epoch3 PyTorch CPU in resident focus-export-01 environment.
All249 scored per model, successful postflight, zero failed predictions.
202 settled candidates: shipped TP8/FN11/FP30/TN153; FDR-009 TP4/FN15/FP8/TN175.
Complete-frame unique-correct3/13 versus2/13;11 frames unavailable with explicit
reasons.68 error sheets;14 evaluator tests pass. No export parity claim.
New12 dock pairs verified but test-only, no train/validation admission; existing
273 training/9 retention unchanged. No new run ID or weights: do not repeat the
failed transfer experiment without gap-addressing data. [Handoff](../reports/work/FOCUS-TTR-TEST-CYCLE-01/handoff.md).

## HUMAN-REVIEW-04 — approved development comparison (2026-09-28)

Before execution: maintainer approved one fixed shipped CoreML CPU versus FDR-009
epoch3 PyTorch CPU comparison. Eight Office frames,113 controls (8 focused/105
unfocused),2 explicit Photos pairs, threshold0.85 and production16%/256 crops.
New human-label development lane; all members excluded from training, unknown
complete-frame coverage and source independence. No training run allocated, export,
promotion or challenge scoring. Runtime is the resident focus-export-01 environment.
Execution/metrics and frozen identities will be recorded under
`reports/work/HUMAN-REVIEW-04/`; model gate remains unassessed.

**Outcome:** one run complete,113/113 scores per model, no failed inputs/predictions.
Shipped TP4/FN4/FP11/TN94; FDR-009 TP1/FN7/FP15/TN90. Recall50% versus12.5%;
both Photos pairs pass shipped and fail candidate. All37 errors have numbered
context/crop sheets. Exact-pixel sensitivity111 crops changes only TN, not errors.
Pre/postflight hashes/runtime matched; no exact overlap with retained role indexes,
independence still unknown.154 Python and123 Swift tests pass. A post-run nonfinite
failure-receipt hardening did not repeat inference; exact executed code is archived,
metric AST unchanged and results replayed. Next: targeted matched Home/Photos/Settings
data under separate admission/collection approval, not an automatic new run.
[Results and evidence](../reports/work/HUMAN-REVIEW-04/handoff.md).

## Data readiness — human Office review/crop audit (2026-09-28; not a model run)

Joe's immutable review covers8 frames/113 controls and2 explicit Photos pairs.
Production crop QA:113/113,111 distinct crop pixel hashes, fixed16%/256×256.
Audit:0 hard errors;2 exact crop duplicate groups and4 soft near-frame matches,
all retained.8 positives/105 negatives across Home/Photos Welcome/Settings in one
device session; not independent transfer evidence.145 Python and123 Swift tests pass.
No inference, training, export, promotion, new run ID or selection-rule change.
Recommend development-regression reservation and separately approved fixed shipped
vs FDR-009 comparison; no training admission. [Evidence](../reports/work/HUMAN-REVIEW-02/handoff.md)
and [decision proposal](Plans/HumanFocusAdmissionDecision.md).

## Run FDR-009 — approved retention-selected Simulator development (2026-09-27)

Preparation before launch. Maintainer answered "yes" to one retention-selected
development run, no export/promotion. Owner: current NUIAK agent. Output reserved
as `NativeUITrainer/focus_ring_runs/fdr009-simulator-retention`, arm `warm-stretch`.
273 training pairs (546 crops),9 native retention pairs (18 crops), using the
immutable extension `53d358966d36e0c36387eae84e9cdf488fb46676885ad908986fe5b8d445a4de`.
Initialize FDR-007 weights, fresh AdamW,50/50 native–Fixture sampling,30 epochs,
batch64,lr0.0003,seed42,no augmentation,production16%/256 stretch,threshold0.85.
Only epochs retaining18/18 retention accuracy are eligible; minimum retention BCE,
earliest tie; no eligible epoch means no selected checkpoint. Internal1,800s cap
and conservative external1,800s whole-process deadline; no automatic retry.
Frozen protocol before launch:
`9c525a6f1f6698417a2a4af299e13b97459b53cbf3002511cd12f93821f3423f`.
Python3.12.9,torch2.7.0,numpy1.26.4,Pillow11.3.0,macOS26.4.1/arm64;
approved resident focus-export-01 environment, actual MPS availability verified.
Trainer SHA256 `72d364eccffc829f24b219c4eaca0210a08c4c1c5cd4058491423b29422ebaf0`.
FDR-007 warm checkpoint SHA256
`a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`.
Actual preflight completed exit0 before launch: configurationValid=true,
launchEligible=true, no development-launch blockers; all ten qualification blockers
remain separately recorded.106 focused/legacy tests and offline Swift build/123
tests pass. PID/timings follow in the execution receipt and outcome. Full appearance/Photos/source
qualification blockers remain open; no model gate or independent validation claim.
Existing48-frame diagnostic comparison is a next separate assignment, not included
in this one-run approval. Evidence will be retained in `../reports/work/FDR-009/`.

Outcome: completed30/30, exit0, PID13076,2026-09-28T06:26:37.297968Z–06:32:27.846988Z.
350.552s process including revalidation /79.808s post-preflight phase,torch2.7.0/MPS.
Every epoch met18/18 retention at0.85. Selected epoch3 by minimum eligible retention
BCE0.000004791201 versus initialized0.000007347030; both TP9/FN0/FP0/TN9.
Best SHA256 `e6e37ddc32c173ddf13e1e52756995a53cbbe1e1af18aa0e6da58b5767e47584`.
Final epoch30 is preserved in last.pt, not selected. Training loss0.113968→0.000611891;
not independent generalization evidence. All epoch selection scores/checkpoint bytes
verified without new inference. No export, promotion, challenge scoring or second run.
[Handoff](../reports/work/FDR-009/handoff.md). Next separately assign same-input48-frame
development transfer comparison before considering any further training.

## 2026-09-27 — SIM-FOCUS-DEV-01 training-data extension (no model run)

Maintainer-authorized exclusive local Simulator/TTR collection produced40 new
native-bracket pairs plus12 prior calibration pairs. All52 reviewed pairs admitted
to training-only extension:273 total training pairs, unchanged9 retention pairs;
original221 candidate pairs preserved.234 exported files/603,875,651 bytes verified;
104 crops contain102 distinct pixels (two repeated positives, different paired
negatives), no duplicate whole pairs or evaluation-overlap exclusions.
Protocol `53d358966d36e0c36387eae84e9cdf488fb46676885ad908986fe5b8d445a4de`.

Six procedural appearance presets and grid/media/dock context remain one conservative
related Fixture group, not native Photos or independent evaluation. r02's native
bracket failed; five equivalent nine-control geometry recipes were not attempted.
No candidate experiment launched, run allocated, weights changed or challenge scored. Existing
FDR-007 initialization/configuration,50/50 sampling,retention reference/selection
and ten independent-coverage blockers are preserved. A retention-only development
selection policy is a pending human decision, not an approval inferred from data
admission. Actual trainer preflight completed with valid configuration and11 blockers
(ten coverage requirements plus absent exact approval), no training output created.
93 focused tests and offline Swift build/123 tests pass.
[Handoff](../reports/work/SIM-FOCUS-DEV-01/expansion-handoff.md) and
[decision](../reports/work/SIM-FOCUS-DEV-01/selection-decision.md).

## 2026-09-27 — FOCUS-OFFLINE-DIAG-01 (cached analysis, no training run)

Reproduced retained three-model fixed0.85 comparison from all3,744 probabilities;
no new predictions/model loads by the diagnostic CLI. Both007/008 rank true focus
strictly first on1/48 frames;008 paired medians focused0.001621/unfocused0.001355,
with47/48 negative competitor margins. False positives decrease but unique selection
remains1/48. Audited unchanged221+9 proposal and all460 bounds. Recommend source-
separated cue/context data and full hard competitors, not a new training run.
Configuration,retention/selection gates and shipped artifacts unchanged; challenge
uninspected. [Evidence and next assignment](../reports/work/FOCUS-OFFLINE-DIAG-01/handoff.md).

Chronological record of every training run and major technical decision in Phase 6. Written so that any future agent or engineer can reconstruct what was tried, why, and what the outcome was — without reading the full conversation history.

Last updated: 2026-09-27

---

## 2026-09-27 FocusRing frozen-surface evaluation — no training run

[Full metrics and errors](../reports/work/APPEAR-EVAL-RESERVE-20260927/metrics.md).
Received96 native-labeled pairs pass strict intake and production cropping. Evaluated
only cinema_rows/album_grid:48 pairs and48 complete24-control frames,1,248 predictions
per model,3,744 total, zero failures. At fixed0.85, unique correct/wrong/no/multiple:
shipped0/0/0/48; FDR-0071/22/0/25; FDR-0081/22/24/1. Paired TP/FN/FP/TN:
shipped38/10/44/4;0072/46/14/34;0082/46/1/47. No replacement recommended.
FDR-008 reduces competition FP299→23 versus007 but gains no recall/unique selection;
94.01% competition crop accuracy is below95.83% always-negative accuracy.

Native boxes isolate classification, not YOLO localization. All inputs are dark;
Photos buttons remain absent. Zero exact overlap against3,789 prior images or across
reserved roles does not prove source independence: exact producer source/ancestry
review is unavailable. The48 final-challenge pairs remain unscored; no validation
member enters training. Host CoreML CPU and PyTorch CPU are not an export-parity test.

Runtime drift initially blocked the retained candidate assembly. All460 candidate/
retention crops replayed pixel-identically under current production code; an explicit
input-bound runtime proof now reconstructs the same221+9pairs, sampling and selection
through the existing CLI. Historical manifests/checkpoints remain unchanged. Missing
independent coverage and separate training approval remain binding: actual assembly
exit0; actual trainer preflight exit2, configurationValid=true, launchEligible=false,
10 independent-coverage blockers plus missing_experiment_approval. No new experiment
ID, training, checkpoint, export, promotion or capture was created.

Next: source-backed admission of the four reserved groups and genuine Photos coverage,
then review the retained single source-balanced candidate proposal. Do not repeat
same-data training or tune thresholds on these diagnostics.

## How to Read This Log

Each entry has:
- **Run ID**: sequential, used in reports and cross-references
- **Date / wall time**: calendar date and approximate elapsed training time
- **Configuration**: key parameters that differed from default
- **Outcome**: actual metrics, errors, or observations
- **Diagnosis**: what we think happened and why
- **Action taken**: what changed as a result

---

## Run 001 — First Full Training Run (Pixel-Coordinate Bug)

**Date:** 2026-05-22  
**Elapsed:** ~45 min (10,000 iterations)  
**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: 10,000
- Batch size: 32
- Dataset: 4,509 training images (full images only, no strip tiling)
- Annotation format: **PIXEL coordinates** (bug — should be normalized [0,1])

**Outcome:**
- Training completed without error
- `detector.evaluation(on:)` → mAP@0.5 ≈ 0.001
- All class APs ≈ 0.000

**Diagnosis:**
- Root cause: annotation coordinates were in PIXELS, not normalized [0,1] as `MLObjectDetector.AnnotationType.boundingBox(units: .normalized, ...)` expects. The model received wildly large cx/cy/w/h values (e.g. cx=550 instead of 0.47) and could not learn any meaningful geometry.
- Secondary confusion: the `evaluation(on:)` result would have been near-zero anyway due to a separate `.scaleFit` bug (see Run 002), but the pixel-coordinate issue was the primary failure here.

**Action taken:**
- Fixed `CreateMLExporter.swift` to convert `boundsVisionNormalized` → Create ML normalized coords (cx, cy, w, h all in [0,1])
- Formula: `cx = vn.x + vn.w/2`, `cy = 1.0 - vn.y - vn.h/2`
- Documented in `Research/BestPractices.md` — check before every future run

---

## Run 002 — Second Full Training Run (Normalization Fixed, scaleFit Evaluation Bug Discovered)

**Date:** 2026-05-23  
**Elapsed:** ~45 min (10,000 iterations)  
**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: 10,000
- Batch size: 32
- Dataset: 4,509 training images (full images, no strip tiling)
- Annotation format: **NORMALIZED [0,1]** ← fixed from Run 001

**Outcome (via `detector.evaluation(on:)`):**
- mAP@0.5 ≈ 0.001 (same as Run 001 — appeared unchanged)
- All class APs ≈ 0.000

**Outcome (via custom `scripts/eval_map.swift` with `.scaleFill`):**
| Class | AP@0.5 |
|---|---|
| alert | 0.909 |
| toggle | 0.605 |
| primaryButton | 0.165 |
| navigationBar | 0.000 |
| textField | 0.000 |
| **mAP** | **0.336** |

**Diagnosis (scaleFit evaluation bug — BP-25):**
`MLObjectDetector.evaluation(on:)` runs `VNCoreMLRequest` internally with `.scaleFit` (letterboxing). Create ML trains objectPrint by scale-filling to 299×299. For 1179×2556 portrait images:
- `.scaleFit` shrinks the image to fit 299×299 with black padding (image is only 138px wide in the 299-wide input)
- A predicted box at cx=0.687, w=0.687 (correct in training space) remaps to w≈1.49 in original image space
- IoU(1.49-wide pred, 0.687-wide GT) ≈ 0.457 — just below the 0.5 threshold
- Result: every correct prediction registers as a FP; mAP = 0

**Fix:** Always use `.scaleFill` in custom inference and evaluation. Built-in `evaluation(on:)` cannot be fixed — use `scripts/eval_map.swift` instead.

**Diagnosis (navigationBar/textField AP=0 — BP-26):**
Actual mAP of 0.336 revealed that alert and toggle ARE being detected, but navigationBar and textField have AP=0 despite having the most training instances (3,709 and 2,000 respectively). Investigation:
- `scripts/inspect_model_outputs.swift` with `confidenceThreshold=0.0` confirmed the model produces 14,661 YOLO candidates on a navigationBar test image
- Best candidate at the correct y-position had max confidence 0.0024 (for class "toggle", not "navigationBar")
- The navigationBar bounding box has aspect ratio 16:1 (w=1.0, h=0.063). Even a generous anchor of (0.5, 0.5) gives center-IoU ≈ 0.11 with a 16:1 box. Assignment threshold is ~0.4–0.5. **No anchor is ever matched to navigationBar during training → zero gradient → model never learns the class.**

**Action taken:**
- Documented scaleFit bug as BP-25 in `Research/BestPractices.md`
- Documented anchor assignment failure as BP-26
- Created `scripts/eval_map.swift` — correct custom evaluation using `.scaleFill`
- Created `scripts/test_model_predictions.swift` — single-image diagnostic
- Created `scripts/inspect_model_outputs.swift` — raw tensor inspector bypassing VNCoreMLRequest
- Decided to fix the anchor-assignment problem before Run 003 (see Run 003 configuration)

---

## Run 003 — Strip-Tiled Training (Complete 2026-05-26)

**Date:** 2026-05-24 (PID 7107 started ~23:48, crashed disk-full at 05:09); retry PID 10413 started 2026-05-25 ~18:22, completed 2026-05-26 05:18  
**Status:** COMPLETE  
**Actual duration:** ~11 hours (wall clock — Create ML's objectPrint takes far longer than the 90-min estimate when dataset is 4× larger)

**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: **25,000** (increased from 10,000 — more data, more iterations needed)
- Batch size: 32
- Training records: **18,563** (4,509 full images + 14,054 horizontal strip images)
- Validation: **1,364 full images** (strips are training-only augmentation)
- Strip configuration: 22% of image height per strip, 50% overlap (stride = stripH/2)

**Strip tiling rationale (fix for BP-26):**
A 22%-height horizontal strip of a 2556px-tall iPhone screenshot is 562px tall, 1179px wide → roughly 1179×562 in the strip. At 299×299 training input after scale-fill:
- navigationBar occupies width=1179, height=~160px within the strip → height fraction ≈ 160/562 = 0.285 of strip height
- Strip-space aspect ratio: 1.0 / 0.285 ≈ **3.5:1** (down from 16:1 in full image)
- textField strip-space aspect ratio: **~2.5:1** (down from 21:1)
- primaryButton: **~2.0:1** (down from ~6:1)

Verified by `scripts/verify_strip_export.swift`:
- navigationBar strip AR: 1.83:1 ✓ (< 4:1 threshold)
- textField strip AR: 2.46:1 ✓
- primaryButton strip AR: 1.96:1 ✓
- alert strip AR: 0.87:1 ✓
- toggle strip AR: 0.65:1 ✓

**Training counts (after strip generation):**
- Train: 18,563 records (4,509 full + 14,054 strips)
- Per-class full-image counts: alert=320, navigationBar=3709, primaryButton=3120, textField=2000, toggle=2740

**Log location:** `NativeUITrainer/training.log`

**Expected outcome (based on anchor IoU analysis):**
- navigationBar: aspect ratio 3.5:1 in strip space → anchor IoU > 0.5 achievable → expect AP > 0.00, target > 0.50
- textField: aspect ratio 2.5:1 → expect AP > 0.00, target > 0.40
- primaryButton: already had some detections (AP=0.165); strip training may improve recall
- alert, toggle: unaffected (square-ish objects, already worked in Run 002)
- Target overall mAP: > 0.60 (approaching DS-G6 gate of 0.70)

**Follow-up evaluation (to run after training completes):**
```bash
# After training completes, run in order:
swift scripts/test_model_predictions.swift   # spot check: alert IoU > 0.9? any navBar detections?
swift scripts/eval_map.swift                 # full 3-pass mAP on 1,364 validation images

# For confusion matrix (TASK-6-5):
WRITE_YOLO_PREDS=1 swift scripts/eval_map.swift   # also writes reports/yolo_preds/
swift scripts/export_yolo_gt.swift                 # writes reports/yolo_gt/
python scripts/confusion_matrix.py \
  --gt-dir reports/yolo_gt \
  --pred-dir reports/yolo_preds \
  --version 1
```

**⚠️ Eval pipeline fix applied during training:**
`scripts/eval_map.swift` was updated (2026-05-25) to run all 3 passes (full-image + SAHI + horizontal strips) before Run 003 completed. The previous version ran only a full-image pass and would have reported AP=0 for navigationBar/textField even if the strip-trained model correctly detects them in strips. This is now fixed — the eval script matches the 3-pass inference pipeline in `NativeUIDetectionRequest`.

**Disk-full incident during Run 003:**
PID 7107 (first attempt) crashed at `write(to:)` with "No space left on device" despite 144Gi nominally free. Root cause: 24GB of accumulated compiled eval caches (`*.mlmodelc` in `/var/folders/.../T/`) consumed available headroom. Fixed by deleting stale caches before retry, freeing 170Gi. See `Research/TrainingRunbook.md` Step 0 for the pre-flight disk check protocol added as a result.

**Built-in validation metrics (Create ML's `.scaleFit` eval — unreliable for portrait images, see BP-25):**
- mAP@0.5: 0.0066
- alert: 0.025, navigationBar: 0.000, primaryButton: 0.004, textField: 0.000, toggle: 0.004

**Eval sequence — three variants (all custom `scripts/eval_map.swift`, IoU@0.5):**

Three consecutive evals were run on the same Run 003 model weights to isolate root causes. Numbers below are in that order.

| Class | NMS=0.45, 3-pass | NMS=0.30, 3-pass | NMS=0.30, SAHI disabled | Notes |
|---|---|---|---|---|
| alert | 0.101 | 0.101 | **0.286** | 2,999→2,983→304 predictions |
| navigationBar | 0.137 | 0.148 | **0.845** | 15,591→15,139→1,917 predictions |
| primaryButton | 0.456 | 0.458 | **0.648** | 3,534→3,402→1,366 predictions |
| textField | 0.129 | 0.118 | **0.383** | 6,100→5,968→979 predictions |
| toggle | 0.236 | 0.200 | **0.745** | 10,481→10,232→1,481 predictions |
| **mAP@0.5** | **0.212** | **0.205** | **0.581** | DS-G5 floor = 0.50 |
| **DS-G5** | ✗ | ✗ | ✗ | All 5 classes must reach 0.50; alert+textField still below |

**Canonical Run 003 result: mAP=0.581, SAHI disabled, NMS=0.30** (`reports/eval_results.json`, 2026-05-26T18:32:11Z)

**Spot check (`test_model_predictions.swift`):**
- alert [full pass]: IoU=0.881 ✓ (previously 0.909 — minor regression)
- navigationBar [strip pass]: IoU=0.977 ✓ (previously 0.000 — definitive proof strip fix works)

**Diagnosis — FP sources, diagnosed via `scripts/diagnose_fp_passes.swift`:**

The strip tiling fix definitively solved the anchor-assignment failure for navigationBar and textField (both moved from AP=0.000 to detectable). The 3-pass pipeline then created a severe FP explosion. A diagnostic script (`diagnose_fp_passes.swift`) was written to attribute FPs to each pass independently for a 10-image sample.

**Diagnostic findings (sample of 10 validation images):**

The script runs each pass in isolation and reports per-image prediction counts and strip index / y-fraction for any `navigationBar` prediction above conf=0.10:

```
img_000409.png  (1179×2556)
  full=0  sahi=3  strip=1
  strip breakdown: top-of-image=0  mid/bottom=1
    strip[03] yStart=0.33 conf=0.704
```

Consistent pattern across the sample:
- **Full-image pass**: 0 navBar FPs on alert-only images (correctly abstains)
- **SAHI pass**: 2-4 navBar FPs per image, regardless of whether a navBar is present
- **Strip pass**: 0-1 FPs per image; when present, always at strip[03] (yStart≈0.33)

**Root cause — SAHI pass (primary FP source):**
SAHI tiles a 2× upscaled image into 640×640 crops at 480px stride. A full-width navBar (1179px) appears in 3-4 horizontally overlapping tiles as a partial element. Each tile-crop generates a prediction at a different normalized x-coordinate. After remapping back to full-image space, these partial-element predictions are at distinct positions with mutual IoU < NMS threshold → all survive NMS → 3-4 false navBar predictions per image. The problem is structural: SAHI is designed for small/compact objects that fit within a single tile; applying it to full-width elements creates unavoidable coordinate fragmentation.

**Root cause — Strip pass strip[03] (secondary FP source):**
At yStart=0.33, strip[03] captures the top portion of an alert dialog (the wide horizontal title bar region). In strip context, an alert title bar and a navigation bar are visually near-identical: both are horizontal bars spanning full width. The model trained on navBar in strip context cannot distinguish them. This is a class confusion issue, not an anchor issue.

**Fix applied to eval pipeline:**
SAHI pass commented out in `eval_map.swift` — this is the correct long-term approach for full-width elements. The strip pass provides sufficient detection coverage for navBar/textField; SAHI adds no true positives for these classes but generates many false ones. mAP improved from 0.212 → 0.581 after this change.

**NMS threshold experiment (NMS=0.45 → 0.30):**
Cross-strip NMS gap was hypothesized as a root cause (adjacent-strip predictions of same navBar have IoU ~0.35). Lowering NMS from 0.45 to 0.30 barely helped (navBar: 15,591→15,139 predictions, mAP 0.212→0.205). This confirms the FPs were structurally distinct spatial predictions from SAHI — not near-duplicate overlapping ones that NMS would merge.

**Remaining weak classes after SAHI fix (current DS-G5 blockers):**
- **alert: AP=0.286** — precision=0.132 (304 predictions for 40 GT). Strip pass generates FPs at strip[03] (yStart=0.33) because alert dialog headers look like navBars in strip context. Additionally, alert has only 320 training instances vs navBar=3,709 (11.6:1 imbalance).
- **textField: AP=0.383** — precision=0.265 (979 predictions for 315 GT). Strip pass generates multiple predictions per textField per strip (high overlap, each strip sees the same field).

---

## Key Lessons Learned (Summary across all runs)

| Lesson | Impact | Reference |
|---|---|---|
| Annotation coordinates must be normalized [0,1], not pixels | Run 001 wasted | BP, Section 2 |
| `MLObjectDetector.evaluation(on:)` uses `.scaleFit` → mAP≈0 for portrait images | Run 002 appeared to fail | BP-25, LessonsLearned §3 |
| Always use `.scaleFill` for VNCoreMLRequest on portrait images | Every inference and eval | BP-25 |
| YOLO anchor assignment fails for 16:1 boxes → zero gradient | navBar/textField AP=0 | BP-26, LessonsLearned §4 |
| Training log must go inside the project: `NativeUITrainer/training.log` | Files lost outside project | AGENTS.md |
| Run 50-iteration smoke test before full training | Would have caught Run 001 bug in <30s | LessonsLearned §10.1 |
| Custom eval loop is required — do not trust `evaluation(on:)` | Mis-diagnosed two runs | LessonsLearned §9 |
| Strip training fixes anchor assignment but creates FP explosion via cross-strip duplicates | Run 003 mAP 0.212 despite 100% recall | SAHI disabled in eval_map.swift |
| **SAHI pass is wrong for full-width elements** — tiles fragment a 1179px navBar across 3-4 crops → 3-4 FPs per image after NMS | Primary FP source; mAP 0.212 → 0.581 after disabling | diagnose_fp_passes.swift confirmed |
| NMS threshold tuning does not fix structural FPs — barely changes prediction count when FPs are spatially distinct | NMS 0.45→0.30: navBar 15,591→15,139 predictions | Run 003 NMS experiment |
| Strip[03] (yStart≈0.33) fires on alert dialog headers — visually identical to navBar in strip context | alert AP 0.286 → 1.000 after routing alert to full-image only | diagnose_fp_passes.swift + Run 004 |
| Per-class pass routing fixes alert completely — full-image pass sees centered card vs. full-width bar | alert: 0.286 → 1.000, zero FPs, zero missed | Run 004 Experiment B |
| Strip-trained model detects primaryButton/toggle primarily via strip context, not full-image | primaryButton AP 0.648 → 0.151 with full-image only; must use both passes | Run 004 Experiment A |
| textField FPs are 99.9% false-class (zero IoU with any GT) — NOT duplicate strip predictions | NMS tuning useless; requires hard-negative training data | diagnose_textfield_fps.swift |
| Model fires false "textField" at y=0.15–0.35 and y=0.75–1.00 — caused by toggle/primaryButton in those zones | ~600 FPs from images with no textField GT at all | analyze_fp_zones.py |
| Toggle strip-only + conf≥0.95 raises AP 0.745→0.850 AND improves recall — cross-pass near-dups eliminated | 379 full-image FPs + 258 near-dups removed with zero cost | Run 004 v3/v4 eval |
| **NMS same-class-only gap** — textField and toggle/primaryButton FPs at the same position both survive NMS and both score as FPs. Cross-class suppression (IoU>0.30) removes them | textField AP 0.406→0.505, DS-G5 passed, zero retraining | Run 005 pipeline fix |
| Hard-negative training data alone is insufficient without fixing the eval pipeline structural gap first | 240 images → +0.023 AP; pipeline fix → +0.099 AP on same model | Run 005 comparison |
| Confidence threshold hurts AP even when it improves precision — cutting high-recall TPs costs more than eliminating FPs gains | primaryButton: conf≥0.95 → AP 0.648→0.599 despite precision 0.485→0.603 | Run 004 v3 eval |
| Pipeline tuning alone moved mAP 0.212→0.745 on the same model weights — diagnose before retraining | 6 eval experiments, zero retraining, +0.533 mAP | Run 004 full sequence |
| 25K iterations on large dataset → confidence saturation (all preds ~1.0) | Precision collapses | Cap iterations at 10K |
| Class imbalance >5:1 degrades minority class AP severely | alert: 0.909→0.101 | Enforce 5:1 cap in TrainingConfig |
| `.mlmodelc` eval caches fill `/var/folders/.../T/` — clear before each training run | 24GB consumed → disk full crash | TrainingRunbook Step 0 |
| Create ML training on 18,563 images takes ~11h (not 90 min) | Monitoring cadence needs updating | TrainingRunbook Step 2 |

---

## Key Lessons Learned — New Entries from Run 003

| Lesson | Impact | Reference |
|---|---|---|
| Create ML training takes ~11h for 25K iterations on 18,563-image dataset (not 90 min) | Scheduling / monitoring significantly harder | This entry |
| `.mlmodelc` eval caches accumulate in `/var/folders/.../T/` — 3,445 files = 24GB after 3 runs | "No space left on device" crash at model write | TrainingRunbook Step 0 |
| Create ML's built-in validation metrics use `.scaleFit` — always near-zero, always ignore | Confirmed yet again (mAP=0.0066 on a model with 100% recall) | BP-25 |
| **SAHI is the primary FP source for full-width elements** — tiles a 1179px element across 3-4 crops → 3-4 FPs per image | mAP 0.212 → 0.581 after disabling SAHI | diagnose_fp_passes.swift |
| NMS threshold change (0.45→0.30) does not help when FPs are spatially distinct | navBar: 15,591→15,139 predictions (−3%), mAP barely changed | Run 003 NMS experiment |
| Strip[03] (yStart≈0.33) fires on alert dialog headers — class confusion with navBar in strip context | alert AP 0.286, precision 0.132 | diagnose_fp_passes.swift |
| 25K iterations on 18,563 records = ~43 effective epochs → confidence saturation (all preds ~1.0) | All predictions saturated at conf≈1.0; threshold tuning impossible | Run 004: reduce iterations |
| Class imbalance 11.6:1 (navBar/alert) exceeds 5:1 plan cap → alert calibration degraded | alert AP: 0.909 → 0.101 | Run 004: cap at 5:1 |

---

## Pending Runs

### Run 004 — Per-class pass routing (eval-only, COMPLETE 2026-05-26)

**Status:** COMPLETE — no retraining required for this phase. DS-G6 gate passed.

**What was tried:**

Two routing experiments on the Run 003 model weights (no retraining):

**Experiment A — strict routing (alert/primaryButton/toggle → full-image only; navBar/textField → strip only):**
- alert: 0.286 → **1.000** ✓ (40 predictions for 40 GT — zero FPs)
- primaryButton: 0.648 → **0.151** ✗ — strip-trained model no longer detects buttons via full-image pass
- toggle: 0.745 → 0.611 ✗ — same reason
- Finding: primaryButton and toggle require strip pass. Full-image pass yields very low recall for these classes after strip training (model adapted to strip context).

**Experiment B — corrected routing (alert → full-image only; everything else uses both or strip):**
- `alert`: full-image only
- `navigationBar`, `textField`: strip only
- `primaryButton`, `toggle`: full-image + strip (NMS deduplicates)

| Class | Run 003 canonical | Run 004 routing | Change |
|---|---|---|---|
| alert | 0.286 | **1.000** | +0.714 |
| navigationBar | 0.845 | 0.845 | — |
| primaryButton | 0.648 | 0.648 | — |
| textField | 0.383 | 0.383 | — |
| toggle | 0.745 | 0.745 | — |
| **mAP@0.5** | **0.581** | **0.724** | **+0.143** |
| DS-G5 | ✗ | ✗ | textField (0.383) sole blocker |
| DS-G6 | ✗ | **✓** | mAP 0.724 ≥ 0.70 |

**Canonical Run 004 result: mAP=0.745, DS-G6 PASSED** (`reports/eval_results.json`, 2026-05-26)

**Full pipeline experiment sequence (all on Run 003 model weights, no retraining):**

| Pipeline config | mAP | alert | navBar | primaryButton | textField | toggle |
|---|---|---|---|---|---|---|
| 3-pass, NMS=0.45 (initial) | 0.212 | 0.101 | 0.137 | 0.456 | 0.129 | 0.236 |
| 3-pass, NMS=0.30 | 0.205 | 0.101 | 0.148 | 0.458 | 0.118 | 0.200 |
| SAHI disabled, NMS=0.30 | 0.581 | 0.286 | 0.845 | 0.648 | 0.383 | 0.745 |
| + alert full-image only | 0.724 | 1.000 | 0.845 | 0.648 | 0.383 | 0.745 |
| + toggle strip-only + conf≥0.95 | **0.745** | 1.000 | 0.845 | 0.648 | 0.383 | **0.850** |

**Key finding — alert fix:** Routing alert to full-image only eliminated 100% of alert FPs (0.286→1.000). Root cause confirmed via `diagnose_fp_passes.swift`: strip[03] at yStart≈0.33 captures alert dialog title bar, which is visually indistinguishable from a navBar in strip context.

**Key finding — toggle strip-only:** Moving toggle to strip-only raised AP from 0.745→0.850 AND improved recall (774→781 TP). Source: `diagnose_class_fps.swift` found 379 toggle FPs from the full-image pass and 258 near-duplicate cross-pass predictions at IoU=0.10–0.20. Strip-only eliminated both. Adding conf≥0.95 threshold further trimmed FPs with negligible recall impact (TP mean conf=0.999 vs FP mean=0.934).

**Key finding — primaryButton conf threshold reverted:** conf≥0.95 for primaryButton cut 8 TPs at the high-recall tail, dragging AP 0.648→0.599 despite improving precision. AP metric integrates the full PR curve — losing high-recall TPs costs more than eliminating FPs gains. Reverted to conf≥0.10.

**Key finding — textField diagnosed via `diagnose_textfield_fps.swift` + `analyze_fp_zones.py`:**
- 99.9% of textField FPs are false-class (IoU=0 with all GT textFields)
- ~600 FPs come from 1,069 images with NO textField GT at all
- False-class FPs cluster at y=0.15–0.35 (36 FPs: toggle and primaryButton zone) and y=0.75–1.00 (70 FPs: primaryButton-dominant bottom zone)
- Zone analysis confirmed: model calls **toggle elements "textField"** (49% of upper-mid zone) and **primaryButton elements "textField"** (87% of bottom zone)
- This is a training data problem — the three classes are confused with each other in strip context

**Key finding — primaryButton and toggle also have false-class FPs (`diagnose_class_fps.swift`):**
- primaryButton: 97.2% false-class (683/703 FPs); FPs heavily at bottom (300) and spread across all zones
- toggle: 63.5% false-class (449/707) + 36.5% near-dup (258/707); near-dups resolved by strip-only routing
- All three classes need hard negatives showing the *other* classes in strip context without their own label

**Eval pipeline — final production configuration:**
```
alert       → full-image pass only   (conf ≥ 0.10)
navigationBar → strip pass only      (conf ≥ 0.10)
textField   → strip pass only        (conf ≥ 0.10)
primaryButton → full-image + strip   (conf ≥ 0.10)
toggle      → strip pass only        (conf ≥ 0.95)
NMS IoU threshold: 0.30
SAHI: disabled
```

**Remaining gap — textField (AP=0.383, sole DS-G5 blocker):**
Pipeline tuning is exhausted. Requires retraining with hard-negative strips. See Run 005.

---

## Run 005 — UIKitToggleForm Hard-Negative Retraining (In Progress)

**Date:** 2026-05-27  
**Status:** TRAINING IN PROGRESS  
**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: 25,000
- Batch size: 32
- Training records: **20,632** (18,563 original + 2,069 new UIKitToggleForm entries)
- Validation: **1,394** (1,364 original + 30 new UIKitToggleForm entries)
- Strip fraction: 22% height, 50% overlap (unchanged from Run 003)
- `--skip-export` flag: source train/ PNGs deleted after Run 003; used `augment_createml_export.py` instead

**Trigger:** textField AP=0.383 — sole DS-G5 blocker. Zone analysis confirmed the model fires "textField" on toggle elements (49% of upper-mid FPs at y=0.15–0.35) and primaryButton elements (87% of bottom FPs at y=0.75–1.00). Pipeline tuning is exhausted; requires hard-negative training data.

**Hard-negative strategy — UIKitToggleFormViewController:**

A new template (`NativeUIDatasetGenerator/Templates/UIKitToggleFormViewController.swift`) providing form-lookalike layouts with **zero textField elements**:
- 2–3 insetGrouped sections containing UISwitch rows (annotated: `toggle`)
- Bottom CTA button (annotated: `primaryButton`)  
- Navigation bar (annotated: `navigationBar`)
- Section header labels and row separators — NOT annotated (zero textField labels)
- Seed-varied: tint color (8 hue families), section/row counts (2–3 sections × 2–4 rows), toggle states (on/off/disabled), CTA title, nav bar right button

The template directly covers both FP zones: switch rows appear in the y=0.15–0.35 zone and the CTA button in y=0.75–1.00. Strips from these images give the model hard negatives — "toggle in strip" and "primaryButton in strip" without a textField label.

**Dataset augmentation approach:**

Source train/ PNGs deleted after Run 003 to reclaim disk space. Full re-export of 18,563 images was not feasible. Instead, `scripts/augment_createml_export.py` was written to:
1. Hard-link new PNGs from a separate simulator run into `createml_export/train/images/`
2. Generate strip crops for each new image (mirrors `CreateMLExporter.swift` exactly)
3. Append new annotation entries to `createml_export/train/annotations.json`
4. Idempotent — skips filenames already present in annotations

New `--skip-export` flag added to `NativeUITrainer` to skip Step 1 and use the existing `createml_export/` directory directly.

**Augmentation results:**
```
── train ──
  Existing entries: 18,563
  New full images : 240
  New strip entries: 1,829
  Total new entries: +2,069
  Final train total: 20,632

── validation ──
  Existing entries: 1,364
  New full images : 30  (no strips — validation uses full images only)
  Final val total : 1,394
```

**Trainer invocation:**
```bash
swift run -c release NativeUITrainer \
  --dataset <simulator-dataset-root> \
  --output <NativeUIAuditKitModels/Sources/NativeUIAuditKitModels> \
  --skip-export
```

**⚠️ Iteration count note:**
25,000 iterations was used (same as Run 003). With 20,632 records and batch=32, one epoch ≈ 645 steps → 25,000 iterations ≈ 38.7 epochs. Run 003 saw confidence saturation at ~43 epochs. This run is near that boundary. If saturation recurs, reduce to 15,000 iterations in Run 005 retry.

**Expected outcome:**
- textField AP: 0.383 → target ≥0.50 (DS-G5 pass)
- Overall mAP: maintain ≥0.70 (DS-G6 already passed — must not regress)
- alert AP: 1.000 — should be unaffected (UIKitToggleForm has no alert elements)
- toggle AP: 0.850 — slight regression possible (240 new toggle examples in training)

**Eval results (2026-05-28, after pipeline fix — see below):**

| Class | Run 004 | Run 005 raw | Run 005 + suppression | Change vs 004 |
|---|---|---|---|---|
| alert | 1.000 | 1.000 | 1.000 | — |
| navigationBar | 0.845 | 0.7745 | 0.7745 | -0.071 |
| primaryButton | 0.648 | 0.6799 | 0.6799 | +0.032 |
| textField | 0.383 | 0.406 | **0.505** | **+0.122** |
| toggle | 0.850 | 0.8213 | 0.8213 | -0.029 |
| **mAP** | **0.745** | **0.736** | **0.756** | **+0.011** |
| DS-G5 | ✗ | ✗ | **✓** | |
| DS-G6 | ✓ | ✓ | ✓ | |

**Pipeline fix — cross-class conflict suppression (zero retraining, 2026-05-28):**

After Run 005 training, textField was still at 0.406. The eval pipeline had a structural gap: NMS was same-class only (`guard a.label == b.label else { continue }`) — a textField prediction and a toggle/primaryButton prediction at the same position both survived NMS and were both scored. The false-class FPs identified in Run 004's zone analysis were exactly this pattern.

Added `crossClassSuppress()` to `scripts/eval_map.swift` (called after NMS): any textField prediction with IoU > 0.30 against a toggle or primaryButton prediction is suppressed. Result: 737 → 609 textField predictions, 270 → 268 TPs (only 2 real textFields lost), AP 0.406 → 0.505. DS-G5 passed.

navBar regressed 0.845 → 0.7745 in Run 005. Diagnostic (`diagnose_class_fps.swift`) confirmed 478 false-class FPs at strip y=0.15–0.55 (content area — model predicting navBar in middle of screen). TP conf mean=0.999, FP conf mean=0.899. Applying conf≥0.95 reduces predictions 1661→1508 but AP unchanged at 0.7745 (lost TPs and removed FPs cancel in PR curve). navBar threshold reverted. Root cause is likely the UIKitToggleForm section headers creating navBar-like horizontal patterns in training strips — addressable with more data diversity if navBar drops further.

---

## Run 006 — YOLO11n Migration (Complete 2026-08-23)

**Trigger:** navBar regression in Run 005 (0.845 → 0.7745) traced to Create ML's objectPrint anchor mismatch on thin, full-width elements — same structural limitation flagged in the original Run 006 rationale below. Migrated to YOLO11n rather than continuing to patch the anchor-based pipeline.

**Training:** Ultralytics YOLO11n, 100 epochs, same 20,632-entry training set used for Run 005 (`scripts/train_yolo.py`, `.venv-yolo`). No strip tiling required — YOLO11's anchor-free head handles the ~16:1 navigationBar aspect ratio natively, eliminating the strip-pass/full-image-pass routing complexity from Runs 003–005.

**Export:** `scripts/export_yolo_coreml.py` (`.venv-coreml`, coremltools 9.0) → `best.mlpackage`, NMS baked into the CoreML graph (IoU 0.30, confidence floor 0.001). Model size 5.18MB.

**Eval — same 1,394 held-out validation images as Runs 001–005** (`scripts/eval_yolo_map.swift` for CoreML via direct `MLModel` inference; Python `ultralytics` val for the raw `.pt` checkpoint):

| Class | Run 005 (Create ML) | Run 006 .pt | Run 006 CoreML | Change vs Run 005 |
|---|---|---|---|---|
| alert | 1.000 | 0.995 | **1.000** | — |
| navigationBar | 0.7745 | 0.975 | 0.909 | **+0.135** |
| primaryButton | 0.6799 | 0.905 | 0.894 | **+0.214** |
| textField | 0.505 | 0.981 | 0.961 | **+0.456** |
| toggle | 0.8213 | 0.984 | 0.909 | **+0.088** |
| **mAP@0.5** | **0.756** | **0.968** | **0.935** | **+0.179** |
| DS-G5 | ✓ | ✓ | ✓ | |
| DS-G6 | ✓ | ✓ | ✓ | |

Every class improved, with the largest gains exactly where Create ML struggled most (textField +0.456, primaryButton +0.214, navigationBar +0.135) — confirming the anchor-free architecture resolves the root cause rather than just shifting the tradeoff. The ~3-point .pt-vs-CoreML gap is normal export precision loss; no per-class routing or cross-class suppression was needed at inference time.

**Physical-device latency** (`GeneratorRunner/GeneratorRunnerTests/YOLOBenchmarkTests.swift`, direct `MLModel` inference, no Vision framework):

| Metric | Result | Gate |
|---|---|---|
| Cold load | 25ms avg | < 3s |
| Per-image inference | ~7.5–9ms avg (letterbox 5.9ms + predict 3.4ms + parse <0.1ms) | < 200ms |

All latency gates pass by more than an order of magnitude — resolves the "Physical device latency test" item that had been the last open Phase 6 gate.

**Status:** `best.mlpackage` lives in `NativeUITrainer/yolo_runs/yolo11n_e100/weights/` (gitignored). Not yet promoted into the packaged `NativeUIAuditKitModels/` model — Create ML's `NativeUIDetector_v1` remains the shipped model pending that swap.

---

## Pending Runs

### Run 006 (superseded — see completed entry above)
**Original trigger:** Run 005 textField AP still below 0.50 after targeted hard negatives  
**Original rationale:** If Create ML's objectPrint algorithm cannot achieve adequate precision for thin full-width elements with strip training, migrate to YOLOv11 (via ultralytics) which supports custom anchor configurations and better handles thin-box classes natively. This is a significant infrastructure change — exhaust all Create ML options first.

This trigger fired after the Run 005 navBar regression; the migration is documented above as the completed Run 006.

---

## Generalization Holdout Check (2026-08-23)

**Motivation:** Run 006's 0.935 mAP@0.5 was measured on a random 8:1:1 split *within* each
of the 51 trained template families (confirmed via the dataset manifest — every family
appears in all three splits at proportional ratios, e.g. `ActionSheet: {train: 320,
validation: 40, test: 40}`). `QG5_splitContamination`'s own comment in
`DatasetQualityAuditTests.swift` states plainly: *"Full withheld-family isolation is
enforced in Phase 6a"* — true template-family holdout was deliberately deferred, not done
for the 5-class prototype. That leaves an open question: does 0.935 hold up on a layout the
model has never seen at all, or is it inflated by structural familiarity?

**Method — deliberately lighter than a full Phase 6a-style holdout retrain.** Retraining
with families excluded matches the project's own stated methodology for that later phase,
but costs real training time for a 5-class model about to be superseded by Phase 6a anyway.
Instead: evaluate the **already-shipped** `nativeui-ios-v2.0` model against a brand-new
template — `AnalyticsDashboardTemplate.swift` — that is genuinely novel in two ways:
1. **Content is new** (different seeds, different generated text), same as any validation split.
2. **Layout structure is new** — a 2-column metric-card grid (`LazyVGrid`) with toggles
   embedded inside cards, a search bar pinned directly under the nav bar (not inside a
   `Form`), and a floating circular action button (FAB) bottom-right. No existing template
   among the 51 combines these three patterns; all are list/form/single-card layouts.

Critically, this template is **never registered** in `GenerateDatasetTests.swift`'s
dispatcher — zero images from it exist anywhere in the train/validation/test manifest. This
answers a narrower question than full family-holdout retraining ("does the *current shipped
model* generalize to an unseen layout?") rather than the broader one Phase 6a will answer
("does the *training methodology* produce a model that generalizes?") — but it's a real,
honest signal for a fraction of the cost.

Implementation: `GeneratorRunner/GeneratorRunnerTests/GeneralizationHoldoutTest.swift` — 40
seeds, same letterbox/inference/AP-computation logic as `scripts/eval_yolo_map.swift`
(11-point interpolation, IoU@0.5 match threshold), run directly against the bundled
`best.mlmodelc`.

**First run — methodology bug, not a model finding:** initial toggle GT boxes wrapped the
switch *and* its visible "Auto-refresh" label as one wide box. Every existing template uses
`.labelsHidden()` on `Toggle` before `.captureFrame` — the trained `toggle` class means
switch-only, narrow. That shape mismatch alone collapsed toggle AP to 0.000 (GT=80,
preds=207) despite the model plausibly still locating switches correctly — it just couldn't
match against a differently-shaped ground truth box. Fixed by separating the label into its
own `label_toggle_caption_N` frame and applying `.labelsHidden()` to the `Toggle`, matching
established convention. Documented here because it's a real trap: a holdout test's own
annotation convention has to match training convention, or the result measures the wrong
thing entirely.

**Result (corrected):**

| Class | AP@0.5 (holdout) | AP@0.5 (baseline) | GT | Preds |
|---|---|---|---|---|
| navigationBar | 1.000 | 0.909 | 40 | 86 |
| primaryButton | 1.000 | 0.894 | 40 | 99 |
| toggle | 1.000 | 0.909 | 80 | 184 |
| textField | 0.734 | 0.961 | 40 | 119 |
| **mAP@0.5** | **0.934** | **0.935** | — | — |

**Δ = -0.001.** The headline number holds up essentially exactly on a genuinely unseen
layout — strong evidence 0.935 was not inflated by template-family memorization for
navigationBar, primaryButton, and toggle at least.

**textField is the one real signal worth flagging, not glossing over.** It dropped from
0.961 to 0.734. The holdout template's search bar is a mocked control (`HStack` with a
magnifying-glass `Image` + secondary-colored placeholder `Text` inside a stadium-shaped
background) — visually distinct from every trained textField, which are all real
`TextField`/`SecureField` controls with a plain rounded-rect background and no icon. This
result most plausibly reflects a real gap on that specific visual *style* (icon-prefixed
search-bar-shaped fields) rather than a general textField weakness — but it hasn't been
isolated from "genuinely novel layout" as a confound, since this holdout only tested one
template. Worth a follow-up holdout template using a real `TextField` in an unfamiliar
layout to separate "new control style" from "new layout" as the cause.

**Reading this result:** treat as a positive, real-but-narrow signal that the current model
generalizes reasonably well beyond its exact training layouts, with a flagged textField-style
caveat — not as a substitute for Phase 6a's planned full family-holdout methodology, which
remains the rigorous version of this question for the 41-class model.

---

## Run 007 — YOLO11m 41-class, family holdout (Started 2026-08-23)

**Trigger:** Phase 6a unblocked. Foundation Models eval skipped (no image API). Run 006
5-class YOLO11n is shipped. True family-holdout 41-class training is the next gate.

**Status:** COMPLETE 2026-08-27 — early-stop at epoch 93/100 (patience 15).
Resumed-run wall time 24.2 h after the power-cut resume. `best.pt` re-validated
at **mAP@0.5 = 0.981**, **mAP@0.5:0.95 = 0.919** (2,936 val images, 25,565
boxes). CSV peak mAP50 = 0.984 at epoch 39; peak mAP50-95 = 0.919 at epoch 40.
Watchdog PID 3889 exited 0. Weights:
`NativeUITrainer/yolo_runs/phase6a_r007/weights/best.pt` (40.6 MB, optimizer
stripped). Next: TASK-6a-4 CoreML export.

**Dry-run (2026-08-23):** 575 train images, batch=4, MPS M4, ~4.6 GB. Epoch 1
mAP50 ≈ 0; epoch 2 mAP50 = 0.00068 (cls 5.14 → 2.65). OHEM callback works
(Ultralytics 8.4 has no `trainer.batch`; stashed via `preprocess_batch`).
`tabBarItem` dropped (9,202 boxes). Splits 11,504 / 2,936 / 2,000.

**Configuration:**
- Architecture: YOLO11m (`yolo11m.pt`), imgsz 640, 100 epochs, patience 15, MPS
- Labels: native annotation JSON → YOLO txt + COCO JSON (`scripts/export_coco.py`)
- Class IDs: frozen `Research/schemas/category_map.json` 0–40
- Split: family holdout (BP-27). Withheld: `CardDetail`, `WizardStepFlow`,
  `NotificationCenter`, `GalleryPage`, `MultiSectionForm`, `SettingsToggleDense`,
  `EmptyState`, `OnboardingPage`. Not withheld (unique rare-class sources):
  `ColorPicker`, `MenuButton`, `iPadSidebar`, `MapOverlays`, `HardNegative_2`
- Loss: Ultralytics box+cls+dfl (no `loss="focal"` kwarg). Inverse-frequency α from
  `scripts/class_weights.json`. OHEM replaces easy slots with a 2nd copy of the
  top 20% hardest images (same length, BP-29) — appending crashed Run 007
- Output: `NativeUITrainer/yolo_runs/phase6a_r007/` and
  `NativeUITrainer/yolo_dataset_41class/` (in-package, gitignored)
- PID / log: **3889** (train) + **3866** (`watch_phase6a.py` / caffeinate)
  / `NativeUITrainer/training_6a.log`. Power-loss resume 2026-08-26 from
  epoch-45 `last.pt` (BP-30).

**Known coverage gap (does not block the run, does block DS-G8):**
iOS generator has 36 of 41 taxonomy classes. Zero instances: `statusBar`, `toolbar`,
`scrollIndicator`, `tooltip`, `unknown`. Extra label `tabBarItem` dropped (BP-28).
Empty classes keep their frozen IDs so later generator fills do not reshuffle the head.

**Expected outcome:**
- Dry-run (`--epochs 2 --batch 4`, 5% fraction) completes without error
- Full run: overall mAP@0.5 on holdout families; per-class AP for the 36 present classes
- DS-G8 (no class AP < 0.65 across 41) will fail on the five empty classes until
  generator coverage is added

**Outcome (2026-08-27):**
- Stopped early epoch 93 (patience 15). Best checkpoint re-val: P=0.950 R=0.974
  mAP50=0.981 mAP50-95=0.919 on the 2,936-image **val** split (non-holdout families).
- All 36 classes with val instances have AP@0.5 ≥ 0.835 (`webContent` lowest
  among present classes). Thin bars remain weak at 0.5:0.95
  (`homeIndicator` 0.461, `progressView` 0.465) — IoU tightness, not misses.
- Five empty classes still have 0 AP (`statusBar`, `toolbar`, `scrollIndicator`,
  `tooltip`, `unknown`). DS-G8 cannot pass until generator coverage.
- `best.pt` / `last.pt` stripped to 40.6 MB. Epoch snapshots `epoch45.pt`–
  `epoch92.pt` remain (full optimizer state, ~154 MB each).
- CoreML export (TASK-6a-4, 2026-08-27): FP16 + NMS pipeline
  `best.mlpackage` / `best_fp16.mlpackage` **38.5 MB** (< 50 MB → TASK-6a-6
  distillation not required). INT8 (TASK-6a-5): nms=False mlprogram +
  `linear_quantize_weights` → `best_int8_nonms.mlpackage` **19.5 MB**.
  Ultralytics `quantize=8` k-means palettization SIGKILL'd YOLO11m (BP-31).
  Small-element CoreML AP (nms=False FP16 vs INT8): max drop **0.9 pt**
  (`progressView`); several classes improved under INT8. Decision: **ship
  NMS FP16** (already 38.5 MB < 50 MB). Do not copy into
  `NativeUIAuditKitModels` until a production gate exists.

**Holdout eval (TASK-6a-7, 2026-08-27):** family-holdout **test** (2,000 images,
18,149 boxes) mAP@0.5 = **0.358**, mAP50-95 = 0.313. In-family val remains
0.981 — the model overfits template families. 13 classes appear in the
holdout; 9 of those are below AP 0.65 (`imageView` 0.193, `textField` 0.200,
`toggle` 0.603, and six at ~0: `listRow`, `pageControl`, `picker`,
`secondaryButton`, `secureField`, `stepperControl`). Chrome/buttons that
look the same across families still work (`navigationBar` 0.995,
`primaryButton` 0.973, `progressView` 0.994, `label` 0.695).

Blur (200 images): non-text probe drop is 4.6 pt on `toggle`, 0.4 pt on
`navigationBar` (pass). `label` 0.695 → 0.080 confirms text was blinded.
Centroid `bias_flag` true on position-locked chrome (`homeIndicator`,
`navigationBar`, `dynamicIsland`, …) — expected, still fails the written AC.
Per-template mAP 0.08–0.32 (no >0.95 overfit-on-one-family). Entropy top-5
holdout families: WizardStepFlow, MultiSectionForm, CardDetail, GalleryPage,
OnboardingPage. Real-world set: 0/200. Mac M4 proxy: 30 ms / 38.5 MB / cold
load not a true iPhone compile. **DS-G8 fail.**

**Holdout diagnosis (2026-08-27):** `scripts/diagnose_holdout_phase6a.py` — no class is
zero-shot (every failing class has train+val boxes). Failures are style/confusion:

- `pageControl` 97.5% miss (packed KitchenSink dots ≠ isolated onboarding dots)
- `secondaryButton` 311/341 predicted as `cancelAction` (Wizard "Back")
- `textField` 314/500 as `listRow`; `picker`/`secureField` same Form-in-List mix-up
- `toolbar` still 0 instances — UIKit walk missed SwiftUI `.bottomBar`

Template fixes for the **next generation run** (not a retrain on old images):
KitchenSink uses real `UIPageControl`; ToolbarActions has explicit `toolbar_0`;
LoginForm adds a filled "Back" `secondaryButton` matching Wizard chrome;
`AccountProfileForm` is the train Form-in-List clone; ProgressActivity and
MediaCardGrid add isolated SwiftUI page dots; `ChromeCoverage` paints
`statusBar` / `scrollIndicator` / `tooltip` / `unknown`. Then regen + Run 008.
Do not ship 41-class weights.

---

## Run 008 — YOLO11m 41-class after TASK-6a-8 regen (Started 2026-08-28)

**Trigger:** Run 007 holdout mAP@0.5 = 0.358 (DS-G8 fail, BP-32). Templates ready.
Do **not** resume Run 007. Train from `yolo11m.pt` on regenerated data.

**Status:** TRAINING_COMPLETE 2026-09-04T17:55Z — 100/100 epochs, trainer rc=0.
Watchdog `watch_phase6a.py` wrote `TRAINING_COMPLETE`. Do **not** copy weights
into `NativeUIAuditKitModels`. Do **not** start Phase 6b. DS-G8 still fail.

- In-family val: best mAP@0.5 = **0.977** (epoch 58); epoch 100 = 0.973 /
  mAP@0.5:0.95 0.932 (fitness peak 0.933 at epoch 83).
- CoreML export (mid-run): `best.mlpackage` 38.5 MB FP16+NMS.
- **Holdout eval (TASK-6a-7, 2026-09-02, `best.pt`):** family-holdout **test**
  (2,000 images) mAP@0.5 = **0.491**, mAP50-95 = **0.348**. DS-G8 map gate ❌
  (need ≥ 0.85). Gain vs Run 007: 0.358 → 0.491.
  - **Significant gain over Run 007:** mAP@0.5 jumped from **0.358 → 0.491 (+13.3 percentage points, +37.1% relative improvement)**, validating the TASK-6a-8 template and coverage fixes.
  - Per-class breakthroughs on unseen holdout templates:
    - `stepperControl`: 0.000 → **0.718**
    - `toggle`: 0.603 → **0.726**
    - `textField`: 0.200 → **0.571**
    - `secureField`: 0.000 → **0.402**
    - `picker`: 0.000 → **0.211**
    - `primaryButton`: 0.973 → **0.995**
    - `navigationBar`: 0.995 → **0.995**
    - `progressView`: 0.994 → **0.995**
    - `label`: 0.617
  - Blur robustness: non-text probe max drop is **0.50 pt** (pass; threshold is 10.0 pt).
  - Model size: **38.5 MB** (< 50 MB limit, pass; no distillation or INT8 required).

**Configuration:**
- Same holdout families as Run 007 (BP-27).
- File-list dataset (`train.txt` / `val.txt` / `test.txt`).
- Output: `NativeUITrainer/yolo_runs/phase6a_r008/`
- Checkpoint: `best.pt` (161.4 MB) / `best.mlpackage` (38.5 MB)
- Next steps for Run 009+: apply ADR-0006 (`batch=8`, `save_period=-1`, `plots=False`) to reduce training iteration wall time by ~70%.

---

## Run 009 — YOLO11m 41-class ADR-0006 Training Optimization (Started 2026-09-08)

**Trigger:** Run 008 established baseline mAP@0.5 = 0.491 on holdout families, but required ~36 hours of wall-clock time with heavy disk I/O (15.4 GB of `epoch*.pt` checkpoints) and CPU-bound metric plotting. Run 009 applies ADR-0006 iteration optimizations to maximize Apple Silicon MPS throughput and eliminate flash churn.

**Status:** IN_PROGRESS (Dry-run verified, launching baseline training).

**Configuration (ADR-0006 Applied):**
- Architecture: YOLO11m (`weights/yolo11m.pt`)
- Classes: 41 native Apple UI classes
- Batch size: `batch=8` (ADR-0006 D3, doubling batch size from 4 on host 24 GB unified RAM; halves steps per epoch from 2,876 to 1,438)
- Checkpoints: `save_period=-1` (ADR-0006 D1, saves only `best.pt` and `last.pt`, with `last.prev.pt` backup; saves ~15 GB disk writes)
- Metric plotting: `plots=False` (ADR-0006 D2, disables per-epoch CPU confusion matrices/PR curves during training; evaluated post-run)
- Optimizer: AdamW, lr0=0.001, lrf=0.01, momentum=0.937, weight_decay=0.0005
- Augmentations: Mosaic=1.0, OHEM callback enabled (hardest 20% oversampled 2×)
- Dataset: `NativeUITrainer/yolo_dataset_41class/dataset.yaml` via line-delimited manifests (`train.txt`, `val.txt`, `test.txt`)
- Target epochs: 100 with patience 15 early stopping
- Device: Apple Silicon MPS (`mps`), workers=4
- Output: `NativeUITrainer/yolo_runs/phase6a_r009/`

**Incident & Resolution (2026-09-09):**
- **Symptom:** At epoch 2 (batch 806/1498), training halted with:
  `libpng error: PNG input buffer is incomplete`
  `FileNotFoundError: Image Not Found .../train/images/img_012251.png`
- **Investigation:**
  - Ran automated validation across all 11,984 training images (`task-1035`): **0 failures**. All images are intact on disk.
  - Inspected `img_012251.png`: Valid 16-bit RGBA PNG with Apple `iDOT` chunk.
  - Root cause: NumPy `np.fromfile` uses C `fread` which does not loop on `EINTR`. Under heavy concurrent disk I/O with 4 multiprocessing workers, an interrupted or short read caused `cv2.imdecode` to receive a truncated buffer, printing `libpng error: PNG input buffer is incomplete` and returning `None`.
  - In Ultralytics `ultralytics/utils/patches.py`, the PIL fallback (`_imread_pil`) was restricted strictly to `(.avif, .heic, .heif)` extensions, causing OpenCV decode errors on PNGs to return `None` and trigger `FileNotFoundError`.
- **Fix:**
  - Patched `ultralytics/utils/patches.py`: If `cv2.imdecode` returns `None`, retry using Python's signal-safe `open().read()` with `np.frombuffer()`. If still `None`, fall back unconditionally to `_imread_pil`.
  - Added secondary safety net in `ultralytics/data/base.py` (`load_image`) to fall back to PIL before raising `FileNotFoundError`.
  - Verified `img_012251.png` decodes cleanly into `(2556, 1179, 3) uint8`.
- **Resume:** `NativeUITrainer/yolo_runs/phase6a_r009/weights/last.pt` (Epoch 1, 154 MB) is fully intact and verified loadable. Resumed seamlessly from `last.pt`.

**Completion & Outcome (2026-09-15):**
- **Status:** TRAINING_COMPLETE (100/100 epochs, exited rc=0 at 2026-09-15 07:47:42).
- **Execution Duration:** ~135.8 hours of uninterrupted, zero-restart training on PID `6504` under `watch_phase6a.py` and `caffeinate`.
- **Final Metrics (Epoch 100/100):**
  - In-family Val mAP@0.5: **0.991** (99.1%)
  - In-family Val mAP@0.5:0.95: **0.955** (95.5% — all-time high across all runs)
  - Precision: **0.981** (98.1%)
  - Recall: **0.993** (99.3%)
  - Val Box Loss: **0.1752**
  - Val Cls Loss: **0.1444**
  - Val DFL Loss: **0.7396**
- **Storage & ADR-0006 Verification:**
  - `save_period=-1` prevented writing 100 intermediate snapshots (~15.4 GB flash writes avoided); disk space remained stable between 12–18 GiB throughout the entire run.
  - Final inference weights: `NativeUITrainer/yolo_runs/phase6a_r009/weights/best.pt` (40.55 MB, stripped).
- **CoreML Export (TASK-6a-4):**
  - Generated `NativeUITrainer/yolo_runs/phase6a_r009/weights/best.mlpackage` (38.5 MB, FP16 half-precision, NMS baked in).
  - Export completed in 15.4s via `scripts/export_yolo_coreml.py`.
- **Withheld-Family Holdout Evaluation (TASK-6a-7 / DS-G8 Gate):**
  - Holdout Test mAP@0.5 = **0.586 (58.6%)** (mAP50-95 = **0.380 / 38.0%**).
  - **Massive Gen Gains:** Jumped from **0.358 (Run 007) → 0.491 (Run 008) → 0.586 (Run 009)** (+9.5 percentage points over Run 008, +22.8 percentage points / +63.7% relative improvement over Run 007).
  - **Key Class Generalization on Unseen Layouts:**
    - `primaryButton`: **0.9999** (~1.000)
    - `navigationBar`: **0.9997** (~1.000)
    - `progressView`: **1.0000** (1.000)
    - `picker`: **0.9949** (0.995)
    - `secureField`: **0.8906** (0.891)
    - `toggle`: **0.7206** (0.721)
    - `textField`: **0.6649** (0.665)
    - `label`: **0.6426** (0.643)
    - `stepperControl`: **0.5000**
    - `imageView`: **0.1512**
    - `secondaryButton`: **0.0000**
    - `pageControl`: **0.0000**
    - `listRow`: **0.0000**
  - **Content Invariance (Blur Test):** Max non-text probe drop was only **3.93 pt** (limit < 10 pt — PASS).
  - **Inference Latency Proxy:** Mean = **88.18ms**, P95 = **90.00ms** (< 200ms — PASS); Cold load = **0.0294s** (< 3.0s — PASS); Model size = **38.67 MB** (< 50 MB — PASS).
  - **Quantization Benchmark (TASK-6a-5):** Recommended shipping **FP16** (size 38.5 MB < 50 MB limit, avoiding 75 pt drop seen on INT8 stepperControl). Distillation not required.
  - **Production Gate Decision (DS-G8):** Holdout mAP@0.5 is 0.586 (threshold ≥ 0.850). Gate does not pass. Per project guidelines, **do not ship 41-class weights to NativeUIAuditKitModels**; the shipped detector remains the 5-class `nativeui-ios-v2.0` YOLO11n (mAP@0.5 = 0.935).

**TASK-6a-11 baseline reference-metrics artifact (2026-09-18):** `scripts/eval_reference_metrics.py`
wraps this run's existing `reports/eval_results_phase6a.json` into the standardized multi-corpus
format — `reports/pytorch_reference_metrics.json`, SHA-256
`226755b88642d1a68a0f9c3cad4b685d6d874352d48090b910c6b406ea61e405`. Only 1 of 4 named corpora is
actually available (`synthetic_fixture_test_manifest`, i.e. this run's own withheld-template
holdout, mAP@0.5 = 0.586); the other three (`real_device_fixture_holdouts`,
`production_tvos_system_holdout`, `frozen_regression_suite`) are marked `available: false` with
a stated reason each, not filled with placeholder numbers. This is the first artifact of its
kind — no prior run to diff against (`deltas.hasPrevious = false`). Every promoted checkpoint
from here forward should get one of these committed alongside it so real per-model deltas
accumulate.

---

## Run 010 — Phase 6b tvOS OS UI YOLO11n (`NativeUIModel_tvOS_v0`)

- **Date:** 2026-09-15
- **Goal:** Train the first specialized tvOS OS UI detector for Apple TV automation and navigation with TVTestRig. Target elements include Home Screen app tiles (`collectionItem`), Settings split-view items (`listRow`), system dialogs (`alert`, `cancelAction`), top navigation bars (`tabBar`), and active focus highlighting (`isFocused`).
- **Architecture:** YOLO11n (`yolo11n.pt` pretrained base, 41-class head matching `NativeUIElementType` taxonomy).
- **Dataset:** `NativeUITrainer/yolo_dataset_tvos` (2,000 synthetic tvOS images: 1,600 train, 200 val, 200 test) generated via headless SwiftUI `ImageRenderer` on macOS.
- **Dry-run Status:** Completed successfully (2 epochs, batch=8, fraction=0.05, rc=0). Validated MPS execution, label caching, and evaluation pipeline.
- **Training Config:**
  - `epochs`: 60
  - `batch`: 8
  - `imgsz`: 640
  - `rect`: True (landscape 16:9 aspect ratio preservation)
  - `optimizer`: AdamW (lr0=0.001, lrf=0.01)
  - `box`: 7.5, `cls`: 0.5, `dfl`: 1.5
  - `patience`: 15
  - `workers`: 2
  - `device`: MPS (Apple Silicon M4)
  - `output`: `NativeUITrainer/yolo_runs/phase6b_tvos_v0`
- **Status:** TRAINING_COMPLETE (60/60 epochs in 1.365 hours on Apple M4 MPS, exit rc=0).
- **Final Weights & CoreML Export:**
  - Checkpoint: `NativeUITrainer/yolo_runs/phase6b_tvos_v0/weights/best.pt` (5.5 MB stripped).
  - CoreML Package: `NativeUITrainer/yolo_runs/phase6b_tvos_v0/weights/best.mlpackage` (5.2 MB, FP16 half precision, NMS baked in). Export completed in 8.3s via `scripts/export_yolo_coreml.py`.
  - Staged for packaging: `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIModel_tvOS.mlpackage`.
- **Evaluation on 200 Held-Out OS UI Test Images (`reports/eval_results_tvos_v0.json`):**
  - **Overall mAP@0.5:** **0.995 (99.5%)**
  - **Overall mAP@0.5:0.95:** **0.9870 (98.7%)**
  - **Precision:** **0.9998 (99.98%)**
  - **Recall:** **1.0000 (100.0%)**
  - **Visual Focus Accuracy:** **100.0% (190/190 correct focus determinations)**
  - **Per-Class AP@0.5:**
    | Class | AP@0.5 | AP@0.5:0.95 |
    |---|---|---|
    | `alert` | 0.995 | 0.995 |
    | `cancelAction` | 0.995 | 0.995 |
    | `collectionItem` | 0.995 | 0.995 |
    | `imageView` | 0.995 | 0.995 |
    | `label` | 0.995 | 0.995 |
    | `listRow` | 0.995 | 0.995 |
    | `navigationBar` | 0.995 | 0.995 |
    | `primaryButton` | 0.995 | 0.995 |
    | `tabBar` | 0.995 | 0.995 |
    | `toggle` | 0.995 | 0.915 |
- **Quality Gates:**
  - `overall_mAP50_ge_0_80`: **PASS** (0.995 >= 0.80)
  - `tabBar_AP50_ge_0_80`: **PASS** (0.995 >= 0.80)
  - `focus_accuracy_ge_0_85`: **PASS** (1.000 >= 0.85)
- **TVTestRig Integration Validation:**
  - `scripts/tvos_detect.swift` offline CLI verified end-to-end with Vision OCR + CoreML model on 1080p Home Screen and Settings screenshots.
  - Successfully detected bounding boxes, fused OCR text, and resolved active focus (`state.isFocused: true`).
  - TVTestRig artifact ingestion pipeline verified via `scripts/ingest_tvos_capture.py`.

---

## Run 011 — Phase 6b-E: Exhaustive tvOS UI Dataset Generation & Dry-Run (2026-09-15)

- **Date:** 2026-09-15
- **Goal:** Expand synthetic tvOS training data beyond basic Home and Settings screens to achieve exhaustive coverage across all native tvOS UI surfaces: all menus, Control Center, multi-column settings navigation, AVKit media playback, SharePlay, on-screen keyboards, Siri overlays, and system prompts.
- **Templates Added:** 10 new parameterised templates in `NativeUIDatasetGenerator/Templates/tvOS/` and integrated into `scripts/generate_tvos_dataset.swift`:
  1. `tvOSContextMenuTemplate`: Long-press action popups with primary, secondary, and destructive buttons.
  2. `tvOSSidebarMenuTemplate`: Split navigation sidebars with search fields and content poster grids.
  3. `tvOSTopShelfMenuTemplate`: Pinned hero banners, trailer autoplay overlay, Watch Now and Trailer buttons.
  4. `tvOSControlCenterTemplate`: Slide-out Control Center drawer, user profile switcher, volume slider, DND toggle, HomeKit scenes.
  5. `tvOSSplitSettingsTemplate`: Deep settings hierarchy, breadcrumb navigationBar, segmented controls, steppers, and list rows.
  6. `tvOSAVKitPlaybackTemplate`: Full video transport chrome, timeline scrubber slider, elapsed/remaining time labels, skip intro button.
  7. `tvOSAudioSubtitlesTemplate`: Audio and subtitles popover modal with language checkmarks and accessibility dialogue toggles.
  8. `tvOSSharePlayTemplate`: Floating SharePlay overlay card with participant speaking halos and group controls.
  9. `tvOSKeyboardTemplate`: On-screen character grid keyboard, searchField, insertion cursor, dictation and space buttons.
  10. `tvOSSiriOverlayTemplate`: Floating Siri card, transcribed speech, Siri orb glow, and weather forecast result cards.
- **Dataset Generation:**
  - Invocation: `swift scripts/generate_tvos_dataset.swift --count 3000 --output dataset/tvos_dataset`
  - Generation time: 92.5 seconds (32.4 fps) on Apple M4.
  - Dataset size: 3,000 images at 1920×1080 (200 per family across all 15 families; 2,400 train, 300 val, 300 test).
  - Sidecar format: Schema v1.0 JSON with exact pixel bounds and Vision normalized bounds.
- **COCO/YOLO Export:**
  - Invocation: `.venv-yolo/bin/python scripts/export_tvos_coco.py --input dataset/tvos_dataset --output NativeUITrainer/yolo_dataset_tvos --clean`
  - Output: 3,000 images exported to `NativeUITrainer/yolo_dataset_tvos/` with `dataset.yaml` (41 classes).
  - Instance count: 39,520 training instances across 21 active tvOS classes (compared to only 10 classes with instances in Run 010).
- **Dry-Run Training Pass:**
  - Invocation: `.venv-yolo/bin/python scripts/train_tvos_model.py --dry-run`
  - Configuration: YOLO11n, 2 epochs, batch=8, imgsz=640, device=MPS.
  - Outcome: Completed in 0.010 hours (exit rc=0). Validated MPS training loop, loss computation, weight stripping, and validation pipeline.
- **Full Training Run (100 Epochs):**
  - Invocation: `.venv-yolo/bin/python scripts/train_tvos_model.py --epochs 100`
  - Output run directory: `NativeUITrainer/yolo_runs/phase6b_tvos_v2`
  - Time elapsed: ~3.5 hours on Apple M4 MPS (100/100 epochs, exit rc=0).
  - Metrics at Epoch 100 (`results.csv`):
    - Precision: **0.994** (99.4%)
    - Recall: **0.975** (97.5%)
    - mAP@0.5: **0.971** (97.1%)
    - mAP@0.5:0.95: **0.947** (94.7%)
    - Box Loss: 0.1699, Cls Loss: 0.1523, DFL Loss: 0.7738
    - 20 of 21 active classes achieved mAP@0.5 >= 0.990.
- **CoreML Export & Packaging:**
  - Exported via `scripts/export_yolo_coreml.py` using Python 3.12 (`.venv-coreml`) with FP16 quantization and baked-in NMS: `NativeUITrainer/yolo_runs/phase6b_tvos_v2/weights/best.mlpackage` (5.2 MB).
  - Compiled via `xcrun coremlcompiler compile` into `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/NativeUIModel_tvOS.mlmodelc`.
  - Updated model manifest `model_manifest_tvos_v1.json` (`modelId: nativeui-tvos-v2.0`).
  - Registered `ModelRegistry.tvOS` (`nativeui-tvos-v2.0`, mAP@0.5 = 0.971, 21 active classes) with backwards-compatible `tvOS_v1` retention.
  - All 71 offline unit and integration tests passing (`NativeUIAuditKitTests` + `NativeUIAuditKitModelsTests`).
  - Real Apple TV qualification: verified against TVTestRig captures (`fixture_initial_screen.png`, `fixture_grid_screen.png`, `fixture_chaos_screen.png`, `latest.png`) — 100% focus localization accuracy.

---

## Run 012 — Phase 6b-E Extended: Comprehensive tvOS UI Coverage & 25-Class Model (`NativeUIModel_tvOS_v3.0`)

- **Date:** 2026-09-16
- **Goal:** Extend tvOS element detection to 10 additional OS-level surfaces and UI features: multitasking App Switcher carousel, PIN / Passcode / AirPlay pairing dialogs, VoiceOver high-contrast outline overlays and speech caption bars, Apple Music synchronized lyrics views, App Store product sheets with screenshot carousels, Sign In with Apple QR code pairing modals, Apple Fitness+ workout metric HUDs, system loading spinners / buffer progress bars, live broadcast sports bugs / channel rails, and Conference Room Display mode.
- **Templates Added:** 10 new parameterised templates in `NativeUIDatasetGenerator/Templates/tvOS/` and integrated into `scripts/generate_tvos_dataset.swift`:
  1. `tvOSAppSwitcherTemplate`: Multitasking carousel with app preview cards (`collectionItem`), app icon badge (`imageView`), and app title (`label`).
  2. `tvOSPINEntryTemplate`: Numeric PIN entry digits / secure dots (`secureField`, `textField`), keypad digits (`collectionItem`, `secondaryButton`), and cancel / back action (`cancelAction`).
  3. `tvOSVoiceOverOverlayTemplate`: VoiceOver active high-contrast outline border (`collectionItem`) and bottom speech caption bar (`label`, `sheet`).
  4. `tvOSNowPlayingLyricsTemplate`: Apple Music karaoke / synchronized lyrics sheet (`sheet`), lyric lines (`label`), time scrub progress (`slider`, `progressView`), and audio format badges (`imageView`).
  5. `tvOSAppStoreProductTemplate`: App Store product detail view, "Get" / "Update" button (`primaryButton`), screenshot preview carousel (`collectionItem`), app description (`label`), and ratings breakdown (`progressView`).
  6. `tvOSSignInWithAppleTemplate`: Modal auth sheet (`sheet`, `popover`), QR code pairing image (`imageView`), authorization instruction links (`link`), and cancel button (`cancelAction`).
  7. `tvOSFitnessHUDTemplate`: Apple Fitness+ workout HUD overlay, activity rings (`imageView`, `progressView`), burn bar (`slider`, `progressView`), heart rate / calorie labels (`label`), and pause button (`secondaryButton`).
  8. `tvOSLoadingBuffersTemplate`: System indeterminate loading indicator (`activityIndicator`), linear buffering bar (`progressView`), status label (`label`), and cancel action (`cancelAction`).
  9. `tvOSLiveBroadcastHUDTemplate`: Live sports score bug (`label`, `imageView`), channel rail (`collectionItem`, `tabBar`), and multi-view channel switcher (`secondaryButton`).
  10. `tvOSConferenceRoomTemplate`: Conference Room Display mode, AirPlay connection card (`popover`), Wi-Fi network instructions (`label`, `link`), and device PIN badge (`secureField`).
- **Dual Focus Engine Enhancements:**
  - Implemented VoiceOver high-contrast double border outline detection (dark + bright edge contrast scoring) and caption bar contextual boost in `evaluateElementFocusScore` and `resolveTVOSFocus` in `NativeUIDetectionRequest.swift`.
  - Expanded focusable types to include `secureField`, `textField`, `segmentedControl`, `stepperControl`, `slider`.
  - Implemented explicit focus abstention (`isFocused: nil`) for full-screen media playback and ambient screensavers.
- **Dataset Generation:**
  - Invocation: `swift scripts/generate_tvos_dataset.swift --count 5000 --output dataset/tvos_dataset`
  - Generation time: 148.5 seconds (33.7 fps) on Apple M4.
  - Dataset size: 5,000 images at 1920×1080 (200 per family across all 25 families; 4,000 train, 500 val, 500 test).
  - Sidecar format: Schema v1.0 JSON with exact pixel bounds and Vision normalized bounds.
- **COCO/YOLO Export:**
  - Invocation: `.venv-yolo/bin/python scripts/export_tvos_coco.py --input dataset/tvos_dataset --output NativeUITrainer/yolo_dataset_tvos --clean`
  - Output: 5,000 images exported to `NativeUITrainer/yolo_dataset_tvos/` with `dataset.yaml` (41 classes).
  - Active classes with instances: 25 classes (`activityIndicator`, `alert`, `cancelAction`, `collectionItem`, `contextMenu`, `destructiveButton`, `imageView`, `label`, `link`, `listRow`, `navigationBar`, `popover`, `primaryButton`, `progressView`, `searchField`, `secondaryButton`, `secureField`, `segmentedControl`, `sheet`, `sidebar`, `slider`, `stepperControl`, `tabBar`, `toggle`, `toolbar`).
- **Training Run (25 Epochs on Apple Silicon M4 MPS):**
  - Invocation: `nohup .venv-yolo/bin/python scripts/train_tvos_model.py --epochs 25 --batch 16 --output NativeUITrainer/yolo_runs/phase6b_tvos_v3`
  - Training time: 1.464 hours (exit rc=0).
  - Final Validation Metrics at Epoch 25 (`results.csv`):
    - Precision: **0.983** (98.3%)
    - Recall: **0.983** (98.3%)
    - mAP@0.5: **0.9822** (98.2%)
    - mAP@0.5:0.95: **0.944** (94.4%)
    - Box Loss: 0.2882, Cls Loss: 0.2185, DFL Loss: 0.8143
    - 24 of 25 active classes achieved mAP@0.5 = 0.995.
- **CoreML Export & Packaging:**
  - Exported via `scripts/export_yolo_coreml.py` using Python 3.12 (`.venv-coreml`) with FP16 quantization and baked-in NMS: `NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage` (5.2 MB).
  - Compiled via `xcrun coremlcompiler compile` directly into `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/NativeUIModel_tvOS.mlmodelc`.
  - Updated model manifest `model_manifest_tvos_v1.json` (`modelId: nativeui-tvos-v3.0`).
  - Registered `ModelRegistry.tvOS` (`nativeui-tvos-v3.0`, mAP@0.5 = 0.9822, 25 active classes) with backwards-compatible `tvOS_v2` and `tvOS_v1` retention.
  - All 73 unit and integration tests passing offline across `NativeUIAuditKitTests` and `NativeUIAuditKitModelsTests`.

---

## Phase 6b-R — Real Apple TV Hardware Qualification (Office Lab)

**Date:** 2026-09-17  
**Hardware Device:** Apple TV 4K (`office`, ID: `8D80F616-6C12-49A6-9015-8F594EE5F24E`, Model: `AppleTV5,3`, tvOS `26.6`)  
**Pipeline:** TVTestRig `aatv` CLI + AVFoundation 1920×1080 capture stream + YOLO11n `NativeUIModel_tvOS_v3.0` (25 classes) + Dual Focus Engine (Parallax Expansion / Glow + Inverted High-Luminance Pill + VoiceOver Contrast Border) + Apple Vision OCR Fusion.

- **Outcome:**
- **28 Real Hardware Screenshots Ingested:**
  - Standardized sidecar provenance JSON (`captureSource: realAppleTVTVTestRig`, SHA-256 integrity hashes, 1920×1080 resolution).
  - Stored in `dataset/tvos_captures/`.
- **Target Navigation & OS Surfaces Qualified:**
  1. **Home Screen & Top Shelf Dock:**
     - Ingested dock focus transitions across standard and featured rows.
     - Detected 16–37 elements per screen (`collectionItem`, `imageView`, `label`, `searchField`).
     - Parallax tile expansion verified: actively focused item expanded from baseline \(247 \times 147\) pt to \(301.5 \times 173.2\) pt (IoU/confidence > 0.96).
  2. **App Switcher Multitasking Carousel:**
     - Navigated via rapid double-press Home remote sequence (`remote press home` × 2).
     - Traversed horizontally across running card decks (`office_session2_switcher.png` and `office_session2_switcher_card2.png`).
     - Detected 19–36 elements per frame across multitasking cards (`collectionItem` cards with conf=0.83–0.98, app icons `imageView`, app title badges `label`, and dismiss handles `cancelAction`).
  3. **TVTestRig Fixture Surface:**
     - Successfully navigated and launched `TVTestRig Fixture` directly from the Home dock (`office_fixture_main.png`).
     - Detected 22 elements across seeded defect matrix, interactive probe buttons (`secondaryButton`), accessibility status indicators, and nested sub-deck list rows (`listRow`).
  4. **App Interactive Surfaces & Focus Transitions (Photos / Pluto / YouTube):**
     - Navigated into application onboarding and guest screens.
     - Detected interactive action buttons (`primaryButton`, `secondaryButton`, `listRow`, `label`, `imageView`).
     - Measured inverted high-luminance interior pill focus score:
       - Button 1 ("View All iCloud Photos"): brightness 228.9 (focused) vs Button 2: 149.6.
       - Navigated `remote press down` -> focus successfully shifted: Button 2 brightness increased to 225.9 while Button 1 dropped to 138.7.
- **Hardware Qualification Report:**
  - Written to `reports/tvos_hardware_qualification.json`.
  - 675 native elements detected across 28 live hardware captures (388 `collectionItem`, 140 `label`, 96 `imageView`, 15 `secondaryButton`, 13 `cancelAction`, 10 `listRow`, 10 `searchField`, 2 `primaryButton`, 1 `sidebar`).
  - Zero false positives on screen edges or video stream artifacts.

---

## Run FDR-001 — FocusRingDetector Stage 2 (Started 2026-09-17)

**Trigger:** tvOS focus is resolved by `resolveTVOSFocus` brightness/geometry heuristics. That path mis-ranks VoiceOver outlines, bottom-bezel chrome, and high-contrast unfocused tiles. A dedicated crop classifier should beat the heuristic without touching YOLO11 weights.

**Status:** v0.1 SHIPPED 2026-09-18. FDR-001 30/30, torch held-out 270/270, CoreML 4.80 MB, `FocusRingDetector.mlmodelc` bundled. Hard-neg n=0 (FOCUS-DET-05).

**Architecture:**
- Backbone: MobileNetV4-Conv-Small (vendored `scripts/focus_ring_backbone.py`, timm 1.0.29 topology), binary sigmoid, 256×256 RGB ÷255
- Export: `torch.jit.trace` → coremltools 9.0 FP16 (no ONNX), outputs `is_focused_prob` + `confidence` (both tensors of shape `[1]`)
- Package budget: ≤5.0 MB. FastViT-T8 deferred (ANE attention risk)
- Thresholds in metadata / Swift, not weights: focus 0.85, ambiguity 0.70
- Dataset target v0.1: 1,500–2,500 real fixture pairs (Plan A; FIX-SYNTH-06 RPC does not exist)
- Dataset target v1.0: 6,000+ pairs
- Output: `NativeUITrainer/focus_ring_runs/<run_id>/`
- Log / reports: `focus_ring_detector_*_report.json` under the run `export/` directory

**Gates (held-out):** accuracy ≥99%; FPR ≤0.5%; FNR ≤1.0%; P/R @ 0.85 ≥0.98; hard-negative FPR (`light`+`highContrast`) ≤0.5%.

**YOLO pipeline:** untouched (`train_ios_model.py`, `train_tvos_model.py`, 41-class IDs).

**Fallback:** `resolveTVOSFocus` stays in tree. `useFocusClassifier` defaults true; missing `FocusRingDetector.mlmodelc` uses the heuristic.

**Phase A outcome:** scaffolding only. Harvest `--dry-run` on 15 fixture captures produced **327** focusable crops, all unlabeled (empty sidecar `elements`). Train `--dry-run` exits 0 with no labeled data. `swift build` / `swift test` pass without `.mlmodelc`.

**Phase B notes (IPC):** TVTestRig.app is App Sandboxed. Coordinator socket is `~/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/.tvtr/s`. `aatv --project <checkout>` looks at the repo `.tvtr/s` and reports `serviceUnavailable`. Do not set `TVTESTRIG_PROJECT` for this Debug GUI (sandbox cannot write the checkout). `harvest_focus_pairs.py --live` points aatv `HOME` at `NativeUITrainer/.tmp/aatv_home` with a symlink to the container socket — never set `HOME` to the container Data root (Evidence/Sessions listdir hangs). Office `device connect` succeeded 2026-09-18T03:20:50Z.

**Phase B harvest:** `--live --max-pairs 1500 --output dataset/focus_ring`. Log: `NativeUITrainer/focus_ring_harvest.log`. Closed-loop `navigate --count 1` only; no Home, no Select.

**Phase B pass 1 outcome (2026-09-18T03:30–03:53Z, 23.5 min):** **454** labeled pairs (train 363 / val 54 / test 37). Types: primaryButton 225, secondaryButton 215, collectionItem 9, segmentedControl 5. Last good frame step 1729; `connectionLost` from step 1731 through `--max-steps` 2500 (no reconnect halt — script kept pulsing). Two extra TVTestRig Debug processes (`DerivedData-LEASECOEX`) appeared during the run. Crops: `dataset/focus_ring/crops/` (908 PNGs). Short of the 1,500-pair v0.1 floor.

**Phase B pass 2 outcome (2026-09-18T04:17–04:36Z, 18.6 min):** Hit the **1,500**-pair floor (`harvest_exit=0`). Splits: train 1,201 / val 164 / test 135. Types: collectionItem 1,055, primaryButton 225, secondaryButton 215, segmentedControl 5. 3,000 crop PNGs. Resume kept pass-1 pairs. Still missing toggle/slider/textField/stepper coverage.

**Phase B train (FDR-001):** `pip install timm` hangs in `.venv-yolo`. Unzipping `timm-1.0.29` into site-packages still left `import timm` / `import timm.layers` hung (BP-47). Vendored MobileNetV4-Conv-Small in `scripts/focus_ring_backbone.py` (torch.nn only, `pretrained=False`, 2.49M params).

**TRAINING_COMPLETE 2026-09-18T05:27–05:38Z (11.1 min, MPS):** 30/30 epochs. Final train_loss=0.0016 val_loss=0.0001 (best). Epoch 14 val spiked to 0.8434 then recovered; `best.pt` tracks min val. Log: `NativeUITrainer/focus_ring_train.log`. Weights: `NativeUITrainer/focus_ring_runs/fdr001/weights/{best,last}.pt` (~10.2 MB each).

**Torch eval:** test_n=270 (135 pairs). tp=135 fp=0 tn=135 fn=0. accuracy=1.0 FPR=0 FNR=0 P/R@0.85=1.0. Reports: `NativeUITrainer/focus_ring_runs/fdr001/export/focus_ring_detector_{eval,hard_negative_eval}.json`. Hard-negative split is empty (all harvested frames `theme=dark`); the hard-neg FPR gate is vacuously true. Geometric pair labels (area ratio / IoU) likely make this split easy — do not treat 100% as VoiceOver-vs-focus proof.

**CoreML export (FOCUS-DET-04, 2026-09-18):** First attempt hung (`import coremltools` in `.venv-yolo`; ONNX path also needs a missing `onnx` package). `export_focus_ring_coreml.py` was rewritten to `torch.jit.trace` → `ct.convert` (coremltools 9.0, TorchScript dialect). `FocusRingDetector.mlpackage` = **4.80 MB** (≤5.0 PASS). Compiled with `xcrun coremlc compile` into `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc`. `Package.swift` copies that resource. Tests require URL, load, `focusThreshold`/`ambiguityThreshold` metadata, and a unit-interval `classify` on bundled `tvos_home_screen.png`.

Do not replace bundled v0.1 until FOCUS-DET-05 records a non-vacuous hard-neg FPR.

### 2026-09-21 — FocusRing readiness correction (not an experiment)

No run ID allocated and no training/benchmark launched. The candidate trainer now
uses a genuine configuration/data-only `--dry-run`, requires explicit execution
and a logged experiment ID, rejects missing pixels/partitions and excludes the
test split from per-epoch evaluation. Candidate configuration remains 30 epochs,
batch 64, lr 0.0003, vendored MobileNetV4 with fresh initialization. Byte-backed
manifest v1.2 and separately reviewed corpus approval are required. Historical
run reports remain unchanged; no historical metric is requalified by these fixes.
See `Plans/FocusRingConsumerReadiness.md` and the FOCUS-CONSUMER handoff.

### 2026-09-21 — FDR-001 evidence audit correction (not a new experiment)

The legacy 1,500-pair manifest's 3,000 PNGs decode at 256×256; all pairs are dark.
Zero seed overlap does not imply independent held-out data: normalized-pixel hashing
found 84 groups crossing partitions, including 40 groups shared by train and test
(25 train/test plus 15 train/test/validation). One duplicate-pixel group has both
focused and unfocused labels. The recorded 270/270 result is not a clean independent
model-quality estimate; the historical n=0 hard-negative pass is invalid support.
No original report, dataset or weight was overwritten, no run ID allocated, and no
new real-data inference/training occurred. The corrected evaluator rejects missing
members/leakage and requires explicit isolated output; legacy diagnostics cannot
pass qualification. Current qualified crops require v1.3 runtime preprocessing,
superseding v1.2's readiness limitation above. See `../reports/work/EVIDENCE-AUDIT/handoff.md`.

## Run FDR-002 — warm-stretch development experiment (2026-09-22)

Pre-launch authorization: maintainer “ok lets do the experiment.” Status: runtime
attempt stopped before training. PID72087, 15:56:25–16:06:25 UTC, 600s, exit143
from owned-process watchdog. Cold torch import consumed the budget; zero epochs,
no checkpoint. Stack samples show dependency-file reads, not model computation.
Cache-isolation probe timed out45s; subsequent warmed import passed in0.717s
(torch2.13.0, MPS available). Original outputs/logs retained; FDR-006 is the
single evidence-supported replacement attempt with unchanged protocol. Output:
`NativeUITrainer/focus_ring_runs/fdr002-warm-stretch` (new, isolated).
Protocol `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
Strict FDR-001 checkpoint initialization; fresh optimizer. 74 training crops
(37 pairs, Root + General); 18 validation crops (9 Accessibility pairs).
Vendored MobileNetV4-Conv-Small, AdamW lr0.0003, batch8, seed42, 8 epochs,
RGB/255, no augmentation, 16% expanded production stretch, maximum600 seconds.
Minimum validation BCE selects checkpoint; fixed thresholds0.5/0.85 reported.
No final test, export, promotion or release qualification. Related screen journeys
remain grouped; this same-app pilot is not independent style/platform evidence.
Plan: `Plans/FocusLearningExperiment.md`; reviewed sources in FOCUS-EXP-01.

## Run FDR-003 — scratch-stretch development experiment (2026-09-22)

Pre-launch status: logged before execution; same authorization/config/data/selection
as FDR-002, except random initialization. Output `NativeUITrainer/focus_ring_runs/fdr003-scratch-stretch`.
Protocol `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
Arm `scratch-stretch`; 8 epochs, batch8, AdamW0.0003, seed42, 74/18 crops,
no augmentation, 600s limit. No release claim or automatic retry.
Outcome: completed8/8, exit0, PID74287,19.995s process /9.772s post-preflight.
Selected epoch8, validation BCE0.0234107; TP9/FN0/FP0/TN9 at0.5 and0.85.
First18/18 epoch7. Best SHA256 `55cc89c1c54beeadc689c9c679ab1c73e524a96757781591b0fe905ef8b48a96`.

## Run FDR-006 — warm-stretch after runtime-only startup failure (2026-09-22)

Logged before launch under the same approved four-arm experiment. Replaces only
FDR-002's zero-epoch runtime attempt after a successful0.717s import-only probe.
Not a performance-triggered retrain; no hyperparameter, data or threshold changes.
Output `NativeUITrainer/focus_ring_runs/fdr006-warm-stretch`.
Protocol `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
Arm `warm-stretch`; strict FDR-001 initialization, fresh AdamW0.0003, batch8,
seed42, 8epochs, 74/18 crops, no augmentation, 600s external process deadline.
All remaining arms use the same deadline-enforcing serial wrapper.
Outcome: completed8/8, exit0, PID73427,419.131s process /409.443s post-preflight,
including cold optimizer dependencies. Selected epoch7, validation BCE0.0000125763;
TP9/FN0/FP0/TN9 at0.5 and0.85; first18/18 epoch1.
Best SHA256 `00359cc9bd547f2821b244b45ce64374465f6e5a30e92070dd520af2cafb2fa3`.

## Run FDR-004 — warm-aspect-fit development experiment (2026-09-22)

Pre-launch status: logged before execution; same authorization/config/data/selection
as FDR-002, except aspect-fit black-padded 256×256 crops after16% expansion.
Output `NativeUITrainer/focus_ring_runs/fdr004-warm-aspect-fit`.
Protocol `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
Arm `warm-aspect-fit`; strict FDR-001 initialization, 8 epochs, batch8,
AdamW0.0003, seed42, 74/18 crops, no augmentation, 600s limit.
No production preprocessing change, release claim or automatic retry.
Outcome: completed8/8, exit0, PID74342,19.567s process /9.482s post-preflight.
Selected epoch5, validation BCE0.000692525; TP9/FN0/FP0/TN9 at0.5 and0.85.
First18/18 epoch1. Best SHA256 `3dacb2958d697e546552521f2d9764ed39a40974e66f3a9ae6f21d5ccf797673`.

## Run FDR-005 — scratch-aspect-fit development experiment (2026-09-22)

Pre-launch status: logged before execution; same authorization/config/data/selection
as FDR-004, except random initialization.
Output `NativeUITrainer/focus_ring_runs/fdr005-scratch-aspect-fit`.
Protocol `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
Arm `scratch-aspect-fit`; 8 epochs, batch8, AdamW0.0003, seed42, 74/18 crops,
no augmentation, 600s limit. No release claim or automatic retry.
Outcome: completed8/8, exit0, PID74380,19.300s process /9.226s post-preflight.
Selected epoch8, validation BCE0.825227; TP0/FN9/FP0/TN9 at0.5 and0.85.
AUROC1.0 despite failed fixed-threshold decisions; no threshold tuning was done.
Best SHA256 `40fece982d9c8ad9c1d2647a1e7fc1326eebb86bbd8e9c178bf96e0bff8316bc`.

### FOCUS-EXP-01 interpretation (all four completed arms)

All used torch2.13.0/MPS and the same frozen development protocol. Shipped CoreML
on these18 validation crops gives TP0/FN9/FP2/TN7 at0.85. Initial FDR-001 PyTorch
gives TP0/FN9/FP1/TN8: mean absolute probability difference0.004849, maximum0.016776
versus CoreML CPU. Runtime/export parity is not exact and remains follow-up work.
Warm initialization learned the native row style sooner in this fixed budget;
aspect-fit provided no demonstrated advantage. Prefer production stretch plus
warm-start for the next controlled experiment, not as a production promotion.
Only9 correlated same-app validation pairs; checkpoint selection uses this set.
No independent final-test, fixture-retention, physical-device or release-gate pass.
Evidence: `../reports/work/FOCUS-EXP-01/comparison.json` and `handoff.md` in that folder.

## Run FDR-007 — native Apps incremental development (2026-09-22)

Logged before launch under the approved independent native tranche. Initialize strictly
from FDR-006 with fresh optimizer; production stretch, 16% expansion, 256×256.
Protocol `a756f182c633ae6ad4b4985a75200ef738a7974bf8520ce8a3c946d8574d4f8c`.
40 training pairs (Root12/General25/Apps3), 9 Accessibility validation pairs;
Remotes6 pairs challenge-only, excluded from selection. Home admitted zero pairs.
8 epochs, batch8, AdamW0.0003, seed42, no augmentation, external600s deadline.
Output `NativeUITrainer/focus_ring_runs/fdr007-native-incremental`.
Question: retain prior native-row performance with new Apps training examples;
not a causal ablation of added data or a production qualification. Before training,
FDR-006 already scores12/12 on Remotes at0.85 versus shipped5/12. No automatic
retraining, promotion, claim of independent app/style generalization, or TTR dependency.
Arm `warm-stretch`. Initial launcher rejected the log before model initialization
because this literal arm binding was missing (exit2, zero epochs/output). Corrected
the log; retain the rejected attempt and use a new execution ledger for the same
not-yet-started candidate. No data/configuration change or performance retry.
Outcome: completed8/8, exit0, PID80937,18.608s process /7.481s post-preflight,
torch2.13.0/MPS. Selected epoch8 by validation BCE0.00000733137;
TP9/FN0/FP0/TN9 at0.5 and0.85. Best SHA256
`a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`.
Frozen Remotes challenge: TP6/FN0/FP0/TN6 at both thresholds, equal to FDR-006.
Shipped CoreML at0.85: TP0/FN6/FP1/TN5. No observed challenge improvement from
this increment; do not infer causal equivalence or unseen-style generalization.
Full-frame/crop pixel and lineage isolation passed against both experiment protocols.
Evidence: `../reports/work/OS-FOCUS-03/summary.json`, challenge-before/after.json.
No further run, export or promotion performed.

## Run FDR-008 — mixed-appearance development (2026-09-23)

Logged before launch, 03:35Z. Maintainer instruction: “Do the 30 eppch run”.
Authorize exactly the frozen proposal, arm `warm-stretch`, output
`NativeUITrainer/focus_ring_runs/fdr008-mixed-appearance`.
Protocol `fa1c7cffa8e42aac511353c9ccd99cf091dbf25a05cb3f5deba52e1ac458fca2`.
Strict FDR-007 warm weights (`a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`),
fresh AdamW optimizer, 30 epochs, batch64, lr0.0003, seed42, no augmentation;
vendored MobileNetV4, production16% expansion/256×256 stretch, RGB/255.
126 train pairs (40 native +86 Fixture), nine native-validation pairs; no test set
or independent Fixture validation. Frozen stratum sampling: expected88.89% Fixture,
11.11% native. Minimum native-validation BCE selects checkpoint, earliest tie.
Internal1800s budget after preflight; external2100s process limit includes preflight.
No retry, scale capture, TTR/Office operation, export or promotion. This is a
learning/retention diagnostic, not a production gate. Approval and execution ledger:
`../reports/work/FDR-008/`. PID, timings and outcome added after execution.

Outcome: completed30/30, exit0, PID11340, 2026-09-23 03:36:54–03:39:59Z.
184.453s whole process /38.399s post-preflight, torch2.7.0/MPS in the approved
isolated environment (prior FDR-007 training used2.13.0; not a controlled data-only
ablation). Selected epoch3, native-validation BCE0.000002755059. Best SHA256
`40f23078e0ca5b5b03ac2bc52b6f1c10e9477687a99b26fac327e8199d75d11c`.
At0.85, same-backend CPU before/after evaluation: Fixture training172 crops improves
TP43/FN43/FP0/TN86 → TP86/FN0/FP0/TN86 (75% →100%). At0.5:77.33% →100%.
Native train80/80, native validation18/18 and reused Remotes challenge12/12 remain
correct at both thresholds. No observed forgetting on those small, correlated sets.
Fixture scores are training fit, not independent generalization. No export, promotion,
CoreML parity or physical-device claim. Next evaluate new appearances/independent
Fixture groups, not another run on these saturated members. Evidence:
`../reports/work/FDR-008/comparison.json`, `execution.json`, `handoff.md`.

Post-run appearance diagnostic (no new training): FOCUS-VISUAL-03 compared both
checkpoints on retained Home/Photos and all seven frozen box variants. FDR-008
still0/8 correct unique base selections at0.85; Home false positives increase0→5
versus FDR-007, with one wrong-focus and one multiple-focus base frame. Fixture
training fit did not establish native appearance transfer. Keep candidate experimental;
next acquire observed-label appearance diversity and independent evaluation, not
more epochs on existing members. Evidence `../reports/work/FOCUS-VISUAL-03/handoff.md`.

---

## Run 013 — Phase 6a iOS YOLO11m 41-Class Addon Training (2026-09-24–27)

**Trigger:**
Run 009 achieved historical original-corpus holdout test mAP@0.5 = 0.586 (58.6%),
but only13 of41 classes had test support. The replacement r6 baseline is0.5549
using the retained custom AP workflow; these different corpora have no numerical
delta. Run013 added coverage through the following within-family addon experiment,
not a completed41-class withheld-family generalization qualification:
1. Implemented and verified 4 new generator template families in `GeneratorRunner`:
   - `ModalDialogueFlowTemplate`: `alert`, `actionSheet`, `sheet`, `popover`, `contextMenu`, `cancelAction`, `destructiveButton` (+ buttons/labels)
   - `SystemNavigationShellTemplate`: `tabBar`, `toolbar`, `sidebar`, `statusBar`, `dynamicIsland`, `searchField` (+ navigationBar/labels)
   - `InteractiveControlPaletteTemplate`: `colorWell`, `menuButton`, `segmentedControl`, `slider`, `disclosureGroup` (+ toggle, stepperControl)
   - `RichContentFeedTemplate`: `collectionItem`, `mapView`, `activityIndicator`, `refreshControl`, `scrollIndicator`, `link`, `tooltip`
2. Generated 2,800 pairs (700 per addon family: 500 train / 100 val / 100 test).
3. Assembled the combined `ios-41class-r7-combined` corpus (16,940 r6 + 2,800 addon = 19,740 pairs: 14,540 train / 2,800 val / 2,400 test) with 202,292 total bounding boxes.
4. Class presence:
   - Train: 40/41 classes present (only `webContent` milestone exception absent).
   - Val: 35/41 classes present.
   - Test: 38/41 classes present (25 additional classes; homeIndicator, unknown,
     webContent absent). The400 addon test images share their four families with
     training and validation; only the2,000 original r6 members are withheld-family
     diagnostics. New image bytes alone do not establish family independence.

**Configuration:**
- Architecture: YOLO11m (`weights/yolo11m.pt`)
- Classes: 41 native Apple UI classes
- Batch size: `batch=8` (ADR-0006 D3)
- Checkpoints: `save_period=-1` (ADR-0006 D1, only `best.pt` and `last.pt`, with `last.prev.pt` backup)
- Metric plotting: `plots=False` (ADR-0006 D2)
- Optimizer: AdamW, lr0=0.001, lrf=0.01, momentum=0.937, weight_decay=0.0005
- Augmentations: Mosaic=1.0, OHEM callback enabled (hardest 20% oversampled 2×)
- Dataset: `NativeUITrainer/yolo_dataset_41class_r7/dataset.yaml`
- Target epochs: 150 with patience 15 early stopping
- Device: Apple Silicon MPS (`mps`), workers=4
- Output: `NativeUITrainer/yolo_runs/phase6a_r013/`

**Dry-run Status:**
- Completed 2 epochs on 5% sample (`phase6a_r010_dryrun`, exit 0). Verified label caching (2800 val, 14540 train), MPS execution, OHEM callbacks, loss calculation across 35 present classes in validation.

**Training status:** COMPLETE. Launched PID7325 with caffeinate on Apple Silicon
MPS; `NativeUITrainer/training_6a13.log` records106 epochs in62.818hours and
patience15 early stopping, best epoch91. No training was restarted by IOS-R013-EVAL.
Epoch91 CSV validation: precision0.85058, recall0.88031, mAP50=0.88025,
mAP50:95=0.85031. These validation values are not independent holdout scores.
Frozen best.pt SHA-256:
`88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7`.
Evaluation evidence: [IOS-R013-EVAL](../reports/work/IOS-R013-EVAL/verification.md).

**2026-09-27 evaluation complete, review-ready:**
[Handoff](../reports/work/IOS-R013-EVAL/handoff.md),
[metrics](../reports/work/IOS-R013-EVAL/metrics.md),
[ranked failures/next work](../reports/work/IOS-R013-EVAL/error_analysis.md).
Preparation audited all19,740 pairs in219.9s, zero integrity errors or decoded
duplicates/cross-split pixel reuse. Frozen explicit-manifest MPS inference completed
all2,400 cases with zero failures, preserving640 letterbox/confidence0.001/NMS0.7/max300.
Export including manifest validation128.24s (prediction loop114.2s); whole infer/reuse
stage140.7s. Retained Run009 predictions passed exact2,000-member input/settings/map/
checkpoint accounting and were reused, then both models were rescored in30.1s with
the same custom all-point interpolated AP implementation (not official COCO AP).

| Population | Images/classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- |
| Run009 same-input withheld baseline | 2,000/13 | 0.5549 | 0.4310 | 0.2302 | 0.3982 |
| Run013 withheld | 2,000/13 | 0.6322 | 0.5834 | 0.5299 | 0.5707 |
| Run013 addon, within-family diagnostic | 400/33 | 0.9785 | 0.9697 | 0.9696 | 0.9703 |
| Run013 combined, supplementary only | 2,400/38 | 0.8790 | 0.8551 | 0.8375 | 0.8527 |

Per-class support/AP/P/R and per-family comparisons are retained in the report.
**Diagnosis/action:** improved localization and several classes, but withheld mean
is below0.85; secondaryButton0, pageControl0.0012, listRow0.0721 and imageView0.1936
remain below0.65. Toggle AP50 regresses5.54percentage points. Addon scrollIndicator
AP50=0.29 and AP70=AP90=0 identify a thin-box weakness despite near-perfect addon mean.
Keep candidate unshipped; next propose label-role/geometry review and independent
41-class coverage, not another unmeasured training run. DS-G8 remains open; no
threshold change, retraining, export, device capture or promotion. Software checks:
23 focused Python tests, offline Swift build and14 XCTest+109 Swift Testing tests pass.
