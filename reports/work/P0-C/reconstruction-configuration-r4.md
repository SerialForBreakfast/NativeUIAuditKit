# P0-C ios-41class-r4 — schema-compatible distinct reconstruction

Frozen 2026-09-22 UTC. Inherits the [r3 configuration](reconstruction-configuration-r3.md)
with these explicit corrections:

- New-only output `NativeUITrainer/reconstructed_corpora/ios-41class-r4`.
- Source identity `source-hashes-r4-20260922.txt`; no source changes after this pin
until capture ends. Same base revision, exact simulator/runtime, counts, families,
  candidate schedule and preservation policy as r3.
- Preserve schema v1.0 cellular enum `[0,1,3,5]`. Its full-scale value 5 maps to the
  painted four-bar glyph. Do not conflate that legacy scale with a literal bar count.
- Status probes emit paired sidecars using supported cellular/Wi-Fi/battery values.
  Twelve fixed-clock status cases pass independent schema/hash/dimension/geometry
  validation, in addition to 108 all-family cases. No post-test source alteration.

Evidence: six native tests passed in `r4-preflight.log`; independent report
`r4-preflight-validation-20260922.json` has zero errors for 108 family pairs and
12 validated status pairs. The fixed map fills its annotated frame on visual review.
Preflight files are retained in `.build/debug-output/p0c-resume/r4-preflight-evidence/`.

r3's 200 manifested members and incomplete remainder are rejected and preserved.
Their schema error is not repaired in place. Full r4 membership, uniqueness, coverage,
rejection accounting, restore verification and eligibility remain to be established.

The exact uncommitted generator patch is preserved as `source-patch-r4.patch`,
SHA-256 `96d095d314aa3033621dd64b04b44f17a18a6c19da8526ea98140bc5d15cba0e`.
Runtime artifact hashes are in `runtime-hashes-r4-20260922.txt`. The frozen source
hash list was rechecked after launch with no mismatch.
