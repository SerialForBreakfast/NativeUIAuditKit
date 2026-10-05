# NUMERICAL-REPLAY-143 — coefficient-filtering cause isolated

One DTM042 solve completed on the same 993 constraints and unchanged objective.
Only primal/dual/IPM tolerances changed from1e-8 to1e-10. Reused entrypoint, with
strict mode and rejected-vector/residual retention; preserved DTM041 source as
`reports/work/CONDITIONED-FEASIBILITY-142/artifacts/ready/conditioned142-source.py`
(SHA256 d063bcbbd72752adbc693f16db02bfd7e4fa3151aec782f13fc372d52fcaad58).

## Result and cause

PID35090, 33 iterations,3.995358seconds solve, status0. Original violation
2.8524338688384887e-5 remains above1e-6: no accepted witness/checkpoint and no actual
runtime evaluation. Finite candidate retained as diagnostic numbers, not weights
approved for deployment, in the sealed result. No extra fit or retry.

Read-only matrix reconstruction using source-bound inputs:

- HiGHS resident `HighsOptions().small_matrix_value` =1e-9.
- 2,234 of942,188nonzero scaled coefficients are at or below that threshold.
- Only row990 exceeds1e-6; this is native index7, a reviewed screen transition.
- Dropped entries contribute2.8524338473342297e-5 at that row.
- Truncated row residual3.0675e-13; whole truncated maximum1.1948469458e-12.
- Original long-double maximum2.8524339314e-5: dot-product precision does not explain it.

This reproduces the numerical discrepancy. Do not infer an incorrect label, lack
of model capacity, or a need for more TTR capture from this solver behavior.

## Verification and scope

Executed `scripts/conditioned142.py --strict --ready reports/work/NUMERICAL-REPLAY-143/artifacts/ready`
with resident Python, project-local TMPDIR, bytecode disabled and two BLAS threads.
Terminal result: `NativeUITrainer/focus_ring_runs/numerical143-dtm042/result.json`.
Protocol SHA256 cfe308685ca7ca5e33abab2c11c51e21dae4da78261d365f0132535e65c43de7.
41 focused Python tests pass in0.576s, including strict option forwarding, rejected
finite vector retention and independent residual rejection despite success status.
Offline Swift build and serial tests pass:14XCTest+128SwiftTesting checks. Logs
`.build/numerical143-{build,test}.log`; established project-local caches and scoped
native-test host permission. Prior source changes and shipped artifacts preserved.

Software verified; data eligible only for this exposed diagnostic; live integration
not assessed; model/witness gate failed. Model-workflow skill preserves these
separate outcomes. No export, promotion, new data, capture, Git write or download.

## Coordination and next substantial outcome

TTR snapshot unchanged18:46:20Z/expired19:46:20Z. Worker141 still reports PyTorch
absent, no training. No new request/status noise: the local numerical diagnosis
does not change peer work. Environment provisioning still needs maintainer authority.

Next: one coefficient-preserving comparison with explicit solver configuration and
regression coverage; verify original residuals, actual float32 head/checkpoint replay
and all original/native/nuisance cases. Only those results determine whether to
change optimization or representation. Preserve failed gates rather than keep
adjusting tolerances. Separately resume worker smoke when environment is authorized.
