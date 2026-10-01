"""Source-pinned SYNTH-01 receipt accounting; no admission or campaign inference."""
from collections import Counter


def validate_coverage(receipt, rows, native_plans):
    def require(ok, reason):
        if not ok:
            raise ValueError('invalid_target_coverage: ' + reason)

    coverage = receipt.get('targetCoverage')
    if coverage is None:
        return {'available': False, 'complete': False, 'reason': 'legacy_coverage_unavailable'}
    require(isinstance(coverage, dict) and set(coverage) == {'targets', 'unavailableRecipes'}, 'fields')
    targets, unavailable = coverage['targets'], coverage['unavailableRecipes']
    require(isinstance(targets, list) and len(targets) <= 10000, 'targets')
    require(isinstance(unavailable, list) and len(unavailable) <= 10000
            and all(isinstance(x, str) and x for x in unavailable), 'unavailable_recipes')
    require(len(set(unavailable)) == len(unavailable), 'duplicate_unavailable')
    allowed = {'accepted', 'rejected', 'unattempted', 'excluded_by_limit', 'excluded_by_selection', 'interrupted'}
    declared = {}
    for target in targets:
        require(isinstance(target, dict) and set(target) == {'recipe','elementID','outcome'}, 'target_fields')
        require(all(isinstance(target[k], str) and target[k] for k in target), 'target_values')
        key = target['recipe'], target['elementID']
        require(key not in declared, 'duplicate_target')
        require(target['outcome'] in allowed, 'outcome')
        require(key[0] not in unavailable, 'unavailable_with_targets')
        declared[key] = target['outcome']
    accepted = []
    for row in rows:
        recipe = row['metadata'].get('recipeFile')
        require(isinstance(recipe, str) and recipe, 'row_recipe_missing')
        accepted.append((recipe, row['expectedFocus']))
    require(len(set(accepted)) == len(accepted), 'duplicate_accepted_row')
    require(set(accepted) == {k for k,v in declared.items() if v == 'accepted'}, 'accepted_membership')
    require(type(receipt.get('acceptedRowCount')) is int
            and receipt['acceptedRowCount'] == len(accepted), 'accepted_count')
    for recipe, planned in native_plans.items():
        require({element for name,element in declared if name == recipe} == set(planned), 'native_membership')
    counts = dict(sorted(Counter(declared.values()).items()))
    # Source inventory can be independently checked only for recipes with native rows.
    unverified = sorted({r for r,_ in declared} - set(native_plans))
    complete = bool(declared) and not unavailable and not unverified and all(v == 'accepted' for v in declared.values())
    return {'available': True, 'complete': complete, 'scope': 'observed_recipe_inventories_only',
            'counts': counts, 'targets': targets, 'unavailableRecipes': unavailable,
            'unverifiedRecipes': unverified}
