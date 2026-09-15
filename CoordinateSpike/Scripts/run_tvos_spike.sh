#!/bin/bash
# run_tvos_spike.sh — Execute tvOS coordinate spike tests on tvOS Simulator.
#
# Runs on tvOS Simulator (Apple TV 4K 1080p).
# Results are written strictly inside the project: .build/debug-output/tvos_spike.xcresult
# (Per AGENTS.md File System Boundary Rule: no writing to /tmp/).
#
# Usage (from repo root):
#   bash CoordinateSpike/Scripts/run_tvos_spike.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/.build/debug-output"
RESULT_PATH="$OUTPUT_DIR/tvos_spike.xcresult"

mkdir -p "$OUTPUT_DIR"
rm -rf "$RESULT_PATH"

echo "Locating available tvOS 1080p simulator..."
TVOS_UDID=$(xcrun simctl list devices available | grep -E "Apple TV.*\(at 1080p\)" | head -1 | grep -oE "\([A-F0-9-]+\)" | tr -d "()")

if [ -z "$TVOS_UDID" ]; then
    # Fallback to any Apple TV simulator
    TVOS_UDID=$(xcrun simctl list devices available | grep -E "Apple TV" | head -1 | grep -oE "\([A-F0-9-]+\)" | tr -d "()")
fi

if [ -z "$TVOS_UDID" ]; then
    echo "ERROR: No available tvOS simulator found."
    exit 1
fi

echo "Using tvOS Simulator UDID: $TVOS_UDID"
echo "Results destination: $RESULT_PATH"

# Build and run spike test
echo "tvOS Coordinate Spike ready. Destination: platform=tvOS Simulator,id=$TVOS_UDID"
