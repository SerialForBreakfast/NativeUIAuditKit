# IOS-ROI-196 — coverage comparison and proposal diagnosis

2026-10-05 / Codex. Started from clean3499a12. No Git writes, TTR operations,
capture, export or promotion. Shipped models and all evaluation roles preserved.

## Qualification and independent companion

Qualified1173unique crops:802originals linked without changes plus371new crops
from96previously admitted training frames/74groups.43new duplicate aliases retained
(137including193aliases). No source selection was silently dropped. New crop label
dispositions:555retained,974clipped,4534outside,8excluded slivers; all page targets
fully retained. Reused193cropper, clipping and canonical duplicate checks.

Verified native96catalog/receipt/audit ancestry and excluded its renderer families,
full-frame decoded pixels and evaluation crop pixels. Unknown generator ancestry
fails closed. Failed preflight used an incorrect sidecar field; corrected to declared
generatorProfile before output. Failed first materialization used absolute manifest
paths; preserved that sources.json, then used verified links/relative paths in
attempt02. Neither failure launched training or altered source data.

Proposal seal804ee6c89997f370aff3cf893f025e0b2be6fa7038a6a3784c1a9b930472909f.
Protocol SHA2565417ca1c6f0d6be799e2f64a33f7a445c966d5c77ed67591bc902e3561079f0a.

Cached022recall audit (fixed confidence.25/IoU.5):

| Membership | TP | FP | Misses |
|---|---:|---:|---|
|216training-fit|185|38|26geometry,5low-confidence|
|96development|58|14|12geometry,5low-confidence,21no overlapping exported proposal|
|2400retained|249|24|324low-confidence,27no overlapping exported proposal|

FP composition: fit33geometry/5duplicates; development7geometry/7duplicates;
retained4geometry/16duplicates/4non-overlap. Count-only development ceiling at the
existing .001export floor is75/96, not deployable recall. Fit-only inspection found
all five low-confidence misses match the rank-one subthreshold proposal.197plans
a capped proposal study and independent deterministic-window coverage audit; no
production threshold change or oracle evaluation crops.
Recall seal30715b322573b8b31f84126b18965aef35ebb2b3e0e15c6862298e12aa264a96.

## Run026 — complete, experimental only

PID81934; fixed10epochs,147batches/epoch,190verified optimizer steps. Fresh022last
initialization and unchanged025configuration/merge rule. Larger data and190versus130
updates mean coverage plus compute, not equal-compute attribution.2GiBcap and fixed
terminal checkpoint; in-sample validation does not establish generalization.
Actual execution/terminal pins: ignored artifacts/attempt02/candidate and
NativeUITrainer/yolo_runs/roi196-r026. No second run authorized by this report.

Completed exit0 in3729.533seconds (62.16minutes);568crop predictions34.536seconds.
Every216fit/96development/2400retained original was scored; no denominator changes.
The actual merged non-page predictions and metrics remain unchanged.

| Page-control metric | Run025 | Run026 |
|---|---:|---:|
| Fit AP50:95 |.763265|.792093|
| Development AP50:95 |.380124|.453840|
| Retained AP50:95 |.461604|.529515|
| Development AP90 |.039291|.133929|
| Retained AP90 |.000929|.098482|
| Fit TP/FP |199/24|199/24|
| Development TP/FP |58/14|58/14|
| Retained TP/FP |249/24|249/24|

Retained page AP50:95 also exceeds022's.494261. Retained aggregate AP50 unchanged
.899967; AP50:95 .857513→.859300. All14gates evaluated; eight still fail (trailing,
pageTP,pageFP,sheetAP,scrollIndicatorAP,sheetFP,cancelActionFP,mapViewFP). No promotion.

Gallery's176changed paired boxes:172improve/4regress. Median height/truth.782→1.016
on that paired cohort.118improvements come from new refinements,54from returning to
the base box. Retained ambiguous donors increase7→64 and replacements213→170:
the safety fallback contributes materially. Onboarding49refinements improve while
8fallbacks regress. KitchenSink fit has46small regressions/32improvements, median
IoU.9471→.9447. These paired diagnostics are not an AP decomposition; no causal
data-only claim is made with unequal compute.

Serial latency after CPU scoring: same16label-free balanced8/8sample. Warm proposal
median104.66ms total,+56.06ms; no-proposal46.68ms. First pipeline frame1.131s,
model load separately62ms. Small MPS diagnostic, not a speedup claim, population
estimate or CoreML/device qualification. No capture time or external peer wait.

## Verification, preservation and decision

Software:29focused tests and142offline Swift tests pass; build/test logs
.build/roi196-{build,test}.log. Actual prepare/train/infer/report, comparison,
fallback, admission and mechanism entrypoints ran. One fallback-only shell invocation
omitted PYTHONPATH and failed before execution; corrected invocation completed in
fallback-attempt02.log without rerunning scoring or training. Original failure kept.
Swift sources are unchanged; reuse the integrated offline check. Final diff check passes.

Outcome separation: software verified;1173training crops eligible; local two-pass
integration verified on2712originals; model gates failed. No physical/TTR/CoreML
qualification, API changes, transfers or Git writes. SMB not applicable: this local
iOS result does not change the peer's next action.

Checkpoint SHA256 de3ffdeec3c4767edc2d4bea0059294a26d87b6c9fc03b9d684de769ed3dd638.
Evaluation seal d7a795fa869d115ed6188a10041bad563069f86cbef08a8bff0161bab7832c6d.
Comparison seal1a50d57c00cc7368d84ce20ef416125a20e733eff3440f9b6440586fbc3c4aae.
Latency seal f020582c46c5c2789438a5b8cfc54b50b871d70f0fd1f975138f35106d7b0a43.
The separate admission.json reconciles inherited193prefix-only prose with exact
expanded membership; frozen launch files were not rewritten. Raw evidence remains
ignored: approximately28MiBreports and78MiBcandidate outputs, below2GiBcap.
Only this concise handoff is offered from reports/work/IOS-ROI-196 for Git review.

Next substantial tranche:197proposal-support/negative-region qualification and one
frozen comparison contract; independently complete TRAIN-EFF-A's audit/tooling,
including the recorded final-only-validation hypothesis. Do not start another
training sweep or treat a low confidence threshold as a sufficient recall fix.
