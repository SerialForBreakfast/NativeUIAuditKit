# LOCAL-TOOLS-02 — completed for review

Owner Codex, 2026-09-30 PDT. Base 413753adc5b7607e08caf783e5535c50ce6976f1;
tranche-1 documentation changes were already present and preserved. No Git writes.

| Outcome | Evidence |
| --- | --- |
| Software | Pass: actual CLI/session and stdio MCP wiring; 8 new Swift tests and 4 real-process tests |
| Data eligibility | Not assessed: two retained test images only; no labels, splits or training admission changed |
| Integration | Pass for local binary/production CoreML/OCR/MCP transport; TTR and agent-client installation not assessed |
| Model gate | Not assessed; shipped models and thresholds unchanged, no training/export/promotion |

## Delivered / acceptance

- Package product nativeui-audit: doctor, scan, scan-batch, mcp. Internal tooling
  types only; no public library API or parallel preprocessing/inference implementation.
- Versioned JSON binds input hashes, requested settings, load-bracketed detector
  identity, production focus receipt, modality health and stage/end-to-end timings.
- Bounded canonical/opened-file root checks, special-file/oversize rejection,
  PNG/JPEG decode checks, sorted batch accounting and four-entry warm session cache.
- Strict mode rejects failed/degraded processing, not heuristic UI warnings.
- MCP initialization, notification silence, tools/list/call, ping, malformed params,
  unknown methods, tool errors, oversized lines and protocol-only stdout verified.
- Tests cover corrupt/missing files, root/symlink escape, FIFO/large inputs, empty/
  mixed/oversized batches, injected unavailable models, strict degradation and
  warning-only success. Missing model behavior is injected, not tested by damaging
  installed resources. Real bundled model loading is separately verified below.
- [Usage and limitations](../../../Tools/NativeUIAuditCLI/README.md) include CLI
  examples, MCP configuration, field/exit semantics, security scope and reproduction.

## Verification and commands

All explicit outputs/caches remained project-local. Swift used resident dependencies,
TMPDIR=$PWD/.build/debug-output, CLANG_MODULE_CACHE_PATH=$PWD/.build/clang-module-cache,
SWIFTPM_MODULECACHE_OVERRIDE=$PWD/.build/swift-module-cache. Scoped host execution
permitted normal Apple-managed CoreML caches; no service/security settings changed.

| Command | Result / evidence |
| --- | --- |
| swift build --disable-automatic-resolution | Exit0, no warnings; swift-build.log |
| swift test --disable-automatic-resolution | Exit0, 120 Swift Testing +14 XCTest passed; swift-test.log (includes all8 new tests) |
| python3 -B scripts/test_nativeui_audit_cli.py | Exit0, 4 process tests; process-tests.log |
| python3 -B scripts/nativeui_cli_smoke.py --output reports/work/LOCAL-TOOLS-02/runtime-final | Exit0; final real doctor/batch/MCP evidence and input hashes in runtime-final; batch child exit1 expected for intentional corrupt entry |
| nativeui-audit scan .../kitchen_sink_screen.png --platform iOS --no-ocr --format table | Exit0, human-readable output; table-smoke.txt |
| git diff --check | Passed |

Generated logs/JSON/images are ignored; reusable smoke/process scripts and Swift
tests are source-controlled candidates. Earlier runtime-01 is preserved, superseded
by final schema/binary evidence. No external SDK install was necessary. Protocol
was checked against official MCP 2025-11-25 stdio/lifecycle/tools specifications
linked from usage. Real-process transcript tests are not proof of every agent client.

## Measured runtime, not accuracy

Apple M4 / Mac16,10 /24GiB, macOS26.4.1. Final binary SHA256
9976d16b5a27ee48a890549b5cd49af59853cb13db24368bb95f50251c103f08.

| Retained case | Wrapper milliseconds | Result |
| --- | --- | --- |
| iOS first in process | 976.95 | 3 elements; production OCR enabled |
| Same iOS pixels, warm session | 137.87 | 3 elements; cached detector |
| tvOS first in process | 1007.32 | 25 elements; actual CoreML focus backend |
| tvOS via fresh MCP process | 290.63 | Successful structured tool result |
| Intentional corrupt batch image | 0.33 | Explicit failure; all4 entries accounted for |

OS caches were not cleared; runs are few and debug-build measurements. Wrapper
times include artifact checks/load but exclude process launch/output serialization.
Inner load timer is zero for preloaded sessions, not proof of free cold start.
No label metrics, exhaustive-candidate claim, latency SLO or model qualification.
Exact model fingerprints and actual focus receipt are in runtime-final/batch.json.

## Next / boundaries

Tranche complete; no running jobs remain. Next assign FOCUS-CORPUS-03: inventory
and coverage/split freeze before scoped native generation, automated intake and
trainer preflight. Do not repeat unchanged training. CLI can inspect existing
screenshots now; installing it into an agent configuration is a separate user choice.

Coordination not applicable: no change to TTR's producer contract or requested next
action. No share access or TTR operation. New lesson is recorded in BestPractices:
session-internal load timing and heuristic audit warnings are not qualification.
