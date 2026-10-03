"""Source-pinned referencePack identity and visible native-control accounting."""
import math

REVISIONS = {
    'native_controls': 'ttr-native-controls-v1',
    'stingray_catalog': '101af47fd75dab4c12e6f802cd5c3b2ed3718b4f',
    'nostalgex_guide': 'ea93629fa10b82f138ea6c2f2a3f70e020b7a0f6',
}


def resolve(recipe, require):
    appearance = recipe.get('appearance') or {}
    pack = appearance.get('referencePack')
    fields = {'version', 'screen', 'mode', 'seed', 'variant', 'frozenEpoch'}
    require(isinstance(pack, dict) and fields <= set(pack) and
            set(pack) <= fields | {'viewportHeight', 'artworkStyle', 'backdrop'}, 'reference_fields')
    version, screen = pack['version'], pack['screen']
    require(type(version) is int and version in (1, 2) and screen in REVISIONS and
            pack['mode'] == 'instrumented', 'reference_version_screen_mode')
    require(type(pack['seed']) is int and 0 <= pack['seed'] <= 1_000_000 and
            type(pack['variant']) is int and 0 <= pack['variant'] <= 2 and
            type(pack['frozenEpoch']) is int and pack['frozenEpoch'] == 1759435200,
            'reference_seed_variant_epoch')
    viewport = pack.get('viewportHeight')
    require(viewport is None or type(viewport) in (int, float) and math.isfinite(viewport)
            and 500 <= viewport <= 720 and screen != 'native_controls', 'reference_viewport')
    if version == 2:
        require(screen != 'native_controls' and viewport is not None and
                pack.get('artworkStyle') in ('city', 'orbit', 'collage') and
                pack.get('backdrop') in ('dark', 'light'), 'reference_rich_fields')
    else:
        require(pack.get('artworkStyle') is None and pack.get('backdrop') is None,
                'reference_legacy_fields')
    count = (24 if screen == 'nostalgex_guide' or pack['variant'] == 1 else 30) if version == 2 else (
        3 if screen == 'native_controls' else (10 if screen == 'nostalgex_guide' or pack['variant'] == 1 else 12))
    require(recipe.get('element_count') == count and recipe.get('archetype') == 'grid_matrix' and
            appearance.get('preset') == 'artwork' and appearance.get('layout') == 'standard' and
            all(appearance.get(k) is None for k in ('canvas', 'focus', 'artwork', 'composition')),
            'reference_recipe_combination')
    canonical = f"reference-v{version}:{screen}:{pack['mode']}:{pack['seed']}:{pack['variant']}:{pack['frozenEpoch']}:{REVISIONS[screen]}"
    if viewport is not None:
        canonical += ':viewport=' + str(float(viewport))
    if version == 2:
        canonical += f":artwork={pack['artworkStyle']}:backdrop={pack['backdrop']}"
    require(appearance.get('family_id') in (None, 'appearance-v1.artwork.standard.' + canonical),
            'reference_family')
    return [f'ref-{i}' for i in range(count)], canonical


def visible_membership(scene, require):
    planned, _ = resolve(scene['recipe'], require)
    visible = {e['element_id'] for e in scene['elements']}
    inventory = scene.get('semantic_inventory') or {}
    exclusions = (scene['observation_diagnostics'].get('nativeProbe') or {}).get('exclusionReasons') or {}
    require(isinstance(exclusions, dict) and all(v in ('partially_clipped_bounds', 'clipped_or_zero_bounds')
            for v in exclusions.values()) and visible.isdisjoint(exclusions) and
            visible | set(exclusions) == set(planned), 'reference_visibility_accounting')
    require(inventory.get('coverage') == 'partial' and inventory.get('truncated') is False and
            set(inventory.get('expected_control_ids', [])) == set(planned) and
            set(inventory.get('visible_control_ids', [])) == visible and
            inventory.get('control_exclusions') == inventory.get('exclusions') == exclusions,
            'reference_inventory_binding')
    require(set(scene['observation_diagnostics']['requiredIDs']) == visible and
            set(scene['observation_diagnostics']['measuredIDs']) == visible,
            'reference_measured_membership')
    return planned
