# P0-A recovery evidence review — handoff

**State:** Blocked/incomplete; not review-ready for P0-B or P0-C dispatch.  
**Scope:** Read-only P0-A recovery assessment review and label-identity remediation.  
**Date:** 2026-09-19.

| Outcome | Result | Evidence |
|---|---|---|
| Software verified | Passed | The manifest-driven, non-overwriting label verifier completed validated chunks and preserves all corpus inputs. |
| Data eligible | Failed | No candidate source has original pixels; test remains 0/2,000 resolvable and train/validation remain incomplete. |
| Integration qualified | Not applicable | No producer, hardware, backup, or external service was used. |
| Model gate passed | Not applicable | No inference, training, or promotion ran. |

## Recovery decision

The bounded source recovery is exhausted for the five documented candidate roots:
all contain **0 of 15,239** expected unique original source paths. This does not
prove deletion or identify a cause. It does establish that P0-B cannot safely
stage a recovery from inputs currently available to this checkout.

The only safe next choices are:

1. The maintainer supplies one specific backup/archive location for a new,
   read-only P0-B candidate assessment; or
2. The architect reviews and explicitly assigns P0-C, including rendering and
   destination authority for a new versioned corpus. It must use paired new
   pixels/annotations and a new Run 009 baseline, never historical labels.

No path was relinked, copied, deleted, regenerated, or overwritten. Historical
manifests, labels, broken links, checkpoint, and Run 009 report remain preserved.

## Label-identity remediation status

The prior P0 assessment counted every label but left its individual SHA-256
unset. [`scripts/verify_p0_label_identity.py`](../../../scripts/verify_p0_label_identity.py)
adds append-only, manifest-derived identity chunks under this directory. It
validates label roots remain inside the checkout, refuses output reuse, does not
read image symlink targets, and refuses finalization unless every manifest row is
represented exactly once.

It has completed **11,415 / 17,040** unique contiguous rows through manifest offset
11,414. Resume attempts created 200 overlapping chunk rows; they are byte-for-byte
identical on their identity fields and the finalizer rejects conflicting duplicates.
The remaining scan is not asserted complete: direct filesystem evidence
shows a 50-label chunk required 16.357 seconds elapsed with 0% CPU. This repeats
the prior local metadata/read stall in a measured, resumable form. Existing
`labels.cache` hashes are retained only as split-level signals and are not
substituted for per-label content identities.

## Evidence and verification

- Existing inventory: [`reports/work/P0/assessment.md`](../P0/assessment.md),
  [`manifest_inventory.jsonl`](../P0/manifest_inventory.jsonl), and
  [`candidate_sources.json`](../P0/candidate_sources.json).
- New partial identity evidence: `label_identity_chunk_*.jsonl` in this
  directory; all outputs are new and in-package.
- `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/verify_p0_label_identity.py --chunk-start 0 --chunk-size 500` — exit 0, 500 rows.
- Repeated bounded chunk verification — exit 0 through offset 11,414.
- `time ... --chunk-start 11365 --chunk-size 50` — exit 0; 16.357 seconds
  elapsed, 0.06s user / 0.02s system.
- Shared-status publication/readback: [`coordination.md`](coordination.md).

## Exact blocker and resume condition

P0-A's full label-hash acceptance criterion remains incomplete because hashing
the remaining manifest-listed local labels is not bounded within this execution
environment. Resume either with a maintainer-approved filesystem-safe batch
method that preserves source data and writes only new in-package evidence, or
when a specific backup/archive location arrives—at which point P0-B verifies
candidate pixels, labels, dimensions, and provenance before any staging.

No safe P0 implementation work remains under the current read-only authority.
Do not overwrite the existing P0 report or partial P0-A chunks.
