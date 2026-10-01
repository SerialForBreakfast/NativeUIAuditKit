# ADR-0013: Model Delivery via Native CLI and Model Context Protocol (MCP)

- Date: 2026-09-30
- Status: Implemented, review-ready as LOCAL-TOOLS-02; agent registration not installed.
- Contract: [Local-first delivery](Plans/LocalFirstDelivery.md).

## Corrected context

The models are already accessible through the Swift package, not confined to eval
scripts. [NativeUIDetectionRequest](../Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift)
provides letterboxing, inference, OCR fusion, focus, audit rules and timings.
[Package.swift](../Package.swift) also has diagnostic tools. The missing product
is a convenient supported general CLI/MCP entrypoint.

Shipped benchmark results (iOS five-class mAP50 0.935; tvOS 0.9822) describe their
recorded corpora, not arbitrary-app guarantees.

## Design

- Implement `nativeui-audit doctor`, `scan` and `scan-batch` using the production
  library. Do not create a parallel detector or re-extract preprocessing/NMS.
- Doctor reports availability, actual model identity, capability limits and actionable
  errors. Presence does not prove inference or Neural Engine execution.
- Scan returns versioned boxes, OCR, focus, warnings, identities and timings,
  preserving unavailable/ambiguous states. Batch reuses a loaded session and accounts
  for every input, including failures.
- Add a thin stdio MCP wrapper with `audit_doctor` and `audit_screenshot`.
  Keep logs separate from protocol output and restrict reads to explicitly configured
  local scope. No uploads, navigation or source-edit side effects.
- Select parsing/protocol dependencies during implementation; new network installation
  is not implicit authority.

## Honest audit and performance contract

Reuse existing audit rules with their uncertainty. Screenshot pixels alone do not
establish point-scale targets or semantic clipping. Edge proximity, legitimate
nesting and ellipses are not automatically defects. Any strict exit policy must
name validated supported failure conditions; heuristics do not silently fail CI.

Structured JSON avoids requiring image inspection by the agent, but is not zero-token.
Sub-200ms latency, fixed cold-start overhead, ~200-token responses and guaranteed ANE
placement are unverified targets, not promises. Measure cold/warm load, detection,
OCR, focus and total latency on named hardware and fixed inputs.

## Acceptance and scope

Implementation and runtime checks completed; see [handoff](../reports/work/LOCAL-TOOLS-02/handoff.md)
and [usage](../Tools/NativeUIAuditCLI/README.md). Two retained screenshots verify
CLI/MCP operation, not arbitrary-app accuracy. First-process versus warmed results
are measured rather than asserting sub-200ms performance.

Implementation contract (LOCAL-TOOLS-02): one dependency-free Swift executable
target with internal types and a test target; no new public library API. Commands
use JSON by default and a thin newline-delimited stdio MCP dispatcher supporting
protocol 2025-11-25. MCP requires an explicit --root; CLI defaults to its working
directory. Canonical path and opened-file checks reject root escapes/special files.
Inputs are bounded to 50MiB/24MP, batches to 128 image files and MCP lines to 1MiB.
Sequential processing reuses a production session; no arbitrary model override.
Doctor hashes bundled resources and validates manifests without claiming load or
hardware success. Scans record loaded detector identity and actual focus receipt;
requested compute units are distinct from unknown hardware dispatch.

Strict mode fails degraded/failed processing, NOT speculative screenshot defects.
Existing audit issues remain warnings. Output includes that policy explicitly.
No screenshot scale/sidecar guess or second OCR pipeline is added. Raw OCR outside
detected controls is not exposed by the current library. Runtime smoke is limited
to the two retained test screenshots and a repeated warm case, plus MCP transport
smokes. Normal Apple CoreML runtime caches may be system-managed; explicit outputs,
logs, temp and configurable caches stay in-project. No daemon or app configuration
is installed automatically.

Protocol references: [stdio](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

Require real CLI/library wiring, positive/negative CLI and MCP tests, retained-image
smokes, complete accounting, offline package checks, usage examples and timings.
Runtime model smoke execution must be included in the assignment; mocks alone do
not establish performance. No weight, stable-taxonomy or production preprocessing
change. Autonomous control and self-healing edits are outside this interface.
