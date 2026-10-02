# Optional TTR batch-performance backlog

Maintainer request October2,2026:
`nuiak-20261002-native26-optional-batch-performance`.

Low priority; suitable companion tasks for smaller tranches without displacing major
goals. Our high-priority native-effect spike is1,000training+250evaluation pairs,
2,500images. These enhancements are not prerequisites for serial generation.

- Pacing/settling: expose or document existing campaign controls first; add missing
  minimum spacing, bounded settle readiness/timeouts and effective settings in receipts.
  Preserve observed focus/geometry stability. Measure render/settle, capture/PNG encoding,
  export and pacing overhead separately where possible; unavailable timing stays unknown.
- Optional multi-Simulator scheduling, default off: bounded workers with exclusive
  target ownership, isolated Fixture endpoints/output roots, deterministic manifest
  partitioning and receipt aggregation. Preserve source groups/splits and exactly
  accounted case IDs across resume. Specify backpressure, memory/disk limits,
  cancellation, partial failure and cleanup. Respect coordinator serialization until
  the supported scheduler is tested.
- Benchmark one versus two workers on matched workload/resolution/settling. Report
  accepted pairs/sec, wall time, median/p95 latency, errors/retries, bytes and resource
  use. NUIAK measures downstream crop/feature encoding, training and evaluation.

Twelve retained native cases average7.449seconds/pair:1,250pairs project2.59hours
case execution before overhead. Measure the serial batch and use actual metrics to
decide optimization priority; do not assume linear speedup.

Please acknowledge with backlog task IDs and already-supported options versus gaps.
When implemented, provide source commit/push identifiers; NUIAK builds locally.
This request dispatches no peer hardware/capture operations.
