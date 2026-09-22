# Approved native Settings recording and replay

Actual execution: 2026-09-22 07:32–07:33 UTC (directory suffix is a preparation
label, not the execution timestamp). User explicitly approved runner installation,
standard simulator runtime storage, Settings activation and six directional inputs.

| Outcome | Result |
|---|---|
| Software verification | Actual XCTest passed, exit 0, 10.407 s; attachment audit and source-bound replay exit 0 |
| Data eligibility | Seven hash-verified observations, four distinct frames; visually reviewed development evidence only |
| Integration qualification | Independent native OS capture/replay works for this bounded Settings scope; not TTR live integration |
| Model gates | Not assessed; development replay exposes focus errors, no training or promotion |

## Target, actions and safety

Exact UUID 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, Apple TV 4K third generation,
tvOS 26.5 runtime, booted and available. No competing XCTest runner found before
execution. The test used test-without-building, parallel testing disabled, one
destination, 120-second test limits, no retries. Source and installed build input
hashes: build-hashes.txt. Full command and test sequence: execution.log / result.xcresult.

Observed focus sequence: General → Profiles and Accounts → Video and Audio →
Screen Saver → Video and Audio → Profiles and Accounts → General. Three Down,
three Up; no Select/Home/Menu, app entry, setting/account change, TTR/Fixture
execution, Office use or training. Runtime runner remains installed; no uninstall
was needed. Settings was left foreground; prior app context was not restored.

All seven PNG/JSON pairs exported plus terminal context. JSON byte hashes match
PNG attachments; all before/after native node lists match and bracket screenshot
time. 3840×2160 PNG versus 1920×1080 point viewport gives measured scale 2.
Repeated return frames have identical hashes; seven observations are not seven
independent training scenes. Four unique full images visually inspected: native
focused labels agree with white focused rows. AX bounds need not include every
focus halo pixel. Temporal bracketing is not atomic framebuffer identity.

Fresh final in-test snapshot passed; terminal reports six inputs and foreground
Settings. Read-only exact-target post-teardown process listing showed Settings PID
22651 and no NativeOSFocus runner entry. Process presence does not prove post-
teardown UI responsiveness; that stronger health claim is not made. No pending
XCTest process/session remains. No service restart or cleanup workaround was used.

Initial attachment export in restricted execution failed on Xcode TestReport cache
access. Approved host-context export succeeded without rerunning capture; standard
report-cache access was explicitly scoped. Raw evidence stays in this repository.

## Model replay

The four visited row candidates were scored on each unique frame: 16 crop cases,
four focused and twelve unfocused. Each uses actual per-frame AX geometry scaled
to pixels. Native focus supplies evaluation truth only; the shipped model supplies
probabilities. No YOLO/OCR proposal quality or model-driven navigation is tested.
All belong to one development journey and must remain in one split.

At fixed probability ≥0.85:

| Path | True positives | False negatives | False positives | True negatives |
|---|---:|---:|---:|---:|
| NUIAK production crop + CPU classifier | 0 | 4 | 4 | 8 |
| Source-bound TTR scorer, `.all` backend | 0 | 4 | 6 | 6 |

Counts are crop classifications, not unique-winner policy or general accuracy.
No TTR failure-to-zero sentinel occurred. Model/source identities are retained in
[replay/report.json](replay/report.json) and the prior FOCUS-PARITY-01 report. Backend
selection differs in this live-data replay, so do not attribute every delta to
cropping. Previous controlled same-CPU comparison remains the crop-isolation test.
Focused NUA probabilities: 0.5923, 0.6079, 0.5327, 0.8193. Inspected representative
focused crops and the high-scoring unfocused Profiles row; genuine distribution
and context weaknesses remain, not merely producer capture failure.

Reproduction: `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python reports/work/OS-FOCUS-01/replay.py`.
The script refuses an existing replay output. Preserve this run; choose a reviewed
new output before any rerun. It audits membership, target, actions, focus count,
temporal order, hashes, dimensions, unique labels, model and peer binary identity.
Production Swift source unchanged; prior final build and 92 package tests remain
applicable. The only new executable content is this run-local audit/replay script,
successfully exercised on the complete recording. No new production helper added.

## Next

Independent acquisition is unblocked for this demonstrated scope, not broad
capture permission. Next useful implementation is OS-FOCUS-03 deterministic Home
coverage, plus OS-FOCUS-02 reviewed native-row pair admission and targeted coverage.
Do not immediately train on four rows: preserve this journey as development evidence,
collect independent layouts/styles/negatives under a bounded assignment, and retain
the existing held-out and model gates. TTR crop-parity and Fixture repair stay separate.
