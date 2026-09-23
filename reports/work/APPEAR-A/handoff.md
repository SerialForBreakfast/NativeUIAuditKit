# APPEAR-A source capability audit — offline slice

2026-09-23. No live process query, simulator operation, capture, training or producer
edit. Producer source pin46dce7b3a79e4f17af49bc0324d4aeba3cc0958d; checkout clean at
inspection. Installed app/helper/Fixture identity has NOT been requalified.

| Requested visual axis | Source finding | Qualification |
|---|---|---|
| Light/dark native buttons | ProceduralSceneView:189 selects light vs dark; Dialog:888 and Hero:1142 use prominent/bordered UIKit configurations | Existing baseline reviewed; new layouts still need pixel qualification |
| Media-card artwork | NativeMediaCardView:952–1002 fixes blue-purple gradient and system film icon | Gradient cards supported; Home artwork diversity missing on this route |
| Bright unfocused grid controls | ProceduralGridCell:1068 uses borderedProminent buttons | Existing crops reviewed; not Home tiles |
| Gray/blank artwork placeholders | No placeholder/artwork recipe field or native media/grid renderer branch found | Missing in inspected procedural route |
| Dock/grid context | GridMatrix builder:298 lays out a matrix; no dock appearance switch | Grid supported; dock missing on this route |
| Focus enlargement | Media didUpdateFocus:1035 applies1.05 scale and white border; native probe records measured geometry | Source-supported; not physical parallax/shader evidence |
| Density | Media/Grid renderers:255–302 consume density; dialog/hero spacing is fixed | Use compact/spacious only for media/grid |
| High contrast | `preferredColorScheme` maps every non-light theme to dark; no separate high-contrast branch in this view | Do not count named theme as a distinct rendered contrast treatment |
| Randomization pack | Builder:201–226 copies badgeCount/usesGradient/fontWeight; these names absent from ProceduralSceneView | Descriptor metadata exists, relevant rendering consumption absent |
| Intentional clipping | Prior maze goal clipping remains a diagnostic exclusion | Do not use clipping defect as approved visual training coverage |
| Native Home labels | Native intake supports home/root but prior Home probes failed tile-level observed-focus binding | No freshly established training capability; requested focus is not truth |
| Native Photos labels | Native intake CLI screen allowlist excludes Photos | No admitted native Photos path today |

Paths above are under TVTestRig/TVTestRigFixture (Views or Models), inspected
read-only. Source-backed claims are scoped to the procedural route, not a claim
that no other future producer feature could implement the appearance.

## Reproducible source references

- Models/FixtureRecipe.swift:
  `6b7eaa81084f27440a2af1ef9b418e8df147a87fadad96d92d9b6e55d7b8ed77`
- Models/DomainRandomizationPack.swift:
  `a690642fcee539d669124d6a4090261f66bdd014dc5203896571031de1473a40`
- Models/ProceduralSceneBuilder.swift:
  `454e42b0e0430ad228cdfbab250f2cd65cd6b424ce40bdf6769b92ecf058992a`
- Views/ProceduralSceneView.swift:
  `292b8f16519f844f5cdeb2b340ce2db46edf55352e9a4a8cb2d5ad369c48393c`

The recipe/builder hashes still match NUIAK's frozen expected-target adapter.
That does not make its catalog extensible: direct_tvos_capture.validate_catalog
accepts only the old42 recipes or its one-dialog smoke. `expected_targets` also
hardcodes old element counts. Do not pass arbitrary producer-valid recipes and
assume capture/admission is ready.

## Frozen provisional pilot

`pilot-proposal.json`:24 development groups, seeds101/211, light/dark. Media shelf
and grid use compact/spacious; dialog/hero retain regular. Counts stay2 dialog/4
others to match source-backed target planning. Expected76 target pairs and100
screenshots (24 reference +76 focus), before duplicate/coverage rejection:
media32, grid28, dialog8, hero8. Grid seed101 has3 enabled targets;211 has4.
No randomization pack or high-contrast visual claim. All groups stay development;
new seeds do not establish independent evaluation. The proposal does NOT fill the
Home-artwork/dock gap and should not be sold as doing so.

Validation executed offline with existing `expected_targets` and `validate_catalog`:
24 recipes/76 targets; changed-catalog test correctly returns `unsupported_catalog`.
ExecutionAllowed=false. No executable catalog was forged, no source whitelist
weakened. Exact target is provisional; endpoint remains null pending fresh identity
and operation authority. Bounds5s HTTP/10s settling/120s per recipe; stop on failure.

## Next local implementation: APPEAR-A1

Extend existing catalog/planning and consumer audit contracts with a versioned,
explicit allowlist for exactly this small pilot; preserve historical catalog behavior
and receipt validation. Pin recipe/builder source hashes and compute every enabled
target deterministically. Do not generalize counts beyond reviewed source rules.
Plan mode must perform no simulator request or mutation; reject altered catalog,
unsupported counts/axes, stale source pins, unsafe output and missing target/endpoint
before execute. Keep per-recipe identity and partial output, source truth and immutable
development membership. Update corresponding validators rather than forging a
42-recipe completed set. Test both actual planning and intake entrypoints plus
required offline checks. No capture included in this software assignment.

After that software tranche, obtain explicit simulator scope for the pilot. This
may expand density/context diagnostics without TTR desktop capture; meaningful
artwork diversity still needs the bounded renderer request below or another
separately qualified source. APPEAR-B remains pending independent new ground truth.

## Coordination and outcomes

Verified mounted endpoint sillycon.local/SharedStatusFile; local/shared guides match.
Published/read back `nuiak/status.yaml`, packet APPEAR-A, request
`nuiak-20260923T035423Z-appearance-rendering-evidence`. It refines existing
`nuiak-20260922T190731Z-fixture-bounded-style-recipes`, not a duplicate project.
Requests actual bounded rendering presets and observability, not a capture rewrite.
Peer acknowledgment not established. Other packets/top-level summary retained;
their stale runtime claims were not renewed. No reservation or permission inferred.

Software: source audit/planning checks complete, implementation extension not done.
Data: no new eligible images. Integration: runtime not assessed. Model gates: not
assessed. This closes the assigned offline audit slice, NOT the whole APPEAR-A pilot.
Only documentation/proposal/status metadata changed; no Swift build required.
Fixture and worker skills kept source support, pixel evidence and operation authority
separate; shared-status skill limited publication to the concrete producer gap.
