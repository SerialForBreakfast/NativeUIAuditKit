"""Source-pinned TTR v2 bracket checks; correlation is not authenticated identity."""
import hashlib
import math
import base64
import json
import unicodedata
from harvest_artwork import artwork_identity, swift_json, validate_hierarchy
from harvest_artwork_geometry import validate as validate_artwork_geometry


class SidecarError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise SidecarError("invalid_metadata: " + reason)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def uint(value):
    return type(value) is int and 0 <= value < 2**64


def identifiers(value):
    return (isinstance(value, list) and all(isinstance(x, str) and x for x in value)
            and len(set(value)) == len(value))


def focus_digest_source(focus):
    """Closed focus-v1 identity matching producer sorted JSON encoding."""
    require(isinstance(focus, dict) and {"version", "kind"} <= set(focus)
            and set(focus) <= {"version", "kind", "custom"}, "focus_fields")
    require(type(focus["version"]) is int and focus["version"] == 1, "focus_version")
    require(focus["kind"] in ("native_image", "native_button", "custom"), "focus_kind")
    canonical = {"version": 1, "kind": focus["kind"]}
    custom = focus.get("custom")
    if focus["kind"] == "custom":
        required = {"scale", "borderWidth", "borderRGB", "shadowOpacity", "shadowRGB", "cornerRadius"}
        require(isinstance(custom, dict) and required <= set(custom)
                and set(custom) <= required | {"tintRGB"}, "focus_custom_fields")
        normalized = {}
        for key, low, high in (("scale", 1, 1.2), ("borderWidth", 0, 8),
                               ("shadowOpacity", 0, 1), ("cornerRadius", 0, 32)):
            value = custom[key]
            require(number(value) and low <= value <= high, "focus_" + key)
            # JSONEncoder emits integral Double values without a decimal suffix.
            normalized[key] = (value if value == 0 and math.copysign(1, value) < 0
                               else int(value) if value == int(value) else value)
        for key in ("borderRGB", "shadowRGB", "tintRGB"):
            value = custom.get(key)
            if key == "tintRGB" and value is None:
                continue
            require(type(value) is int and 0 <= value <= 0xFFFFFF, "focus_" + key)
            normalized[key] = value
        canonical["custom"] = normalized
    else:
        require(custom is None, "focus_native_override")
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), allow_nan=False)
    # All strings above are closed enum/key literals. Preserve JSONEncoder's
    # signed Double zero spelling without touching arbitrary string content.
    encoded = encoded.replace(':-0.0', ':-0')
    return "focus@" + base64.b64encode(encoded.encode()).decode()


def appearance_digest_source(recipe):
    """Closed producer appearance-v1 contract; absent/null preserves legacy hashes."""
    appearance = recipe.get("appearance")
    if appearance is None:
        return ""
    require(isinstance(appearance, dict) and {"version", "preset", "layout"} <= set(appearance)
            and set(appearance) <= {"version", "preset", "layout", "family_id", "canvas", "focus", "artwork", "composition", "referencePack"},
            "appearance_fields")
    require(type(appearance["version"]) is int and appearance["version"] == 1,
            "appearance_version")
    if appearance.get('referencePack') is not None:
        from fixture_reference import resolve
        _, suffix = resolve(recipe, require)
        return ':appearance@1:artwork:standard:' + suffix
    if appearance.get('composition') is not None:
        from fixture_composition import resolve
        require(recipe['archetype']=='grid_matrix' and appearance['preset']=='artwork' and appearance['layout']=='standard' and
                all(appearance.get(k) is None for k in ('canvas','focus','artwork')), 'composition_appearance')
        _,suffix=resolve(appearance['composition'],recipe,require)
        require(appearance.get('family_id') in (None,'appearance-v1.artwork.standard.'+suffix),'appearance_family')
        return ':appearance@1:artwork:standard:'+suffix
    require(isinstance(appearance["preset"], str) and appearance["preset"] in
            {"artwork", "bright_unfocused", "gray_placeholder", "blank_placeholder",
             "high_contrast", "photos_like"}, "appearance_preset")
    require(isinstance(appearance["layout"], str) and appearance["layout"] in
            {"standard", "dock"}, "appearance_layout")
    require(recipe.get("archetype") == "grid_matrix" or
            (recipe.get("archetype") == "media_shelf" and appearance["layout"] == "standard"),
            "appearance_archetype_layout")
    # cda0a32 FixtureAppearance.decodeIfPresent: optional derived identity, not
    # another hash input or an assertion of independent evaluation membership.
    suffix = ""
    canvas = appearance.get("canvas")
    if canvas is not None:
        fields = {"version", "columns", "spacing", "inset", "backgroundRGB", "showLabels"}
        require(isinstance(canvas, dict) and fields <= set(canvas)
                and set(canvas) <= fields | {"pairing", "presentation", "selectedIndex", "mixedSizes", "tabCount", "labels", "fillViewport", "nativeButton", "nativeTable", "collectionStyle", "collectionContext", "cardGeometry", "composition", "contrastNeighbors"},
                "canvas_fields")
        for field, lo, hi in (("version",1,2), ("columns",1,8), ("spacing",16,80),
                              ("inset",40,160), ("backgroundRGB",0,0xFFFFFF)):
            require(type(canvas[field]) is int and lo <= canvas[field] <= hi,
                    "canvas_" + field)
        require(type(canvas['showLabels']) is bool, "canvas_showLabels")
        require(recipe.get('archetype') == 'grid_matrix' and appearance['layout'] == 'standard',
                "canvas_archetype_layout")
        suffix = f"canvas@{canvas['version']}:" + ':'.join(str(canvas[k]) for k in
                    ('columns','spacing','inset','backgroundRGB')) + ':' + str(canvas['showLabels']).lower()
        require(canvas.get('pairing') in (None, 'competitor_v1'), 'canvas_pairing')
        if canvas.get('pairing') is not None:
            suffix += ':' + canvas['pairing']
        presentation = canvas.get('presentation')
        require(presentation is None or (isinstance(presentation, str) and presentation in
                {'cards', 'buttons', 'settings_rows', 'tabs', 'nested_tabs_v1', 'native_table_v2', 'native_collection_v1'}), 'canvas_presentation')
        if presentation is not None:
            suffix += ':presentation=' + presentation
        style=canvas.get('collectionStyle')
        if presentation=='native_collection_v1':
            require(style in ('poster','landscape','mixed','mixed_items','sectioned','small_controls') and canvas['version']==2 and
                canvas['columns']==4 and canvas['showLabels'] and canvas.get('cardGeometry') is not None and
                canvas.get('mixedSizes') is not True and canvas.get('fillViewport') is not True and
                all(canvas.get(k) is None for k in ('composition','nativeButton','nativeTable')) and
                (canvas.get('contrastNeighbors') is None or style in ('mixed_items','sectioned','small_controls')),
                'canvas_collection_contract')
            suffix+=':collection='+style
        else:require(style is None,'canvas_collection_style')
        context=canvas.get('collectionContext')
        if context is not None:
            # 4f9273cc FixtureCanvas.canonical; preserve absent/null legacy hashes.
            require(context in ('city','orbit','collage','checkerboard') and
                presentation=='native_collection_v1' and style=='sectioned' and
                canvas.get('contrastNeighbors') is not True, 'canvas_collection_context')
            suffix+=':collectionContext='+context
        selected = canvas.get('selectedIndex')
        if selected is not None:
            rich_table=presentation=='native_table_v2' and (canvas.get('nativeTable') or {}).get('version')==2
            require(type(selected) is int and (presentation in ('tabs', 'nested_tabs_v1') or rich_table) and
                    0 <= selected < 64 and uint(recipe.get('element_count')) and
                    selected < recipe['element_count'] and (not rich_table or selected<6), 'canvas_selectedIndex')
            suffix += ':selected=' + str(selected)
        mixed = canvas.get('mixedSizes')
        if mixed is not None:
            require(type(mixed) is bool, 'canvas_mixedSizes')
            suffix += ':mixed=' + str(mixed).lower()
        tabs = canvas.get('tabCount')
        if presentation == 'nested_tabs_v1':
            require(type(tabs) is int and 2 <= tabs <= 8 and
                    tabs < recipe['element_count'] <= 64 and type(selected) is int and
                    0 <= selected < tabs, 'canvas_tabCount')
        else:
            require(tabs is None, 'canvas_tabCount')
        if tabs is not None:
            suffix += ':tabs=' + str(tabs)
        labels = canvas.get('labels')
        if labels is not None:
            require(isinstance(labels, list) and len(labels) == recipe['element_count'] <= 64
                    and canvas['showLabels'] and presentation in
                    ('buttons', 'settings_rows', 'tabs', 'nested_tabs_v1', 'native_table_v2', 'native_collection_v1') and
                    all(isinstance(s, str) and 0 < len(s.encode('utf-8')) <= 128 and
                        not any(unicodedata.category(c) in ('Cc', 'Cf') for c in s)
                        for s in labels), 'canvas_labels')
            suffix += ':labels=' + base64.b64encode(swift_json(labels)).decode()
        fill = canvas.get('fillViewport')
        if fill is not None:
            require(canvas['version'] == 2 and type(fill) is bool, 'canvas_fillViewport')
            suffix += ':fill=' + str(fill).lower()
        # Source-pinned matched-appearance revision2; logical points, not pixel bounds.
        table = canvas.get('nativeTable')
        if presentation == 'native_table_v2':
            # 50ff7fd8 FixtureAppearance.NativeTable; preserve v1 canonical bytes.
            fields={'version','width','rowHeight','x','y'}
            require(isinstance(table,dict) and fields<=set(table) and set(table)<=fields|{'viewportHeight','richContent'}, 'canvas_native_table_fields')
            version=table['version']
            require((version==1 and table.get('viewportHeight') is None and table.get('richContent') is None) or
                (version==2 and table.get('richContent') is True and type(table.get('viewportHeight')) is int and
                 360<=table['viewportHeight']<=860 and type(table['y']) is int and table['y']+table['viewportHeight']<=1040), 'canvas_native_table_version')
            require(all(type(table[k]) is int for k in fields) and version in (1,2) and
                600<=table['width']<=1400 and 80<=table['rowHeight']<=120 and
                80<=table['x']<=400 and 120<=table['y']<=220 and
                table['x']+table['width']<=1840 and table['y']+table['rowHeight']*6<=980,
                'canvas_native_table_geometry')
            require(canvas['version']==2 and canvas['showLabels'] and canvas['columns']==1 and
                recipe['element_count']==6 and (selected is None or version==2) and tabs is None and
                mixed is not True and fill is not True and all(canvas.get(k) is None for k in
                ('composition','nativeButton','cardGeometry','contrastNeighbors')), 'canvas_native_table_layout')
            suffix += ':native-table@' + ':'.join(str(table[k]) for k in ('version','width','rowHeight','x','y'))
            if version==2:suffix+=f":viewport={table['viewportHeight']}:rich=true"
        else:
            require(table is None, 'canvas_native_table_presentation')
        button = canvas.get('nativeButton')
        if button is not None:
            require(isinstance(button, dict) and set(button) == {'version', 'width', 'restingFill'},
                    'canvas_native_button_fields')
            require(type(button['version']) is int and button['version'] == 1 and
                    type(button['width']) is int and 120 <= button['width'] <= 1200 and
                    button['restingFill'] in ('gray', 'light'), 'canvas_native_button_values')
            require(canvas['version'] == 2 and presentation == 'buttons' and
                    canvas['showLabels'] and mixed is not True and fill is not True,
                    'canvas_native_button_combination')
            suffix += f":native-button@1:{button['width']}:{button['restingFill']}"
        geometry = canvas.get('cardGeometry')
        if geometry is not None:
            require(isinstance(geometry, dict) and set(geometry) == {'version', 'width', 'height'},
                    'canvas_card_geometry_fields')
            require(type(geometry['version']) is int and geometry['version'] == 1 and
                    type(geometry['width']) is int and 80 <= geometry['width'] <= 1200 and
                    type(geometry['height']) is int and 72 <= geometry['height'] <= 900,
                    'canvas_card_geometry_values')
            require(canvas['version'] == 2 and presentation in (None, 'cards', 'native_collection_v1') and
                    button is None and mixed is not True and fill is not True,
                    'canvas_card_geometry_combination')
            suffix += f":card-geometry@1:{geometry['width']}:{geometry['height']}"
        composition = canvas.get('composition')
        if composition is not None:
            require(composition in ('hero_neighbors_v1','tab_artwork_v1') and canvas['version'] == 2 and
                    (presentation == 'nested_tabs_v1' if composition == 'tab_artwork_v1' else presentation in (None, 'cards'))
                    and geometry is None and button is None
                    and mixed is not True and fill is not True and
                    type(recipe.get('element_count')) is int and
                    (tabs < recipe['element_count'] <= 64 if composition == 'tab_artwork_v1' else 2 <= recipe['element_count'] <= 5),
                    'canvas_composition')
            suffix += ':composition=' + composition
        contrast = canvas.get('contrastNeighbors')
        if contrast is not None:
            require(type(contrast) is bool and canvas['version'] == 2 and
                    (presentation in (None, 'cards') or (presentation=='native_collection_v1' and
                     style in ('mixed_items','sectioned','small_controls'))),
                    'canvas_contrast_neighbors')
            suffix += ':contrast=' + str(contrast).lower()
    focus = appearance.get('focus')
    focus_suffix = ''
    if focus is not None:
        focus_suffix = focus_digest_source(focus)
        require(canvas is not None and recipe.get('archetype') == 'grid_matrix'
                and appearance['layout'] == 'standard', 'focus_canvas')
        require(focus['kind'] != 'native_button' or canvas['showLabels'], 'focus_button_labels')
    if canvas is not None and canvas.get('presentation') not in (None, 'cards'):
        require(focus is not None and (focus['kind'] == 'native_button' or
                (canvas.get('presentation') == 'native_collection_v1' and focus['kind'] == 'native_image') or
                (canvas.get('composition') == 'tab_artwork_v1' and focus['kind'] == 'native_image')) and
                canvas['showLabels'], 'canvas_presentation_native_button')
    artwork = appearance.get('artwork')
    if canvas is not None and canvas.get('nativeButton') is not None:
        require(focus is not None and focus['kind'] == 'native_button' and artwork is None,
                'native_button_focus_artwork')
    artwork_suffix = ''
    if artwork is not None:
        require(canvas is not None and (canvas.get('presentation') in (None, 'cards') or
                canvas.get('composition') == 'tab_artwork_v1') and
                (focus is None or focus['kind'] != 'native_button'), 'artwork_canvas')
        artwork_suffix = artwork_identity(artwork, require)
    family = appearance.get("family_id")
    require(family is None or (isinstance(family, str) and family ==
            f"appearance-v1.{appearance['preset']}.{appearance['layout']}" + ('.'+suffix if suffix else '')
            + ('.'+focus_suffix if focus_suffix else '')
            + ('.'+artwork['familyID'] if artwork is not None else '')), "appearance_family")
    return (f":appearance@1:{appearance['preset']}:{appearance['layout']}" + (':'+suffix if suffix else '')
            + (':'+focus_suffix if focus_suffix else '')
            + (':'+artwork_suffix if artwork_suffix else ''))


def dialog_style_digest_source(recipe):
    """Closed producer dialog-style-v1; null/absent leaves historical identity intact."""
    style = recipe.get("dialog_style")
    if style is None:
        return ""
    require(isinstance(style, dict) and set(style) == {"version", "size", "shape", "palette", "content"},
            "dialog_style_fields")
    require(type(style["version"]) is int and style["version"] == 1, "dialog_style_version")
    require(recipe.get("archetype") == "action_dialog", "dialog_style_archetype")
    for field, allowed in (("size", {"small", "medium", "large"}),
                           ("shape", {"standard", "rounded", "pill"}),
                           ("palette", {"system", "warm", "cool", "high_contrast"}),
                           ("content", {"short_label", "long_label", "icon", "badge"})):
        require(isinstance(style[field], str) and style[field] in allowed, "dialog_style_" + field)
    return ":dialog-style@1:" + ":".join(style[k] for k in ("size", "shape", "palette", "content"))


def surface_digest_source(recipe):
    """Closed surface-v1 extension, verified against four received producer vectors.

    Recipe compatibility does not attest renderer independence or assign a split.
    """
    surface = recipe.get("surface")
    if surface is None:
        require(recipe.get("archetype") != "surface_template", "surface_missing")
        return ""
    require(isinstance(surface, dict) and {"version", "template"} <= set(surface)
            and set(surface) <= {"version", "template", "family_id"}, "surface_fields")
    require(type(surface["version"]) is int and surface["version"] == 1, "surface_version")
    template = surface["template"]
    require(isinstance(template, str) and template in
            {"cinema_rows", "album_grid", "memory_mosaic", "icon_shelf"}, "surface_template")
    require(recipe.get("archetype") == "surface_template" and recipe.get("appearance") is None
            and recipe.get("dialog_style") is None, "surface_archetype")
    require(surface.get("family_id") in (None, "surface-v1." + template), "surface_family")
    return ":surface@1:" + template


def recipe_hash(recipe):
    require(isinstance(recipe, dict), "recipe_missing")
    require(recipe.get("schema_version") == 1 and type(recipe.get("schema_version")) is int,
            "recipe_version")
    require(all(uint(recipe.get(k)) for k in ("seed", "step_index", "element_count"))
            and recipe["element_count"] > 0, "recipe_numbers")
    require(all(isinstance(recipe.get(k), str) and recipe[k] for k in ("archetype", "theme", "density")),
            "recipe_fields")
    require(recipe["density"] in {"compact", "regular", "spacious"}, "recipe_density")
    pack = recipe.get("randomization")
    canonical_pack = "identity@1:system:regular:0:false:false:false:false"
    if pack is not None:
        require(isinstance(pack, dict), "randomization")
        strings = ("pack_id", "version", "palette_name", "typography_weight")
        flags = ("gradient_overlay", "simulate_voiceover_running", "simulate_reduce_motion", "simulate_bold_text")
        require(all(isinstance(pack.get(k), str) and pack[k] for k in strings)
                and uint(pack.get("badge_count")) and all(type(pack.get(k)) is bool for k in flags),
                "randomization_fields")
        canonical_pack = (f"{pack['pack_id']}@{pack['version']}:{pack['palette_name']}:"
                          f"{pack['typography_weight']}:{pack['badge_count']}:"
                          + ":".join(str(pack[k]).lower() for k in flags))
    canonical = ":".join(str(recipe[k]) for k in
                         ("schema_version", "archetype", "element_count", "theme", "density", "seed", "step_index"))
    return hashlib.sha256((canonical + ":" + canonical_pack + appearance_digest_source(recipe)
                           + dialog_style_digest_source(recipe) + surface_digest_source(recipe)).encode()).hexdigest()


def scene_check(scene, size, expected, *, transition_visibility=False):
    require(isinstance(scene, dict), "scene_missing")
    require(scene.get("is_settled") is True and scene.get("focused_element_id") == expected
            and scene.get("harvest_challenge_active", False) is False, "scene_focus")
    for alias, canonical in (("activeFocusId", "focused_element_id"), ("isSettled", "is_settled")):
        require(alias not in scene or scene[alias] == scene.get(canonical), "scene_alias_conflict")
    require(all(number(scene.get(k)) and scene[k] == v for k, v in zip(("scene_width", "scene_height"), size)),
            "scene_dimensions")
    elements = scene.get("elements")
    require(isinstance(elements, list) and elements and all(isinstance(e, dict) for e in elements), "elements")
    ids = [e.get("element_id") for e in elements]
    require(identifiers(ids), "element_ids")
    focused = []
    for e in elements:
        validate_artwork_geometry(e.get("artwork_geometry"), size, require)
        require(type(e.get("is_focused")) is bool and isinstance(e.get("taxonomy_class"), str), "element_label")
        if e["is_focused"]:
            focused.append(e["element_id"])
        p, n = e.get("pixel_bounds"), e.get("normalized_bounds")
        require(isinstance(p, list) and isinstance(n, list) and len(p) == len(n) == 4
                and all(number(x) for x in p + n), "element_bounds")
        x, y, w, h = p
        require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= size[0] and y+h <= size[1]
                and 0 <= n[0] < n[2] <= 1 and 0 <= n[1] < n[3] <= 1, "element_bounds")
        projected = [n[0]*size[0], n[1]*size[1], (n[2]-n[0])*size[0], (n[3]-n[1])*size[1]]
        require(all(abs(a-b) <= 1.5 for a, b in zip(p, projected)), "coordinate_conflict")
    require(focused == ([] if expected is None else [expected]), "focused_elements")
    observation = scene.get("focus_observation")
    diagnostics = scene.get("observation_diagnostics")
    require(isinstance(observation, dict) and isinstance(diagnostics, dict), "native_observation_missing")
    scene_recipe=scene.get('recipe')
    require(isinstance(scene_recipe,dict),'scene_recipe')
    scene_appearance=scene_recipe.get('appearance')
    require(scene_appearance is None or isinstance(scene_appearance,dict),'appearance_fields')
    reference = (scene_appearance or {}).get('referencePack') is not None
    navigation = observation.get('verificationMode') == 'native_navigation'
    from fixture_native_visibility import kind, visible_membership as native_membership
    native_table = kind(scene) in ('native_table_v2','native_collection_v1')
    if native_table:
        appearance_digest_source(scene['recipe'])  # exact source-pinned layout, never a string-only bypass
    require(observation.get('verificationMode') is None or navigation and (reference or native_table) and transition_visibility,
            'native_verification_mode')
    if navigation:
        require('requestedID' not in observation and 'requestedID' not in diagnostics and
                observation.get('initialRequestedID') in observation.get('plannedFocusIDs', []),
                'native_navigation_initial_request')
    require(observation.get("verified") is True and observation.get("source") == "uikit_focus_system"
            and observation.get("geometrySource") == "uikit_window_converted_bounds"
            and observation.get("observedID") == expected and (navigation or observation.get("requestedID") == expected),
            "native_focus")
    planned = observation.get("plannedFocusIDs")
    inventory=scene.get('semantic_inventory') or {}
    allowed=(inventory.get('expected_control_ids',[]) if transition_visibility and
             inventory.get('coverage')=='incomplete_declared_composition' else ids)
    if reference:
        from fixture_reference import visible_membership
        allowed = visible_membership(scene, require)
        require(set(planned or []) == set(allowed), 'reference_planned_membership')
    elif native_table:
        allowed=native_membership(scene,require)
        require(set(planned or [])==set(allowed),'native_planned_membership')
    require(identifiers(allowed) and identifiers(planned) and set(planned) <= set(allowed)
            and (expected is None or expected in planned), "planned_focus")
    generation = observation.get("generation")
    require(uint(generation) and all(type(diagnostics.get(k)) is int and diagnostics[k] == generation
                                    for k in ("generation", "sampledGeneration")), "generation")
    from fixture_rendered_body import validate as validate_body
    for element in elements:
        try:
            validate_body(element.get('rendered_body_geometry'), size, element['element_id'], generation)
        except ValueError as error:
            raise SidecarError('invalid_metadata: '+str(error)) from error
    require(uint(diagnostics.get("sampleCount")) and diagnostics["sampleCount"] > 0
            and number(diagnostics.get("sampleAgeMilliseconds"))
            and 0 <= diagnostics["sampleAgeMilliseconds"] < 1000, "stale_sample")
    require(diagnostics.get("reason") == "ready" and diagnostics.get("nativeFocusResolved") is True
            and (navigation or diagnostics.get("requestedID") == expected) and diagnostics.get("observedID") == expected,
            "native_readiness")
    require(number(diagnostics.get("stableMilliseconds")) and number(diagnostics.get("requiredMilliseconds"))
            and diagnostics["requiredMilliseconds"] >= 0
            and diagnostics["stableMilliseconds"] >= max(150, diagnostics["requiredMilliseconds"]), "unsettled")
    require(identifiers(diagnostics.get("requiredIDs")) and identifiers(diagnostics.get("measuredIDs"))
            and diagnostics.get("missingIDs") == []
            and set(diagnostics["requiredIDs"]) <= set(diagnostics["measuredIDs"]), "missing_geometry")
    if expected is None:
        probe = diagnostics.get("nativeProbe")
        require(isinstance(probe, dict) and probe.get("referenceAttached") is True
                and probe.get("referenceFocused") is True, "unverified_reference")
    recipe = scene.get("recipe")
    require(recipe_hash(recipe) == recipe.get("recipe_hash"), "recipe_hash")
    validate_hierarchy(scene, require, transition_visibility=transition_visibility)
    if scene.get('semantic_inventory') is not None:
        from fixture_semantic_inventory import validate as validate_semantics
        try:
            validate_semantics(scene['semantic_inventory'], scene, transition_visibility=transition_visibility)
        except (ValueError, KeyError, TypeError) as error:
            require(False, str(error))
    return generation


def validate(meta, row, size, hashes):
    """Returns raw evidence only after validating all four endpoint scenes."""
    version = meta.get('schema_version')
    require(type(version) is int and version in (2, 3), 'sidecar_version')
    competitor = meta.get('competitor_element_id')
    if version == 3:
        require(meta.get('pairing_mode') == 'competitor_v1' and isinstance(competitor, str)
                and competitor and competitor != row['expectedFocus'], 'competitor_identity')
    else:
        require('pairing_mode' not in meta and 'competitor_element_id' not in meta, 'pairing_downgrade')
    require(meta.get("bounds_semantics") == "measured_view_bounds; not_focus_effect_segmentation", "bounds_semantics")
    require((meta.get("scene_width"), meta.get("scene_height")) == size, "dimensions")
    generations = {}
    for role, key, scene_key, expected in (
            ("unfocused", "reference_capture", "baseline_scene", competitor),
            ("focused", "focused_capture", "focused_scene", row["expectedFocus"])):
        capture = meta.get(key)
        require(isinstance(capture, dict) and capture.get("correlation") == "validated_capture_bracket", "capture_bracket")
        require(capture.get("frame_png_sha256") == hashes[role] == meta.get(role + "_sha256"), "frame_hash")
        require((capture.get("frame_width"), capture.get("frame_height")) == size, "frame_dimensions")
        times = [capture.get(k) for k in ("before_scene_received_host_ns", "frame_received_host_ns", "after_scene_received_host_ns")]
        require(all(uint(t) for t in times) and times[0] <= times[1] <= times[2], "host_order")
        before, after = capture.get("before_scene"), capture.get("after_scene")
        bgen, agen = scene_check(before, size, expected), scene_check(after, size, expected)
        require(bgen == agen and all(before.get(k) == after.get(k) for k in
                ("recipe", "elements", "focus_observation", "semantic_inventory")), "changed_bracket")
        require(after == meta.get(scene_key), "scene_alias_conflict")
        generations[role] = agen
    require(generations["focused"] > generations["unfocused"], "pair_generation")
    focused, baseline = meta["focused_scene"], meta["baseline_scene"]
    present=[s.get('semantic_inventory') is not None for s in (baseline,focused)]
    require(len(set(present))==1, 'semantic_inventory_pair_disappearance')
    availability=meta.get('semantic_inventory_availability')
    complete=all(present) and all(s['semantic_inventory'].get('coverage')=='complete_declared_composition' for s in (baseline,focused))
    require(not any(present) or len({s['semantic_inventory'].get('coverage') for s in (baseline,focused)})==1,'semantic_inventory_pair_coverage')
    require(availability is None or availability==('complete_declared_composition' if complete else 'partial_instrumented_components' if all(present) else 'unavailable_legacy'),
            'semantic_inventory_availability')
    artwork = (focused['recipe'].get('appearance') or {}).get('artwork')
    if artwork is not None:
        require(artwork['split'] == row.get('split'), 'artwork_split_reservation')
    require(meta["reference_capture"]["after_scene_received_host_ns"] <=
            meta["focused_capture"]["before_scene_received_host_ns"], "pair_host_order")
    require(baseline["recipe"] == focused["recipe"], "pair_recipe")
    pairing = ((focused['recipe'].get('appearance') or {}).get('canvas') or {}).get('pairing')
    composition = (focused['recipe'].get('appearance') or {}).get('composition')
    if version == 3 and (focused['recipe'].get('appearance') or {}).get('referencePack') is not None:
        from fixture_reference import resolve
        focusable, _ = resolve(focused['recipe'], require)
        require({competitor, row['expectedFocus']} <= set(focusable), 'reference_competitor_membership')
    elif version == 3 and composition is not None:
        from fixture_composition import resolve
        items, _ = resolve(composition, focused['recipe'], require)
        focusable = {item['id'] for item in items if item['focusable']}
        require({competitor, row['expectedFocus']} <= focusable, 'composition_competitor_membership')
    else:
        require(pairing == ('competitor_v1' if version == 3 else None), 'pairing_recipe')
    if version == 3:
        planned = baseline['focus_observation']['plannedFocusIDs']
        require(set(planned) == set(focused['focus_observation']['plannedFocusIDs'])
                and {competitor, row['expectedFocus']} <= set(planned), 'competitor_membership')
        baseline_types = {e['element_id']: e['taxonomy_class'] for e in baseline['elements']}
        focused_types = {e['element_id']: e['taxonomy_class'] for e in focused['elements']}
        require(baseline_types == focused_types, 'pair_element_membership')
        def relationships(scene):
            return {e['element_id']: (e.get('parent_element_id'),
                    'isSelected' in e.get('accessibility_traits', [])) for e in scene['elements']}
        require(relationships(baseline) == relationships(focused), 'pair_hierarchy_changed')
    require(all(meta.get(k) == focused.get(k) for k in
                ("recipe", "elements", "focused_element_id", "is_settled", "scene_width", "scene_height")), "flat_alias_conflict")
    require(all(k not in meta or meta[k] == focused.get(v) for k, v in
                (("activeFocusId", "focused_element_id"), ("isSettled", "is_settled"))), "flat_alias_conflict")
    require('semantic_inventory' not in meta or meta['semantic_inventory']==focused.get('semantic_inventory'),
            'semantic_inventory_flat_alias_conflict')
    exclusions = meta.get("layout_exclusions")
    require(isinstance(exclusions, dict) and all(isinstance(k, str) and k and isinstance(v, str) and v
                                               for k, v in exclusions.items()), "layout_exclusions")
    require(not set(exclusions) & {e["element_id"] for e in focused["elements"]}, "excluded_annotation")
    probe = focused["observation_diagnostics"].get("nativeProbe") or {}
    require(exclusions == (probe.get("exclusionReasons") or {}), "exclusion_alias_conflict")
    target = row["expectedFocus"]
    require(any(e["element_id"] == target for e in baseline["elements"]), "reference_target_missing")
    result = {"schemaVersion": version, "correlation": "validated_capture_bracket",
            "baselineScene": baseline, "focusedScene": focused,
            "referenceCapture": meta["reference_capture"], "focusedCapture": meta["focused_capture"],
            "layoutExclusions": exclusions, "boundsSemantics": meta["bounds_semantics"]}
    if version == 3:
        result.update(pairingMode='competitor_v1', competitorElementID=competitor)
    return result
