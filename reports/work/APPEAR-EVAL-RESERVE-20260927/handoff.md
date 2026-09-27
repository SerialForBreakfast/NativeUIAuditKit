# tvOS focus intake-to-decision handoff

2026-09-27 — APPEAR-EVAL-RESERVE; NUIAK architect. Approved local tranche is
review-ready. Independent qualification and candidate launch remain blocked.
No model replacement is recommended; no training or final-challenge scoring occurred.

## Results and independent outcomes

| Outcome | Evidence and limit |
| --- | --- |
| Software | Native surface-v1 consumer and explicit validation adapter implemented; legacy visual comparator unchanged.105 Python tests plus offline Swift build/123 tests pass. No public Swift API/taxonomy change. |
| Data | All4 archive hashes rechecked;96/96 rows accepted for diagnostics,0 rejected,0 missing.96 complete pairs/192 exported frame files,100 distinct byte hashes;48 validation and48 protected challenge pairs. Source independence remains unknown; no independent v2 admission. Genuine Photos/light/high-contrast support unavailable. |
| Integration | Production16%-expanded256 crops and bounded batching exercised. All3,744 validation predictions complete across3 exact models. Real retained221+9-pair assembly succeeds; trainer preflight validates configuration but refuses launch. No device, end-to-end YOLO localization, export parity or physical integration claim. |
| Model gate | Not passed. Unique correct focus: shipped0/48, FDR-0071/48, FDR-0081/48. Candidate misses46/48 despite reduced false positives. No release/promotion or training approval. |

Shipped frame outcomes unique/wrong/none/multiple are0/0/0/48; FDR-0071/22/0/25;
FDR-0081/22/24/1. FDR-008 reduces competitor false positives299→23 against007,
but adds no focus hits or unique-correct decisions. Its94.01% crop accuracy is below
the95.83% always-negative baseline. See [metrics and ranked failures](metrics.md).
CPU CoreML and CPU PyTorch paths differ; latency is not directly comparable.

## Acceptance evidence

| Assigned work | Evidence |
| --- | --- |
| Safe intake and every-row accounting | `extraction.log`; `intake/intake.json` and four group records; original archives and extracted raw exports preserved. Gitignored new dataset destinations. |
| Role reconciliation | Exact source inventories and normalized membership bound to cinema_rows/album_grid validation and memory_mosaic/icon_shelf challenge. Three raw training defaults unchanged. Unresolved lineage quarantined from independent reservation-v2 admission and training. |
| Crops, overlap and support | `crop-audit/crops.json`, `overlap.json`, [pre-inference visual review](visual-review.md).1,344 production crops;3,789 prior images audited,zero exact prior/cross-role pixel overlap. Zero overlap does not prove ancestry. |
| Frozen three-model comparison | `protocol.json`; `comparison/{shipped,fdr007,fdr008}.json` and `comparison/comparison.json`. Fixed0.85, original boxes,1,248 predictions/model;48 complete24-candidate frames. Challenge receives crop/label QA only,zero scores. |
| Immutable candidate and real preflight | `candidate-dataset/focus_dataset_manifest.json`, `candidate-execution.json`, `trainer-preflight-requalified.log`. Existing221 pairs+9 retention, sampling, initialization and selection reference unchanged. Actual assembly exit0, preflight exit2 with configurationValid=true and launchEligible=false. |
| Verification | [Verification receipt](verification.md): positive/adversarial/legacy tests; required offline Swift checks; preserved initial failure logs and repaired runtime-identity integration. `final-verification.json` rechecks all frozen references, recomputes metrics from existing predictions, checks exact assembly preservation and validates YAML without rescoring images. |
| Next assignment and coordination | [Source admission and exact missing data](next-assignment.md); [publication status](coordination.md). Local status YAML updated; no shared publication/readback/peer acknowledgment because SMB is disconnected. |

Frozen evaluation seal:
`d6fd77c74fc5de7bf672e71b252a54173e387ea54f94c5919eb06a3d95a3c460`.
Candidate assembly seal:
`5674102f9d7fa0cd73d03770f53e51c5430e2822d047a443dd50e3b2519cb8da`.

Runtime identity drift initially prevented reconstructing the historical candidate.
All460 production crops replayed pixel-identically. The explicit input-bound runtime
requalification records actual execution identity, preserves historical files and
default strict checks, and reconstructs identical membership/sampling/selection.
This is crop compatibility, not model export parity or independent data qualification.
The model-workflow and worker-execution skills required these separate evidence/gate
outcomes and actual CLI verification; neither grants training or device authority.

## Next action and exact unblock conditions

1. Review the exact producer revision `a101c4fcb7bfdf904cb5da499703cd9a78d1cd8f`
   or a hash-bound renderer/recipe/asset/layout/journey/prior-use relationship record
   for all four retained groups. Local Git object lookup and source inspection cannot
   establish this; that revision is absent and the share is disconnected. Bind
   independently qualified sources and exact membership with reservation-v2 afterward.
2. Obtain actual native-labeled Photos-button coverage from four unrelated unused
   source groups (two validation,two challenge), only after a supported route and
   separate acquisition authority exist. Fixture detail_action is not Photos.
3. Review the single retained FDR-007-init proposal after these data gates are met;
   training requires separate approval. Configuration stays30epochs,batch64,
   lr0.0003,seed42,1,800s,fresh optimizer,50/50 native–Fixture. Retention floor1.0;
   minimum equal-source validation loss among eligible epochs,earliest tie;
   no eligible epoch means no selected checkpoint. Narrowing requires a new decision.

The exact preflight blockers are five required strata across each of validation and
challenge, plus missing_experiment_approval. Unknown independence remains diagnostic,
not silently accepted. No extra transfer, recapture, generic rebuild or cleanup request.
Photos, VoiceOver, sender cleanup and iOS DS-G8 did not block local evaluation;
evaluation did not wait for a new model. Training waits for qualified evaluation and
approval, breaking the circular dependency without weakening its gates.
