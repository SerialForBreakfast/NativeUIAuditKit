# HCF337 — handoff closure, TTR intake, requirements, and pilot scorer

Owner: Maximum-mini-NUIAK. Date: 2026-10-11 (UTC). [Plan](Plans/HCF337.md).

## Coordinator messages

Attention showed 2 unread forwards from Sillycon-TTR at cursors 211 and 213. NUIAK read both and acknowledged cursor 213.

| Cursor | Message | Action |
| --- | --- | --- |
| 211 | TTR received the HCF336 archive and accepts intake and source-review ownership | Receipt verified; shared copy removed |
| 213 | TTR asks for a data and review requirements matrix | [Matrix](HCF337TTRRequirements.md) published and sent |

NUIAK sent 3 messages. All pass exact-ID status readback. The coordinator has not read them yet.

| Request ID | Cursor | Content |
| --- | ---: | --- |
| `nuiak-hcf337-handoff-01` | 214 | Receipt verification, cleanup, and intake findings |
| `nuiak-hcf337-requirements-01` | 216 | 8-part requirements summary and SMB document hash |
| `nuiak-hcf337-correction-01` | 218 | Corrects the REVIEW304 hash abbreviation in message 214 |

## Handoff closure

| Transfer | TTR receipt | Check | Shared copy |
| --- | --- | --- | --- |
| `nuiak-hcf336-source-v1` | `tvtestrig/hcf336-source-receipt.json` | 16,998 bytes; SHA-256 `43bee9cd…0d15d` matches local original and shared copy | Removed |
| `nuiak-tvos-review304-handoff` | `tvtestrig/tvtestrig-20261010-review304-intake-receipt.json` | 5,816,443 bytes; outer `8ee3c41a…e60d1ab` and inner `063d7c4c…747b7e1a` match | Removed |

Both local originals remain under `reports/work/`. The REVIEW304 offer file remains on SMB.
TTR reports 25/25 reference detections at `cc72583` on macOS 26.5. NUIAK records this as peer-reported.
TTR did not supply raw test logs. TTR keeps HCF336 implementation, host qualification, and macOS 14 runtime work.

## TTR SMB offers r48, r50, and r51

NUIAK copied each archive to ignored local storage. All 3 SHA-256 values match TTR's declarations.
Extraction used the tar `data` filter in new empty folders. No member is unsafe.
Receipt: `nuiak/nuiak-hcf337-ttr-intake-receipt.json`, SHA-256 `cb3d3a0e…53fc50`, read back equal.

| Archive | Bytes | Finding | Decision |
| --- | ---: | --- | --- |
| Crop triplets v1 | 29,414,766 | 15 crops from 4 frames. Every role is `control_wrapper`, which is not in the 41-class map. | Not admitted |
| Top 10 difficult UI | 2,198,912 | Manifest states 2,171,940 bytes. All 10 named full frames are missing. Same lineage as the crop triplets. | Not admitted |
| Interruption hardening | 54,347,379 | Manifest states 54,483,756 bytes. Seven of 9 frames are byte-identical. Tests 1 and 2 show no banner, modal, or scrim. | Not admitted |

Only interruption test 3 shows a real change: an app switch to Settings and back.
TTR's own markers for tests 1 and 2 record no scrim, 0% luminance change, and 0 OCR divergence.
These archives remain development evidence only. `trainingEligible=false`. TTR owns removal of its shared copies.
[BP-114](BestPractices.md) records the intake lesson.

## HCF pilot scorer

`scripts/score_hcf_pilot.py` scores rules, models, or hybrids against verified focus truth on identical membership.
It reports wrong focus, misses, abstention, coverage, no-focus specificity, IoU, warm latency, and paired differences.
It counts repeated images in 1 group once. Intervals resample layout-family and scene groups with a fixed seed.
It keeps development and reserved roles separate. It rejects mismatched membership, hashes, and invalid boxes.

| Check | Result |
| --- | --- |
| New scorer tests | 12 pass |
| HCF333 and HCF334 tests | 9 pass |
| Offline Swift build (`--build-system native`) | Pass |
| Offline Swift tests (`--no-parallel`) | 14 XCTest and 173 Swift Testing tests pass |

Synthetic test inputs make no accuracy claim. No retained replay runs.
The retained HCF-NATIVE261 frames have no independent truth. Their boxes come from rule proposals, so they cannot score the rules.

## Remaining blockers

The matched pilot needs the 48-screen campaign with verified truth. Sillycon-TTR must supply these inputs:

1. A committed profile command contract.
2. Restart-restoration evidence for profile changes.
3. Per-frame runtime focus ID and profile receipt.
4. A verified way to produce no-focus frames.

When those inputs exist, convert each sidecar to `hcf-pilot-truth-v1` and score the existing rules and the shipped model first.
No capture, inference, training, image generation, data admission, TTR source edit, or Git write occurred.
Raw evidence stays under ignored `reports/work/HCF-337/`.
