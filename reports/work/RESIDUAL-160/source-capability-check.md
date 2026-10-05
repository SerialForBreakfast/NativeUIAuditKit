# Same-focus appearance capability check — 2026-10-05

Later peer evidence: TTR's03:33:01Z status acknowledges seeded artwork replacement
plus native moves/no-ops as supported; dark/light table/rich-table next batch planned.
This supersedes any inference that this older local source inventory blocks all
appearance collection. Runtime/label binding and genuine returned data remain pending.
NUIAK response `nuiak-20261005-residual160-supported-artwork` published/read back;
no arbitrary contrast-control feature is required. Inspection findings below remain
specific to the recorded bytes.

Read-only inspection of the local TVTestRig checkout at HEAD
`46dce7b3a79e4f17af49bc0324d4aeba3cc0958d`. The checkout is dirty; these file
hashes identify inspected bytes, not a shipped build or the peer's newest source.
No device, app, capture or HTTP mutation was performed.

Inspected files under `TVTestRig/TVTestRigFixture/`:

| File | SHA-256 |
| --- | --- |
| Telemetry/FixtureTelemetryServer.swift | c595ed62a98321a36bd119767c1d2f1d4132924236331a01e008b336e9ab0f10 |
| Coordinators/FixtureCoordinator.swift | a9a7e0b3566b9b8e4d64150ac16f2290b3e5291115fdddaeade4d34d0d6251f7 |
| Models/FixtureRecipe.swift | 6b7eaa81084f27440a2af1ef9b418e8df147a87fadad96d92d9b6e55d7b8ed77 |

The complete HTTP route switch supports state/scene/timeline/device queries,
recipe loading, focus set/next, reset and harvest challenge/identity. It exposes
no separate in-place appearance mutation. Theme is part of the recipe hash.
`updateProceduralScene` invalidates native observations, rebuilds scene descriptors,
reloads the focus sweep and clears requestedFocusID. Source therefore does not
establish preservation of native focus across a recipe/theme change.

This does not prove the latest peer build lacks the capability. Nor does it prove
that recipe reload necessarily moves focus. It means reload alone cannot label a
pair unchanged, and a reused element ID is insufficient without scene correspondence
and fresh observed focus/geometry. Endpoint equality also does not prove no interim
focus movement; any future dataset must define endpoint versus interval semantics.

Decision: retain the existing request `nuiak-20261004-residual160-native-appearance`;
do not fabricate appearance negatives, repeat a capture with unchanged capability,
or modify producer source. Resume native planning when TTR identifies a supported
control with preserved element correspondence and fresh observation brackets, or
provides qualified captured evidence under that request. Local iOS comparison and
Big Dog's counterfactual robustness campaign proceed independently.

Verification: source inspection only. Runtime integration and new data eligibility
not assessed; model gates unchanged. No code changes or new build/test required.
