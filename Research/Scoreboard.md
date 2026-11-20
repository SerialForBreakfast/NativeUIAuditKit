# Scoreboard — tvOS real-app accuracy

Owner: Maximum-mini-NUIAK. Plan: [RESET604](Plans/Reset604.md). This file is the only source for headline accuracy numbers.
A row enters "Accepted" only after Joe approves it in chat (AGENTS.md, 2026-11-04). All other rows are provisional.
Numbers come from the scorer output on the shipping path: Core ML, 640 × 640 letterbox, explicit thresholds.

## Accepted

| Date | Benchmark | Model | Controls found | Focused control found | Scope |
|---|---|---|---|---|---|
| 2026-11-01 | REALAPP554 pilot (spent) | `nativeui-tvos-v3.0` + FocusRing v0.1 | 23 of 207 (AP50 0.206) | 0 of 15 | 9 NewsTV screens (controls); 21 screens, 3 apps (focus) |

## TVBench v1 (not built yet)

| Model | Control recall | Control precision | Focus top-1 | No-focus false selections | Seeds | Status |
|---|---|---|---|---|---|---|
| `nativeui-tvos-v3.0` + FocusRing v0.1 | — | — | — | — | — | not measured |
| R5 (`pills560-platter-r5`) + FocusRing v0.1 | — | — | — | — | — | not measured |

Benchmark state: 0 of 150 screens labeled. Noise floor: not measured. Minimum detectable effect: not set.

## TRAIN666 provisional development baselines

| Frozen development scope | Detector + shipped FocusRing | Localization recall | Localization precision | Correct focus | False selections on explicit no-focus |
|---|---|---:|---:|---:|---:|
| [Kanopy, one recording](../reports/work/TRAIN666/development-rescore/Kanopy-Standard-focus.json) | Standard | 234/476 | 234/1,525 | 1/18 | 2/2 |
| [34 Settings routes and Home](../reports/work/TRAIN666/ax-development-r1/Standard-score.json) | Standard | 203/334 | 203/860 | 0/34 | 0/1 |
| [Same reviewed screens](../reports/work/TRAIN666/ax-development-r1/R5-score.json) | R5 | 207/334 | 207/684 | 0/34 | 0/1 |

Counts pool appearances within each scope. The linked TVBench reports include app-level denominators and equal-app means. Independent layouts and the paired D1 result remain unverified.

## Provisional development evidence (not a benchmark)

R5 on 2 development apps (screens that guided the tuning): pills 168 of 170, focused control 18 of 21, cards 60 of 60. See [PILLS560](Plans/Pills560.md#results-summary).
