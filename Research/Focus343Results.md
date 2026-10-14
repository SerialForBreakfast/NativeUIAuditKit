# FOCUS343 — native transfer remains the main failure

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Date: 2026-10-12. Owner: research-host-NUIAK.
Seven diagnostic jobs complete. No model changes or promotion occur.

## Findings

| Test | FOCUS329 baseline | FOCUS342 preservation |
|---|---:|---:|
| Retained artwork comparison, 240 authored pairs | 223 correct | 226 correct; 0 old successes lost |
| New identical-artwork neighbors, 32 authored pairs | 32 correct | 32 correct |
| Native corner movement, 8 directed pairs | 0 correct; 8 missed | 0 correct; 8 missed |
| Native stable repeats, 8 directed pairs | 8 correct | 8 correct |
| All 1,200 retained authored pairs | 978 correct | 955 correct; 35 old successes lost |

FOCUS341 content and FOCUS342 rotation also miss all 8 native changes.
Each loses 4 successes on the 32 new authored pairs through abstention.
Native reversals share one scene. They are not independent trials.

The original detail windows cover every changed native body completely, within floating-point precision.
The added boundary window is absent in all 8 native movement comparisons.
Focused bodies measure about 216.5 × 59.5 px in the 3840 × 2160 capture.
They measure about 10.8 × 3.5 px in the whole-frame input.
Missing body coverage does not explain these failures. Coverage alone does not prove the cause.

All 35 retained losses from preservation concern artwork-only changes.
Preservation also turns 3 authored abstentions into wrong confident decisions.
More content suppression alone is not a justified solution for missed native growth.

## Capture and preservation

The exact Simulator is `[local resource identifier]`, running tvOS 26.5.
Xcode 27.0, build 27A266a, supplies the command tools.
The desktop TTR app is absent. The Simulator Fixture runs independently on port 8080.
The runner binds that listener to the selected process and installed binary hashes.
Eight frames pass dimension, fresh observation, capture interval, focus identity, and body checks.
The runner preserves the recipe and restores the original focus. Capture takes 8.06 s.

The first attempt stops because transient observations omit focus fields.
The corrected wait handles temporary omissions within 10 s.
A separate recovery record confirms restoration before the second attempt.
Both attempts remain preserved. No automatic retry occurs.

The older composition adapter rejects version 5. This diagnostic does not weaken that adapter.
The diagnostic uses current raw observations and the existing rendered-body validator.
Capture intervals are not atomic framebuffer identities. No TTR receipt is invented.
The installed source/build match remains unverified. These images stay outside training.
Visual review confirms native growth and clipped short titles on the sparse corner screen.
This scene is not a realistic media app or an independent real-app test.

The authored comparison uses 2 reviewed artwork families, 4 layouts, and 2 focus targets per layout.
The runner verifies renderer hashes and every required asset file. Missing-file fallback cannot explain this bounded comparison.
Related artwork retains its training ancestry. New comparisons are development-only.
The first combined job reaches its output guard before completion.
Two revised jobs use reusable artwork inputs and separate families. Both finish without reducing planned coverage.
The failed attempt stays visible. No failed result becomes a success.

## Cache and execution evidence

The fixed 8-example check preserves logits, gradients, and one SGD update exactly after disk retrieval.
Tests reject changed identities, corrupted values, duplicate writes, and incomplete entries.
No trained checkpoint is saved. Full-run caching remains disabled.
This does not establish an end-to-end training speedup.

| Queue job | Wall time |
|---|---:|
| `focus343-artwork` | 0.24 s |
| `focus343-margins` | 0.24 s |
| `focus343-native` | 5.33 s |
| `focus343-native-detail` | 1.51 s |
| `focus343-cache-parity` | 2.53 s |
| `focus343-identical-neighbors-r2-0` | 6.49 s |
| `focus343-identical-neighbors-r2-2` | 6.36 s |

Attempts retain inputs, predictions, raw counts, model hashes, and output hashes.
Evidence stays under `reports/work/research-queue/jobs/<job>/attempts/1/`.
Native evidence stays under `reports/work/FOCUS-343/native-corner-r2/`.
These times exclude implementation, review, tests, and failed attempts.

## Verification and coordination

All 109 focused tests pass. The offline Swift build passes.
The serial Swift suite passes 187 tests: 14 XCTest tests and 173 Swift Testing tests.
The sandbox first blocks loopback and Apple runtime access. Scoped execution passes the same checks without service changes.
The queue contains 99 complete jobs, 43 blocked jobs, and 1 preserved failure.
Completion counts include historical placeholder jobs. They are not measured model successes.

The coordinator stores requirements at cursor 317 and results at cursor 322. Readback confirms both messages.
Forwarding and recipient acknowledgment remain unconfirmed. No new artifact is offered in the read replies.
The initial estimate is 45–90 min. This tranche takes about 27 min, including implementation and checks.

## Decision

Keep the baseline. Test native body size, aspect ratio, and effect appearance before another correction.
Use [the native experiment plan](Plans/NativeAppExperiments343.md), starting with R4, R3, R1, and R2.
Select one correction only when measurements distinguish the likely cause.
Retest all previous-success sets before accepting a candidate.
Do not wait for all 3 planned Fixture apps before testing one qualified path.
