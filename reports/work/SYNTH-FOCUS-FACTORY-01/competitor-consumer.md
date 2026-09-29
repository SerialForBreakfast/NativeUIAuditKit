# Competitor-v3 consumer handoff — 2026-09-29

**Superseded receipt boundary:** the archive was subsequently approved, delivered
and qualified for reviewed development. See [actual pilot handoff](repaired-pilot-handoff.md).
The blocked state below records the earlier software-only checkpoint.

| Outcome | Result |
|---|---|
| Software verified | Pass:48 Python tests, offline Swift build,123 Swift tests |
| Data eligible | Blocked: retained producer pixels not received; no new training admission |
| Integration qualified | Offline source-contract/crop integration passes; real repaired pilot unassessed |
| Model gate passed | Not assessed; no inference, training, export or promotion |

## Delivered

`harvest_sidecar_v2.py` now explicitly dispatches sidecar2/3. V3 requires
competitor_v1, a distinct observed competitor, matching recipe pairing, stable
native capture brackets, consistent eligible membership and per-state geometry.
V2 keeps neutral-reference behavior; dropping the version or pairing fields does
not upgrade/downgrade evidence. Existing hashes, freshness and image checks remain.

Independent native_image/native_button/custom styles have closed validation and
source-compatible identities. Native buttons require visible labels. Unknown
custom fields are rejected rather than silently excluded from identity.
`harvest_bundle_validation.py` and `ttr_focus_manifest.py` integrate this in the
actual intake/crop path. Derived manifests retain schemaVersion3, pairingMode,
competitorElementID and the negative frame's actual observed focus ID. Public API,
taxonomy, preprocessing, sampling and admission gates are unchanged.

## Evidence

- `competitor-tests.log`:34 tests, including7 new competitor/identity cases;
  actual CLI renders the generated bundle through production16%/256px crops.
- `competitor-harvest-tests.log`:14 existing harvest tests pass.
- `competitor-swift-build-approved.log`: offline build exit0, no warnings.
- `competitor-swift-test.log`:14 XCTest+109 Swift Testing pass.
- `identity-probe/main.swift`: compiled against the retained producer
  `FixtureAppearance.swift` from verified archive4069730b65dec563dc836fb4de5e0f51b873e86d81306326c7aafa3dd90610d9.
  Three permanent emitted vectors are embedded in `test_ttr_competitor.py`;
  extended probe covers11 cases, including fractional, tiny and signed-zero values.
- Adversarial checks: absent/wrong competitor, target==competitor, extra focus,
  altered membership/recipe/manifest identity, downgrade, invalid style/ranges;
  test-only output still fails training preflight. Legacy corruption/hash/bracket
  tests remain green. Source images and annotations were not edited.

Commands used project-local TMPDIR and caches. Python: `.venv-yolo/bin/python -m
unittest discover -s scripts -p 'test_ttr_*.py' -v` and equivalent
`test_harvest_*.py`. Swift build/test used `--disable-automatic-resolution
--cache-path .build/swiftpm-cache`. Initial nested sandbox build failed at
`sandbox_apply`; scoped host execution passed without disabling SwiftPM security.
`git diff --check` passes. Existing research/model-cycle edits were preserved.

## Remaining real-data boundary

TTR reports12 completed pairs including4competitor-v3. This is producer-reported,
not consumer-verified. Exact pending file:
`ttr-repaired-focus-pairs-20260929.tar.gz`,34778079 bytes,
SHA256 `3d6846c909b63e06bc57ef2db70b72d9211fa8f339eed0cf642b701338c6b89b`.
Producer state is project-local, not published. Maintainer explicitly approved
this34778079-byte file; approval recorded2026-09-29T06:18:38Z and published to the
owned shared packet. Exact shared path is absent. No transfer or receipt is claimed.

Resume: producer publishes immutable approved archive;
consumer verifies receipt, safely extracts into fresh ignored storage, accounts
for every pair, runs actual production crop QA and visually checks representative
native/custom/competitor examples. Retain partial/rejected evidence. Then decide
corpus eligibility and address measured rows/buttons/tabs gaps; twelve pilot pairs
are not a broad corpus or release qualification. Reuse these pixels before
considering another Simulator session. Local TTR deployment remains unchanged.

Software slice is complete for review. The real-data slice is blocked only by
approval/delivery; no helper or passing generated fixture is claimed as complete
factory qualification. No processes remain running. Human annotation is untouched.
Coordination publication/readback is recorded in `competitor-coordination.md`;
peer acknowledgment is a separate fact.
