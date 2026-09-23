# Replacement build and appearance-v1 check

Observed 2026-09-23 05:43–05:54 UTC. Read-only diagnosis; no recipe mutation,
capture, inference, training, installation, or restart.

## Local runtime

- Running TVTestRig PID 54877; matching bundled helper SHA256
  `c06623a04523c289486432fb276b09d559db6812d8e82af04486a21b6d125fcb`.
- Fixture PID 54790 on simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`;
  installed debug dylib SHA256
  `6aae0701d748437bd618735b5813eda117586e49d76926901a25db967f113457`.
  Bytes differ from the previously qualified build. Port 8080 belongs to this Fixture.
- All eight exact-target infrastructure readiness checks pass; ownership clear.
  App idle, queue zero. Fixture HTTP responds. Default scene has no native sample;
  no recipe was applied, so this alone is not a capture failure.
- Evidence: `hashes.txt`, `status.json`, `readiness.json`, `device.json`, `scene.json`.
  Infrastructure readiness is not new-build capture qualification.

## Producer delivery versus consumer acceptance

Read source revision e3d55d1 and `Docs/CLI/fixture-appearance-v1.md` in TVTestRig.
Appearance v1 supports artwork, bright_unfocused, gray_placeholder, standard layouts,
and grid dock layout. Its recipe hash adds `:appearance@1:<preset>:<layout>`;
legacy recipes without appearance retain their existing hash.

The existing NUIAK `harvest_sidecar_v2.recipe_hash` matches **0/3** published
appearance vectors. All three collapse to the same legacy hash. Correct new v2
sidecars therefore fail the existing recipe-hash check. See `hash-compatibility.json`.
Do not bypass that check. Next consumer work: closed/versioned appearance validation,
supported archetype/layout checks, canonical hash binding, retained appearance lineage,
legacy regression tests, and malformed/dropped/changed appearance rejection.

Peer APPEAR-VISUAL-20260922 reports ten completed pairs across grid-artwork,
dock-bright and media-placeholder, 48 verified exported files, 52 archive members,
and healthy postflight. These are **producer-reported results on Sillycon**, not local
intake or current installed-build qualification. The archive is not present at the
corresponding local producer path. Maintainer-mediated delivery remains pending:

- `.local-work/appearance-visual-20260922/nuiak-appearance-visual.tar.gz`
- 116122181 bytes; SHA256
  `d80f14887c399e85c738ba3705096fc4ad6d116d37a38c5ca36d872919b5764a`.
- Suggested NUIAK destination: gitignored `dataset/tvos_captures/ttr-appearance-v1-delivery/`.
  Status share carries metadata only.

Peer acknowledged `nuiak-20260923T053700Z-independent-appearance-families`
at 05:40:27Z. Artwork/bright/placeholder/dock capability is now evidenced by producer
source and its bounded trial; distinct high-contrast, Photos-like focus, and independent
challenge families remain open. Three dark/regular/seed7 recipes do not establish
independent evaluation coverage. Do not request another rebuild for the consumer gap.

## Outcomes and next action

Software verification: new contract compatibility fails 0/3 vectors; no code changed.
Data eligibility: new archive not assessed; previous catalog development intake unchanged.
Integration: local readiness passed; new appearance end-to-end intake not assessed.
Model gates: not assessed. No accuracy improvement established by this build check.

Next substantial tranche is NUIAK appearance-v1 adapter plus independent archive
intake, production crop/label review, duplicate/lineage accounting and scoped eligibility
report. Preserve all final-evaluation exclusions; do not launch training from readiness.
