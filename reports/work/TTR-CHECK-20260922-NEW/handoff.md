# Updated TTR/Fixture diagnostic — 2026-09-22 17:26 UTC

User requested read-only checks and status publication. No recipe, focus request,
navigation, capture, installation, launch, restart, Office or training operation.

- New local TTR PID84718, Fixture PID84676. Fixture listener8080 maps to the exact
  simulator9026ECA9-77DB-4AE6-8FE6-BB239E9571FA and installed container20FF2EF4.
  Matching embedded helper help/status/readiness succeed, exit0.
- All8 infrastructure checks ready; can_run=true, persisted ownership clear;
  coordinator command/observation inactive, queue0. Readiness request
  C92EC092-D043-42A3-8B64-905FF575CA34. This does not check Fixture focus/capture.
- Fixture HTTP device/scene respond. Instance D386D6EF-5298-4E56-B970-D0F55CB2C5B7,
  run1CDAAE97-AC6E-44A3-8273-1AF4312292BF, tvOS26.5,1920×1080 points,scale2.
- Fixture launcher SHA2565444c9b52a03254ac5afb1a1b7a7731b974b5d3865826e0b9d46a3ebcb8f3a4a;
  debug d2c0af65803bfc86f8b905259e316d3480198392982391115645e0382b8c81d1.
  Both differ from the historical failing build. Current dialog/sweep source hashes
  match the producer candidate receipt (717e48ff…/32f85b78…). Source match and
  changed binary are evidence, not a cryptographic source-to-build attestation.
- App launcher2f83191b…/debug68811337… also changed; full hashes in hashes.txt.
  Checkout1e46611 is separately observed, not inferred loaded-build identity.
- Initial passive shelf sample:no_sample/zero geometry. One later passive reading:
 294 samples, age31.43ms, nativeFocusResolved=false, non_view/unmapped_item,
  isSettled=false, six measured media_card IDs, missing6/7,3840×2160 pixels.
  Current scene media_shelf/dark/regular/seed1042. No requested-focus labels used.

## Interpretation

Infrastructure and endpoint are unblocked. New action_dialog candidate is available
for a separately authorized two-button smoke; its actual focus/capture/export/intake
remains unqualified. The candidate intentionally changes dialog UIKit buttons only,
not shelf SwiftUI focus. Therefore this shelf result is an outstanding coverage gap,
**not** proof that the dialog repair failed. Producer unknown-cleanup evidence names
a different host target2BAA6307; do not import that guard onto this locally clear target.

Producer candidate request tvtestrig-20260922T164925Z-native-dialog-candidate received
and source scope/hash acknowledged. Offline benchmark request
tvtestrig-20260922T171658Z-offline-benchmark-receipt also received as metadata only;
archive transfer/current-helper parity not verified by this diagnostic. No assignment
or execution authority is inferred from either request.

Outcomes: software tests not reassessed; status/readiness/HTTP integration passed in
that limited scope; training-data eligibility blocked/unqualified; model gates not
assessed. No code changes requiring build/test. Evidence: help, status, readiness,
device, two scene snapshots and separate stderr. All diagnostic calls exit0.

Next: one authorized dialog reference+two-target smoke through capture/export/intake
and postflight. If successful, qualify that narrow family; do not claim seven-family
or6000-pair readiness. Retain shelf issue separately and continue independent NUA work.
CoreML export startup is a separate local dependency issue and is not published as
a TTR blocker. Shared publication/readback recorded in coordination.md.
