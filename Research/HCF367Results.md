# HCF367 — native capture recovery

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

research-host-NUIAK runs recovery through the existing background queue.
research-host-TTR uses revision `6c85728c605102a9afd38794b08acdd5045b5be4`.

## Verified recovery

- The queued job completes in 71.6 s.
- TTR enables HCF and restores Standard with 12 inputs and 28 observations.
- The remote session closes. The postflight check reports clear ownership.
- Fixture returns to its previous scene and observed focus.
- The job preserves the exact failed guard before removing it.
- Recovery produces no training images and admits no training data.

The receipt is `reports/work/research-queue/jobs/hcf367-recover/attempts/1/out/recovery.json`.
The earlier clipped-row failure remains preserved. This successful recovery does not prove every capture path succeeds.

## Fresh pilots

The runner accepts 3 native capture jobs and 3 matched comparisons.
The pilots cover small dark, large dark, and small light controls.
Each pilot requests 8 frames across Standard and HCF profiles, including repeated captures.
Each job uses the existing 800 s and 100 MB limits.
The jobs retain the original development group and training exclusions.
The comparisons ask whether native profile differences exceed repeated capture noise.

## Software checks

The 32 focused recovery and queue tests pass.
The offline Swift build passes. The sandboxed Swift tests report 15 issues, including denied Core ML access.
The host-context run passes all 173 Swift tests in 53.4 s. Its result remains separate from capture qualification.

## First capture failure and correction

The large-dark pilot fails before capture. Its 320-point control exceeds the 200-point region in the submitted recipe.
Fixture rejects this recipe with HTTP 400. The subsequent Standard check reports ambiguous observations without sending input.
The queue preserves a new guard. The other 2 pilots stop at that guard and produce no images.

The revised preparation expands each region to contain its control without changing the region origin.
It rejects regions outside the screen. Two added tests check these cases.
The revised recovery job preserves the new failed attempt. Corrected capture still requires successful recovery.

Recovery revision 2 stops with `reason: ambiguous`, 2 observations, and 0 attempted inputs. Its session closes.
The exact recipe defect is corrected; the current Settings observation still blocks fresh capture.
The original handoff requests a manual starting screen. [HCF368](HCF368Results.md) supersedes that request with verified TTR navigation and successful recovery.
Do not remove the guard manually. No model improvement or new training corpus is claimed.
