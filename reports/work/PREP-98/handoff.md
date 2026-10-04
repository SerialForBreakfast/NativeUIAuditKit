# PREP-98 / INTAKE-99 — preparation and retained TTR transfer

October3 local / October4 UTC. Existing RANKING97 documentation changes preserved.
No model training, new data admission, device work, source checkout changes or promotion.

| Outcome | Evidence |
|---|---|
| Software verified |15focused Python tests; offline Swift build and134tests pass|
| Data eligible |Existing roles unchanged;122derived negatives proposed only; context60 not admitted|
| Integration qualified |Actual self-pair preparation passes; context60 byte transfer passes, v17 semantics blocked|
| Model gate passed |Not assessed; no model launched|

## Derived-input preparation

Existing `focus_change_adaptation.py` now supports `--self-pair-proposal` separately
from experiment preparation. It revalidates source-derived corpus membership and
sealed parent/tensor bytes, deduplicates decoded pixels, rejects cross-role byte/
pixel conflicts and inconsistent repeated tensors, and retains every origin index,
group and hash. It writes no approval, experiment ID, checkpoint or training protocol.
The training loader rejects the new proposal version; CLI rejects combining it with
`--approve` or experiment options. Encoded input reference is reused, not copied.

Real command (exit0):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/focus_change_adaptation.py --prepare reports/work/PREP-98/derived --self-pair-proposal reports/work/RESOLUTION-96/ready/protocol.json
```

Result:122training-frame derivations,9development frames excluded,73original pairs
unchanged. Preparation16.1907seconds, no model load or training. Proposal seal
`59cb9359c40c4fdf6b9b8c449a0410cdbe99ce47a03080bc93990ed042dd5ce3`.
Old protocol source pins remain historical; no old training approval was rebound.
The pending maintainer role decision is still required before implementing/launching
the proposed equal-group-loss comparison as an admitted training run.

Tests cover deterministic selection, origin preservation, decoded duplicate handling,
cross-role leakage, byte/tensor conflicts, malformed/range/nonfinite tensors, roles,
output collision, changed parent/source, and dispatcher rejection.15tests pass1.432s.

## TTR transaction

Source checkout remains50ff7fd8; no local v16/v17 source publication. Named producer
handoff `tvtestrig-20261003-native-context60` received with the existing bounded
receiver. Archive166,910,453bytes; SHA256
`0c8ddb401c6abe1a3487e9b814d9aac16c9d624c0e9d0f6f27407b31622ca1ef`.
919safe archive members,212,146,024expanded bytes. All835delivery inventory files
verify (211,952,904bytes); only inventory file itself is unlisted, covered by archive
identity. Raw outputs explicitly gitignored at `reports/work/INTAKE-99/received/`.
Archive and producer originals preserved; receiver deleted nothing.

Producer reports60pairs:24appearance,12boundary unchanged,12content-only,12scrolling;
96unique images, shared Fixture ancestry. These remain producer assertions pending
source-backed semantic consumer qualification. Exact stationary-box scrolling remains
unsupported; no training/final role is inferred from delivery. Failed pilot evidence
is preserved inside the archive. No repeated capture or binary request is needed.

Published/read back:

- `/Volumes/SharedStatusFile/nuiak/responses/nuiak-20261004-context60-receipt.yaml`
- `/Volumes/SharedStatusFile/nuiak/status.yaml`, owned `packets.INTAKE-99`

Fresh mount verified as expected SMB; duplicate-key-safe status parse/readback;
unrelated document digest unchanged. Sender receipt acknowledgment and cleanup remain
unverified, distinct from publication. Sender owns exact shared-copy cleanup and must
retain originals. Receipt authorizes neither semantic intake nor training.

## Verification / blockers / next tranche

Build passes. Initial sandboxed Swift test fails Apple E5RT cache creation under
`~/Library/Caches/swiftpm-testing-helper`; failure log retained. Scoped host test
execution approved through the tool, then14XCTest+120SwiftTesting pass. Logs:
`.build/prep98-build.log`, `.build/prep98-test.log`, `.build/prep98-test-host.log`.
No service reset, HOME spoof, signing change or simulator launch. Explicit logs,
temporary files and configurable caches stay project-local. Tests were run once
integrated; focused test rerun followed an added changed-source case.

Source/role gates are real, not waits on an active process. No process remains running.
Next integrated tranche: admit the122derived negatives only after the pending decision,
execute one fixed600epoch equal-group comparison with frozen geometry/ranker, and
reconcile context60/layout28 against published v16/v17 source. Follow with small-control
coverage audit and independently reviewed native evaluation roles. Do not substitute
another resolution sweep, relabel calibration, or weaken schema validation.
