# IOS190 and native24 reconciliation — completed diagnostic, blocked native comparison

Base33bfddd; initial tree clean. No production API/model changes, capture, training,
inference, Git writes or external-repository edits. Both selected lanes accounted.

| Outcome | Evidence |
|---|---|
| Software verified |7focused tests; actual cached derivation/scoring CLI; offline build and142Swift tests pass.|
| Data eligible |Existing roles unchanged; no native24 semantic admission or new labels.|
| Integration qualified |Local two-export derivation/scoring passed; nativeTable-v3 producer integration blocked on exact source.|
| Model gate passed |No:8/14development gates fail; no replacement or promotion.|

## Fixed cached geometry experiment

216training-fit,96development,2400retained records. Original022@640detections retain
count/order/classes/confidences. Only page coordinates use024@1280proposals with
confidence≥.25and IoU≥.25, mutual degree-one. All original page proposals participate,
including low confidence; no truth or confidence-based tie-breaking in association.
Every source export validated with original model/settings/hash bindings; derived
results independently reproduced after writing. Non-page metrics exactly unchanged.

| Measure |022reference|Derived190|
|---|---:|---:|
| Fit leading/center/trailing, each /72|68/72/45|68/71/52|
| Page development TP/FP,96truth|58/14|58/14|
| Page development AP50|.619261|.653204|
| Retained page TP/FP,600truth|249/24|245/28|
| Retained page AP50|.858402|.843625|
| Retained all-supported-class AP50|.899967|.899578|

Seven of31prior fit misses recover; one old hit regresses.15fit/23development/
60retained proposals matched.514/98/113page proposals respectively remain ambiguous;
383/12/682have no eligible match. Eight original gates fail, including trailing,
development TP/FP and existing retained-class failures. Reject this fixed rule;
no threshold search or automatic next fit. Requires two inference paths; cached
scoring time does not represent deployment latency or CoreML parity.

Final `attempt02/artifacts/evaluation.json` seal:
`68870d27c04c6e4a0833b498f579e97099022f8225a55b5a4a54596e102debc5`.
15.861seconds,18,019,918bytes. Original `artifacts/` result preserved: code review
found successful empty-vs-nonempty exports should not require equal status. Added
regression test and reran in isolated output; actual numerical results unchanged.
Total both output trees ~36MB, below128MiB; no recapture/full-corpus decoding loop.

## Native24 lane and TTR follow-up

Exact source still unavailable. Read-only local TTR HEAD46dce7b3a79e4f17af49bc0324d4aeba3cc0958d;
FixtureRecipe.swiftSHA2566b7eaa81084f27440a2af1ef9b418e8df147a87fadad96d92d9b6e55d7b8ed77
matches previous rejected intake. `git cat-file -t` for b98402df,4f9273cc,4b9b57e
fails128. Dirty unrelated producer files preserved. No unchanged validator rerun:
the exact failed boundary/source is unchanged. Existing337verified payloads and
48PNGs/24intervals remain preserved, with8content_only/8boundary_unchanged/8focus_moved.

Resume requires maintainer publication/synchronization of exact v3recipe, hashing,
callback and viewport implementation. Then targeted legacy/negative consumer tests,
native label/crop audit, followed by fixed DTM050/051/052comparison using calibration/
development roles. No speculative version whitelist, recapture or binary request.

Verified SMB endpoint, safely parsed version1YAML with duplicate-key rejection,
minimally patched owned `nuiak/status.yaml` RESIDUAL-160entry at23:06:15Z, and read
back. All unrelated content semantically unchanged (SHA256
`481d78d93e64a3e175b034ac7a55c63a7fb23d086e2d870af4aa92ae4ad946ff`). Existing request
ID preserved. Added188source-sensitive findings and explicit24-case comparison
scope; no iOS metrics in shared status. Peer acknowledgment of this update unknown.
TTR top-level19:00Zstatus expired; not evidence of current runtime readiness.

## Verification and next tranche

`PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python -m unittest discover -s scripts -p test_refine190.py`
passes7tests. `scripts/refine190.py` real entrypoint exits0. Tests cover immutable
geometry-only results, ambiguity/duplicate proposals, exact threshold boundaries,
missing/empty donors, identity/membership mismatches, tampered derivations/version,
failed inference and output collision. Existing strict export validation retained.

Offline `swift build --disable-sandbox --disable-automatic-resolution --skip-update`
passes. Restricted Swift tests failed with15Vision/OCR issues; preserved
`.build/refine190-test.log`. Approved host-access `swift test --skip-build
--disable-automatic-resolution --skip-update --no-parallel` exits0:14XCTest plus
128Swift Testing tests. No assertions changed, service resets or installations.
Logs `.build/refine190-{build,test-host}.log`. Build reports1.84s; host suite test
durations sum~4.9s, excluding process startup. Native capture and peer wait time0.

Next substantial tranche: first complete native24 compatibility/scoring when source
arrives, alongside an iOS small-control representation/label-resolution feasibility
audit using existing training sources. Freeze one justified candidate proposal with
same retained gates before training; do not continue failed matching/loss/scale
sweeps. Current190scope is complete for review; native comparison concretely blocked.
