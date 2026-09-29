"""Offline gap-targeted recipe pack and retained-bundle audit. Never captures/trains."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from focus_dataset_contract import ROOT, local
from harvest_sidecar_v2 import recipe_hash
from harvest_bundle_validation import validate_bundle


def plan():
    slots = []
    for i, (theme, count) in enumerate((('dark', 4), ('light', 4), ('dark', 8), ('light', 8))):
        for lane in ('button-appearance', 'settings-rows', 'selected-tabs'):
            key = f'{lane}-{i + 1:02d}'
            row = dict(id=key, lane=lane, role='development', trainingAdmission=False,
                       collectionTarget=count, status='contract-unavailable', recipe=None)
            if lane != 'selected-tabs':
                r = dict(schema_version=1, archetype='grid_matrix' if lane == 'button-appearance' else 'settings_list',
                         element_count=count, theme=theme, density='regular', seed=41001+i, step_index=0)
                if lane == 'button-appearance':
                    r['appearance'] = dict(version=1, preset='artwork', layout='standard',
                        canvas=dict(version=1, columns=2 if count == 4 else 4, spacing=32 if i < 2 else 48,
                                    inset=80, backgroundRGB=2105376 if theme == 'dark' else 14737632,
                                    showLabels=True, pairing='competitor_v1'),
                        focus=dict(version=1, kind='native_button'))
                    row.update(status='ready-for-runtime-pilot', expectedClasses=['collectionItem'],
                               limitation='Native button appearance; grid taxonomy remains collectionItem.')
                else:
                    row.update(status='reference-diagnostic-only', expectedClasses=['listRow', 'toggle', 'destructiveButton'],
                               limitation='Current row contract cannot request competitor negatives.')
                row.update(recipe=r, recipeSHA256=recipe_hash(r))
            else:
                row['limitation'] = 'Missing selected-tab role/state and competitor export contract.'
            slots.append(row)
    return dict(version='focus-gap-plan-v1', purpose='development-collection',
                producerContract='retained-0ef89d79', trainingAdmission=False, slots=slots)


def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def prepare(output):
    output = local(output)
    if output.exists(): raise ValueError('output_collision')
    document = plan()
    output.mkdir(parents=True)
    recipes = output/'recipes'; recipes.mkdir()
    for slot in document['slots']:
        if slot['recipe'] is not None: write_new(recipes/(slot['id']+'.json'), slot['recipe'])
    write_new(output/'plan.json', document)
    return document


def audit(document, assignments):
    # This version is intentionally immutable; a changed schedule requires a new
    # version/assignment, not silent recipe substitution after seeing outcomes.
    if document != plan(): raise ValueError('changed_collection_plan')
    if not isinstance(assignments, dict) or set(assignments) - {s['id'] for s in document['slots']}:
        raise ValueError('unknown_assignment')
    roots = [str(local(Path(p))) for p in assignments.values()]
    if len(set(roots)) != len(roots): raise ValueError('duplicate_bundle_assignment')
    results = []; pixels = set(); pair_count = 0
    for slot in document['slots']:
        result = dict(id=slot['id'], lane=slot['lane'], state='missing', pairs=0,
                      collectionTarget=slot['collectionTarget'], competitorRequirementMet=False)
        if slot['recipe'] is None:
            result['state'] = 'unsupported-contract'
            if slot['id'] in assignments: raise ValueError('unsupported_slot_assignment')
        elif slot['id'] in assignments:
            root = local(Path(assignments[slot['id']]))
            try:
                contract = validate_bundle(root)
                rows = contract['usableRows']
                if not rows: raise ValueError('empty_bundle')
                if contract['unknownClassCount'] or len(rows) != contract['acceptedRowCount']:
                    raise ValueError('unsupported_or_missing_rows')
                classes = Counter()
                for row in rows:
                    if recipe_hash(row['recipe']) != slot['recipeSHA256']:
                        raise ValueError('recipe_membership_mismatch')
                    binding = row.get('observationBinding')
                    if not binding: raise ValueError('native_brackets_missing')
                    target = next(e for e in binding['focusedScene']['elements'] if e['is_focused'])
                    if target['taxonomy_class'] not in slot['expectedClasses']:
                        raise ValueError('unexpected_target_class')
                    classes[target['taxonomy_class']] += 1
                competitor = all(r['observationBinding'].get('pairingMode') == 'competitor_v1' for r in rows)
                coverage = contract['targetCoverage']
                result.update(pairs=len(rows), competitorRequirementMet=competitor, targetCoverage=coverage,
                              classSupport=dict(classes), requestedCountMet=len(rows) == slot['collectionTarget'],
                              state='ready-for-crop-review' if competitor and coverage['complete'] and len(rows) == slot['collectionTarget'] else 'partial-diagnostic')
                # Repeated neutral frames are not additional independent images.
                from PIL import Image
                slot_pixels = set()
                for row in rows:
                    for key in ('focusedPath', 'unfocusedPath'):
                        with Image.open(root/row[key]) as im:
                            im = im.convert('RGB')
                            slot_pixels.add(hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest())
                pixels.update(slot_pixels)
                pair_count += len(rows)
            except (ValueError, OSError, KeyError, StopIteration, TypeError) as error:
                result.update(state='blocked', pairs=0, error=str(error), competitorRequirementMet=False)
        results.append(result)
    return dict(version='focus-gap-audit-v1', trainingAdmission=False, modelExecuted=False,
                complete=all(r['state'] == 'ready-for-crop-review' for r in results),
                acceptedPairs=pair_count, distinctFramePixels=len(pixels), slots=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare'); prep.add_argument('--output', type=Path, required=True)
    check = sub.add_parser('audit')
    check.add_argument('--plan', type=Path, required=True)
    check.add_argument('--assignments', type=Path, required=True, help='JSON object mapping slot IDs to local bundle paths')
    check.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.output)
            print(json.dumps({'slots':len(result['slots']), 'recipes':sum(s['recipe'] is not None for s in result['slots'])}))
        else:
            result = audit(json.loads(local(args.plan).read_text()), json.loads(local(args.assignments).read_text()))
            write_new(local(args.output), result)
            print(json.dumps({'complete':result['complete'], 'acceptedPairs':result['acceptedPairs']}))
        return 0
    except (ValueError, OSError, TypeError) as error:
        parser.exit(2, str(error)+'\n')


if __name__ == '__main__': raise SystemExit(main())
