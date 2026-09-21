# Office intake readiness — 2026-09-20 continuation

No producer bundle was reported. TTR acknowledged receipt only and explicitly reported
no smoke dispatch. Therefore no live intake, data eligibility or model result is asserted.

## Prepared consumer path

- Intended raw destination: new unique directory below
  `dataset/tvos_captures/office/`; read-only git check-ignore confirmed a representative
  member is excluded. No destination or placeholder bytes were created.
- First obtain producer revision/build evidence, final bundle location, member hashes,
  completion and healthy cleanup evidence, and confirm the transfer route.
- After copying, compare source hashes before deriving artifacts. The actual entrypoint
  `scripts/ingest_fixture_batch.py --input <received-bundle> --output <new-project-local-output> --dry-run`
  validates the completed bundle before parsing supported annotations. Do not use
  `--legacy-fixture-mode`; that bypass is test-only.
- Run the full planned per-member/visual inspection, not merely a CLI exit-code check.
  Preserve physical source context and keep integrity separate from training eligibility.

## Targeted physical extraction gap

Read-only source inspection found `harvest_focus_pairs.extract_fixture_bundle` calls
`build_simulator_manifest`; `simulator_focus_manifest.build` emits
`sourceKind: simulatorFixture` and simulator-use eligibility. Therefore the new
`--fixture-bundle` route must not be used unchanged to classify Office captures.
This is a specific physical-adapter/review requirement, not a claim the ordinary
completed-bundle validator is unusable. Do not relabel physical data to satisfy it.

Before accepting physical crop extraction, require a source-aware physical manifest
path with regression coverage that cannot emit simulator-only provenance for Office,
while preserving existing simulator behavior. Verify focused and unfocused frame
geometry independently. No implementation change or inference was performed here.

## Completion/blocker

Acknowledgment reconciled and continuation published/read back. Queue updated without
changing unrelated worker state. Software/data/integration/model outcomes remain
not assessed. Remaining smoke work is on the TTR host, with local authority/readiness
not yet accepted; intake additionally awaits genuine bytes and confirmed transfer.
No SSH, device commands, simulator operation, capture, training or recurring monitoring.
