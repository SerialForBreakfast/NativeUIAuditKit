# RANK-75 — visual ranker and shared-image crop batching

One registered candidate DTM016 completed through train_focus_ring_detector.py.
Existing32train/5development roles unchanged; no capture,export,promotion or git writes.
All prior dirty files/artifacts preserved. SMB not applicable: no producer action changes.

## Outcomes

- Software:59focused Python tests,offline Swift build and14XCTest+120Swift Testing pass.
- Data: existing admitted membership preserved; derived image-only bank2,141candidates,
  59unique frames,50training frames. No new admission or independent final evaluation.
- Integration: real crop helper and trainer CLI verified; no TTR runtime operation.
- Model:600epochs/600updates complete,64/64training endpoints/32paired successes;
  exposed Settings0/10endpoints/0paired successes. No quality gate or promotion.

DTM013change probabilities frozen. Best positive Settings ranks20–27; automatic boxes
exist but learned visual ranking does not transfer. No confidence calibration: top-one
ranking produces no abstentions here despite failure. Do not use it for navigation.
Checkpoint replay from saved weights matches every selected box; reversed candidate
order preserves decisions. Labels loaded only after prediction in verification.

## Efficiency companion

FocusRingTool caches source images for one request, retains hash/bounds checks and
128item/80Munique-pixel limits. Existing adapter callers retain16item batches; opt-in
shared-image batching allows128items.59same-image crops pass byte-identical comparison
with single invocation; conflicting hash and invalid second-box bounds reject.

Production16%/256crops then RGB16×16bilinear encodings prepared once29.639s in59calls.
600epoch fit1.014s,whole model execution2.357s. Warm bank validation/load0.130s.
This is not a measured simulator setup speedup; no simulator was used. Candidate bank
and model output remain below2GiB. Protocol repair reused bank without recropping.
Post-run dependency hardening validates original preparation numpy/pillow versions,
not just new run pins. Historical protocols remain unchanged; do not bypass their
intentional code-pin invalidation for a new launch.

## Evidence and commands

- scripts/focus_candidate_ranker.py --prepare reports/work/RANK-75/ready: exit0.
- Initial trainer preflight: exit2, missing CLI arm enumeration, before model execution.
  Corrected arm; --prepare ready-r2 --reuse-bank ready/bank.json: exit0.
- train_focus_ring_detector.py --experiment-protocol reports/work/RANK-75/ready-r2/protocol.json
  --experiment-arm transition-candidate-ranker --experiment-approval reports/work/RANK-75/ready-r2/approval.json
  --name rank75-dtm016 --experiment-id DTM016 --execute: exit0,PID35773.
- scripts/verify_rank75.py --result NativeUITrainer/focus_ring_runs/rank75-dtm016/result.json
  --output reports/work/RANK-75/replay.json: exit0 before post-run cache hardening.
- unittest scripts.test_rank75 scripts.test_proposal74 scripts.test_proposals73
  scripts.test_campaign71:59pass,21.084s, .build/rank75-tests-final-r2.log.
- Offline Swift build/test: exit0,.build/rank75-swift-{build,test}.log. git diff --check passes.

Checkpoint4d6886c4f0bf567e1e5ddd32bf722b72a8600200ff54a8c7231ef3fe0ed8d7a7.
Protocol6d47c759a9b907c949c8ce3abfa47a196c6ff58b27a9996b17ce2e7217c714bc.
Raw model/cached tensors stay local; concise report and artifact hashes are review evidence.
Replay CPU ranking cold0.130ms,warm median0.0186ms,p950.0274ms exclude proposals,
crop/encoding,DTM013and application routing. No end-to-end deployment latency claim.

## Next substantial tranche

Resolve actual supported stationary campaign bindings, reconcile native appearance
coverage and reserve independent groups. Execute one authorized multi-batch session
when runtime/scope are verified; intake each new shard once, freeze corpus, and
prepare shared inputs for several predeclared experiments. Until then, source/contract
work remains independent. More unchanged epochs on this exposed corpus are not justified.
