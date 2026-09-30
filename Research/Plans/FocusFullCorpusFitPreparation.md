# FOCUS-FIT-PREP-02 — full-corpus experiment preparation and crop evidence

## Execution amendment — approved2026-09-30

Maintainer approved implementation and the single bounded run below. FOCUS-FULL-FIT-03
owns FDR020 (`fdr020-full-corpus-fit`). Implement a new sealed protocol/adapter in the
existing trainer; preserve FDR019 and all legacy behavior. Model execution is MPS-only,
cached features only, with no export/promotion. Log before launch; preserve diagnostic
last weights and select best only under unchanged eligibility. Approval does not
authorize a second run if unsuccessful. Whole-tranche completion includes integrated
tests/offline build, actual preflight, execution, prediction replay and status/handoff.

Assigned2026-09-30, owner Codex. Prepare the next experiment after FDR019 and
receive/review the two named TTR artwork archives. No training, inference, capture,
data admission or promotion in this tranche. Preserve all existing sources.

Deliver a source-bound full-corpus loss/schedule proposal, explicit readiness and
acceptance checks, verified archive receipts and production crop evidence where
the delivered contract supports the existing consumer. Reuse reviewed intake and
crop tools. Report producer parity independently of semantic correctness and
model performance. Publish exact receipts and actionable crop findings only.

The experiment proposal must use existing admitted members, keep315development
and18retention separate, account for source/class loss mass and retained duplicate
groups, and measure full training fit instead of assuming30epochs is enough.
Specify one bounded schedule and unchanged release gates, not an automatic search.
Execution and any necessary trainer extension remain a separate assignment.

## Prepared experiment for approval

Use all928 currently admitted training controls:790native/Fixture crops from395
genuine pairs and138human controls (8focused/130unfocused). Keep315development
controls and18retention crops unchanged;64excluded human controls stay excluded.
The four newly received calibration pairs are NOT added to this training proposal.
No new run number is allocated until execution is assigned and logged.

Pin the FDR017 cached576-dimensional features, source protocol, production crop
hashes and current evaluator. Fresh577-parameter linear head, seed42; no encoder
training/inference, augmentation, invented human pairs or new data admission.

Loss is weighted plain BCE over every training member on every update:

- Native/Fixture80%total: retain existing equal-appearance/label weights, giving
 40%focused/40%unfocused total mass. Preserve historical native duplicate weights
 for this proposal rather than silently changing membership or sampling again.
- Human20%total: equal weight to each of eight frames and each label within that
 frame; within a frame/label distribute mass equally across distinct crop pixels,
 then across duplicate IDs. This gives10%focused/10%unfocused total mass.
- Overall50/50 label mass. No paired-margin auxiliary objective and no stochastic
 resampling. Report unweighted metrics as well as weighted loss; weighting never
 makes138human controls into138independent screens.

Proposed single bounded schedule: AdamWlr0.01, weight_decay0.01, full feature-batch928,
maximum1000updates or300model-seconds;600second external process deadline. This is
an explicit extension of the successful tiny-fit stress schedule, NOT an established
full-corpus optimum. Do not sweep automatically if it fails. Every update records
overall and per-source/class training BCE,0.5classification,0.85focused recall/FP,
and confidence separation (.85positive/.15negative), plus finite gradients.
Stop at the cap or five consecutive full-training checks satisfying all examples'
confidence separation and each source's normalized weighted BCE<=.05. These are
diagnostic stop criteria, not altered production qualification thresholds.

Score the unchanged development/retention initially, every25updates and terminally.
These observations must not change optimizer, weights, membership or stop timing.
Among scheduled snapshots, retain the existing minimum-balanced-development-BCE
checkpoint rule with earliest tie, and existing eligibility checks:

- Retention18/18; fixed threshold0.85.
- DevelopmentTP>3 andFP<=9;14complete frames, at least2unique correct,
  zero wrong and zero multiple-focus selections.
- Existing stratum floors: buttons/tabs/otherFP0; artworkTP>=1/FP<=9;
  rowsTP>=2/FP0. Missing support remains unavailable, not a pass.
- No eligible snapshot means no selected checkpoint. Diagnostic last weights remain
  explicitly unselected. Even an eligible development candidate is not production
  qualified: export parity, independent coverage and TTR testing remain separate.

This is one changed optimization recipe, not an experiment isolating the causal
effect of learning rate, loss or balancing. If full training fit remains poor,
inspect residuals/duplicate-label conflicts and optimization before proposing a new
encoder. If fit succeeds but development stays poor, prioritize transfer/representation
and artwork evidence. Do not ask for indiscriminate extra annotation by default.

## Frozen preparation and implementation acceptance

`reports/work/FOCUS-FIT-PREP-02/full-corpus-proposal.json` records exact member IDs,
per-example weights, unchanged selection policy and source references. Proposal seal:
`ef8001be1109177728ecd35ec8fd473bee31a6bf61782c08737070eb84a44537`.
All source crops were revalidated.26same-label exact-pixel training duplicate groups
contain65members and6.47%proposed loss mass; no exact train/development overlap or
conflicting labels observed. Similar sources remain related, not independent.

This JSON is a preparation artifact, not a supported executable trainer protocol or
approval. Next assignment must implement an explicit versioned adapter in the existing
trainer, preserve legacy modes, and test weight normalization, duplicate handling,
source/class accounting, training-only stopping, scheduled checkpoint selection,
stale approval/hash rejection, incomplete/nonfinite predictions and no eligible
checkpoint. Run actual preflight, focused tests and offline Swift build/test before
any separately approved launch. Existing FDR01948crop mode must not be repurposed
by overriding its sealed constants. No training has started in this preparation.
