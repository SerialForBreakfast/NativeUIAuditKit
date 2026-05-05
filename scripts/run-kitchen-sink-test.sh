#!/usr/bin/env bash
# run-kitchen-sink-test.sh
#
# Builds and runs KitchenSinkValidationTest on the first available booted
# iPhone simulator, then extracts the PNG attachments so you can inspect them.
#
# Usage:
#   scripts/run-kitchen-sink-test.sh [<simulator-udid>]
#
# If no UDID is supplied the script picks the first booted iPhone simulator.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT="$PROJECT_ROOT/GeneratorRunner/GeneratorRunner.xcodeproj"
XCRESULT="$PROJECT_ROOT/.build/debug-output/KitchenSinkValidation.xcresult"

# Resolve simulator UDID.
if [[ -n "${1:-}" ]]; then
    UDID="$1"
else
    UDID=$(xcrun simctl list devices booted --json \
        | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data['devices'].items():
    for d in devices:
        if d['state'] == 'Booted' and 'iPhone' in d['name']:
            print(d['udid'])
            exit()
" 2>/dev/null || true)

    if [[ -z "$UDID" ]]; then
        echo "No booted iPhone simulator found. Boot one first:" >&2
        echo "  xcrun simctl list devices available | grep iPhone" >&2
        echo "  xcrun simctl boot <UDID>" >&2
        exit 1
    fi
    echo "Using simulator: $UDID"
fi

# Clean up previous result so the extract script always sees a fresh bundle.
rm -rf "$XCRESULT"
mkdir -p "$(dirname "$XCRESULT")"

echo "Running KitchenSinkValidationTest..."
xcodebuild test \
    -project "$PROJECT" \
    -scheme "GeneratorRunnerTests" \
    -destination "platform=iOS Simulator,id=$UDID" \
    -configuration Debug \
    -only-testing "GeneratorRunnerTests/KitchenSinkValidationTest/testKitchenSinkBoundingBoxes" \
    -resultBundlePath "$XCRESULT" \
    2>&1 | grep -E "^(Test Case|error:|warning: |Build|Executed|✅|❌)" || true

echo ""
"$SCRIPT_DIR/extract-xcresult-images.sh" "$XCRESULT"
