# COVERAGE119 — full endpoint consistency and exposure closure

DTM030passes all282unique training endpoints paired with themselves, expanding the
previous226checks by56new collection images. All433retained cases also keep their
correct confident decision when frame order is reversed. No fitting, export,
conversion, capture, role change or promotion performed.

## Results

-282/282confident unchanged;zero false changes/abstentions. Maximum self-pair
  probability0.04832765. Difference from frozen DTM025base≤2.61e-8, reflecting
  different inference batching; not a claim of bit-exact cross-batch probabilities.
-433/433reversed cases confidently correct,zero categorical changes. Largest
  probability change0.010991. This establishes tested behavior, not universal
  architectural symmetry or performance on unseen UIs.
-207original pairs contain178Fixture-renderer and104Settings images. Every image
  has exact hash/origins and training/exposed role in the inventory. No independent
  final membership exists. Different hashes/filenames from these ancestry groups
  do not establish a new final partition.

## Evidence and tests

scripts/audit_transition119.py validates current source/result/checkpoint hashes,
reconstructs all endpoints, rejects differing tensors for an identical image hash,
replays DTM030exactly before reversal and scores all self-pairs. No new trainer.
Report: artifacts/audit/report.json;SHA256:
a637256160afc73f83941f296c8cb7f99ea89ece1b25a7eacfc12b66d89bf085.
4.371seconds,exit0.23Python tests and offline Swift build/138tests pass; logs
.build/transition119-{build,test}.log. git diff --check passes. Original checkpoints,
images and unrelated dirty changes preserved; no Git writes.

The two outcomes are full endpoint/reversal qualification and an actionable current
exposure inventory for EVAL90. Software verified; data roles unchanged; producer
integration not assessed; independent model gate not assessed. These synthetic
self/reverse checks must not be presented as additional captured training examples
or separate held-out accuracy.

## Boundaries / next substantial tranche

New DTM030CoreML export remains blocked by the execution reviewer's demand for
explicit export authority; no retry or indirect conversion attempted. After approval,
finish SHADOW118native parity, portable isolated build and TTR receipt delivery.
Separately reserve new native evaluation sources before labels enter development.
Geometry109still needs consistent source boxes; existing images cannot supply
independent final coverage merely by changing their role.

Peer status remained at08:45:09UTC (survey17, safe Learn Remote stop). No new
handoff/independent membership was available. No shared publication for this local
audit: it does not alter TTR's next action or the existing export-blocked status.
The broad support/model-improvement goal remains active and incomplete.
