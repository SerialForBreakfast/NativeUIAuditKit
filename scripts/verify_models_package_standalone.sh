#!/usr/bin/env bash
# Test the actual standalone package. Keep all explicit caches inside the project.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

mkdir -p .build/standalone-tmp .build/clang-module-cache .build/swift-module-cache
export TMPDIR="$PROJECT_ROOT/.build/standalone-tmp"
export CLANG_MODULE_CACHE_PATH="$PROJECT_ROOT/.build/clang-module-cache"
export SWIFTPM_MODULECACHE_OVERRIDE="$PROJECT_ROOT/.build/swift-module-cache"

swift test --build-system native \
  --package-path NativeUIAuditKitModels \
  --scratch-path "$PROJECT_ROOT/.build/release300-models-native" \
  --disable-sandbox --jobs 2 --no-parallel \
  --cache-path "$PROJECT_ROOT/.build/swiftpm-cache" \
  --config-path "$PROJECT_ROOT/.build/swiftpm-config" \
  --security-path "$PROJECT_ROOT/.build/swiftpm-security"

# The standalone package has no network dependencies.
if rg -n '^import (Python|PythonKit|CreateML)' NativeUIAuditKitModels/Sources --glob '*.swift'; then
  echo "FAIL: forbidden host dependency"
  exit 1
fi
if rg -n '\.package\(' NativeUIAuditKitModels/Package.swift; then
  echo "FAIL: unexpected package dependency"
  exit 1
fi
echo "PASS: standalone package builds and loads all current models."
