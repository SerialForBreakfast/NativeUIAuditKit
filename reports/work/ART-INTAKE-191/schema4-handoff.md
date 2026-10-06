# Schema4 selected-subset intake — October 6, 2026

Implemented an explicit inspection path in the existing `ttr_focus_manifest.py` CLI:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/ttr_focus_manifest.py \
  --review-schema4-subset --bundle <verified-local-subset> --output <new-local-directory>
```

It validates bounded safe recipe references, exact source/image hashes and dimensions,
duplicate-key JSON rejection, capture clocks/aliases, observed native target identity,
target-body generation and visible/full/normalized geometry. Missing or invalid pairs
remain individually reported; partial success exits2. Output collisions fail. It never
emits crop images or a training manifest, and never relabels schema4 as3. Existing
v2/v3 admission behavior remains unchanged. Source canonical-recipe/composition-v5
semantics and pixel-level validation remain unresolved, not implicitly passed.

Actual CLI run `artifacts/schema4-review02/schema4-review.json`:20/20pairs structurally
reviewed,40endpoints,18clipped,38nominal/body differences,28frames with missing other
bodies. Report SHA256 `cd5978143f10b4650b52112e0ff5fba630ab9e949f8b33afb8af2f2bd4fac287`.
All remain training-ineligible. This does not close full schema4 consumer admission.

15focused tests pass (`test_harvest_schema4_review.py`, `test_ttr_sidecar_v2.py`),
including actual CLI output/collision, invalid/missing/symlinked images, corrupted
source binding, geometry checks reached independently of aliases, and retained v2
behavior. Real review completed in approximately2seconds without native capture.

Swift build passes with scoped project-local caches. Initial default cache attempt
failed; corrected paths before retry. Default Swift test engine hits generated xctest
Finder-metadata signing error; native SwiftPM engine verification recorded separately.
No certificate, system service or installed-app mutation.

Native test continuation: session79344, swift-test PID26442, helper26612 remain live.
One-second read-only sample shows existing FrameSimilarityTests waiting inside Vision
`VNControlledCapacityTasksQueue`; evidence `.build/schema4-test-helper-sample.txt`.
Do not report full test success, kill a system service or restart this run on an
observation timeout. Recheck the same session before any new test launch.

Implementation checkpoint published/read back at
`nuiak/responses/nuiak-20261006-art191-schema4-review.json`, SHA256
`cec245dbc1cba17f0b7ffdb6bc271f2af3ac0ebbba185cf72ecc96303e40ee9a`.
Peer acknowledgment remains pending. Focused software and real structural intake pass;
full offline test verification remains pending; training/data/model gates unchanged.

## Runtime crop qualification follow-up

`--review-crops` now materializes inspection derivatives through the existing
FocusRingTool adapter, using each endpoint's measured visible body. Partial reviews
fail before crop generation. Modified metadata/images are rechecked at the boundary;
no alternate cropper, dataset admission or inference path was introduced.

Actual CLI output `artifacts/schema4-crops01`:40valid256×256crops for20pairs. Local
FocusRingClassifier source exactly matches TTR's recorded pin
`e04bee2d2e0090d679dfad03051702203c008e4b30dc3bb8314aee7f1599fcad`;
helper SHA `87f7f831d58e5a72014a8552c6479c213bdcd0927b707283e81462a1c92dacb7`.
Crop manifest SHA `b4615d67c72bc0d54ba015d572f4d419cf98639339ed054546105c854d22cf67`.
Producer derivative pixels were not transferred, so cross-host byte/pixel equality
is **not established**. Source-pin agreement and actual local crop execution are.

All20pairs have nonidentical decoded crops; RGB mean absolute difference spans
10.133–37.776/255(median25.239). Reported full-body width growth spans1.06–1.17.
The catalog-light pair was visually inspected: appearance remains similar after
per-endpoint resize. Growth normalization is a hypothesis for future model comparison,
not proof of failure, a reason to change production preprocessing, or label rejection.
Other crop pixels are machine-checked, not all visually reviewed.

18focused Python tests pass, including actual runtime crop integration and legacy
sidecar behavior. Full Swift attempt was deliberately stopped after repeated live
observations and the preserved Vision wait sample: owned helper26612and parent26442
only, session79344exit143. No daemons or system settings changed. A separate native
Swift run excluding FrameSimilarity passes124tests/16suites in3.091seconds; this is
partial verification, not a full-suite pass. Log `.build/schema4-test-without-vision.log`.
Full FrameSimilarity/Vision qualification remains open; no test process left running.

Superseding result: VISION209isolated the existing test successfully, then ran all132
Swift tests/17suites with explicit `--no-parallel` and no exclusions(exit0,4.100seconds).
Full offline verification is now passed for this tranche. Root cause of the earlier
wait is not proven; see [verification handoff](../VISION-OFFLINE-209/handoff.md).

Companion benchmark readiness check: current worker145/153packagers deliberately pin
108procedural pairs and cannot supply the required512representative examples. Do not
repeat these tensors and call them a representative benchmark. WORKER198-A review is
complete; B packaging still requires the current model/data contract and qualified
512-member selection. Existing pool167/native_adapt152 inputs are the next source to
audit, preserving their development/final membership and portable architecture.

Next substantial work: source-backed composition-v5 semantics and per-frame production
crop parity, plus a separately pinned representative worker bundle. No further artwork
generation needed for the intake boundary. Shipped models are unchanged.
