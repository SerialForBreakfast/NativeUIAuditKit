# ART191 + IOS192 — receipt/audit and independent ROI feasibility

| Outcome | Result |
|---|---|
| Software verified |6new archive-audit+4ROI tests,12existing intake tests; real audit/planner entrypoints; offline Swift build/142tests passed.|
| Data eligible |New TTR data not admitted. Existing iOS training roles unchanged; no crops generated.|
| Integration qualified |SMB transfer/USB preservation verified; extraction and producer schema semantics blocked.|
| Model gate passed |Not assessed: no capture, training, inference, export or promotion.|

Pre-existing190edits preserved. Source base33bfddd; no Git writes or producer edits.

## TTR update and bounded intake

Fresh peer status23:19:24Z reports qualified-artwork handoff, not native24source
publication. Local TTR still46dce7b; new source-review HEAD3e9e05d496a5904c15d6d6dc41714ce92fd512ab
is absent (`git cat-file -t` exit128), with producer uncommitted files reported.
No running-app identity or fresh runtime capability inferred from that status.

Received `tvtestrig-20261005-qualified-artwork-feedback.tar.gz`,849392816bytes,
SHA256 `4dd9c8459958aedf36526c0699703585a4c874c1e1343abc40cae84cb40fe9ce`.
Existing shared_transfer receive CLI exits0, exact immutable local copy verified.
Receipt published/read back at `nuiak/responses/nuiak-art191-receipt.yaml`.
Sender alone owns exact shared-copy cleanup; acknowledgment/cleanup pending.

Strict existing extraction preflight rejects `archive_size_limit`. Read-only bounded
header audit reveals943entries:543regular files,245hardlinks,155directories.
The claimed788members count reconciles as non-directories, not a missing-files issue.
`assets/asset-library.json` is36190870bytes, exceeding32MiB; all245hardlinks also
violate the extraction policy. No extraction, hardlink following or code execution.

The new audit hashes regular data streams without materializing incoming paths.
542manifest-listed regular files match sizes/hashes; manifest itself is protected
by whole-archive hash.245hardlinked entries remain unresolved. All28selection
sidecars are regular and hash-linked:15pilot_review_accepted,5retained_geometry_calibration,
5superseded_render_review,3superseded_baseline_geometry. These remain producer review
decisions; no consumer semantic/visual/label admission. Eight compatibility vectors
are available as metadata, not executed mutation instructions. Canonical source
hash/callback/hydration behavior still requires exact matching producer source.

Audit seal `f236f2fec7cb3b49d302c29477277c94bfc721054429c5ca076cae38e98f063e`,
2.872s. Initial audit used an incorrect expected producer disposition name and
failed closed; corrected to actual `retained_geometry_calibration`, no data admitted.
No candidate or model metric produced. Current validator is not weakened to admit4.

## Storage and recovery

Verified USB/APFS `/dev/disk7s1`, volumeUUID FD8D8E36-FAAC-4205-87ED-86134C3582B1.
Original archive copied and both hashes reverified at:
`/Volumes/training-drive/data/NUIAK/archive/ART-INTAKE-191-20261005/feedback.tar.gz`.
Removed only the untracked, hash-identical local archive after verification,
reclaiming849392816bytes. Compact transaction/audit/USB/reclamation receipts remain
in local ignored `artifacts/`. No corpus, models, environments or extracted data moved.
Restore: verify USB archive against hash above, copy exclusively to
`reports/work/ART-INTAKE-191/artifacts/feedback.tar.gz` before replaying the audit.
Never overwrite another file. USB archive is preservation, not redundant backup;
producer originals remain its responsibility. No automatic registry mapping/symlink.

Owned ART-INTAKE-191 status published/read back23:31:16Z; unrelated YAML content
preserved, checksum excluding owned packet:
`70d4cb98ef740df8b4fee46fb011b85f2b79a2d0373a9a1da051d12328302289`.
Requested minimal regular-file-only consumer subset from retained data, without the
unnecessary generation library/redundant review rasters, plus exact source through
maintainer Git. No recapture, binary handoff or source-patch execution. This clears
transfer uncertainty but not the concrete packaging/source dependencies.

## Independent iOS192 outcome

216admitted training-fit images only,72perplacement. Fixed square window half image
width centered on training truth and clamped inside image. No evaluation truth used.

| Representation |Median target-box height|Below8pixels|
|---|---:|---:|
| Full640 |5.75872|162/216|
| Full1280 |11.51744|0/216|
| ROI640 |24.97140|0/216|

All216targets fit; every window clips at least one other annotation. This is box
support, not glyph-pixel quality or model accuracy. The truth-centered view is a
training representation upper bound; deployed missing/wrong proposals remain unsolved.
No pixels generated or source labels changed. Feasibility seal
`3aa5c622384219fc89a2fa1eca9a3934f9a6b9cfc45b8baae9df42aba00f1d08`,339075bytes.
193nowdefines all-class crop/jitter qualification and non-oracle evaluation planning
before a single candidate. No automatic matching/window/epoch search.

## Verification and completion

New entrypoints `scripts/artifact191.py`, `scripts/roi192.py` exit0. Focused suites
test_artifact191(6),test_roi192(4),test_synth05_intake(12) pass. One initial wrong
test filename discovered zero tests/exit5; not counted as verification, corrected
to real existing12test suite. Offline Swift build43.79s;142tests pass via known
host-access context, no dependency downloads or test modifications. Logs
`.build/art191-{build,test}.log`. Filesystem permission escalation used only for
volume identity, USB archive and known native test access. No runtime/capture waits.

Tranche complete for review: safe receipt/metadata audit and independent representation
feasibility delivered. New semantic intake/scoring concretely blocked on packaging
and exact source; no valid independent alternative can manufacture that evidence.
Next substantial tranche: IOS193qualified crop/annotation+proposal pipeline locally;
in parallel source-pinned schema4/native24 intake and matched transition evaluation
when TTR/maintainer deliver the existing requirements. Preserve all model gates.
