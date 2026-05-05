#!/usr/bin/env bash
# extract-xcresult-images.sh
#
# Extracts all PNG XCTAttachments from an xcresult bundle into a flat directory.
# Handles both the legacy (SQLite-based) and current (Data-blob) xcresult formats.
#
# Usage:
#   scripts/extract-xcresult-images.sh [<xcresult-path>] [<output-dir>]
#
# Defaults:
#   xcresult-path  .build/debug-output/KitchenSinkValidation.xcresult
#   output-dir     .build/debug-output/attachments
#
# After extraction the output directory is opened in Finder.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

XCRESULT="${1:-$PROJECT_ROOT/.build/debug-output/KitchenSinkValidation.xcresult}"
OUT_DIR="${2:-$PROJECT_ROOT/.build/debug-output/attachments}"
DB="$XCRESULT/database.sqlite3"

if [[ ! -d "$XCRESULT" ]]; then
    echo "error: xcresult not found: $XCRESULT" >&2
    echo "Run the kitchen-sink test first:" >&2
    echo "  scripts/run-kitchen-sink-test.sh" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"

# Build the list of "filename|payloadRefID" pairs.
# Use SQLite for the legacy xcresult format (Xcode ≤15); fall back to xcresulttool
# object-graph traversal for the current format (Xcode 16+, no database.sqlite3).
if [[ -f "$DB" ]]; then
    PAIR_LINES=$(sqlite3 "$DB" \
        "SELECT filenameOverride || '|' || xcResultKitPayloadRefId FROM Attachments WHERE uniformTypeIdentifier = 'public.png';")
else
    PAIR_LINES=$(python3 "$SCRIPT_DIR/_xcresult_attachments.py" "$XCRESULT")
fi

if [[ -z "$PAIR_LINES" ]]; then
    echo "No PNG attachments found in $XCRESULT"
    exit 0
fi

COUNT=$(echo "$PAIR_LINES" | wc -l | tr -d ' ')
echo "Extracting $COUNT PNG attachment(s) to $OUT_DIR"

while IFS='|' read -r FILENAME REF_ID; do
    [[ -z "$REF_ID" ]] && continue

    # Strip the UUID suffix Xcode appends: "foo_0_UUID.png" → "foo.png"
    CLEAN_NAME=$(echo "$FILENAME" | sed -E 's/_[0-9]+_[A-F0-9-]{36}(\.png)$/\1/I')
    [[ "$CLEAN_NAME" == *.* ]] || CLEAN_NAME="$FILENAME"

    OUT_FILE="$OUT_DIR/$CLEAN_NAME"

    xcrun xcresulttool export object --legacy \
        --path "$XCRESULT" \
        --output-path "$OUT_FILE" \
        --id "$REF_ID" \
        --type file 2>/dev/null

    SIZE=$(du -sh "$OUT_FILE" | cut -f1)
    echo "  $CLEAN_NAME  ($SIZE)"
done <<< "$PAIR_LINES"

echo "Done."
open "$OUT_DIR"
