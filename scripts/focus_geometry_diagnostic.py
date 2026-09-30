"""Explicit role crops from pinned TTR intake. Diagnostic only; never loads a model."""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from focus_dataset_contract import ROOT, digest, image, local, member, validate_manifest
from focus_runtime import RUNTIME_PREPROCESSING, bounded_batches, identity, invoke
from harvest_artwork_geometry import ROLE, STATUS
from ttr_focus_manifest import require

VERSION = "focus-geometry-diagnostic-v1"
WRAPPER = "measured_control_wrapper"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan(manifest, expected_hash, role):
    manifest = local(manifest)
    require(sha(manifest) == expected_hash, "changed_source_manifest")
    doc = json.loads(manifest.read_text())
    require(doc.get("version") == "1.5", "ttr_manifest_required")
    require(role in (WRAPPER, ROLE), "unsupported_geometry_role")
    # Do not let the existing legacy adapter's development alias erase test roles.
    require(all(p.get("split") == "development" and p.get("original_split") in
                ("train", "validation") for p in doc.get("pairs", [])),
            "protected_or_unsupported_input")
    validate_manifest(doc, manifest.parent)
    runtime = identity()
    root = local(ROOT/doc["sourceRoot"])
    records = []
    for pair in doc["pairs"]:
        for state, scene_key in (("focused", "focusedScene"), ("unfocused", "baselineScene")):
            frame = pair["frames"][state]
            scene = pair["observationBinding"][scene_key]
            element = next(e for e in scene["elements"] if e["element_id"] == pair["elementID"])
            geometry = element.get("artwork_geometry")
            reason = None if role == WRAPPER else (
                "not_supplied" if geometry is None else geometry.get("unavailable_reason"))
            bounds = (element["pixel_bounds"] if role == WRAPPER else
                      geometry["pixel_bounds"] if reason is None else None)
            binding = {"sourceManifestSHA256": expected_hash, "pairID": pair["pair_id"],
                       "elementID": pair["elementID"], "state": state, "geometryRole": role,
                       "frame": frame, "wrapperBounds": element["pixel_bounds"],
                       "selectedBounds": bounds, "artworkGeometry": geometry,
                       "runtime": runtime, "preprocessing": RUNTIME_PREPROCESSING}
            records.append({"id": digest(binding), "binding": binding,
                            "status": "blocked" if reason else "pending_crop", "reason": reason})
    require(len({r['id'] for r in records}) == len(records), "duplicate_geometry_members")
    return {"version": VERSION, "purpose": "development-diagnostic-only", "trainingAdmission": False,
            "sourceManifest": {"path": str(manifest.relative_to(ROOT)), "sha256": expected_hash},
            "sourceRoot": str(root.relative_to(ROOT)), "geometryRole": role,
            "presentationBoundsStatus": STATUS, "runtime": runtime,
            "preprocessing": RUNTIME_PREPROCESSING, "records": records}


def counts(records):
    return {k: sum(r['status'] == k for r in records) for k in ('rendered', 'blocked', 'failed')}


def validate_report(report, output):
    require(report.get("version") == VERSION, "unsupported_geometry_report")
    require(report.get('errors') == [], "incomplete_geometry_crops")
    ref = report["sourceManifest"]
    expected = plan(member(ROOT, ref["path"]), ref["sha256"], report["geometryRole"])
    require({k: report.get(k) for k in expected if k != "records"} ==
            {k: v for k, v in expected.items() if k != "records"}, "changed_geometry_protocol")
    actual = report.get("records", [])
    require(len(actual) == len(expected["records"]), "changed_geometry_membership")
    for row, source in zip(actual, expected["records"]):
        require(row.get('id') == source['id'] and row.get('binding') == source['binding'],
                "changed_geometry_membership")
        if source['status'] == 'blocked':
            require(row == source, "changed_unavailable_geometry")
        else:
            require(row.get('status') == 'rendered' and row.get('reason') is None,
                    "incomplete_geometry_crops")
            require(row.get('crop', {}).get('path') == row['id']+'.png', "changed_crop_identity")
            image(output, row['crop'], (256,256))
    require(report.get('counts') == counts(actual), "changed_geometry_counts")
    items = [{"id": r['id'], "path": str(member(ROOT/report['sourceRoot'], r['binding']['frame']['path'])),
              "sha256": r['binding']['frame']['sha256'], "bounds": r['binding']['selectedBounds']}
             for r in actual if r['status'] == 'rendered']
    rows = {r['id']: r for r in actual}
    for batch in bounded_batches(items):
        for crop in invoke(batch)['results']:
            raw = base64.b64decode(crop['png'], validate=True)
            require(hashlib.sha256(raw).hexdigest() == rows[crop['id']]['crop']['sha256'],
                    "geometry_crop_parity_mismatch")
    return report['counts']


def derive(manifest, expected_hash, output, role):
    output = local(output)
    require(not output.exists(), "output_collision")
    result = plan(manifest, expected_hash, role)
    frozen = digest(result)
    output.mkdir(parents=True, exist_ok=False)
    records = {r['id']: r for r in result['records']}
    items = [{"id": r['id'], "path": str(member(ROOT/result['sourceRoot'], r['binding']['frame']['path'])),
              "sha256": r['binding']['frame']['sha256'], "bounds": r['binding']['selectedBounds']}
             for r in result['records'] if r['status'] == 'pending_crop']
    errors = []
    for batch in bounded_batches(items):
        try:
            reply = invoke(batch)  # Crop mode only. No model argument or model loading.
            for crop in reply['results']:
                row = records[crop['id']]
                raw = base64.b64decode(crop['png'], validate=True)
                name = row['id']+'.png'
                with (output/name).open('xb') as stream:
                    stream.write(raw)
                row['crop'] = {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}
                image(output, row['crop'], (256,256))
                row['status'] = 'rendered'
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(str(error))
            for item in batch:
                row = records[item['id']]
                if row['status'] == 'pending_crop':
                    row.update(status='failed', reason=str(error))
    try:
        require(digest(plan(manifest, expected_hash, role)) == frozen, "changed_source_or_runtime_during_crop")
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    result['counts'] = counts(result['records'])
    result['errors'] = errors
    if not errors:
        try:
            validate_report(result, output)
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(str(error))
    with (output/'geometry-diagnostic.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    require(not errors, "geometry_diagnostic_failed: " + '; '.join(errors))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--manifest-sha256', required=True)
    p.add_argument('--geometry-role', choices=(WRAPPER, ROLE), required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        report = derive(args.manifest, args.manifest_sha256, args.output, args.geometry_role)
        print(json.dumps({'version': VERSION, 'counts': report['counts'], 'trainingAdmission': False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
