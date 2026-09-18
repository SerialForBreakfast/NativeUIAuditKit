#!/usr/bin/env bash
# verify_models_package_standalone.sh
#
# Guards TASK-DIST-02's standalone-build guarantee for NativeUIAuditKitModels: it must build
# with zero external Python or host-tool dependencies, and zero Swift package dependencies of
# its own (NativeUIAuditKit's SPM manifest currently declares only swift-docc-plugin, and that's
# a doc-generation plugin dependency of the whole package, not of this target specifically).
#
# No CI runs in this repo (see AGENTS.md) — this is the local, repeatable substitute.
#
# Usage:
#   scripts/verify_models_package_standalone.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

FAILURES=0

echo "1. Building NativeUIAuditKitModels in isolation..."
if swift build --target NativeUIAuditKitModels; then
    echo "   OK"
else
    echo "   FAIL: target did not build standalone"
    FAILURES=$((FAILURES + 1))
fi

echo "2. Checking for forbidden imports under NativeUIAuditKitModels/Sources/..."
FORBIDDEN_PATTERN='^\s*import\s+(Python|PythonKit|CreateML)\b'
if grep -rEn "$FORBIDDEN_PATTERN" NativeUIAuditKitModels/Sources/ 2>/dev/null; then
    echo "   FAIL: forbidden host-tool import found above"
    FAILURES=$((FAILURES + 1))
else
    echo "   OK — no Python/PythonKit/CreateML imports"
fi

echo "3. Checking for non-Swift host-tool sources under NativeUIAuditKitModels/Sources/..."
STRAY_FILES=$(find NativeUIAuditKitModels/Sources -type f \( -name "*.py" -o -name "*.sh" \) 2>/dev/null || true)
if [[ -n "$STRAY_FILES" ]]; then
    echo "   FAIL: found host-tool scripts inside the package target:"
    echo "$STRAY_FILES" | sed 's/^/     /'
    FAILURES=$((FAILURES + 1))
else
    echo "   OK — Swift/resource files only"
fi

echo "4. Checking Package.swift declares no package dependencies for the NativeUIAuditKitModels target..."
# Anchored on the target's unique `path:` line (not the earlier `.library` product declaration,
# which also contains the string "NativeUIAuditKitModels") through the start of the next target.
TARGET_BLOCK=$(awk '
    /path: "NativeUIAuditKitModels\/Sources\/NativeUIAuditKitModels"/ { capture=1 }
    capture { print }
    capture && /\.target\(|\.executableTarget\(/ && !/NativeUIAuditKitModels/ { exit }
' Package.swift)
if [[ -z "$TARGET_BLOCK" ]]; then
    echo "   FAIL: could not locate the NativeUIAuditKitModels target block in Package.swift — anchor line may have changed"
    FAILURES=$((FAILURES + 1))
elif echo "$TARGET_BLOCK" | grep -q 'dependencies:'; then
    echo "   FAIL: NativeUIAuditKitModels target declares a 'dependencies:' key"
    FAILURES=$((FAILURES + 1))
else
    echo "   OK — no dependencies: key on this target"
fi

echo ""
if [[ "$FAILURES" -eq 0 ]]; then
    echo "PASS: NativeUIAuditKitModels is standalone."
    exit 0
else
    echo "FAIL: $FAILURES check(s) failed."
    exit 1
fi
