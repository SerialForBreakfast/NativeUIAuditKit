# ADR-0021 — Evidence-driven focus qualification

Accepted October 6, 2026 for measurement and shadow evaluation, not navigation authority.

## Decision

Extend existing focus and transition reports, not a new inference/training pipeline.
Separate procedural, native Fixture, real-app Simulator and physical capture evidence;
unknown domain remains unknown. Separate visual focus, focus transition and temporal
settling. Pixel change is an observation, not an oracle for those semantic tasks.
Keep existing synthetic retention and physical/model gates; add deployment-domain
evidence without treating native Fixture pixels as real-app generalization.

Report error/support, coverage, abstentions and error among emitted negative/stable
decisions separately. Unknown labels cannot contribute to accuracy denominators.
One-sided exact 95% binomial limits require independently justified trials; related
frames, reverse pairs and repeated scores cannot inflate support. Group bootstrap
comparisons are descriptive and cannot certify rare-event safety with zero errors.
Illustrative 1%/5% targets are not adopted deployment thresholds. Previously exposed
development examples do not become untouched final evaluation.

## Research basis and limits

- [YOLO11 synthetic-to-real](https://arxiv.org/html/2509.15045v1): single-object
  study supports real-domain evaluation, not a universal synthetic-data conclusion.
- [Label errors](https://arxiv.org/html/2609.21822v1): unmatched confidence is a
  useful review baseline; results vary by detector/error convention. Never auto-label.
- [WUICC](https://arxiv.org/html/2607.01728v1): asymmetric VLM errors and nuisance
  pixel alarms support task-specific measurements, not absolute pixel supremacy.
- [Release-side audit](https://arxiv.org/html/2605.20956v2) and
  [anytime risk control](https://arxiv.org/html/2602.04364v1): assumptions and
  calibration roles matter; neither automatically covers domain shift or clustered data.
- [GUI-G2](https://arxiv.org/html/2507.15846v3) concerns spatial grounding rewards,
  not D-pad graph-distance rewards. RL, 10x rollout speed and label-free native truth
  are not established for this project.
- CoSA, Kalman tracking and SubspaceAD remain hypotheses, not qualified tvOS models.
  Unverified citations in supplied research remain watchlist material, not requirements.

## Consequences

Use cached predictions, original labels and connected ancestry; target missing native
evidence before more artwork. Do not change production cropping after CROP222's
unqualified but unfavorable union diagnostic. Reuse BD18/22/25/14/27 assignments.
No new architecture, threshold, model promotion or public Swift API in this tranche.
See [implementation contract](Plans/EvidenceDrivenFocusQualification.md).
