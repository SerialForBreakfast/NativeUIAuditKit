# IOS-ASSET-200 — native artwork grid milestone

October 5, 2026. Software and bounded native grid integration verified; full campaign
remains open. No training, detector export, promotion or Git writes.

## Delivered

- Strict generator-only artwork catalog: exact hashes, dimensions, bounded decoding,
  development role and review evidence; reject traversal, symlinks and unknown fields.
- Opt-in MediaCardGrid fit/fill rendering; original seeded defaults remain available.
- Native three-frame probe: default, fit and fill, four measured image viewports each.
- Independent validator checks membership, hashes, theme, geometry, annotation stability
  and pixel changes. Two visually reviewed assets accepted only for development rendering.
  See [review](review.md); broader asset admission remains pending.

## Evidence

Artifacts are retained locally under `artifacts/`, not intended for Git.
`swift-build.log` and `swift-test.log`: build passed; 131 Swift Testing plus14 XCTest
tests passed (145 total). Six Python probe tests passed, exit0,0.278s. Native probe02
passed in0.968s; build and test logs are `ios-build-theme-repair.log` and
`native-probe02.log`, with `probe02.xcresult` retained.

Exact target: `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`, iOS26.5.
Container resolved freshly after each test installation; no stale UUID reused.
Accepted output: `artifacts/native-probe02`; accounting: `artifacts/probe02-validation.json`.
Catalog SHA256: `bf9d4e7b82c09d6201b6ca9d9c87baa28c253906a804b42e5d3e680eb680f8de`.
Receipt SHA256: `f348469bde418eb2cc3c7cbc66dbe42a63bc2138d168e20806a883d66b753d11`.
Full seven-file seal (including sidecars): `artifacts/probe02-sha256.txt`, SHA256
`b421747be53640cf317a064bc016e2b51ba98025b8cd7e0385d78c5504982378`.
Postflight exact-target `simctl getenv ... HOME` succeeded; `git diff --check` passed.
Fit changed483177 pixels; fill676351; both have zero changes outside the four viewports.
All native element annotations match default. Native fit/fill images and source artwork
were visually reviewed. No claim of complete semantic or model qualification.

Probe01 is preserved but rejected: generic config reported dark while seeded template
rendered light. Probe02 derives capture metadata from actual template configuration;
validator now rejects the incorrect theme. Receipt alone does not seal sidecar bytes;
sidecar contents must be checked, as this trial demonstrates.

The initial default build failed on Finder metadata in an existing build product.
A fresh project-local native Swift scratch directory passed without signing repair
or removing attributes from existing files. Simulator remains available for reuse.

## Parallel coordination and remaining work

ARTWORK204 acknowledgment verifies the published request hash;256-slot catalog prepared,
GPU queued after owned work. This is not a completed artwork return. TTR local source
remains46dce7b3a79e4f17af49bc0324d4aeba3cc0958d; required550a2d374801fb99120d3aed4168c1de9e7ef83d
is absent. No checkout modifications or repeated build request.

Next substantial tranche: complete the second composition, review low-detail/busy assets,
freeze and capture the96-scene development campaign, then compare detector failures on
fixed membership. Keep artwork ancestry out of independent final evaluation. Existing
unrelated changes and iOS reconstruction evidence preserved.

Outcomes: software verified; two assets development-eligible; native grid integration
qualified only for this exact sample; model gates not assessed. Local progress does not
require an SMB publication; no new peer action introduced by this grid probe.
