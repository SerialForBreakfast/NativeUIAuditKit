# IOS-ASSET200 campaign and DETECTOR207 benchmark slice

October6,2026 UTC. Completed native development acquisition and one fixed-model
benchmark; no training, production changes, Git writes or physical-device use.

| Outcome | Result |
|---|---|
| Software verified | 146 offline Swift tests,10 campaign tests; native capture and resume pass |
| Data eligible | 96 development-only frames, one shared artwork ancestry; not admitted to training |
| Integration qualified | Native iOS grid/detail artwork, exact simulator below; not tvOS compatibility |
| Model gate passed | Not assessed; benchmark exposes substantial remaining failures |

## Delivered and acceptance

Reused CardDetail rather than creating a new renderer; opt-in hero image/height
leaves its seeded default behavior unchanged. GeneratorArtworkCampaign freezes the
exact target/catalog and96recipes; existing ScreenshotCapture/AnnotationWriter own
native measurements. `testArtworkCampaign` executes48-frame shards, hashes PNGs and
sidecars, resumes completed seals and refuses partial/colliding destinations.

Fixed the plan arithmetic before capture:2layouts×2themes×2densities×4seeds×3conditions
=96. Seeds200–203. Grid4cards/2columns or6/3; detail220-point/short body or300/fullbody.
Conditions procedural, reviewed thumbnail04(lower detail), thumbnail03(busier).
Native controls/geometry identical across each matched triplet. Relative content
contrast also changes colors/composition; it does not isolate clutter causally.
Four newly/previously reviewed assets total; this campaign uses two. [Review](review.md).

All290files accounted:96PNG/sidecar/scene-seal triples and two terminal receipts.
Every hash, native bound, theme, asset binding and content extent passed.96distinct
decoded rasters; no cross-role split because all membership is development.64artwork
frames differ from matched procedural pixels only within native image viewports.
Reviewed eight annotated busy examples covering both layouts/themes/densities,
alongside full-resolution input artwork. No flagged geometry anomalies remain.
Raw art is not native UI truth. CardDetail remains an existing withheld family;
these scenes and all IMAGE201derivatives must not enter future final evaluation or
be silently admitted for training.

## Native execution and timing

Exact simulator F3EF9DB8-0B0F-4757-B653-D1628269F6FF, iOS26.5, iPhone17Pro.
Fresh toolchain Xcode27.0/27A266a. Approved build/install/container/runtime storage;
all explicit host outputs under `reports/work/IOS-ASSET-200/artifacts` and `.build`.
Existing simulator boot reused, no service reset, download or signing repair.
Available space45GiB local/1.7TiB USB at preflight; retained campaign roughly145MiB,
evaluation image copies144MiB, well below20GiB cap. No local artifacts deleted.

Native build initially failed missing `try` in new resume reads; corrected and
rebuilt successfully (`campaign-ios-build02.log`), failed log retained. Shard0 passed
13.393s; shard1 passed13.811s. Receipt capture intervals total27.1777s. Capture-only
throughput≈12716scenes/hour, **not end-to-end throughput**; build/setup/review/intake
not included and not measured as a single wall interval. Each shard bounded120s.
Fresh container resolution after each installation/test prevented stale-container use.
Postflight exact-target `simctl getenv ... HOME` succeeded; simulator left available.

Simulated interruption before shard publication: copied48sealed scene triples into
a new owned resume directory without terminal receipt. Native replay validated all48,
captured0, completed0.071s test/0.0614s receipt interval. This proves sealed-scene
publication recovery, not recovery from arbitrary crash states. Missing partial files
remain fail-closed. Original completed campaign was not altered.

## Fixed Run022 findings

Used existing `eval_phase6a.export_predictions`/`eval_run013` scorer,640letterbox,
MPS, fixed confidence0.25/IoU0.5operating counts. One inference pass,96images.

| Image-view detections | Procedural | Lower detail | Busy |
|---|---:|---:|---:|
| Grid TP /80 |80|12|3|
| Detail hero TP /16 |16|16|16|
| Grid collection-item TP /80 |80|80|73|

Grid busy missed image views:21have a matching box below threshold;56have no
exported same-class box meetingIoU0.5. Lower detail:28lowconfidence/40no match.
These best-candidate diagnostics are not AP's one-to-one matching and do not prove
absence of internal network proposals. Case-linked records are in `diagnosis.json`.
Grid aggregate customAP50 1.0/.89954/.85563 obscures the image-view operating collapse.
Detail secondaryButton0/16in every condition is a separate persistent weakness.
Only two related artworks: no unseen-app or general dataset-quality claim.

Prediction export succeeded; reporting initially exceeded the small coordination
parser's20000-event budget. Preserved `campaign-evaluation01.log`; recovered the
same predictions using existing evaluator schema validation and a32MiBread bound.
No repeated inference, changed thresholds or globally relaxed parser limit. Exact
inference elapsed time was not persisted before that failure; recorded as unavailable.

## Verification and identities

- `python -m unittest discover -s scripts -p test_artwork200_campaign.py`:10pass,
  8.059s, including real CLI/collision, wrong target, partial output, altered sidecar,
  symlink, unreviewed same-name bytes and resealed outside-artwork changes.
- `swift build` and serial `swift test`, native build system, scratch
  `.build/asset200-offline`:exit0;132 Swift Testing +14 XCTest pass. Logs retained.
- Native `xcodebuild test-without-building` named test passed both shards and resume;
  `.xcresult` bundles retained. No whole-dataset tests rerun between internal steps.
- Actual campaign `prepare`, `validate`, `review`, `evaluate`, recovery `report` and
  `diagnose` CLI paths exercised. Full source/build seal retained in artifacts.

SHA256 identities:

- Plan:3cc846c2f159c3b81eb59ca42ecc0470b35c207af2ad789d131303aae37fdde4
- Validation:3a29644c8d27e1516835e7ecb2da802068a1f273d3cd6dd25c9f59f05b975a93
- Evaluation:7d2ea816315731817aeb5953647709de9758c26dd803d40dff54a1eabafb153b
- Diagnosis:eb70cfb9b3ba7c6ea3592418c488b089acf3d7b4b1d0ff7396470f98712f153a
- Source/build index:619054b7ac65075da7bc320e8549afdb31ae0b175ee2e77abec77155c3249f18
- Model:d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d

## Coordination and next substantial tranche

Published/readback verified metadata-only
`nuiak/responses/nuiak-20261006-artwork200-native-findings.yaml`, SHA256
d954406f6f1a1954dec5fc5056919a3a93f3d24186cf7d256e2019392b1f6d0e.
Peer acknowledgment pending. No images transferred. Big Dog204still reports catalog
prepared/GPU queued; no completed generation claimed. TTR source remains46dce7b,
required550a2d3object absent; no fetch or peer edits. This does not block local work.

Next: finish197proposal-support diagnosis using retained data; intake/review204asset
families when available; then freeze207's bounded training-compatible grid treatment
and all-class retention comparison. Do not retrain merely by recycling these96frames.
tvOS202can qualify independently after source reconciliation. Existing source, iOS
reconstruction and unrelated dirty changes preserved. Raw evidence remains ignored;
same-volume retention is not an independent backup.
