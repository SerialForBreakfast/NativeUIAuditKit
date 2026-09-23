# Repaired source versus installed Fixture — 2026-09-23 00:22 UTC

Scope: continue authorized pilot if the repaired runtime is available. Read-only
source/runtime/candidate inspection; no mutation, installation, signing or capture.

## Findings

- Producer HEAD now `60936636cba3e71e203ee6988dfccad24401a875`, observed-focus
  admission and sidecar v2. Source review confirms Fixture publishes only measured
  elements and explicitly excludes unrendered design headers. Host retains resolved
  recipes and capture brackets; it rejects coordinate disagreement instead of
  rebasing boxes. Producer handoff describes offline tests, not live qualification.
- Running Fixture PID28018 still owns8080 on the authorized simulator
  `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`. Its dylib remains
  `9bd3859b9f71e6255bba0a3d64cfdd31cad323a67d70416826330c1414fa70f0`.
  Bounded `/scene` GET still returns the mixed-coordinate `header_shelf` in a
  3840×2160 scene. No unchanged capture retry.
- Existing repaired candidate:
  `TVTestRig/.local-work/nuiak-admission-2026-09-22/fixture-signed/DerivedData/Build/Products/Debug-appletvsimulator/TVTestRigFixture.app`.
  Executable SHA256 `021420354b9dd2e11572ed032a03adb2b343af5cc77ec739d9b8116da4d7b128`;
  dylib SHA256 `46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095`.
  Signature metadata is ad hoc, TeamIdentifier not set. Local
  `codesign --verify --deep --strict` **fails**: resource fork/Finder information or
  similar detritus not allowed. The separate `codesign -dv` metadata read succeeds;
  its success is not signature verification. Producer had reported a successful
  ad-hoc build; that is not current artifact validity.
- Shared-status mount and path are absent at this check. No local lookalike created.
  Prior update delivery remains unverified; current feedback is unpublished.

## Outcome and exact next action

Software: existing NUA continuation tests remain passed; producer repair is
source-inspected only. Data eligibility: no change. Integration: blocked on a valid
repaired installed Fixture. Model gates: not assessed.

Need explicit setup authority to stage a separate project-local candidate copy,
remove only signature-prohibited filesystem metadata from that copy, verify the
existing signature without re-signing, and install/relaunch only the named Fixture
on the exact simulator if verification passes. Preserve producer originals and
existing evidence; no host-app replacement, certificate/Keychain changes, blanket
xattr clearing, Simulator restart or permission weakening. If verification still
fails, return the exact failure to the producer, not a signing workaround.

After valid installation and fresh ownership/endpoint checks, record the repair
review and execute the already-authorized one-recipe media boundary, then remaining
pilot, full assembly/visual review and shipped-model baseline. TTR host signing and
sidecar-v2 consumer work remain independent of the direct lane.

The producer's historical-bundle suggestion to exclude headers does not authorize
rewriting old NUA evidence. Original failed receipts/bytes remain unchanged.
