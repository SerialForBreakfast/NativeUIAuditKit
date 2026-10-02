# FOCUS-INTAKE-13: intake and scene corroboration

Assigned October 1, 2026. Owner: Codex. Preserve all prior experiments.

Receive the exact verified25 r2 archive named in Tasks.md using the existing
bounded receiver. Verify manifest members, native geometry and production crops;
inspect the producer coverage proposal against observed transfer failures. Keep
calibration ancestry and separate human review/data-use decisions from integrity.

Diagnostic hypothesis: requiring one gaining and one losing persistent control,
with complete candidate coverage, rejects isolated content-only changes. It cannot
prove focus if two content changes imitate a switch. Test this limitation explicitly.
Reuse frozen Alignment12 outputs, without threshold tuning or truth-based selection;
report correct/wrong/abstained frame directions and candidate completeness separately.
Add an opt-in JSON CLI consuming attributed per-control diagnostic results, never
granting control authority. Unknown coverage/identity and removed controls abstain.
Compare a permissive candidate arm (unknown unchanged-background controls remain
explicitly unresolved) against a strict arm requiring every background control
resolved. Neither arm treats opposing changes as causal proof. Persist a whole-scene
pixel counterexample through both actual CLIs, not merely mocked decisions.

Budget: CPU-only retained analysis and native crop QA, no encoding/training,
at most 2 GiB new outputs. No device work, downloads, export or promotion.
Tests include missing identity, duplicate IDs, multiple gains/losses, no-op,
single and paired content confounds, strict malformed input and actual CLI calls.
Run focused tests and offline Swift build/test before handoff.
