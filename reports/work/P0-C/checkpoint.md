# P0-C working checkpoint — not a completed handoff

Updated 2026-09-22 UTC. Owner: NUIAK architect. User authorized reconstruction and
then explicitly chose preserving the 16,940 target through deterministic variants.

Current capture: `ios-41class-r5`; do not launch a second generator. Running command
logs to `.build/debug-output/p0c-resume/generation-r5.log`; current tool session 39754.
Locate/verify the exact owned process before any stop; never use a saved PID blindly.
Exact simulator and configuration are in `reconstruction-configuration-r5.md`.
Current app-container UUID is `88AC0AA8-2D4B-4227-A312-2412848577D9`; standard simulator
data subtree `Documents/dataset` is staging, not the final in-project corpus.
Xcode's continuation test install migrated the preflight container (formerly
`BBCF6A26-31DF-4FB3-AF3D-C092E7334AF9`). Re-resolved via exact UDID/bundle ID;
prefix is preserved. The running driver's final copy still references the old
container and will need explicit postflight finalization from the freshly resolved
container after confirming test success and status-override cleanup. Do not restart
or interrupt a healthy capture to repair that retrieval path.

Implemented: strict full-decode/schema/hash/geometry validation, BP-28 writer fix,
clipped-box intersection, native navigation/search geometry, map/date annotation
fixes, bounded decoded-pixel selection with retained rejections, expanded loading
backdrops, and configuration-bound painted status variation.

Evidence so far: eight native preflight tests; 346 independently valid preflight
pairs; 14 Python tests; 92 offline Swift tests; source/runtime pin checks.
r4 stopped at a MenuButton candidate-space exhaustion; complete evidence is preserved.
Only its 7,500 independently verified manifested images and 666 associated rejections
enter a new r5 continuation. All 103 uncommitted accepted references / 349 unfinished
rejections remain in preserved r4 evidence, not r5. The remaining 9,440 images are
being captured with corrected MenuButton contextual variation and a failure guard.
Twenty-eight first-family overlays were inspected; full review remains pending.
Use `audit_live_r5.py` for incremental checks, not the old r4 helper. Final full
validation is still mandatory. Unrelated ADR-0008/roadmap edits are preserved.

Preserve `.build/debug-output/p0c-resume/` and all P0-C report/configuration/hash/patch
files. r1/r2/r3 partial output is rejected, retained and never reused. No old
datasets, labels, symlinks or historical Run 009 reports were changed.

Remaining authorized work: wait for the owned capture to finish while checking for
failures, complete independent corpus/ledger validation, review representative final
images, execute a project-local recovery drill, record evidence and update the queue.
Do not claim model gates or start training/inference. No TTR/SMB coordination applies.
External backup remains a maintainer-owned separately authorized step.

Post-capture code-review follow-up: `ChromeCoverageConfig`'s optional-status fallback
still declares cellular value 4. The actual reconstruction always supplies an explicit
schema-valid status, so captured data is unaffected. After the frozen run finishes,
change that unused fallback to the schema's full-scale value 5, normalize its legacy
single-digit clock hour to HH:mm, and add targeted native default-value assertions.
The explicit current capture settings already meet both constraints.
Preserve the actual r5 capture source/runtime pins;
record this as a subsequent software-only correction, not a different capture build.
