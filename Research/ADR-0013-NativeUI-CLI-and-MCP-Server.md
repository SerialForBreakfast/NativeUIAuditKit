# ADR-0013: Model Delivery via Native CLI and Model Context Protocol (MCP)

- Date: 2026-09-30
- Status: Accepted / Active
- Scope: Model productization, developer tooling (`nativeui-audit`), and AI agent integration (MCP server).
- Relates to: [ADR-0005](ADR-0005-Native-Screenshot-Flow-And-Pedagogy-Validation.md), [NativeUIElementDetection](NativeUIElementDetection.md).

---

## 1. Context and Problem Statement

NativeUIAuditKit possesses two mature, high-performing YOLO11n CoreML models:
- **`nativeui-ios-v2.0`**: 5-class iOS model with mAP@0.5 = 0.935.
- **`nativeui-tvos-v3.0`**: tvOS model with mAP@0.5 = 0.9822.

However, neither model is currently accessible outside of isolated offline evaluation scripts (`scripts/eval_yolo_map.swift`). Developers cannot easily run scans from their terminal, CI/CD pipelines cannot gate on UI layout regressions, and AI agents (such as Claude Code, Cursor, or Antigravity) cannot use the models to inspect generated UIs without relying on expensive, slow, and hallucination-prone multimodal image tokens.

Because the models are locked in a research silo, there has been no real-world developer feedback loop to guide further model improvements.

---

## 2. Decision Drivers

- **Zero-Token AI Agent Feedback:** Allow non-multimodal and reasoning LLMs to receive structured JSON layout audits (bounding boxes, clipping, touch targets, truncation) in milliseconds without processing image pixels in context.
- **Single Source of Truth:** Prevent logic drift between command-line tools and AI agent integrations.
- **Fast Cold-Start & Zero-Daemon Overhead:** The tool should run on demand over `stdio` without requiring background daemon services or complex multi-tenant servers.
- **Actionable Self-Healing for Agents:** Error outputs must provide structured remediation hints (`nextCommand`, `fixSuggestion`) rather than raw stderr stack traces.

---

## 3. Considered Options

- **Option A (Xcode-Only Integration):** Package models strictly as internal SPM libraries consumed by XCTest suites inside Xcode projects.
- **Option B (Cloud/REST Microservice):** Host models in a Python/FastAPI web service accessed over HTTP.
- **Option C (Native CLI Binary + Thin Stdio MCP Server — Selected):** Build a standalone macOS CLI executable (`nativeui-audit`) using `ArgumentParser` and CoreML, and wrap it with a lightweight Model Context Protocol (MCP) server communicating over `stdio`.

---

## 4. Decision

We adopt **Option C: Native CLI Binary + Thin Stdio MCP Server**.

### 4.1 Architecture
1. **Core Library Target (`NativeUIDetector`):**
   - Extract the validated letterbox, `CVPixelBuffer` creation, CoreML inference, and greedy NMS logic from `scripts/eval_yolo_map.swift` into a reusable Swift target.
   - Implement `IssueClassifier` to evaluate native UI rules:
     - `tappableTargetTooSmall`: control size < 44pt equivalent.
     - `clippedElement`: control bounding box within 2px of screen edge.
     - `overlappingElements`: cross-class IoU collision > 0.3.
2. **Native CLI Target (`nativeui-audit`):**
   - Subcommand `doctor`: Verifies model presence, weights integrity, and neural engine availability; outputs JSON diagnostics with `recommendedNextCommand`.
   - Subcommand `scan <image>`: Scans a single screenshot with `--format json|table` and `--strict` (exit code 1 on defects for CI gates).
   - Subcommand `scan-batch <dir>`: Scans multiple images in a single warm-model invocation to avoid repetitive CoreML cold-load penalties.
3. **Model Context Protocol (MCP) Server:**
   - Thin stdio server exposing two primary tools:
     - `audit_doctor()`: Preflight environment check.
     - `audit_screenshot(imagePath, minConfidence)`: Executes `nativeui-audit scan --format json` and returns compact structured defect reports.
   - Future M2 extension: `audit_swiftui_view(code, matrix)` to render and audit views across device and dynamic type permutations.

---

## 5. Consequences

### Positive
- **Instant Agent Utility:** AI agents can audit UI code changes deterministically in <200ms using local Apple Silicon compute.
- **Context Preservation:** Replaces thousands of multimodal image tokens with compact ~200-token structured JSON responses.
- **CI/CD Integration:** The `nativeui-audit scan --strict` command can immediately serve as a visual linter in local pre-commit hooks and GitHub Actions.
- **Codebase Momentum:** Shifting focus to tool delivery activates the models in daily work, generating real user feedback.

### Negative / Tradeoffs
- **CoreML Cold Start:** One-off CLI calls incur a 0.5–1.0s model compilation/loading overhead. (Mitigated by adding `scan-batch` and potential persistent daemon mode for tight agent loops).
- **Maintenance Surface:** Adding CLI and MCP targets expands the surface area of `Package.swift` and requires maintaining argument parsing and documentation.
