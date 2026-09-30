# Verification

Final CLI exited0, reconciled40frames/517controls and138/315 conditional membership.
All2,132 frozen input references rechecked after output. Repeated full audit gave
identical inventory fields and identical membership; final version additionally
pins the two prior protocols. Both retain the exact453 selection IDs disjoint from
their training IDs. Original files untouched.

Authoritative gitignored local output: `final-results/`.
Earlier `results/` and `verified-results/` are superseded intermediate audit evidence.

| File | SHA256 |
|---|---|
| inventory.json | dba7aef9d42b045813573db2261b74fad9598dc34dc7543185b7f4e11365e0fb |
| membership-proposal.json | 4a4ca6f8a470d88236f9b85d2e045bf4ff550dd58717ec5dfc7d2f3bd0727b18 |
| inputs.json | ae7825311590668aafe1e129f96c2d7de345f68674be9a3418490b81b7e9e672 |

15focused tests pass (`python-tests-final.log`), offline `swift build` passes,
offline `swift test` passes123tests (14XCTest,109Swift Testing). Swift commands used
existing checkout dependencies, `--disable-automatic-resolution`, project-local
TMPDIR/module/cache/config/security paths, and scoped sandbox escalation.
`git diff --check` passes. No model was loaded, no pixels from protected challenge
were inspected, no training run was allocated, and no human annotation was changed.
