# NATIVE578 and IOS579 — Native focus and iOS confidence

Owner: Maximum-mini-NUIAK. All computed results remain provisional for Joe's review.

The native lane scores retained production crops. The independent iOS lane tests one training correction.
The detached runner executes both lanes. Standard, shipped models, thresholds, and the optional observer stay unchanged.

## Native focus question

Does the retained native-trained classifier improve observed native focus decisions over FDR-001?

- Use 24 crops from 8 unique screenshots across 3 related construction groups.
- Keep the 12 capture events separate from unique screenshots and independent groups.
- Keep every source role as `review_only`. Keep unknown profiles explicit.
- Compare FDR-001 with the retained FOCUS568 native candidate on identical source pixels and boxes.
- Use production crop expansion of 16% and size 256 × 256.
- Keep crop thresholds at 0.85 and 0.70.
- Select exactly 1 score at or above 0.85. Otherwise, abstain.
- Count verified no-focus abstentions as correct. Count unknown references as unscored.
- Report multiple high scores and crop false positives even when the selector abstains.
- Verify native observations, source hashes, crop hashes, and actual PyTorch input hashes.

Eight T63 jobs produce matched scores. One cached comparison reports recovered cases, lost successes, and new wrong selections.
Each job permits 800 s and 100 MB. These are short diagnostics within 1 investigation.
PyTorch scoring with production crops does not establish TTR execution or full-screen selection.
Unknown profiles prevent HCF qualification. No source receives training admission from this comparison.

If results support the candidate, use the observed failure groups to select a separate training correction.
If results lose a success or add a wrong selection, preserve the baseline and diagnose those cases.
If observations remain insufficient, request only the missing profile or reference evidence.

## iOS confidence question

Does classification preservation at teacher foreground positions reduce retained losses while preserving new row detections?

IOS577 uses the original 16 selected loss IDs. Twelve retain correct-class boxes below production confidence 0.5.
Four still have class or assignment problems. These selected development cases do not establish accuracy or causality.
The 0.01 diagnostic floor remains separate from the unchanged production threshold.

IOS579 changes classification preservation support from all locations to teacher foreground positions.
Select positions where the teacher's maximum class probability is at least 0.25.
Sum classification loss across classes. Average it over selected positions within each eligible training image.
Average those image means. An image without teacher foreground contributes no preservation penalty.
This normalization increases foreground emphasis. It does not preserve the previous effective penalty magnitude.

- Reuse the same 157 training images: 125 original anchors and 32 native row images.
- Reuse Run013 initialization, seed 371, batch 8, and learning rate 0.0001.
- Keep warmup bias rate 0.0001, 30 epochs, and fixed final checkpoint selection.
- Keep geometry preservation, teacher targets, coefficients, and training data unchanged.
- Use the original training anchors only. Keep evaluation labels outside training.
- Compare the candidate with completed IOS573 outputs on the same 7 development sets.
- Run full Run013 and ROW545 retention reports.
- Reject replacement after any lost previous success or new wrong selection.

The existing compiler produces 19 jobs: 1 fit, 7 scores, 2 decisions, 2 retention parts, and 7 conditional diagnoses.
The fit permits 43,200 s and 2 GiB. Expected training takes 20–25 min from recent matched fits.
The guard does not extend 30 epochs. Dependent diagnostics do not establish 19 independent investigations.

If preservation and native gains pass, prepare fresh consumer qualification for Joe's review.
If losses persist, diagnose the exact score, class, and assignment changes. Do not repeat this factor unchanged.
If execution fails, preserve the attempt and repair the exact cause through an immutable successor.

## Remaining boundaries

Native training still needs applicable profile evidence and eligible groups.
Temporal training still needs action-linked observations. Static repeated frames do not prove transitions.
Standard consumer verification still needs an executed-input receipt through TTR.
TTR reports no new reply after the retained acknowledgment. Preserve its reported build and test pause.

The broad isolation test exposes an older dependency through capture validators and SDK authoring helpers.
The new label checker has no authoring imports. The queue-wide isolation defect remains a separate implementation task.
Do not lower that test or remove evidence checks to hide the defect.

Private manifests, exact models, results, and command receipts remain under `reports/work/NATIVE578` and `reports/work/IOS579`.
