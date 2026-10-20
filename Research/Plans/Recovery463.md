# RECOVERY463 — Verified offload and recovery

## Decision

Use the existing offload tool and recovery gate. Do not change the storage policy or repeat completed captures.

The failed row capture stops when TTR rejects its evidence reservation. Restoration also stops before input.
Its failed receipt, partial shard, and recovery guard remain preserved.

## Verified storage

- Verify the mounted USB identity before writes.
- Copy each unique PNG payload to the USB archive and verify its SHA-256.
- Preserve all 691 evidence paths and their bytes.
- Replace 187 duplicate directory entries with verified hard links.
- Preserve all recovery journals without modification.

The archive contains 45 unique payloads and 242,138,795 bytes.
Read-only accounting measures 379,547,433 retained bytes after compaction.
The existing policy reserves 134,217,728 bytes and forecasts 68,157,440 bytes for the next operation.
Their sum stays below the unchanged 1,073,741,824-byte limit.
This accounting check does not establish native restoration. The queued recovery must establish that result.

## Execution graph

1. Run the exact failed-guard recovery successor through the detached runner.
2. Require verified Standard, Fixture restoration, screenshot readback, and closed ownership.
3. Run the existing admission gate for 4 pinned capture successors.
4. Verify retention between captures through the existing serial dependencies.
5. Run the 36 existing matched analyses on their resulting evidence.

The row-top successor uses a new shard. Other scientific settings and comparisons remain unchanged.
Failed or uncertain recovery blocks captures. No process completion grants model acceptance.
Standard and iOS remain independent. No labels or training roles change.

## Evidence

Local records reside in `reports/work/RECOVERY463/`.
They include offload receipts, the storage check, the original guard, immutable specifications, and successor mappings.
The existing iOS label-review tasks remain independent of TTR. This tranche does not repeat completed iOS diagnostics.
