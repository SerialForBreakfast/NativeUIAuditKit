# Accepted full-backlog delivery decisions

**FocusRing priority amendment, 2026-09-20:** usable TTR focus detection is the highest
new-dispatch priority. [FR-SIM contracts](Plans/FocusRingSimulator.md) extend the
simulator dataset foundation through a shipped-model baseline before scale-up, one
separately authorized candidate, and TTR comparison. Preserve existing workers and
physical gates. SIM-DATA-05 remains secondary/nonblocking. This supersedes the earlier
dataset-only scope for the overall lane, not for the five SIM-DATA packets themselves.

**Simulator addendum accepted 2026-09-20:** [SIM-DATA-01–05](Plans/SimulatorDatasets.md)
creates an independent local NUIAK-Mac lane ending at validated simulator datasets.
Pin initial producer source to `c6ec816bd94e9526f890e4894ad6a71f9e840e58`;
record actual runtime builds separately. Inventory and offline consumer extensions
are independently dispatchable; installation/storage/capture require explicit authority.
No training, remote execution, Sillycon mutation or renewed Office permission follows.
Defer navigation-defect and VoiceOver datasets. Visual-only simulator examples need
no semantic alignment matrix, but do not close physical FocusRing gates, replace iOS
data, satisfy DS-G8, or establish physical-device performance.

**Accepted by the maintainer:** 2026-09-19, Full Backlog Delivery Plan. This records planning decisions, not completed implementation or changed shipped artifacts. Runtime taxonomy, schemas, and model resources remain unchanged until their assigned implementation passes review.

1. **Independent acceptance:** software, data eligibility, integration qualification, and model quality are separate outcomes. Reviewed interfaces unblock consumers before full upstream delivery. Tasks.md is the sole state/ownership queue.
2. **Recovery fallback:** preserve originals and evidence; attempt bounded read-only recovery. If historical identity cannot be established, use a versioned replacement corpus, paired new annotations, and a new Run 009 baseline. Never call new pixels a reproduction of historical 0.586.
3. **41-class first:** retain category IDs 0–40 and the original taxonomy for the current milestone. Full-frame gates are fixture mAP50 ≥0.94, mAP50:95 ≥0.78; toggle and stepperControl AP50 ≥0.88; synthetic withheld-template DS-G8 mAP50 ≥0.85. Report both holdouts independently. The nonexistent badge requirement is removed from this milestone and assigned below.
4. **Badge next:** define a notification/status dot or count marker as `badge`, excluding ordinary buttons/decorative text. Future category ID 41 is appended without reordering 0–40. Version taxonomy/library additively and the dataset according to its taxonomy-change policy. Decoding selects each model's declared category map. Badge AP50 ≥0.88 on supported holdouts is a later 42-class gate. Enclosing container boxes remain annotated. No current schema/enum/model changes are made by this record.
5. **Priority:** immediate assignments are H1, P1-A, P0-A, P4-A, P5-A; selector and consumer contract work remain independent options. Hardware windows prioritize one genuine compatibility batch, FocusRing, real tvOS holdout scale, then larger fixture batches. FocusRing is the first later model priority; macOS implementation follows DS-G8; crop/unified experiments have lower priority. Badge specification may proceed independently but its candidate follows the 41-class milestone.
6. **Crop metric:** `crop_relative_gain = (candidate_crop_mAP50 - baseline_crop_mAP50) / baseline_crop_mAP50`; require ≥0.15 and full-frame loss ≤0.01 in normalized mAP. A zero baseline makes the relative gate undefined, not automatically passed; return for a documented gate amendment. Crop-area fraction is 0.6–1.0; full-frame remains default.
7. **FocusRing:** at least 6,000 labeled pairs with established scene/theme quotas; ≥100 held-out hard negatives across light/highContrast × imageView/collectionItem, with every combination nonempty and reported separately. All six quality gates and export checks apply. Preserve crop contract and optional-model fallback. Version labels must be reconciled with packaged metadata, not guessed.
8. **Consumers:** ScreenAuditKit retains optional uiElements, confidence default 0.75, no-op default, explicit recognition failures, and none/coreml CLI semantics. TVTestRig owns identity lifecycle and producer wire changes. External work requires its own repository assignment; this document does not authorize edits or send requests there.
9. **Release:** a qualified 41-class release need not wait for later FocusRing/badge/macOS/crop/unified work. Maintainer owns tagging and history rewriting. No automatic retraining, promotion, hardware action, recovery mutation, or git write follows from accepting a plan.

These decisions supersede conflicting planning prose only on the named points. Existing production inference, stable API values, filesystem boundaries, and phase gates remain binding. Evidence of implementation belongs in packet handoffs; no experiment entry is created until an actual run is assigned and prepared.
