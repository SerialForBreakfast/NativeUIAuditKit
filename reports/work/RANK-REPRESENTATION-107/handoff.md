# RANK107 + TTR feedback reconciliation

October3local/4UTC. Completed the feature audit and actionable peer response. No
new training, capture, data admission, model export, deletion or Git writes.

## What changed our next action

The5022candidate/187frame bank has **zero exact opposite-label collisions** in
either768RGB features or770RGB+size features. That does not prove that downsampling
preserves all useful detail, but model failure alone cannot establish lost information.
All reference labels come from approved training rows; Settings remains exposed
development and never supplies a reference. Same-frame candidates are excluded
from nearest-neighbor references. Related recipes are not independent holdouts.

| Group | Unique frames | Candidates | Positive candidates | Fixed-distance correct frames |
|---|---:|---:|---:|---:|
| Old training |122|2846|245|121|
| New training |56|1953|142|56|
| Exposed Settings |9|223|9|9|

Distance contrast is d(nearest negative)-d(nearest positive) in the unchanged770
feature space, with deterministic candidate-ID ties. This was an exploratory
diagnostic, not a predeclared independent model evaluation. Settings scores9/9
using older training references only but0/9using new-cohort-only references.
All9positive Settings crops are closer to a training positive than a negative;
their median positive RMS is0.126 versus0.0226old-training/0.0640new-training.
The diagnostic loses one formerly correct old frame, so it does not pass retention.

**Decision:** do not assume a larger image/CNN is the next necessary step. Prepare
RANK-METRIC108: versioned, chunked, training-reference scoring and exact paired
evaluation, including the old failure, cost and deployability. No threshold or
architecture sweep. Larger-context work remains proposed if this evidence warrants
it later. The delivered DTM025 and retained DTM020 are unchanged.

## Verification and efficiency

`scripts/audit_representation107.py` uses the existing strict bank/admission loader,
positive-proposal labels and cached features. It reports collision groups, per-source
support, nearest other-frame training references, deterministic whole-frame selections
and reference-cohort sensitivity. Full report:
`artifacts/audit-qualified/audit.json`. Earlier partial diagnostics remain preserved.
Final audit23.356s,1,889,645bytes; SHA256
`cfb6b017f2544c7fc4121738bdd5c303bb284fde981002ac140dd126574db6aa`.
No native crop invocation, simulator setup, new image encoding or model fitting.

17focused/regression Python tests pass:6new audit tests plus actual trainer/readout
and collection regressions. They cover contradictory labels, train/development
separation, normalized-size distinction, same-frame exclusions, deterministic ties,
missing-reference rejection and prior training safeguards. Offline Swift build/test
exit0:14XCTest+123SwiftTesting. All explicit caches/logs local; normal Apple test-cache
access used scoped approval. `git diff --check` passes.

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/audit_representation107.py --output reports/work/RANK-REPRESENTATION-107/artifacts/audit-qualified
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python -m unittest scripts.test_representation107 scripts.test_retention105 scripts.test_collection104
```

Logs: `.build/representation107-{audit-qualified,tests,swift-build,swift-test}.log`.
Current source hash matches the final audit's implementation reference. No raw
images or full inventories belong in Git; artifacts are ignored. Pre-existing
dirty work preserved.

## TTR update and delivered response

Read verified SMB status06:08:17Z: TTR reports104single-frame candidates scored
on8retained frames, not transition inference or independently reviewed body accuracy.
Its new screenshot sample remains unpublished pending specific egress permission.
Local source HEAD remains4f9273cc; no Git synchronization/write was performed.
No exact DTM025delivery receipt/acknowledgment was present. The delivered198,134byte
archive still matches its SHA256; no repeated transfer or cleanup occurred.

Answered `tvtestrig-20261003-training-usb-retention` with NUIAK ownership and canonical
volume-relative convention `data/NUIAK/archive/tvtestrig/<transfer-id>/<sha256>/<file>`.
Existing pinned `/dev/disk25s1` local APFS mount verified via registry and OS mount;
approximately1.7TiBUSB/56GiBinternal available. DiskManagement detail query was
unavailable in the sandbox; no service repair attempted or UUID invented. This
defines future storage, not a claimed durable copy/retrieval test of absent data.
Response specifies exact hash/size receipts, source preservation, privacy/role
separation, bounded retrieval verification and no new access services.

Published/read back immutable response:
`nuiak/responses/nuiak-20261004-shadow-delivery-and-retention-followup.yaml`, SHA256
`4b8d1ebfb87854da2915fa65120a8634f4a818625aca3706705cb1e90370136c`.
Local copy `ttr-followup.yaml` is byte-identical. Updated own SHADOW-FEEDBACK01packet
to point at the existing DTM025delivery, superseding transition-unavailable only
for change classification. Duplicate-key-safe readback passed; after removing
that owned packet, unrelated status semantic SHA256 remained
`96c8baa1eacd5c0b8afb5d4deb4868e34e34ac78c8ad0f1c3feeab398394b99c`.
Peer acknowledgment of this response, archive receipt and live hook proof remain
separate pending facts. No private screenshot transfer or deletion authorized here.

## Outcomes / next substantial tranche

- Software:PASS, reproducible audit and17Python/137Swift tests.
- Data:unchanged eligibility; no peer data received or newly admitted.
- Integration:coordination publication/readback PASS; live TTR hook NOT ASSESSED.
- Model:diagnostic only; no production or independent-quality gate passed.

Next: implement RANK-METRIC108's bounded scorer and matched comparison, diagnose its
one old miss, and measure full bank/inference cost before any export proposal. In
parallel, reconcile TTR's exact transition receipt and permitted feedback handoff
when published. Do not let either wait block the local scorer comparison, and do
not turn the9/9exposed result into a production claim.
