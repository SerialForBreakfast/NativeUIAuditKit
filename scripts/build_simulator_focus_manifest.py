#!/usr/bin/env python3
"""Create a simulator-only FocusRing intake manifest from a completed fixture bundle."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harvest_bundle_validation import HarvestValidationError, validate_bundle
from simulator_focus_manifest import SimulatorManifestError, build, fingerprint

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--producer-reference", required=True)
    parser.add_argument("--requested-target-json", help="Recorded target object; does not establish identity")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        output.relative_to(ROOT)
    except ValueError:
        print(f"ERROR: refusing to write outside package: {output}", file=sys.stderr)
        return 2
    if output.exists() and not args.dry_run:
        print(f"ERROR: refusing to overwrite existing output: {output}", file=sys.stderr)
        return 2
    try:
        target = json.loads(args.requested_target_json) if args.requested_target_json else None
        if target is not None and not isinstance(target, dict):
            raise SimulatorManifestError("invalid_requested_target")
        manifest = build(validate_bundle(args.bundle), args.corpus_id, args.producer_reference, target)
    except (HarvestValidationError, SimulatorManifestError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"corpusID": manifest["corpusID"], "pairs": len(manifest["pairs"]), "fingerprint": fingerprint(manifest)}, sort_keys=True))
    if args.dry_run:
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
