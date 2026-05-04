#!/bin/bash
# run_spike.sh — Execute CoordSpikeHostedTests on both target simulators.
#
# Runs the Phase 1 coordinate spike on:
#   @3x: iPhone 17 Pro (iOS 26.4)
#   @2x: iPhone SE 3rd gen (iOS 17.5)
#
# Results are written to /tmp/spike_3x.xcresult and /tmp/spike_2x.xcresult.
# JSON attachments from each test method are stored inside the xcresult bundles.
#
# Usage (from repo root):
#   bash CoordinateSpike/Scripts/run_spike.sh
#
# To run a single test:
#   bash CoordinateSpike/Scripts/run_spike.sh testGeometryReaderAlignment

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../CoordSpikeRunner" && pwd)"
PROJECT="$PROJECT_DIR/CoordSpikeRunner.xcodeproj"
SCHEME="CoordSpikeRunner"

# Device UDIDs (update if you recreate simulators).
UDID_3X="812EDC32-DB8D-49D6-B130-2279180CCDEB"  # iPhone 17 Pro  @3x iOS 26.4
UDID_2X="1A331965-FAA7-477E-A1D1-51B2868D6A88"  # iPhone SE (3rd gen) @2x iOS 17.5

RESULT_3X="/tmp/spike_3x.xcresult"
RESULT_2X="/tmp/spike_2x.xcresult"

rm -rf "$RESULT_3X" "$RESULT_2X"

ONLY_TESTING=""
if [ -n "$1" ]; then
    ONLY_TESTING="-only-testing CoordSpikeHostedTests/CoordSpikeHostedTests/$1"
fi

echo "Running CoordSpikeHostedTests on iPhone 17 Pro (@3x)..."
xcodebuild test \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -destination "platform=iOS Simulator,id=$UDID_3X" \
    -resultBundlePath "$RESULT_3X" \
    $ONLY_TESTING \
    | grep -E "Test Case|error:|passed|failed|CoordSpike"

echo ""
echo "Running CoordSpikeHostedTests on iPhone SE 3rd gen (@2x)..."
xcodebuild test \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -destination "platform=iOS Simulator,id=$UDID_2X" \
    -resultBundlePath "$RESULT_2X" \
    $ONLY_TESTING \
    | grep -E "Test Case|error:|passed|failed|CoordSpike"

echo ""
echo "Results:"
echo "  @3x: $RESULT_3X"
echo "  @2x: $RESULT_2X"
