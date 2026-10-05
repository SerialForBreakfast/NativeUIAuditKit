# Run020 evaluation and TTR handoff reconciliation — 2026-10-05

Run020 materially improves page-control fitting and exposed development detection,
but fails its predeclared per-placement fit gate and regresses retained classes.
No promotion, threshold change, additional epochs or new training performed.

| Evidence | Run019 | Run020 |
|---|---:|---:|
| Fit leading hits /72 | 0 | 70 |
| Fit center hits /72 | 62 | 72 |
| Fit trailing hits /72 | 8 | 56 |
| Fit page TP/FP/FN | 70/6/146 | 198/28/18 |
| Development page hits /96 | 19 | 59 |
| Development page AP50 | .343791 | .627804 |
| Retained 2400-image mAP50 | .882978 | .871533 |
| Retained mAP50:95 | .841897 | .831885 |
| Retained page TP/FP/FN | 79/2/521 | 199/17/401 |
| Retained cancelAction TP/FP | 76/73 | 80/85 |
| Retained mapView TP/FP | 100/0 | 100/10 |

Custom all-point interpolated AP, not official COCO/Ultralytics AP. Fixed confidence
.25/IoU .5. Training monitoring and fit scores are in-sample; the 96 development
probes and repeatedly used retained corpus are not untouched final qualification.

## Diagnosis and decision

The fit gate requires at least90% recall in **every** placement. Trailing56/72
(77.8%) fails despite aggregate198/216 (91.7%). All18 remaining fit misses are
low-confidence matches:11trailing/system-blue/light,5trailing/semantic-label/dark,
2leading/semantic-label/light. No absent or localization-miss dispositions remain.
Median oracle-match height ratios improve leading2.430→1.288,
center1.349→1.125 and trailing2.625→1.435. These are diagnostic best-IoU candidates,
not a proposed runtime oracle. Better geometry does not justify threshold tuning.

The largest retained AP50 losses are sheet−.789844 and scrollIndicator−.231953;
overall mAP falls1.145percentage points. Concentrated fine-tuning supports that
off-center geometry is learnable in this setup, but does not isolate sampling from
epoch effects or prove generalization. Retention loss is consistent with narrowed
training exposure; its cause needs a controlled diagnostic, not an assertion.

Next bounded proposal: reuse these predictions to stratify the18low-confidence
cases and case-account sheet/scrollIndicator losses; audit existing training
support, then freeze one mixed-replay sampling comparison only if supported.
Keep the full original annotations, confidence threshold, existing data roles and
evaluation memberships. Do not start another run merely to raise trailing recall.

## Execution and integrity

Existing pinned `scripts/fit175.py infer` and `report` both exited0. Exported and
validated216fit +96probe +2400retained records; zero degenerate boxes rejected.
Reused Run019 predictions rather than rerunning that model. Input/source/initializer
hashes, saved arguments,20finite epochs and fixed-last selection passed real
entrypoint checks. Training receipt:875.142s wall; CSV last elapsed847.549s.
Inference progress timers11.7s/4.7s/119.5s exclude other validation/publication work.
Report runtime was not separately instrumented. No external waits were scheduled.

Checkpoint SHA256: `6b4e22ba5971d26566f213c43d43ea81dce909c61cddd8da390e464cc6f1944c`.
Evaluation seal: `140e17a933db7766ba215f3175658d3fa2c3986f753d4c769caa4f048f29bf85`.
Machine evidence: `artifacts/evaluation.json`, prediction files, `completion.json`
and protocol. Kept ignored/local; no Git writes or migration of these inputs.

Existing10focused tests and integrated offline Swift evidence reused unchanged;
no implementation code changed this turn. Documentation checked with git diff --check.
Software verification passed; existing diagnostic data roles preserved; local
model execution/evaluation passed; model acceptance failed and production gates
remain unassessed.

## Independent TTR work completed

Reconciled stale FLOW123/124 queue wording: transfer repair exists, and the exact
54,763-byte FLOW176 archive remains published with matching SHA256
`a286ec244697f634606be7f6a77a96f7b0be950ae6e45baee3436c9f798aeb34`.
Receiver receipt and11-case replay absent on fresh check; no repeat upload needed.

Native24 remains blocked: local TTR HEAD46dce7b3; `git cat-file -t b98402df...`
fails because object is absent. Peer reports source-based semantic block and completed
sender cleanup. Existing337verified payloads/24cases remain retained; no recapture,
admission or weakened v3 checks. Resume when maintainer publishes/synchronizes exact
v3 validation/hash/callback source. No agent Git writes or peer source edits.

All seven artwork tranches now mapped by TTR's named response; local queue and shared
ART-HANDOFF-178 acknowledge accepted/deferred order. Updated RESIDUAL-160 with exact
source/replay next actions, preserved other packets, parsed/read back shared YAML.
Model-only iOS results were not published to SMB. No hardware, SSH or new service.
