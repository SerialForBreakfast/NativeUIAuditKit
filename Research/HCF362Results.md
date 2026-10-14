# HCF362 — native capture qualification

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Decision

The updated TTR build works. One native HCF roundtrip passes with verified restoration.
Unattended capture remains blocked by a Settings text-recognition mismatch.
This failure does not show that HCF is untrainable.

## Verified results

| Check | Result | Meaning |
| --- | --- | --- |
| Signed research-host-TTR build | Pass, 76.7 s | Revision `6c85728c605102a9afd38794b08acdd5045b5be4` builds with its bundled helper. |
| Workspace access and target readiness | Pass | The selected tvOS 26.5 Simulator permits the bounded test. |
| Standard → HCF → Standard | Pass | TTR verifies both the requested setting and restoration. |
| Native capture pilot | Stops before input | An unrelated clipped row differs between 2 text observations. |
| Other capture pilots | Guarded failures | The persistent guard prevents further target operations. |
| Office comparison | Complete | Different scenes require separate device evaluation. |
| Focused queue and HCF tests | 100 pass | Queue integration and capture checks pass their automated tests. |
| Office comparison tests | 3 pass | The pixel comparison handles its tested input cases. |
| Integrated Swift tests | 173 pass, 24 suites | The existing Swift tests show no regression. |

The roundtrip uses 18 inputs and 40 observations. It makes no external model calls or image uploads.
The session closes and Fixture returns. The setting returns to Standard.
The installed Fixture binary remains separately identified. Do not assume it matches the newly built host source.

## Capture blocker

Both observations identify Display, Focus Style, and Standard.
The clipped bottom row produces different text: `Ihlhi+ D i` and `Alhita D`.
TTR compares the entire row array and stops safely.
The failed attempt sends 0 remote inputs and captures 0 training frames.
The session closes. The capture guard remains until recovery checks and the controller repair qualify.

TTR should test clipped-row handling without weakening page, focused-row, setting, or restoration checks.
research-host-NUIAK needs a repair revision before creating a new immutable attempt.
Do not retry the unchanged job or copy its uncertain state into training labels.

## Prepared queue

Three capture jobs test small/dark, large/dark, and small/light native image cards.
Each job requests 8 frames across 2 focus targets, 2 OS profiles, and 2 repeats.
Three dependent comparisons measure repeat noise and matched profile differences.
These are development pilots, not a diverse training corpus.
The jobs retain the 800 s and 100 MB limits. TTR receipt storage has a separate 1 GiB limit.
The background runner executes the jobs. This work does not restart or replace the runner.
All 3 capture attempts fail; the 3 dependent comparisons remain blocked.

## Office comparison

The independent job compares Office F121/F122 with retained Fixture button and artwork pairs.
It checks original resolution and a common 1920 × 1080 view.
At the common resolution, changed pixels cover 44.74% of Office, 3.24% of the button pair, and 5.11% of the artwork pair.
Changes above 32 RGB levels cover 1.58%, 2.07%, and 2.54%, respectively.
These values measure pixel changes, not focus accuracy or HCF benefit.
Different scene content prevents a causal device-versus-Simulator comparison.
Office has 1 inspected journey. Exact per-frame HCF receipts and control-body labels remain unavailable.
Keep Office in development. Test device transfer separately after label review.

## Evidence and next batch

- Native qualification: `reports/work/HCF362/qualification-01/qualification.json`.
- Queue specifications: `Research/ResearchSpecs/HCF362/`.
- Failed capture: `reports/work/research-queue/jobs/hcf362-large-dark-capture/attempts/1/out/capture/`.
- Office result: `reports/work/research-queue/jobs/hcf362-office-scale-compare/attempts/1/out/summary.json`.
- Focused tests: `.build/hcf362-focused-tests.log`.
- Swift tests: `.build/hcf362-swift-test.log`.

First, qualify the repaired controller against the saved mismatch and a native roundtrip.
Then submit new capture attempts with fresh pins and verified recovery.
Use visible, repeatable native effects to choose families for the first 1,000-frame training stage.
No model weights, training roles, or production decisions change in this tranche.
