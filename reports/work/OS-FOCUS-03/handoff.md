# Independent native focus tranche — 2026-09-22

## Outcome

Delivered new native Settings acquisition, immutable incremental development data,
one trained candidate and before/after challenge evaluation without TTR. Home
implementation is present but its live acquisition is concretely blocked; no Home
labels, navigation coverage or model-driven traversal success is claimed.

| Outcome | Evidence |
| --- | --- |
| Software verified | Actual Settings capture/intake, experimental preparation/preflight/training and challenge CLI passed;63 focus Python tests,19 native intake tests,93 Swift tests; Swift build passed. |
| Data eligible | Apps3 pairs train, Remotes6 pairs challenge; all18 new crops visually reviewed before scoring.40 total train/9 validation/6 challenge pairs, development only. Zero Home pairs. |
| Integration qualified | Native XCTest→xcresult→strict intake→production crops→trainer/report, for exact simulator/runtime and two menus only. No TTR/Fixture qualification. |
| Model gate passed | Not assessed. Small native development evaluation only; no export, promotion, fixture-retention or physical evidence. |

## Evidence and results

[Summary](summary.json) binds protocol, run and both challenge report file hashes.
[Review](review.md) pins Apps/Remotes manifests before scoring; [sources](sources.json)
freeze Root/General/Apps training and Accessibility validation; [challenge](challenge.json)
freezes Remotes separately. Home and related layout lineage stay challenge-only.

FDR-007 warm-starts FDR-006 with fresh AdamW, seed42,8 epochs,batch8,lr0.0003,
no augmentation, production16% expansion/256×256 stretch. MPS training completed
in18.608s process time (7.481s post-preflight), PID80937, exit0. Selected epoch8
using validation BCE0.00000733137, not challenge metrics. Candidate SHA256:
`a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`.

At fixed0.85: validation TP9/FN0/FP0/TN9; challenge TP6/FN0/FP0/TN6.
FDR-006 already achieved the same challenge decisions. Shipped CoreML gives
TP0/FN6/FP1/TN5 on that identical12-crop challenge. Before/after files preserve
probabilities, false positives/misses, fixed0.5/0.85 decisions and cold/warm timings.
No selective-abstention policy was evaluated. Torch CPU vs CoreML CPU is not
export-parity evidence. New training membership and challenge have no exact decoded
source/crop pixel or lineage overlap; these remain correlated same-app/style groups,
not independent applications or final-release holdouts. No causal added-data gain
demonstrated, no further same-style epochs justified.

Initial launcher rejected missing literal `warm-stretch` in the experiment log,
exit2 before any epochs/output. The corrected log-only launch is separately retained
in `fdr007-launch02-execution.json`; it is the sole trained candidate, not a
performance-triggered retry. ExperimentLog was populated before execution.

## Capture and blocked Home branch

Exact target9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, tvOS26.5/23L470,
Apple TV4K3rd generation;1920×1080 viewport,3840×2160 pixels. Existing isolated
NativeOSFocus runner rebuilt/installed under scoped runtime approval. No TTR capture,
Office, simulator restart, settings change or remote host operation.

Apps:4 capture directions+1 setup direction,5 observations/3 unique frames,
3 paired rows,9.742s test body. Remotes:7+2 directions,8 observations/6 unique
frames,6 paired rows,13.484s body. Both selected only a verified root disclosure,
retained pre-Select screenshot, swept Up/Down, then one Menu return. All child rows
were focus-only, including disabled-looking or action rows. In-test root return
passed. Final process inventory finds no owned NativeOSFocus/xcodebuild runner;
post-teardown Settings responsiveness was not separately exercised.

Home trials retained separately:

- `home-01`: PineBoard shell has anonymous full-screen focus; bounded settle fails10.742s.
- `home-02`: source/process-informed HeadBoard observer loses foreground; fails0.978s.
- `passive-01`: observation-only tree exposes repeated AppCell identifiers and app
  labels, transitional geometry, no qualified tile focus; screenshot blank.
- `home-03`: bounded foreground-transition observation still fails10.696s; blank PNG.

Each Home operation sent zero directional inputs; no repeated unchanged attempt,
service reset, synthetic focus claim or partial-corpus publication. Resume requires
stable HeadBoard native tile identity/viewport matching a visible image. This is a
local native acquisition blocker, not evidence of a TTR defect. Home snakes, spirals
and systematic coverage remain incomplete.

## Implementation and checks

Changed NativeOSFocus runner, native intake, experimental protocol v2 and challenge
reporting with explicit incremental-membership exclusion. Existing v1 behavior and
shipped library preprocessing/model resources preserved. Added Home identity/action/
terminal/transition tests and challenge pixel/lineage/corrupt-protocol tests.
Updated canonical plan, queue, roadmap, catalog, experiment log, current state,
BP-71 and raw-capture ignore rules. Existing dirty library, tools, TTR skill and
other workers' changes were not reverted or taken over.

Commands/evidence:

- `xcodebuild build-for-testing` and exact-UUID `test-without-building`: build logs
  here; each trial's `execution.log`/`result.xcresult` retains invocation/outcome.
  Apps/Remotes exit0; failed Home trials are not passing checks.
- `xcrun xcresulttool export attachments`: each trial `export.log`; no recapture
  needed for export permission. Intake CLI invocations/results in `intake.log`.
- `focus_learning_experiment.py --incremental-native`:98 samples, protocol
  `a756f182c633ae6ad4b4985a75200ef738a7974bf8520ce8a3c946d8574d4f8c`.
- Existing trainer `--preflight`: configurationValid/launchEligible true,
  releaseEligible false; exact execute command/PID/exit in launch02 ledger.
- `focus_learning_report.py --native-challenge ... --training-protocol ...`:
  after report exit0; before report exit0 against previous protocol. The added
  training protocol exclusion passes before after-report publication.
- Python discovery `test_focus*.py` and `test_native_os_focus_dataset.py`:
  final logs, exits0.63 tests2.3s approximately;19 tests<0.1s.
- Offline `swift build --disable-sandbox`: exit0,3.44s, no warnings. First restricted
  `swift test` failed CoreML system-cache permissions; retained log. Scoped host
  rerun exit0,93 tests2.518s. No source workaround or permission weakening.
- `git diff --check`: passed. No git writes.

Capture test bodies23.226s successful+22.416s failed Home; Xcode startup/export,
visual review and intake are additional time and not conflated with capture.
No time spent waiting for TTR in this tranche. Exact model inference timings are
in challenge JSON; training18.608s. Raw data, crops and xcresults remain gitignored.

## Next useful work

1. Offline isolated candidate CoreML trace-export/parity on these frozen samples;
   establish probability/threshold agreement and package size before consumer use.
2. Qualify native Home observation, then capture different focus appearances under
   a separate bounded assignment. Do not rerun Settings solely to increase counts.
3. Admit repaired Fixture data later for different controls/themes and retention
   tests. Full quotas, hard negatives and all model gates remain required.

Local-only tranche: SMB coordination not applicable; no noisy status publication,
no claim that the outstanding TTR repair was solved. No background operation remains.
