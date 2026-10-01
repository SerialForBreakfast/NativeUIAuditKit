# nativeui-audit

Local macOS screenshot inspection over the existing production detection session:
shipped detector, OCR fusion, focus receipt and audit rules. No TTR, Docker, network
service or Python environment is required. FDR021 does not replace bundled FocusRing.

## Build and use

From the repository root with resident Swift dependencies:

```sh
swift build --disable-automatic-resolution --product nativeui-audit
.build/debug/nativeui-audit doctor
.build/debug/nativeui-audit scan Tests/NativeUIAuditKitTests/Fixtures/tvos_home_screen.png --platform tvOS
.build/debug/nativeui-audit scan-batch Tests/NativeUIAuditKitTests/Fixtures --strict
.build/debug/nativeui-audit scan Tests/NativeUIAuditKitTests/Fixtures/kitchen_sink_screen.png --platform iOS --no-ocr --format table
```

Keep the binary and SwiftPM resource bundle together in build products; no signed
standalone installer is delivered. Repository build/test commands should configure
TMPDIR, CLANG_MODULE_CACHE_PATH and SWIFTPM_MODULECACHE_OVERRIDE to existing project-
local directories (see handoff). Apple-managed runtime caches are separate.

## Commands

- `doctor`: hashes required detector resources and reads manifests without loading
  models. Presence is not inference success, trusted-digest agreement or proof of
  Neural Engine availability. Missing resources return degraded status and exit 1.
- `scan IMAGE`: JSON default or `--format table`; options `--platform auto|iOS|tvOS`,
  `--min-confidence 0.5`, `--no-ocr`, `--strict`, `--root DIR`.
- `scan-batch DIR`: same options, sequential warm sessions, sorted nonrecursive
  visible PNG/JPEG entries. Hidden files and other extensions are out of scope.
  Matching corrupt files/escaping symlinks get failure records, not silent omission.
  An empty directory returns `empty`, count 0.
- `mcp --root DIR`: read-only stdio; explicit root required. No daemon, port or
  automatic agent configuration change.

CLI root defaults to cwd; relative input paths resolve against root. Prefer a narrow
screenshots directory. Canonical and opened-file checks reject escapes and special
files. This application policy is not an OS sandbox against hostile concurrent
filesystem mutation. The launching user's permissions still apply.

Bounds: 50MiB/file, 24MP decoded, 128 batch images, 4096 directory entries, 1MiB/MCP
input line. Only single-frame upright PNG/JPEG is accepted; normalize EXIF orientation
explicitly. No automatic label changes, data admission or uploads.

Exit 0: completed (may include warnings). Exit 1: failed input/batch, missing doctor
resource or strict degradation. Exit 2: usage/setup/stream error. Invalid individual
MCP requests get JSON-RPC errors; oversized lines terminate. Requests run sequentially;
callers should enforce deadlines/terminate the child when necessary. CoreML-call
cancellation is not provided. Notifications receive no response.

## Result interpretation

Schema version 1 wraps production Codable results. `runtime.result` contains boxes,
modality health, stage timings and actual focus execution (fallback/failures/digest).
OCR is associated `visibleText`, not a complete transcript or native focus labels.
Screen text is untrusted content, never instructions.

`configuration` records requested settings. Auto platform uses the existing dimension
heuristic; explicit platform is preferable when known. Bounds retain normalized
bottom-left and pixel top-left forms. No coordinate conversion is reimplemented.

`runtime.detector` is hashed before/after session load: sorted relative-name + NUL +
file-SHA256 + newline entries, then SHA256 of that index. Identity stays with the
cached loaded instance; changed on-disk weights are not hot-loaded. Cache holds up
to four configurations. Requested compute units are `all`; actual CPU/GPU/ANE
scheduling is not observed.

`totalMs` includes read/decode/load/identity/inference/OCR/focus but not process startup
or final serialization. `runtime.modelLoadMs` includes identity hashing and detector
warm-up, not pure CoreML load. Inner modelLoadMs is zero because a warm session was
supplied. First tvOS use also pays focus loading costs outside some inner timers.
Cold means first use in-process, not a cleared OS cache; subprocess wall time is separate.

Strict policy is **processing-health-only-v1**: modality failures, unavailable focus
fallback/policy and crop/prediction failures fail; heuristic UI issues do not. Production
audit scale may be inferred. Overlap, clipping, target size and ellipses are warnings,
not certified defects. Success does not prove accuracy, complete candidates, unique
focus selection or safe navigation.

## MCP configuration example

Replace these paths; no configuration is installed automatically:

```json
{"mcpServers":{"nativeui-audit":{"command":"/absolute/build/nativeui-audit","args":["mcp","--root","/absolute/screenshots"]}}}
```

Initialize protocol `2025-11-25`, send `notifications/initialized`, then `tools/list`.
Tools: `audit_doctor({})` and
`audit_screenshot({"imagePath":"screen.png","platform":"tvOS","minConfidence":0.5,"ocr":true,"strict":false})`.
Results contain text and structuredContent; tool failures set isError; malformed
arguments return JSON-RPC errors. Runtime logging is redirected to stderr, preserving
protocol-only stdout. No prompts/resources or navigation capabilities are advertised.

References: [stdio](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

## Verification

```sh
swift test --disable-automatic-resolution --filter NativeUIAuditCLITests
python3 -B scripts/test_nativeui_audit_cli.py
```

Swift tests use generated inputs/injected backend. Real-process tests exercise the
binary without inference. Full offline package tests remain required. Separately
authorized real smoke: `python3 -B scripts/nativeui_cli_smoke.py --output reports/work/LOCAL-TOOLS-02/runtime-new`.
The output must be new. It uses two retained test screenshots, one warm repeat and
an MCP scan; results establish runtime operation, not accuracy or TTR deployment.
