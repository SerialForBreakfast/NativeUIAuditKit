# RANK-GEOMETRY109 — extent audit and guarded candidate path

October4,2026. **Software completed for review; real candidate blocked on precise
geometry.** No DTM028 launched, new capture, data-role change, model export,
promotion, deletion or Git writes. Existing DTM020/025 preserved.

## Whole-bank result

Audited all187frames/5022candidates on frozen108training/5Settings development
pairs. Continuous IoU comes from existing endpoint annotations; no runtime labels
or new cropper. For conflicting annotations the report gives all variants and
conservative IoU ranges, not a replacement annotation.

| Group | Frames | Covered at IoU0.5 | Multiple positive proposals | Positive IoU spread>0.1 | Conflicting geometry |
|---|---:|---:|---:|---:|---:|
|Old training|122|122|102|40|0|
|New training|56|56|56|29|11|
|Settings development|9|9|0|0|0|

Thus69training frames have meaningful extent differences hidden by the binary
positive set. Old mean selected IoU: DTM0200.9058,DTM0270.8872,metric1080.8703.
New conservative mean selected IoU:0.1123,0.9395,0.8345 respectively. Settings:
0.5269,0.1921,0.9076. Only one old frame has maximum available IoU below0.75;
it is the known guide-row failure. This supports testing geometry-aware ordering,
not a conclusion that a larger representation is necessary.

## Concrete blocker and source trace

11exact PNG hashes have annotations[208,376,784,976] and[200,385,800,958].
They span33endpoint occurrences in22boundary-unchanged/content-only cases, all
from context60 native sectioned collection captures. Existing binary-positive
proposal sets agree. New continuous supervision cannot silently choose one extent.

Verified each occurrence's image and original`transition-case.json` hashes.
Producer`capture_endpoint.frame_png_sha256` matches the image; focused
`rendered_body_geometry.visible_pixel_bounds` matches the NUIAK annotation in
**both before_scene and after_scene**. All33occurrences therefore trace back to
producer telemetry, not an importer transformation. Internally stable brackets
still disagree across identical pixels. Possible capture reuse, guide-vs-render
variation or other binding defects require producer investigation; not diagnosed
as a particular root cause yet. No metadata or pixels were repaired speculatively.

Detailed trace: `artifacts/source-audit/audit.json`, SHA256
`74ca9798762a293a937aa3f425e52e59654fbab2130e77865198bfb6e91297a6`.
Includes full hashes, occurrences, timestamps, scene generations, raw geometry
source and all candidate/model measurements. An earlier strict diagnostic stopped
at the first conflict; the reporting path was extended to preserve all variants,
while training retains the strict guard.

## Integrated implementation

- `geometry109.py`: whole-bank audit, verified source tracing and candidate protocol
  preparation. No automatic launch approval when geometry is ambiguous.
- Existing `focus_candidate_ranker.py`: opt-in geometry configuration, train-only
  exact-frame target reconciliation, and original positive-set loss plus mean
  best-IoU pairwise hinge. Hinge margin is IoU difference; coefficient1; same770→32→1,
  DTM020 initializer,600epochs,CPU2threads,fixed-last and2GiB cap. No sweep.
- Existing evaluator: geometry candidate uses unique-frame retention gates under
  DTM025, without incorrectly imposing DTM027's frozen-readout condition.
- Original model configurations, training rows, crops, checkpoints and historical
  evidence remain unchanged. A new configuration/source pin requires a fresh
  protocol; old experiment evidence is not silently resealed.

Actual candidate preflight:
`artifacts/preflight/preflight.json`, `launchEligible:false`, first blocker
`geometry_truth_conflict:b54b7f8b695cff6d0c1f57c94346bf4850c28f9b1469766a4e5e18daaab18bed`.
All11conflict IDs included. Protocol recognizes the configuration, but cannot pass
data qualification. No approval file, run ID or real-data output checkpoint exists.

## Verification and commands

27Python tests pass:5new geometry tests plus22metric/representation/retention/
collection regressions. The real trainer runs600epochs on deterministic test-only
fixtures, verifies checkpoint replay and178training-frame membership, excludes
development, and rejects a conflicting target before creating the output directory.
Tests also cover loss ordering, permutation, ties, invalid targets, missing training
membership and conflicts hidden by binary labels. These are software tests, not a
new experiment or evidence of model quality.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/geometry109.py --output reports/work/RANK-GEOMETRY-109/artifacts/source-audit
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/geometry109.py --prepare-from-audit reports/work/RANK-GEOMETRY-109/artifacts/source-audit/audit.json --output reports/work/RANK-GEOMETRY-109/artifacts/preflight
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/train_focus_ring_detector.py --preflight --experiment-arm transition-candidate-ranker --experiment-protocol reports/work/RANK-GEOMETRY-109/artifacts/preflight/protocol.json --name geometry109-candidate
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python -m unittest scripts.test_geometry109 scripts.test_metric108 scripts.test_representation107 scripts.test_retention105 scripts.test_collection104
```

Audit and report preparation exit0; actual training CLI preflight exits2 with the
expected geometry blocker. Test suite exit0,11.02s. Offline Swift build/test exit0:
14XCTest+123SwiftTesting; build1.79s, test build1.61s plus~3s execution. Full audit
including source trace0.47s; no recropping, simulator setup or external waits.
Logs `.build/geometry109-{python-tests-final,real-preflight,swift-build,swift-test}.log`.
Existing artifact destinations are immutable; do not rerun into them. `git diff
--check` passes; bulky evidence remains ignored. Preserved prior dirty changes.

## TTR / independent companion work

Checked mounted status06:48:52Z: private language sample still unpublished awaiting
specific screenshot-egress authority; no assigned artifact available to receive.
No alternative transfer/capture attempted. Existing DTM025 integration remains
independent. Published one actionable geometry request and own packet status with
safe YAML readback and unrelated entries preserved. [Coordination](coordination.md)
records exact destination/hash and timestamp correction. Peer acknowledgment is
pending, not implied by readback. This is a substantial audit/implementation/source
diagnosis tranche, not a helper-only completion; unavailable peer data blocked only
its intake.

## Outcomes and next substantial tranche

- Software verified: passed offline tests, synthetic real-trainer path, real-data
  CLI refusal. Successful actual-data fit/evaluation remains unexecuted.
- Data eligibility: existing roles unchanged; continuous geometry training blocked.
- Integration: source/import agreement verified; new live TTR integration not assessed.
- Model gates: not assessed; no new candidate, deployed artifacts unchanged.

Resume: TTR supplies source-backed, versioned correction or maintainer-reviewed
geometry resolution for all11identities. Review against retained pixels, preserve
originals, explicitly rebind affected evidence/admission and derivative identities,
then register and execute the one frozen600epoch candidate. Complete whole-bank
retention/extent/paired evaluation under DTM025 and return one decision. Do not
omit affected frames or weaken the guard to launch. Independently, TTR can finish
the already-delivered change observer's passive hook and publish an authorized tiny
feedback archive; receive/validate that without treating it as training-approved.
