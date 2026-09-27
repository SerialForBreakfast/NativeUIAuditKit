# Photos pilot — preparation delivered; live session pending

2026-09-27 · PHOTOS-PILOT-01 · current NUIAK worker · base63d2ff4.

| Outcome | Status and evidence |
| --- | --- |
| Software verified | Pass: real import/review CLI, strict human-review binding, production crop integration,96 Python tests and offline Swift build/123 tests. |
| Data eligible | Not assessed for real Photos: zero live frames/pairs captured. Generated test evidence is diagnostic-only and rejected by training/evaluation admission. |
| Integration qualified | Offline software path passed; installed Office TTR capture/export/target/ownership integration not run. |
| Model gate passed | Not assessed: no Photos model comparison, training, export or promotion. Existing gates unchanged. |

## Delivered

- [CLI and formats](cli-contract.md): separate versioned diagnostic importer/reviewer,
  raw hash-preserved TTR files, numbered full-frame review sheets, per-frame boxes,
  explicit human confirmation, paired production crops and complete dispositions.
- [Operator checklist](operator-checklist.md): you control Photos; maximum60minutes
  supervised/45minutes capture, first-two-pair smoke,20attempt cap/three screen states,
  ownership/stop/cleanup and cross-host receipt boundaries.
- [Capability matrix](capabilities.md): source-backed interfaces separated from
  live verification and absent/unknown capability. Native Photos telemetry remains
  unestablished; TTR focus predictions are not labels.
- [Verification](verification.md): real subprocess integration plus positive,
  adversarial and preserved legacy behavior. Generated full-frame/paired sheets
  retained for software QA, not substituted for the planned Photos data.

Implementation: `scripts/photos_focus_pilot.py` and `scripts/test_photos_focus_pilot.py`.
Research contract and task/current-state/catalog updates accompany the code. The
worker/TTR/model guidance kept diagnostics separate from native truth and prevented
a runtime absence from becoming unauthorized app launch, navigation or training.
BP-101 records the discovered raw-metadata filename collision and tested fix.

## Acceptance boundary

| Assigned criterion | Result |
| --- | --- |
| Installed runtime/capability check | Safe host/process/filesystem checks completed; exact Office installation is unresolved. No runtime qualification claim. |
| Local importer, human review and production crops | Implemented, real CLI/helper tests pass; unknown/invalid examples remain blocked. |
| Preserve originals, count all frames/pairs and duplicates | Tested; input hashes unchanged, safe namespaces, sealed output and explicit partial failure accounting. |
| Reject diagnostic data from training/evaluation | Existing validators and actual trainer preflight reject it; no policy changes. |
| Supervised Office session and first-two-pair smoke | Pending: no known running TTR host/helper, no verified exclusive Office session, and no confirmed maintainer availability. |
| Genuine Photos annotations/crops/next coverage decision | Blocked on that session. No human review invented. Existing source independence work does not block this pilot. |
| Local documentation/status and shared coordination | Updated locally; shared update unpublished because SMB is unmounted. |

## Exact next action

Identify the Mac actually running TTR, its matching helper and Office target; agree
the supervised window with the maintainer. Verify current exclusive readiness and
outputs there before capture. If remote, use the established metadata/receipt
workflow—not SSH or new services. Do not restart or replace an occupied app.

Then conduct the two-pair smoke using the checklist, review the genuine images with
the maintainer and continue toward10 nonduplicate pairs only if it passes. The user
drives every input. If capture works but native labels remain unavailable, finish
the selected human-reviewed diagnostic pilot and propose a separately scoped
human-label admission lane; do not automatically request a native provider rebuild.

All independent local preparation is complete. The full assigned pilot remains
incomplete only at its explicitly supervised/runtime-dependent boundary. No process
is left running and no automatic monitoring or future capture is scheduled.
