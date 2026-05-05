#!/usr/bin/env python3
"""
_xcresult_attachments.py — internal helper for extract-xcresult-images.sh

Usage:
    python3 scripts/_xcresult_attachments.py <xcresult-path>

Prints one "filename|payloadRefID" line per PNG attachment found in the
xcresult bundle, using xcresulttool to traverse the object graph.
Works with both the legacy (Xcode ≤15) and current (Xcode 16+) xcresult formats.
"""

import json
import subprocess
import sys
import os


def xcresulttool_get(xcresult: str, ref_id: str | None = None) -> dict:
    cmd = ["xcrun", "xcresulttool", "get", "--legacy",
           "--path", xcresult, "--format", "json"]
    if ref_id:
        cmd += ["--id", ref_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def find_first(obj, type_name: str, key: str) -> str:
    """Return the first _value found at obj[type_name][key] in the tree."""
    if isinstance(obj, dict):
        if obj.get("_type", {}).get("_name") == type_name:
            return obj.get(key, {}).get("id", {}).get("_value", "")
        for v in obj.values():
            r = find_first(v, type_name, key)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_first(v, type_name, key)
            if r:
                return r
    return ""


def find_all_values(obj, type_name: str, key: str) -> list[str]:
    """Return every _value found at nodes of type_name[key]."""
    results = []
    if isinstance(obj, dict):
        if obj.get("_type", {}).get("_name") == type_name:
            v = obj.get(key, {}).get("id", {}).get("_value", "")
            if v:
                results.append(v)
        for v in obj.values():
            results.extend(find_all_values(v, type_name, key))
    elif isinstance(obj, list):
        for v in obj:
            results.extend(find_all_values(v, type_name, key))
    return results


def find_attachments(obj) -> list[tuple[str, str]]:
    """Return (name, payloadRefID) for every ActionTestAttachment with a PNG name."""
    results = []
    if isinstance(obj, dict):
        if obj.get("_type", {}).get("_name") == "ActionTestAttachment":
            name = obj.get("name", {}).get("_value", "")
            ref  = obj.get("payloadRef", {}).get("id", {}).get("_value", "")
            if name and ref and name.lower().endswith(".png"):
                results.append((name, ref))
        for v in obj.values():
            results.extend(find_attachments(v))
    elif isinstance(obj, list):
        for v in obj:
            results.extend(find_attachments(v))
    return results


def main():
    if len(sys.argv) < 2:
        print("usage: _xcresult_attachments.py <xcresult-path>", file=sys.stderr)
        sys.exit(1)

    xcresult = sys.argv[1]

    root = xcresulttool_get(xcresult)
    if not root:
        sys.exit(0)

    # Navigate: root → ActionRecord.actionResult.testsRef → test summaries
    tests_ref = find_first(root, "ActionRecord", "testsRef")
    if not tests_ref:
        # Try older schema key name
        tests_ref = find_first(root, "ActionResult", "testsRef")
    if not tests_ref:
        sys.exit(0)

    tests_obj = xcresulttool_get(xcresult, tests_ref)

    # Find every individual test case summary reference
    summary_refs = find_all_values(tests_obj, "ActionTestMetadata", "summaryRef")

    for sref in summary_refs:
        summary = xcresulttool_get(xcresult, sref)
        for name, ref_id in find_attachments(summary):
            print(f"{name}|{ref_id}")


if __name__ == "__main__":
    main()
