# P1-A handoff — prediction export software

| Outcome | Status | Evidence / reason |
|---|---|---|
| Software verified | PASS | Manifest preflight, serializer, isolated export mode, and six synthetic contract tests pass. |
| Data eligible | FAIL | The real Phase 6a test corpus has dangling image links; no corpus inference ran. |
| Integration qualified | NOT APPLICABLE | This is an NUA-local prediction artifact contract, not external integration. |
| Model gate passed | NOT APPLICABLE | Synthetic tests do not produce metrics or alter DS-G8. |

**Status:** Review-ready. **Packet:** P1-A revision 4. **Parent:** TASK-6a-11.

## Outcome and changed paths

Implemented `prediction-artifact-v1`: a versioned, hash-linked, manifest-driven
per-image prediction export. The isolated evaluator mode requires explicit
manifest, checkpoint, and new output arguments; validates every requested image
and YOLO label before constructing the model; produces explicit `ok`, `empty`,
or `failed` records; and never reuses a prior `save_txt` directory. The normal
evaluation path now shares explicit image-size/NMS/confidence settings with the
exporter.

Changed paths:

- `scripts/eval_phase6a.py`
- `scripts/prediction_artifact.py`
- `scripts/test_prediction_artifact.py`
- `Research/schemas/prediction-artifact-v1.md`
- `Tasks.md`
- `reports/work/P1-A/handoff.md`

Base revision: `96e4b0e83229ab0578b830262dea839930a89264`. Pre-existing
untracked `reports/coordination/Instructions.md` and
`reports/coordination/SharedStatusSkill.md` were preserved and not inspected or
changed by P1-A.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Versioned fields, hashes, settings, result states, and example | PASS | `Research/schemas/prediction-artifact-v1.md`; `P1-A-example-rect-empty` is tested with a real 320×180 non-user PNG. |
| Explicit isolated checkpoint/output mode | PASS | `scripts/eval_phase6a.py --prediction-manifest --prediction-checkpoint --prediction-output`; all three are required together. |
| Validate complete input before inference | PASS | `load_request` resolves symlinks, decodes images, checks labels/IDs, and hashes all members before `YOLO(...)`. Missing/corrupt members fail readiness. |
| Original-image coordinate and output validation | PASS | Serializer rejects invalid IDs/scores/xyxy and records original decoded width/height. |
| No stale reuse or output collision | PASS | Direct result extraction avoids old labels; new output collision is rejected. |
| One record per requested image in complete run | PASS | `build_artifact` rejects missing, duplicate, unexpected, or count-mismatched results. |

## Verification

| Command | Exit | Result |
|---|---:|---|
| `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/test_prediction_artifact.py` | 0 | 6 tests passed: rectangular/empty, failed, invalid detection, corrupt image, duplicate/dangling members, incomplete result/collision. |
| `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/eval_phase6a.py --help` | 0 | CLI parses without inference. |
| Isolated export with nonexistent manifest and explicit Run 009 checkpoint/output | 1 (expected) | Fails readiness before model import: `input manifest does not exist`; no output created. |
| `swift build` with project-local module cache | 0 | Passed (required sandbox escalation because SwiftPM manifest sandbox is unavailable under managed sandbox). |
| `swift test` with project-local module cache | 0 | 14 XCTest and 90 Swift Testing tests passed. |
| `git diff --check`; local Markdown link check | 0 | Passed. |

An initial combined test invocation overlapped the same test cleanup directory
and failed nondeterministically. The test was corrected to use a distinct
in-project temporary directory per test, then rerun alone successfully. No
production or corpus artifact was affected.

Final implementation SHA-256 values:

- `scripts/eval_phase6a.py` — `8bf175a44e33ae77f3d008732979f66a6ab836cb4d40f46e8193acaf967824ec`
- `scripts/prediction_artifact.py` — `f7dba909b92f8757563a011a97b894b2b0e995a871892d485c1c6c5c9075eaeb`
- `scripts/test_prediction_artifact.py` — `c381d6f0339fb06aebe2b1c7d87dbe2bd6c4004bea4c20b6661bade987b4d79e`
- `Research/schemas/prediction-artifact-v1.md` — `f597cf0410bbd8f3568e6c344f2779e40975c8ff32eff2660c74cbbc2f9c5c75`

## Risks and continuation

- P1-B remains blocked on a complete, eligible P0 test corpus. It must invoke
  the explicit export mode with Run 009 checkpoint and a reviewed manifest; it
  must not use historical `phase6a_r009_test_pred` labels as fresh output.
- P2-A can now implement reference comparison against this schema/example;
  comparisons must still enforce equivalent corpus/settings/hash identity.
- The normal `run_val` behavior now uses explicit settings matching the export
  contract. Its actual metric effects are intentionally unmeasured until P1-B.
- Next substantial ready packet: P4-A, offline harvest-bundle consumer
  validation/normalization using H1's source-pinned contract. Do not claim
  trusted capture or training eligibility from its synthetic fixtures.
