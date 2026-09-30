# OHEM batch safety and timing — TRAIN-OHEM-TIMING-12

Authorized scope: offline repair/testing and instrumentation, not training.

Installed Ultralytics 8.4.124 consumes label `shape` during rectangular setup.
Calling `set_rectangle()` again is therefore not safe without reconstructing it.
Keep the original batch geometry and restrict each replacement to a slot with
the same original rectangular output shape. This preserves collation, padding
and cardinality without reading images or inventing geometry. Report unfulfilled
replacement requests; never fall back to cross-shape replacement. Reject changed
dataset identity, batch geometry, malformed metadata or ambiguous original paths
before mutation. Clear decoded caches and the augmentation buffer, then reset
the loader. Each epoch starts from original membership (no compounding).

The ranking remains a batch-loss proxy, not per-image loss. This repair does not
establish that OHEM improves accuracy. Same-shape restrictions can reduce the
requested oversampling factor and must be visible in reports.

Optional timing uses a monotonic wall clock: batch callback interval, inter-batch
gap (not pure loader time), preprocessing, optimizer step, validation, checkpoint
save, checkpoint mirror, OHEM recording/replacement and epoch total. Nested timings
are not additive. No device synchronization or GPU-kernel attribution is claimed.
Append bounded aggregate epoch records and a terminal record to a fresh project-local
JSONL file. Preserve exceptions and partial evidence; do not overwrite prior logs.
Tests use fake trainers/clocks and exercise actual registration, not model execution.

Acceptance: rectangular and nonrectangular paths, exhausted compatible slots,
partial batches, repeated epochs, drift rejection before mutation, cache/label
alignment, timing disabled/enabled/error paths and actual trainer integration.
Run offline focused Python tests and required Swift build/test. Coordination is
not applicable: this changes no TTR action or producer contract.
