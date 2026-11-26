#!/bin/zsh
# TRAIN666 W2: run 1 routed accessibility capture (NativeOSFocusTests.testRoutedSnapshot).
# Usage: ax_capture666.sh BUNDLE SCREEN_ID [ROUTE "a|b"] [SWEEP "down:10,right:6"]
# Output: reports/work/TRAIN666/ax-capture/SCREEN_ID.xcresult (never overwritten).
set -u
ROOT="${0:A:h:h}"
UDID="${AX_UDID:-9026ECA9-77DB-4AE6-8FE6-BB239E9571FA}"
OUT="$ROOT/reports/work/TRAIN666/ax-capture"
mkdir -p "$OUT"
R="$OUT/$2.xcresult"
[ -e "$R" ] && { echo "exists: $R"; exit 2; }
TMPDIR="$ROOT/.build/native-os-focus/tmp" TEST_RUNNER_AX_BUNDLE="$1" TEST_RUNNER_AX_SCREEN="$2" \
TEST_RUNNER_AX_ROUTE="${3:-}" TEST_RUNNER_AX_SWEEP="${4:-}" TEST_RUNNER_AX_NO_RETURN="${AX_NO_RETURN:-0}" TEST_RUNNER_AX_MENU_FIRST="${AX_MENU_FIRST:-0}" TEST_RUNNER_AX_ALLOW_SELECT="${AX_ALLOW_SELECT:-}" TEST_RUNNER_AX_SECRET_FILE="${AX_SECRET_FILE:-}" \
xcodebuild test-without-building -project "$ROOT/NativeOSFocus/NativeOSFocus.xcodeproj" -scheme NativeOSFocus \
  -destination "platform=tvOS Simulator,id=$UDID" -derivedDataPath "$ROOT/.build/native-os-focus/DerivedData" \
  -only-testing:NativeOSFocusTests/NativeOSFocusTests/testRoutedSnapshot -parallel-testing-enabled NO \
  -test-timeouts-enabled YES -maximum-test-execution-time-allowance 300 -resultBundlePath "$R" CODE_SIGNING_ALLOWED=NO 2>&1 \
  | grep -E "Test Case.*(passed|failed)|error:|TEST EXECUTE"
