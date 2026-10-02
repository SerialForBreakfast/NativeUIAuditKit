# Updated local TTR — planner works; retained Vision access still fails

October 1, 2026 PDT. Used the TTR and worker-execution workflows. No implementation
change, capture, training, admission, Git write, app restart or producer build request.

## Local acceptance results

- Running GUI PID24088 identified; its matching bundled helper now advertises
  plan/generate/resume. Identity hash and path retained in [identity](artifacts/identity.json).
  On-disk identity is not loaded-image attestation or exact Git provenance.
- Actual `campaign plan` succeeds for the previously rejected exact structural-48
  example. All48cases validate through NUIAK's existing composition and recipe-hash
  consumer:12each composite_card/hero/home_icon/ranked_row;36custom-focus and12native-image.
  Complete four-family × two artwork × two background × three position membership
  verified, with target plus competitors and common ancestry/calibration preserved.
- Plan SHA`01c633cc1194f0cb8488d5b519c4d1c8d8db5914e712302210e52a0e5862de3d`
  matches the retained producer receipt. Repeated exact request is identical;
  reordered axes produce identical manifest/plan while retaining a different request
  byte hash. Five plan-only invalid cases reject: motion, unknown family, duplicate
  position, training designation and undersized case budget. No generate/resume call.
- Coordinator status succeeds: no active command/observation, NUIAK feature disabled
  by default. No feature toggle changed. Booted local tvOS26.5 Simulator
  `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` reports `can_run=true`; coordinator, companion,
  storage and runner checks pass. Fixture explicitly `not_checked`; this is not
  capture success or proof the installed Fixture matches the latest compiler.

[Plan parity](artifacts/verification.json), [full actual plan](artifacts/plan.stdout),
[coordinator](artifacts/status.stdout), [readiness](artifacts/readiness.stdout).
Example target is a placeholder, intentionally not a live generation request.

## Exact retained Vision retry

Reverified every file against the retained FBACA6BC export receipt, then called the
updated helper on its original synth-0 unfocused/focused PNGs. One attempt, no recapture:

`vision preprocess-pair`: exit1, `persistenceFailed`, stage **before_preflight**,
`access_denied; NSCocoaErrorDomain:513`; request
`D5D22AFB-DCFA-4F88-9835-8FBB9B7201BE`. No sidecar produced, so actual importer
acceptance cannot run. The old generic serviceUnavailable message is now actionable;
same-helper coordinator status passes. This is helper file access, not evidence that
the GUI is closed, OCR is inaccurate, or images need recapture. No permission
weakening, container copies or repeated identical retry attempted.

[Structured failure](artifacts/vision.stdout), [stderr](artifacts/vision.stderr).
Resume after a supported retained-file grant/IPC path is available for this helper.
Ask TTR for source support/instructions, not a rebuild or replacement binary.

## Next dependency and verification

Last producer update02:55:11UTC reports48appearance pairs+16controlled transitions
verified locally, but explicitly advertises no new archive. Consumer pixels and crop
acceptance remain missing. Ask for those **captured data exports**, not another
capture or a build. Keep exact source revision request for reproducibility: configured
local TTR Git HEAD remains46dce7b even though the running helper exposes the new API.
Do not overwrite a checkout or rebuild old source to replace this working app.

Fourteen existing consumer tests pass; results in [log](artifacts/consumer-tests.log).
No implementation changed, so prior93Python/134Swift integrated checks from tranche17
remain unchanged evidence, not new execution claims. Documentation diff checked.

Outcomes: local planner integration passed; capture/generation/export not newly
qualified; retained Vision integration blocked at file access; no new data admitted;
model unchanged. Publication is recorded in [coordination](coordination.md).
