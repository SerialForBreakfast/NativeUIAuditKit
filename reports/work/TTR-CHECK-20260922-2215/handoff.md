# Fixture repair follow-up — 2026-09-22 22:15 UTC

Continued the authorized repair check read-only. No recipe mutation, capture,
installation, restart, training or producer edit.

## Fresh evidence

- Producer HEAD `36671853861c7cc94326f4e89a9ad7337a012b27` updates export
  documentation/tests and acknowledges geometry/sidecar repairs as next work.
  It does not deliver either repair. Reviewed commit file list and diff.
- Fixture listener PID28018 still owns port8080; installed dylib SHA256 remains
  `9bd3859b9f71e6255bba0a3d64cfdd31cad323a67d70416826330c1414fa70f0`.
- Bounded GET `/scene` succeeds. Unlike the22:07 initial observation, native probe
  is now ready, verified and settled: sampleCount5022, sampleAge23.81ms,
  all8 media cards measured, no missing required IDs. This is passive health,
  not qualification of a new capture or the planned four-card recipe.
- Scene3840×2160 still includes `header_shelf` pixel bounds `[40,120,600,48]`
  and normalized corners `[0.0208333333,0.1111111111,0.3333333333,0.1555555556]`.
  These are inconsistent; native probe excludes that header as
  `unattached_or_hidden` while the annotation retains it. Geometry blocker persists.
- Verified smbfs mount at `sillycon.local/SharedStatusFile`. Producer22:00:22Z
  status acknowledges requests214400/214600 as next work, not completed repairs.
  Export byte transfer remains solved; no duplicate transfer needed.

## Separate resume conditions

**Direct pilot:** repaired installed Fixture geometry, source-target reconciliation
and reviewed multi-run completion implementation. This lane does **not** wait for
the TTR exported-sidecar repair. Existing read-only resume plan verifies12 recipes/
30 retained pairs and enumerates30 recipes/216 pairs remaining; it cannot execute
or admit a failed run. No unchanged recipe retry was performed.

**TTR intake:** supported versioned sidecars preserving resolved recipe and native
capture observations; test those against the strict consumer. This is separate
from direct HTTP interval evidence. Do not invent missing labels or frame identity.

Software verification: prior20 focused tests and package checks reused, no code
changed. Data eligibility: no new admission. Integration: partial, above blockers
confirmed. Model gates: not assessed. Diagnostic command wall time0.08s; no external
wait loop, capture, inference or test rerun.

Next: verify actual geometry repair before resuming missing-group work, preserving
the failed run and per-run build identities. Training and scale remain unauthorized.
