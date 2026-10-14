#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT_ROOT="$PWD"
DESTINATION="$PROJECT_ROOT/.build/model-free-consumer-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$PROJECT_ROOT/.build/standalone-tmp" "$PROJECT_ROOT/.build/clang-module-cache" "$PROJECT_ROOT/.build/swift-module-cache"
mkdir "$DESTINATION"
mkdir "$DESTINATION/Sources"
cp Tests/ModelFreeConsumer/Package.swift "$DESTINATION/Package.swift"
cp -R Sources/NativeUIAuditKit "$DESTINATION/Sources/NativeUIAuditKitRuntime"
cp -R NativeUIAuditKitModels/Sources/NativeUIModelContracts "$DESTINATION/Sources/NativeUIModelContracts"
cp -R Tools/ModelFreeProbe "$DESTINATION/Sources/ModelFreeProbe"
diff -qr Sources/NativeUIAuditKit "$DESTINATION/Sources/NativeUIAuditKitRuntime"
diff -qr NativeUIAuditKitModels/Sources/NativeUIModelContracts "$DESTINATION/Sources/NativeUIModelContracts"
export TMPDIR="$PROJECT_ROOT/.build/standalone-tmp"
export CLANG_MODULE_CACHE_PATH="$PROJECT_ROOT/.build/clang-module-cache"
export SWIFTPM_MODULECACHE_OVERRIDE="$PROJECT_ROOT/.build/swift-module-cache"
swift run --package-path "$DESTINATION" --build-system native --disable-sandbox --jobs 2 \
  --cache-path "$PROJECT_ROOT/.build/swiftpm-cache" \
  --config-path "$PROJECT_ROOT/.build/swiftpm-config" \
  --security-path "$PROJECT_ROOT/.build/swiftpm-security" ModelFreeProbe
if find "$DESTINATION" \( -name '*.mlmodelc' -o -name '*.mlpackage' -o -name '*.mlmodel' \) -print | rg .; then
  echo 'FAIL: model bytes exist in the consumer'
  exit 1
fi
echo "PASS: exact runtime sources build without model files or package dependencies: $DESTINATION"
