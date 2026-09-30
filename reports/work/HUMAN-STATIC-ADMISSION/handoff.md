# Static-human experiment — completed runs, no release candidate

| Outcome | Result |
|---|---|
| Software | Passed: explicit static-human lane through the actual trainer;70focused/legacy Python tests and123offline Swift tests |
| Data | Passed for this bounded development experiment:395native/Fixture pairs,138human auxiliary controls,18retention crops,315development controls;64exclusions preserved |
| Integration | Local production-crop/feature/trainer/metric integration passed; no TTR live/model integration claimed |
| Model gate | Failed: neither arm has an eligible epoch or best.pt; shipped model unchanged |

## Answer

The approved real-data mixture **did not improve focus detection**. It lost the
one detected tab and introduced ten additional artwork false positives. Do not
repeat or promote this recipe. It is not evidence that human annotations are wrong,
nor proof that real data cannot help; this tests one frozen representation and mixture.

| Identical315-control development set, final epoch30 | FDR017 baseline | FDR018 human auxiliary |
|---|---:|---:|
| Focused controls found /27 |1|0|
| Misses /27 |26|27|
| False positives /288 |5|15|
| Complete-frame unique correct /14 |1|0|
| Complete-frame no focus /14 |13|14|
| Complete-frame wrong / multiple |0 /0|0 /0|
| Retention correct /18 |9|9|
| Balanced development BCE, lower better |0.488012|0.549087|
| Eligible epochs |0|0|

All false positives are artwork:5/181→15/181. Buttons remain0/3focused,
rows0/7, artwork0/12, other0/2; tabs1/3→0/3. The18incomplete frames remain
unavailable for unique-selection accuracy, not silently counted as correct.
Neither arm meets retention at any epoch (best observed11/18versus9/18).
Both rank the true focused control first without ties on12/14complete frames;
that unchanged diagnostic rank is not a qualified0.85decision. Added false positives
are Home(+8) and Home top shelf(+2); the lost focused hit is an App Store tab.

## What was actually compared

Both arms: exact395 genuine pairs, frozen ImageNet MobileNetV3-small encoder/BN,
fresh577parameter linear head, AdamW0.0003seed42,30epochs,13updates/epoch,
same pair draws and138auxiliary slots per epoch. Baseline auxiliary crops come from
the existing native/Fixture corpus; human auxiliary crops come from one approved
eight-frame session, once/crop/epoch, equal total frame weight.80%pair loss/20%BCE
auxiliary loss. No invented human pairs. Production16%expanded256stretch crops,
ImageNet normalization, fixed0.85threshold and existing absolute eligibility guards.

The whole supplement session and descendants are reserved for training; its17excluded
controls remain excluded. Original annotations/reservations and historical453-member
evaluations are preserved; the additive amendment governs this experiment. All32other
human frames remain development, including the confirmed Photos completeness amendment.
There is no untouched real-world test, and no broad transfer/production claim.

FDR017 PID30063:18:13:22–18:14:34UTC,72.28s including preflight; model execution4.85s.
FDR018 PID30313:18:15:08–18:16:20UTC,72.14s including preflight; model execution4.54s.
Both used actual MPS, PyTorch2.13.0/torchvision0.28.0, completed without timeout;
exit2 signifies failed checkpoint eligibility, not interrupted training. Original
last.pt files and all epoch predictions are retained, diagnostic-only.

## Limitations and next assignment

Matched compute does not mean matched label prior: human auxiliary positive loss mass
is6.68%, whereas baseline slots average about50%. Source and class balance change
together, so a causal “real-data effect” cannot be isolated. Despite the negative-heavy
human mix, artwork false positives increased; merely calling this conservative
calibration would be wrong. Frozen feature suitability and mixture weighting remain
hypotheses, not established root causes. More epochs or extra copies of these screens
are not a justified next action.

**Next useful assignment:** receive TTR's now-published four-pair measured-artwork
proof and verify production crop geometry against the retained wrapper examples.
That directly addresses the outstanding geometry question without more human annotation.
Use that evidence plus this failed mixture to specify the next changed-representation
experiment (for example a bounded last-block fine-tune with controlled class weights),
with a new frozen comparison and explicit approval. Do not launch it automatically.
The remaining60artwork pairs are not qualified or admitted by this experiment.

## Reviewable evidence

- [Execution contract](../../../Research/Plans/FocusHumanStaticExperiment.md)
- [Verification](verification.md) and [coordination](coordination.md)
- `frozen-ready/protocol.json`, `reservation.json`, bound approvals and real preflights
- `17/18-started.json`, `17/18-backend.json`, `17/18-execution.json`, training logs
- `NativeUITrainer/focus_ring_runs/fdr017-static-baseline/` and `fdr018-static-human/`:
  exact feature receipts/cache, initial and30epoch predictions, diagnostic last.pt
- `comparison.json`: metric replay, common-budget comparison, stratum/family deltas,
  frame outcomes/ranks, feature/initialization equality and source preservation

No original data files edited, no challenge pixels scored, no export/promotion, no git
writes. Main implementation is a separate versioned adapter with additive trainer
dispatch; legacy protocols retain their original13-frame default. Final source
verification and comparison readback are recorded in verification.md.
