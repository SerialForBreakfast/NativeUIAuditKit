"""Offline coverage requests and conservative recipe reservations; never executes jobs.

The optional lineage catalog is a local consumer planning format, not a TTR API.
Existing inventory/assembly roles and production gates are never modified.
"""
import argparse
from collections import Counter, defaultdict
import json

import human_annotation_review as h
import focus_corpus_inventory as inventory
from focus_ring_readiness import MIN
from human_corpus_inventory import metadata_hashes

VERSION = 'focus-corpus-plan-v1'
CATALOG = 'focus-corpus-lineage-catalog-v1'
VARIATIONS = {
    'artwork': ('mixed-aspect-shelf', 'dense-image-grid', 'hero-with-neighbors', 'placeholder-and-bright-neighbor'),
    'tabs': ('selected-parent-child-focus', 'tab-strip-with-content'),
    'rows': ('accessory-rows', 'long-label-and-mixed-width-rows'),
    'buttons': ('dialog-actions', 'wide-and-compact-buttons'),
}
THEMES = ('dark', 'light', 'highContrast')
NEEDS = {
    'artwork': ['observed control bounds', 'artwork body separate from wrapper', 'portrait/landscape/square content',
                'bright unfocused competitors', 'observed native focus brackets'],
    'tabs': ['selected state separate from focus', 'selected unfocused parent with focused child',
             'parent/child identity', 'complete competitor inventory'],
    'rows': ['observed control-wrapper bounds', 'accessories and neighboring rows', 'long and duplicate labels'],
    'buttons': ['observed control-wrapper bounds', 'resting fill versus focus effect', 'short/wide aspect ratios'],
}
GROUP_FIELDS = ('sourceGroups', 'layoutGroups', 'componentGroups', 'assetGroups', 'nearDuplicateGroups')


def slots(pairs_per_slot=8):
    h.require(type(pairs_per_slot) is int and 1 <= pairs_per_slot <= 64, 'invalid_collection_target')
    return [dict(id='-'.join((family, role, variation, theme)), priority=priority,
                 family=family, intendedRole=role, requestedVariation=variation, theme=theme,
                 targetPairs=pairs_per_slot, targetMeaning='collection target across recipes in this slot, not a qualification threshold',
                 requiredEvidence=NEEDS[family], sourceRequirement='separate reviewed source/layout ancestry by role')
            for priority, (family, variants) in enumerate(VARIATIONS.items(), 1)
            for role in ('training', 'validation') for variation in variants for theme in THEMES]


def verified_inventory(path):
    """Reproduce the relevant retained audit; no runtime refresh, crop rendering or model."""
    report = h.read(path)
    h.require(report.get('version') == inventory.VERSION, 'unsupported_inventory')
    protocol_path = h.checked(h.ROOT, report['protocol'])
    protocol = inventory.sealed(protocol_path, 'protocolSHA256')
    h.require(protocol['version'] == 'focus-reviewed-full-fit-v1', 'unsupported_protocol')
    admission = inventory.sealed(h.checked(h.ROOT, report['admission']), 'assemblySHA256')
    h.require(report['protectedMetadata'] == admission['protectedMetadata'], 'changed_protected_reference')
    protected = metadata_hashes(h.read(h.checked(h.ROOT, report['protectedMetadata'])))
    held_hashes = metadata_hashes(admission.get('heldMembers', []))
    held_hashes.update(r['recipeHash'] for r in admission.get('heldMembers', []) if r.get('recipeHash'))
    cache = {}
    def check(ref, size):
        h.require(ref['sha256'] not in protected and ref.get('pixelSHA256') not in protected,
                  'protected_reference_before_decode')
        key = (ref['path'], ref['sha256'], size)
        if key not in cache:
            inventory.image(h.ROOT, ref, size)
            cache[key] = inventory.pixel_digest(h.ROOT, ref)
        return cache[key]
    audit = inventory.audit_rows(protocol['samples'], protected, check)
    for key in audit:
        h.require(audit[key] == report[key], 'inventory_drift:'+key)
    h.require(inventory.coverage(audit['records']) == report['coverage'], 'inventory_coverage_drift')
    h.require(report['heldPairs'] == len(admission.get('heldMembers', [])) and
              report['excludedSelection'] == len(admission.get('excludedSelection', [])), 'changed_held_membership')
    pairs = defaultdict(list)
    for row in protocol['samples']:
        if row['use'] == 'train-candidate':
            pairs[row['sourceID'], row['pairID']].append(row)
    complete = [members for members in pairs.values() if len(members) == 2 and {r['label'] for r in members} == {0, 1}]
    h.require(len(complete) == len(pairs) and not audit['dispositions'].get('blocked'), 'baseline_not_valid')
    scenes = Counter(members[0]['scene'] for members in complete)
    # Keep held/protected exclusions conservative; neither is a new collection source.
    return report, protocol, audit, protected | held_hashes, scenes


def strings(values, reason):
    h.require(isinstance(values, list) and len(values) <= 10000 and
              all(isinstance(v, str) and v.strip() and v not in ('unknown', 'unavailable') for v in values) and
              len(values) == len(set(values)), reason)
    return values


def baseline_keys(row, record):
    keys = set()
    for value in (row.get('sourceID'), row.get('sourceSessionID'), row.get('relatedGroup')):
        if value and value != 'unknown': keys.add(('sourceGroups', value))
    for value in (row.get('intrinsicGroup'), row.get('family')):
        if value and value != 'unknown': keys.add(('layoutGroups', value))
    for value in (record['framePixels'], record['cropPixels'], row.get('frame', row.get('image'))['sha256'], row['crop']['sha256']):
        keys.add(('content', value))
    return keys


def reservations(catalog, requests, protocol_ref, samples, records, protected):
    """Union known relationships transitively; no random row splitting or source claims."""
    requested = {r['id']: r for r in requests}
    baseline = {r['id']: r for r in samples}
    observed = {r['id']: r for r in records}
    nodes = {('baseline', sid): dict(role=observed[sid]['role'], keys=baseline_keys(row, observed[sid]))
             for sid, row in baseline.items()}
    rows, links = [], []
    if catalog is not None:
        h.require(catalog.get('version') == CATALOG and catalog.get('baselineProtocol') == protocol_ref,
                  'unsupported_or_unbound_lineage_catalog')
        entries = catalog.get('recipes')
        h.require(isinstance(entries, list) and len(entries) <= 10000, 'invalid_recipe_membership')
        ids = [h.identifier(e['id']) for e in entries]
        h.require(len(ids) == len(set(ids)), 'duplicate_recipe_identity')
        for entry in sorted(entries, key=lambda e: e['id']):
            row = dict(id=entry['id'], slotID=entry.get('slotID'), status='blocked', reasons=[])
            rows.append(row)
            try:
                h.require(entry['slotID'] in requested, 'unknown_collection_slot')
                slot = requested[entry['slotID']]
                row['intendedRole'] = slot['intendedRole']
                # Keep known relationships even if later evidence is invalid; otherwise
                # removing a bad bridge could make its peers appear falsely separated.
                group_keys = set()
                nodes['recipe', entry['id']] = dict(role=slot['intendedRole'], keys=group_keys)
                for field in GROUP_FIELDS:
                    for value in strings(entry.get(field, []), 'invalid_'+field): group_keys.add((field, value))
                h.require(entry.get('intendedRole') == slot['intendedRole'], 'role_drift')
                h.require(entry.get('priorUse') in ('new', 'training', 'development', 'retention', 'protected', 'held', 'unknown'),
                          'prior_use_required')
                row['priorUse'] = entry['priorUse']
                if entry['priorUse'] in ('retention', 'protected', 'held', 'unknown'):
                    row['reasons'].append('prior_use_not_available_for_new_reservation')
                if slot['intendedRole'] == 'training' and entry['priorUse'] == 'development':
                    row['reasons'].append('development_source_cannot_become_training')
                if slot['intendedRole'] == 'validation' and entry['priorUse'] == 'training':
                    row['reasons'].append('training_source_cannot_become_validation')
                recipe = h.checked(h.ROOT, entry['recipe'])
                h.require(recipe.suffix == '.json', 'recipe_json_required')
                # Only integrity, not interpretation of an unqualified producer schema.
                if entry['recipe']['sha256'] in protected:
                    row['reasons'].append('protected_or_held_recipe_overlap')
                h.require(type(entry.get('relationshipsKnown')) is bool, 'relationships_state_required')
                content = strings(entry.get('contentSHA256', []), 'invalid_content_hashes')
                h.require(all(len(v) == 64 and all(c in '0123456789abcdef' for c in v) for v in content), 'invalid_content_hashes')
                if set(content) & protected:
                    row['reasons'].append('protected_or_held_content_overlap')
                group_keys.update(('content', v) for v in content)
                group_keys.add(('recipe', entry['recipe']['sha256']))
                relatives = strings(entry.get('relatedSampleIDs', []), 'invalid_related_samples')
                h.require(set(relatives) <= set(baseline), 'unknown_related_sample')
                peers = strings(entry.get('relatedRecipeIDs', []), 'invalid_related_recipes')
                h.require(set(peers) <= set(ids) and entry['id'] not in peers, 'unknown_related_recipe')
                if not entry['relationshipsKnown'] or not entry.get('sourceGroups') or not entry.get('layoutGroups'):
                    row['reasons'].append('unknown_source_or_layout_relationships')
                if entry.get('review'):
                    h.checked(h.ROOT, entry['review'])
                else:
                    row['reasons'].append('missing_lineage_review')
                links += [(('recipe', entry['id']), ('baseline', sid)) for sid in relatives]
                links += [(('recipe', entry['id']), ('recipe', sid)) for sid in peers]
                row.update(recipe=entry['recipe'], review=entry.get('review'),
                           relationshipsKnown=entry['relationshipsKnown'], status='proposed-source-separated')
            except (OSError, ValueError, KeyError, TypeError) as error:
                row['reasons'].append(str(error))
    parents = {k: k for k in nodes}
    def root(k):
        while parents[k] != k:
            parents[k] = parents[parents[k]]; k = parents[k]
        return k
    def join(a, b):
        a, b = root(a), root(b)
        if a != b: parents[max(a, b)] = min(a, b)
    seen = {}
    for key, node in sorted(nodes.items()):
        for relation in sorted(node['keys']):
            if relation in seen: join(key, seen[relation])
            else: seen[relation] = key
    for a, b in links:
        if b in nodes: join(a, b)
        else:
            next(r for r in rows if r['id'] == a[1])['reasons'].append('related_recipe_invalid')
    groups = defaultdict(list)
    for node in sorted(nodes): groups[root(node)].append(node)
    by_id = {r['id']: r for r in rows}
    components = []
    for members in sorted(groups.values()):
        recipe_ids = [key[1] for key in members if key[0] == 'recipe']
        roles = {nodes[key]['role'] for key in members}
        # Existing development/retention cannot supply a new training reservation.
        role_conflict = 'training' in roles and len(roles) > 1
        component_reasons = sorted({reason for rid in recipe_ids for reason in by_id[rid]['reasons']})
        if role_conflict: component_reasons.append('cross_role_relationship')
        cid = h.digest(members)
        components.append(dict(id=cid, baselineIDs=[key[1] for key in members if key[0] == 'baseline'],
                               recipeIDs=recipe_ids, roles=sorted(roles), crossRole=role_conflict))
        for rid in recipe_ids:
            by_id[rid]['component'] = cid
            by_id[rid]['reasons'] = sorted(set(component_reasons))
            if component_reasons: by_id[rid]['status'] = 'blocked'
    for row in rows:
        if row['reasons']: row['status'] = 'blocked'
        row.update(trainingEligible=False, sourceIndependenceEstablished=False, captureAuthorized=False)
    return rows, components


def build(report, protocol, audit, protected, scenes, catalog=None, pairs_per_slot=8):
    requests = slots(pairs_per_slot)
    rows, components = reservations(catalog, requests, report['protocol'], protocol['samples'], audit['records'], protected)
    for request in requests:
        matching = [r for r in rows if r['slotID'] == request['id']]
        proposed = [r for r in matching if r['status'] == 'proposed-source-separated']
        request.update(candidateRecipeIDs=[r['id'] for r in matching],
                       proposedRecipeIDs=[r['id'] for r in proposed],
                       state='proposal-needs-source-review' if proposed else 'blocked-recipes' if matching else 'unbound',
                       acceptedPairs=0)
    gates = [dict(scene=k, retainedPairs=scenes[k], existingMinimum=v, arithmeticShortfall=max(0, v-scenes[k]))
             for k, v in MIN.items()]
    return dict(version=VERSION, protocol=report['protocol'], baselineCoverage=report['coverage'],
                baselineDisposition=audit['dispositions'], baselineSamples=len(protocol['samples']),
                exactDuplicateCropGroups=audit['duplicateCropGroups'],
                baselineCrossRoleRelationships=audit['crossRoleRelationships'],
                unknownSourceSamples=sum(r['source'] == 'unknown' for r in audit['records']),
                nativePairs=sum(scenes.values()), productionSceneGates=gates,
                unmappedScenes={k:v for k,v in sorted(scenes.items()) if k not in MIN},
                preserved=dict(heldPairs=report['heldPairs'], excludedSelection=report['excludedSelection'],
                               roles=dict(Counter(r['role'] for r in audit['records'])), protectedMetadata=report['protectedMetadata']),
                requests=requests, reservations=rows, sourceComponents=components,
                counts=dict(requestedSlots=len(requests), targetPairs=sum(r['targetPairs'] for r in requests),
                            proposedRecipes=sum(r['status']=='proposed-source-separated' for r in rows),
                            blockedRecipes=sum(r['status']=='blocked' for r in rows),
                            unboundSlots=sum(r['state']=='unbound' for r in requests)),
                limits=['Collection targets are not qualification thresholds or verified recipe capabilities.',
                        'No lineage catalog means unbound requests, not invented source reservations.',
                        'Known groups and declared near-duplicates are linked; no perceptual similarity search performed.',
                        'Distinct components are not proof of independence; evidence review and admission remain required.',
                        'Legacy tab-looking primaryButtons remain unchanged; label counts do not measure all visual tab coverage.',
                        'Selected-parent and appearance-hard-negative counts remain unknown without explicit measured fields.',
                        'Keyboard optional/unsupported; protected challenge pixels are never opened.',
                        'Existing theme/hard-negative/physical-transfer gates are unchanged and not passed here.'],
                captureAuthorized=False, trainingEligible=False, releaseEligible=False)


def markdown(result):
    lines = ['# Coverage-driven collection plan', '',
             'Planning only. No capture, admission, model execution or gate change.', '',
             f"Retained: {result['baselineSamples']} crops, {result['nativePairs']} native pairs.", '',
             '| Family | Training focused / unfocused | Development focused / unfocused | Proposed train / validation pairs |',
             '| --- | ---: | ---: | ---: |']
    for family in VARIATIONS:
        def support(role):
            row = next(r for r in result['baselineCoverage'] if r['role']==role and r['stratum']==family)
            return f"{row['focused']} / {row['unfocused']}"
        quantities = [sum(r['targetPairs'] for r in result['requests'] if r['family']==family and r['intendedRole']==role)
                      for role in ('training', 'validation')]
        lines.append(f"| {family} | {support('training')} | {support('development')} | {quantities[0]} / {quantities[1]} |")
    lines += ['', '## Priorities and required evidence', '']
    for family, variants in VARIATIONS.items():
        lines += [f"- {family}: {', '.join(variants)}. Evidence: {'; '.join(NEEDS[family])}."]
    lines += ['', '## Source reservations', '', json.dumps(result['counts'], sort_keys=True), '',
              'Unknown or cross-role related recipes stay blocked. No old members move between roles.', '',
              '## Existing scene requirements', '', '| Scene | Retained pairs | Existing minimum | Shortfall |',
              '| --- | ---: | ---: | ---: |']
    for r in result['productionSceneGates']:
        lines.append(f"| {r['scene']} | {r['retainedPairs']} | {r['existingMinimum']} | {r['arithmeticShortfall']} |")
    lines += ['', 'Unmapped retained scenes: '+json.dumps(result['unmappedScenes'], sort_keys=True), '',
              '## Limits', ''] + ['- '+s for s in result['limits']]
    return '\n'.join(lines)+'\n'


def run(inventory_path, output, catalog_path=None, pairs_per_slot=8):
    out = h.fresh(output)
    report, protocol, audit, protected, scenes = verified_inventory(h.local(inventory_path))
    catalog = h.read(catalog_path) if catalog_path else None
    result = build(report, protocol, audit, protected, scenes, catalog, pairs_per_slot)
    result['inputs'] = dict(inventory=h.ref(h.local(inventory_path)),
                           lineageCatalog=h.ref(h.local(catalog_path)) if catalog_path else None)
    out.mkdir(parents=True)
    h.write(out/'plan.json', result)
    h.write(out/'lineage-catalog-template.json', dict(version=CATALOG, baselineProtocol=report['protocol'], recipes=[]))
    (out/'collection.md').write_text(markdown(result))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory', required=True)
    p.add_argument('--lineage-catalog')
    p.add_argument('--pairs-per-slot', type=int, default=8)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        result = run(args.inventory, args.output, args.lineage_catalog, args.pairs_per_slot)
        print(json.dumps(result['counts'], sort_keys=True))
        return 0  # A planning gap is a reported outcome, not a failed command.
    except (OSError, ValueError, TypeError, KeyError) as error:
        print('Planner rejected input: '+str(error))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
