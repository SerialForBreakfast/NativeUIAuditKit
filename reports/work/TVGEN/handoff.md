# Parallel acquisition handoff — 2026-09-22 UTC

Assigned scope: [parallel acquisition](../../../Research/Plans/ParallelTVOSAcquisition.md).
Software delivered; genuine pilot and baseline remain blocked, not complete.
No training, scale capture, Office use, producer edits, installs, resets or promotion.
Existing iOS reconstruction artifacts/ownership preserved. Worktree was clean at
entry, NUA HEAD `2031f996c72a4be78397d0f1f295bbc51c2e6b5f`.

## Results and acceptance

| Outcome | Evidence |
|---|---|
| Software verified | 10 direct tests, 14 consumer tests, 14 launch tests pass; Swift build and 92 Swift tests pass. |
| Data eligible | Blocked: one valid reference PNG, zero complete pairs. No completed capture receipt or derived genuine manifest. |
| Direct integration | Screenshot/HTTP reference interval works; actual focused target cannot resolve native identity. |
| TTR integration | Independent app-managed job fails native-focus prerequisite; export/intake not reached. Screenshot repair remains unqualified, not newly disproved. |
| Model gate passed | Not assessed. Test-only CoreML round trip is software evidence, not a genuine baseline. |

Implemented `direct_tvos_capture.py`: read-only planning, exact UUID/listener process
binding, immutable catalog, five-second HTTP calls, ten-second settling, two-minute
recipe deadline, before/after native observation validation, hash/dimension/coordinate
checks, new-only outputs and retained failures. No coordinator/companion/export calls.
`direct_focus_manifest.py` supplies development-only v1.4 through existing production
16%/256×256 crops. Existing validation/baseline entrypoints consume it; older v1.2/v1.3
remain supported. `focus_corpus_overlap.py` checks seed/group/decoded-pixel isolation
across qualified manifests without deleting intentional focus pairs.

Tests cover target and endpoint mismatch, conflicting/stale observations, missing/
corrupt pixels, hash changes, incomplete membership, output collisions, versions,
false reviewed provenance, split leakage and crop-pixel mismatch. Actual derived
manifest and baseline CLIs run on explicitly test-only pixels using production crops
and shipped CoreML. Full pilot, focused visual scaling/clipping and genuine baseline
acceptance are unexecuted because native label binding failed. Do not infer them from
offline success. Catalog counts are frozen; live supported-target reconciliation
remains a pilot acceptance requirement.

## Runtime and genuine trials

Target `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, Apple TV 4K (3rd generation),
tvOS26.5, Xcode26.6/17F113. Matching installed Fixture launched once, PID7156,
listener `http://127.0.0.1:8080` bound via lsof/ps to its exact simulator bundle.
Fixture instance `DAD1C2CE-F5F1-401D-8F54-E0A0AAD20771`, run
`B4FCA8AA-3598-4035-9F91-DFA794BFD33B`. Installed executable/dylib match the
corresponding Debug-appletvsimulator build artifacts; neither was installed/rebuilt.

| Artifact | SHA256 |
|---|---|
| Fixture executable | `28cb31b6c0f10a2c9aecec8979d5e3bdc7437f40b7496b83a39f9e9345f243c3` |
| Fixture debug dylib | `d9a7cf770d7deff35c11d004cd761112ff2742817520e4110de3ed01707a0427` |
| TTR executable | `c2dd24b2e2b591c121ff0d41769f5797f1b6b0831f6618fcaddadfef5884428d` |
| TTR debug dylib | `22573dfceb3b7dc4bdc9a9e5019de24dc53c2fa35a7eb06477e1e4e7989121ae` |
| Companion executable | `6f47d797952ee55e767c9ea3b97b09b868ac2efbdb17d403c56e9daabbccf68e` |

TTR checkout `0dfb373ad0341e9f36fa9bf32d92afafa1318750` (Screenshot repair).
On-disk source revision is recorded separately, not proof of the loaded binary's
source. Matching CLI is the running Debug TVTestRig.app's `Contents/MacOS/TVTestRig
--tvtr-stable-cli --json`, not an unrelated aatv.

1. Direct smoke: action_dialog, two elements, high_contrast, regular, seed7, step0.
   `--execute --catalog reports/work/TVGEN/smoke-catalog.json --target
   9026ECA9-77DB-4AE6-8FE6-BB239E9571FA --endpoint http://127.0.0.1:8080
   --output dataset/tvos_captures/direct-smoke-20260922` exited2.
   Preserved raw `started.json`, reference PNG/sidecar and `failed.json` in that
   gitignored directory. PNG3840×2160 SHA
   `6a0fb106e8f1376915e32664c0e897f2cdb4a21aaf25a97d8c12325112536873`.
   Reference before/after observation settled and verified. Visual inspection of
   `.build/debug-output/tvgen/reference-overlay.png` confirms both button boxes and
   dialog container align qualitatively. No focused image exists to inspect.
2. First focused target `dialog_btn_0` timed out: `nativeFocusResolved=false`,
   `reason=unresolved_focus`, `focusedItemKind=non_view`, `resolution=unmapped_item`,
   `missingIDs=[]`. Geometry is present; native identity is absent. Requested focus
   was not substituted. Second target not attempted; no automatic retry.
3. Independent TTR prepare/run-job/job-status reached job
   `5063F0AF-6120-4619-9E87-F56210E1228F`, recipe hash
   `212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
   Terminal request `249D9476-0CFC-4422-AF3F-10292673F7BB` reports failed
   `native_focus_or_geometry_unavailable:sceneNotSettled`, same non-view/unmapped
   diagnostic, generation5, 39 samples, no missing IDs. CLI response success means
   job-status retrieval succeeded, not capture success. No completed files/export.
4. Both postflights: Fixture responsive. TTR readiness ready, ownership clear;
   see `postflight-device.json`, `postflight-scene.json`, `ttr-postflight-readiness.json`.
   No running harvest remains; Fixture left running, no user runtime terminated.

The failed direct output predates offline additions retaining `lastObservation`,
`evidenceKind` and runner hash. It remains unmodified partial evidence; the final
runner revision has not been re-executed against live Fixture after this failure.

## Verification and time accounting

All commands from package root, exit0 unless noted:

```sh
.venv-yolo/bin/python scripts/test_direct_tvos_capture.py
.venv-yolo/bin/python scripts/test_focus_consumer_integration.py
.venv-yolo/bin/python scripts/test_focus_launch.py
swift build
swift test
```

Logs here: `direct-tests.log` (10,0.673s), `consumer-tests.log` (14,0.700s),
`launch-tests.log` (14,1.112s), `swift-build.log` (2.96s, no warnings/errors),
`swift-test.log` (92 tests,2.406s execution). These are reported framework times,
not total shell/setup time. Direct reference screenshot interval was0.3625s;
failed focus settling approximately10s. TTR run/terminal evidence spans06:03–06:04Z;
exact job wall duration is not supplied by terminal response. Intake/capture of
qualified pairs: none. No external wait loop; peer repair is outstanding, not
unrecorded compute. No second full Swift cycle for documentation-only updates.

## Resume and next action

[Pilot gap/next-stage proposal](pilot-gaps.md); [SMB coordination](coordination.md).
Producer-owned fix must bind the non-UIView native focus item independently to the
Fixture element and demonstrate reference plus both focused targets. Current
ProceduralSceneView native probe and FocusSweepController fail closed correctly;
do not use requested focus or box proximity as ground truth. NUA cannot modify
that repository under this assignment. After matching fixed artifact and fresh
target/endpoint reconciliation, use a new smoke destination; then continue the
already frozen direct pilot and genuine baseline if all label/visual checks pass.
No unchanged attempt, model training or scale collection is authorized here.
