#!/usr/bin/env bash
# TASK-6a-8: generate recovery families on the iPhone 16 simulator, merge into
# dataset/dataset, then stop. Export + Run 008 are separate so a failed merge
# cannot start training on stale images.
#
# All output stays inside the package (AGENTS.md filesystem boundary).

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

UDID="${1:-50B7A5E5-3114-4525-994F-C7D547D3E5B8}"
export TMPDIR="$PROJECT_ROOT/.build/tmp"
mkdir -p "$TMPDIR" .build/xcode-dd .build/debug-output
LOG="$PROJECT_ROOT/NativeUITrainer/gen_6a8.log"

echo "TASK-6a-8 regen start $(date -u +%Y-%m-%dT%H:%M:%SZ) udid=$UDID" | tee "$LOG"

xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b

caffeinate -i xcodebuild test \
  -project GeneratorRunner/GeneratorRunner.xcodeproj \
  -scheme GeneratorRunnerTests \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath "$PROJECT_ROOT/.build/xcode-dd" \
  -resultBundlePath "$PROJECT_ROOT/.build/debug-output/gen_6a8.xcresult" \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateLoginFormImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateToolbarActionsImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateProgressActivityImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateMediaCardGridImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateAccountProfileFormImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateChromeCoverageImages \
  -only-testing:GeneratorRunnerTests/GenerateDatasetTests/testGenerateKitchenSinkImages \
  CODE_SIGNING_ALLOWED=NO \
  2>&1 | tee -a "$LOG"

if ! grep -q "TEST SUCCEEDED" "$LOG"; then
  echo "ERROR: generation tests did not succeed" | tee -a "$LOG"
  exit 1
fi

CONTAINER=$(xcrun simctl get_app_container "$UDID" com.nativeuiauditkit.generatorrunner data)
SRC="$CONTAINER/Documents/dataset"
echo "Merging from $SRC" | tee -a "$LOG"

"$PROJECT_ROOT/.venv-yolo/bin/python" "$PROJECT_ROOT/scripts/merge_generator_batch.py" \
  --source "$SRC" \
  --dest "$PROJECT_ROOT/dataset/dataset" \
  --families "LoginForm,ToolbarActions,ProgressActivity,MediaCardGrid,AccountProfileForm,ChromeCoverage,KitchenSink" \
  2>&1 | tee -a "$LOG"

echo "TASK-6a-8 regen done $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
