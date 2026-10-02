# Visibility-aware intake and source status

October 1, 2026 PDT. Local implementation complete for review. No capture, new data
admission, training, model export/promotion, Git writes or peer repository edits.

## Results

- New review batches seal `visibilityPolicy: native-observed-v1`; old batches without
  it retain their original projection. Existing detector classes and sidecars unchanged.
- Explicit hidden/zero-alpha controls excluded, not labeled as negative examples.
  A focused/invisible contradiction blocks the frame and its paired examples.
  Partial transparency remains reviewable. Optional visibility/scroll fields retained
  on proposals, with missing values left unknown; no claim of occlusion detection.
- Actual intake/crop/review tests prove hidden geometry does not become a crop.
  Unsupported/resealed policies fail. The retained50frame batch validates unchanged,
  SHA256`6717016366f269a291c9ec3728abc80c8c2cafed0df8d4f5b79ec3f8aaed106f`.
  [Legacy replay](artifacts/legacy-review-replay.json).
-84Python tests pass, including structural, semantic, sidecar, body geometry,
  offline pipeline, generation readiness and body assembly callers.
  [Log](artifacts/python-tests-full.log). Offline Swift build and134tests pass
  (14XCTest+120Swift Testing): [build](artifacts/swift-build.log), [tests](artifacts/swift-test.log).

Python command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/tmp" .venv-yolo/bin/python -m unittest test_fixture_batch_review test_fixture_structure test_fixture_rendered_body test_fixture_semantic_inventory test_fixture_composition test_ttr_sidecar_v2 test_focus_generation_readiness test_fixture_offline_pipeline test_focus_native_body_assembly -q`

Swift commands use `--disable-automatic-resolution` and project-local cache/config/
security/module/TMPDIR paths. `git diff --check` passes. No dependency installation.

## Source and TTR status — exact unresolved dependency

TTR01:12:19UTC acknowledges no producer build request: Git source and local consumer
builds are the agreed workflow. Producer reports Simulator recovery passed, first
composite-card case rejected at validation (`commandRejected`), zero accepted pairs
and three unattempted. No retry issued by NUIAK; producer owns diagnosis.

The configured local checkout is `/Users/josephmccraw/Documents/GitHub/TVTestRig`.
Read-only inspection found master/HEAD/origin-master46dce7b and fetched
origin/simulator-harvest967d585; neither Git tree nor working copy contains
`CorpusCoverageRequest.swift`. One worktree exists, with unrelated dirty changes.
No fetch/checkout/merge was attempted or stale build run. This says nothing about
unfetched remote commits. [Exact source/status evidence](artifacts/source-status.json).

Requested exact branch/commit or intended updated checkout; if unpublished, only a
maintainer commit/push. **No build/binary/package requested.** Once that source is
available, resume local build and read-only planner verification. Actual corpus
qualification additionally needs the first four measured proofs after TTR repair.

## Independent outcomes and handoff

Software: passed. Data admission: not applicable. Live integration: blocked by
source availability and missing producer proofs. Model gate: not assessed; FDR021
unchanged. Annotation need: none now. Existing approved reviews untouched.

Published/read back FOCUS-VISIBILITY-16 in
`/Volumes/SharedStatusFile/nuiak/status.yaml`; request
`nuiak-20261002-visibility16-source-revision`. Duplicate-key/schema and unrelated-entry
preservation checks pass. New request acknowledgment pending; prior no-build directive
is acknowledged. Repository-local work is complete; no background activity promised.
