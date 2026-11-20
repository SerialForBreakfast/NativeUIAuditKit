---
name: model-improvement-loop
description: Governing checklist for any NUIAK work that plans, admits, trains, scores or decides on a detector or focus model. Read it before experiment-task-authoring, backlog-grooming and nativeui-model-workflow. It keeps work on the fixed benchmark and the 3 active hypotheses, and it lists the drift signs that require a stop.
---

# Model improvement loop (TRAIN666)

Source: [TRAIN666](../Plans/Train666.md), approved by Joe on 2026-11-16. It restores [RESET604](../Plans/Reset604.md) and adds enforcement.
This skill has priority over older queue-filling guidance in the other skills. It grants no execution authority.

## Why this exists

From 9 to 16 November 2026 the models did not improve. The evidence:
- The benchmark had 0 of 150 screens labelled. Each experiment built its own panel, so no result could be compared or accepted.
- Fits used 60 to 300 images with augmentation off. Seed differences were larger than the effects.
- The 1 run with enough data (D1: 378 of 438 real-app controls after 1 epoch, against 103 for the shipped model) stayed paused for 6 days.
- 138 work folders and more than 60 experiment IDs ran in 7 days. The runner was 3.4 % used.

The goal is a better model on real screens. Evidence quality for 1 experiment is not the goal.

## The loop

1. **Choose a hypothesis.** `Tasks.md` has 1 "Active hypotheses" table with at most 3 rows. Work only on those rows. To add a row, close a row.
2. **Predict.** Write the expected scoreboard change in the hypothesis row and in the training specification before admission.
3. **Train at scale.** Use the full eligible membership and 2 seeds. Start from pretrained weights, not from a shipped checkpoint. Train 1 model on the union of the data.
4. **Score on the benchmark.** Use `scripts/tvbench.py` on the frozen TVBench manifests. Report 3 numbers per app and as an equal-app mean:
   - class-agnostic localization recall and precision;
   - role accuracy on localized targets;
   - focus top-1, and false selections on `known_no_focus` screens.
5. **Decide.** Accept a paired gain beyond the measured noise floor. List lost cases. Lost cases are not a veto.
6. **Record.** Put the row in `Research/Scoreboard.md` and 1 short report per hypothesis. Joe approves metrics and promotion separately.

## Hard rules

- **Benchmark only.** A custom panel is a debug aid. It cannot open, close or change a hypothesis.
- **30 independent screens.** Make no decision from fewer. Frames of 1 screen (scroll, focus and repeat states) count once.
- **No zero-loss veto.** Do not write a gate that needs "0 lost previous successes". Small panels fail that gate by chance.
- **No small fits.** Do not admit a detector fit on fewer than 1,000 training rows, unless Joe approves that exact fit as a diagnostic.
- **No fine-tune from a shipped checkpoint** to repair 1 failure family. Such fits forget the other domain.
- **Detector before focus.** Focus selection is limited by missing boxes (30 / 30 with supplied boxes, 14 / 30 with detector boxes). Do not train FocusRing crop variants.
- **A label-policy change does not pause training.** It creates a new benchmark label version and a re-score of the baselines. Legacy-label runs continue as labelled baselines.
- **Real data belongs in training.** Split by whole app. No app is on both sides. Record Joe's approval for each app that changes role.
- **Paused tracks stay paused.** iOS, HCF and FocusRing crop variants get no admissions until the tvOS detector has an accepted scoreboard row.
- **Keep the runner busy with real fits.** Do not fill the queue with short diagnostics. If no fit is ready, report the blocker.
- **TTR annotations are the trusted training source.** Qualify each recipe family or SDK app once with a Q-packet. Then admit its frames by the importer checks and a 1 % audit. Do not write per-frame reconciliation reports for an admitted family. Human review time is for the benchmark only.
- **Synthetic accuracy is never a decision.** Reliable labels do not prove transfer. Measure every data change on the real-app benchmark.
- **Draft labels are not references.** SDK, accessibility and model drafts need review. Missing focus is `unknown`, never "no focus".

## Stop and report when you see a drift sign

- A fourth hypothesis, or a new experiment ID that belongs to no row of the table.
- A decision table that does not come from `scripts/tvbench.py`.
- A result that appears at 1 seed only, or counts repeated frames of 1 screen as separate wins.
- A training set smaller than the previous one, or a new filter that removes most of the data.
- A new gate, contract or review step that blocks the only full-scale run.
- More than 1 day without a running fit while a hypothesis is open.
- A nightly review longer than 1 page, or one without a scoreboard change, runner use and blockers.

When 1 sign appears: stop the new work, state the sign in chat, and ask Joe to choose between the table and the new work.

## Checklist before admitting a training job

1. The job belongs to 1 row of the "Active hypotheses" table.
2. The specification states the expected scoreboard change and the decision rule.
3. The membership has at least 1,000 training rows, passes `detector_training419.prepare`, and has 0 overlap with sealed benchmark apps.
4. The run is logged in `Research/ExperimentLog.md` before it starts.
5. The job compiles through `scripts/hcf_templates395.py` (T107 for detectors). The limit is 43,200 s.
6. If the counted output is above 2 GiB because of linked images, use an EXTENSION408 restart (`scripts/research_extensions.py save`) with Joe's approval.

## Checklist before reporting a result

1. Both seeds are complete, with final checkpoint digests.
2. The scores come from the benchmark, with the count of independent screens and the interval by app.
3. The report states the predicted change beside the measured change.
4. The report lists lost cases, unsupported classes, and what the result does not show.
5. All results stay provisional until Joe approves them in chat.

## Tools

- Membership: `scripts/d1_membership666.py`, `scripts/ttr_detector_ingest604.py`, `scripts/framework_projection604.py`.
- Fits: `scripts/train666_queue_plan.py`, `scripts/train_detector604.py`, `scripts/research_extensions.py`.
- Benchmark drafts: `NativeOSFocusTests.testRoutedSnapshot`, `scripts/ax_capture666.sh`, `scripts/ax_snapshot_drafts666.py`. Follow [tvos-safe-navigation](../../.agents/skills/tvos-safe-navigation/SKILL.md): Select only on a row with a chevron, never Home.
- Scoring: `scripts/tvbench.py`. Scoreboard: `Research/Scoreboard.md`.
