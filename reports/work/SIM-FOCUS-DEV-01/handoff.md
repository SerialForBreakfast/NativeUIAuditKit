# SIM-FOCUS-DEV-01 — local capture proven; training decision pending

2026-09-27 local / 2026-09-28 UTC. Base revision
`be85889adb30fb931de9671d22250a8397f983a3`; existing dirty work preserved.

| Outcome | Result / evidence |
|---|---|
| Software verified | Pass for reused capture/intake/crop mechanisms;29 focused regressions pass. No implementation code changed. |
| Data eligible | Pass for12 reviewed development pairs only; training/independent qualification not admitted. |
| Integration qualified | Local exact-Simulator → native-v2 export → production-crop intake passed on three real jobs. Remote pairing/switching not qualified. |
| Model gate passed | Not run. No inference, training, export or promotion; shipped weights unchanged. |

## Actual execution and acceptance

User authorized exclusive Simulator use. Matched running TTR helper and exact
tvOS26.5 target9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, bound loopback8080 to the
Fixture process in that target. App executable SHA256
`af824888d0c667bbf0157592302424a5639b7c034fb4251bfab6458a9a37d2d7`;
Fixture executable SHA256
`c1b5f5ee2cb5b0e011925bd71b2ca33b9c5845110def2b6bccfaf9f6ebe07d98`.
These are executable identities, not a recursive hash of all loaded debug libraries.
Source remains reported/not-attested. [Preparation](preparation.md) retains context.

| Bundle | Frozen appearance/layout | Completed job | Accepted/rejected |
|---|---|---|---|
| smoke | artwork/standard | C72FBD94-96B0-46BA-B170-8950143EF86C | 4/0 |
| bright | bright_unfocused/standard | F3CC5DEA-DB0B-4FC7-B6E8-FF54DAF32E9B | 4/0 |
| dock | photos_like/dock | C79107C9-036A-4A07-81DA-AE211C450882 | 4/0 |

All recipes: grid_matrix,4 elements,dark,regular,seed20260927,step0; explicitly
producer calibration. Consumer preserves mapped original validation label but assigns
development purpose/split; no untouched validation claim. All three are related.

For each: `fixture prepare --recipe-json … --split calibration` → one
`run-job --simulator-udid … --fixture-url http://127.0.0.1:8080` → terminal
`job-status` → shipped caller-side `export-fixture-job.rb` → existing
`ttr_focus_manifest.py --test-only` → visual review → hash-bound reviewed import.
Every command completed exit0. No replay, app restart, physical fallback, model,
audio or producer edit. Chunk export avoided direct app-container access.

Originals under `dataset/tvos_captures/sim-focus-dev-01-{smoke,bright,dock}`;
QA and final reviewed crops under
`dataset/focus_ring/sim-focus-dev-01-{smoke,bright,dock}-{qa,reviewed}`.
All bulky data is gitignored. Job/export JSON, recipes, stderr, crop runtime identities,
receipts and `accounting.json` are retained in this report directory.
54 files/146,852,369 bytes verified against producer sizes/hashes.24 frame files
contain15 distinct decoded frames: each recipe reuses one baseline four times.
24 crop samples have24 distinct decoded pixels; reviewed outputs regenerate the
same samples rather than adding support.12 accepted,0 rejected,0 blocked pairs
for development QA. No training-admitted examples.

[Visual review](visual-review.md) covers all24 production16%-expanded256×256 crops
and representative full-frame context. Exact source IDs, native brackets and
per-state boxes survive intake. Standard-grid lower-row geometry shifts in focus;
the existing adapter correctly crops each state separately. Baseline Reference
frame is focused outside corpus controls: paired classification is not complete
whole-screen focus selection. Artwork is procedural, not custom-photo coverage.
Top Shelf/sample-app capture, arbitrary focus-color control and physical transfer
are untested. No protected challenge data accessed.

## Verification and remaining decisions

`PYTHONPATH=scripts … python -B -m unittest test_ttr_appearance test_ttr_sidecar_v2
test_harvest_bundle_validation`:29 tests pass (`intake-regressions.log`).
Actual strict import and reviewed import pass for each real bundle, not just fixtures.
No source code changed, so no new full Swift build/test required for this docs/data
tranche. Existing production crop executable identity is recorded in each manifest.
Final coordinator status: no command/observation active,queue0,disconnected,
experimental NUIAK still disabled (`final-postflight.json`). All owned jobs terminal;
Simulator and Fixture left running, no unrelated resources released. No background
training/capture remains. Available disk remains~41GiB.

Helper diagnostics consistently report persistenceFailed24 for their diagnostic
file sink while structured IPC/capture succeeds. Logs retained; logging health is
degraded, not silently repaired or conflated with failed captures.

**Recommendation:** approve a separately scoped Simulator-only development
experiment, preserving full candidate221+9 coverage gates. These12 related pairs
prove the pipeline, not sufficient train/validation independence. Before a run:
freeze expanded training recipe groups and separate development validation/retention
membership, qualify admission/selection with existing trainer preflight, pin full
model/runtime identities, record bounded configuration/approval and only then launch.
Never split sibling frames or treat recolors as independent sources. Original
Photos/source-independent candidate remains blocked; no run ID allocated.

**Remaining scope blockers:** a narrower experiment decision is still unanswered;
no training/admission contract is silently invented to bypass original gates.
Remote mode requires the actual packaged paired client, exact artifact/session
schema and representative receipt. Local success does not qualify remote access.
Explicit profile switching contract is in
[the research plan](../../../Research/Plans/LocalSimulatorFocusDevelopment.md);
no mid-job automatic fallback. Resume with the experiment decision and freeze its
data/selection contract; remote implementation resumes on its exact producer schema.

Capture/QA is review-ready; broader training and seamless remote switching are
incomplete for those explicit dependencies. Existing output directories are immutable;
reuse receipts, do not recapture to repair a downstream report. Coordination is
recorded separately in [coordination.md](coordination.md).
