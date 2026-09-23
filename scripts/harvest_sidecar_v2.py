"""Source-pinned TTR v2 bracket checks; correlation is not authenticated identity."""
import hashlib
import math


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


def appearance_digest_source(recipe):
    """Closed producer appearance-v1 contract; absent/null preserves legacy hashes."""
    appearance = recipe.get("appearance")
    if appearance is None:
        return ""
    require(isinstance(appearance, dict) and {"version", "preset", "layout"} <= set(appearance)
            and set(appearance) <= {"version", "preset", "layout", "family_id"},
            "appearance_fields")
    require(type(appearance["version"]) is int and appearance["version"] == 1,
            "appearance_version")
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
    family = appearance.get("family_id")
    require(family is None or (isinstance(family, str) and family ==
            f"appearance-v1.{appearance['preset']}.{appearance['layout']}"), "appearance_family")
    return f":appearance@1:{appearance['preset']}:{appearance['layout']}"


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
                           + dialog_style_digest_source(recipe)).encode()).hexdigest()


def scene_check(scene, size, expected):
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
    require(observation.get("verified") is True and observation.get("source") == "uikit_focus_system"
            and observation.get("geometrySource") == "uikit_window_converted_bounds"
            and observation.get("observedID") == expected and observation.get("requestedID") == expected,
            "native_focus")
    planned = observation.get("plannedFocusIDs")
    require(identifiers(planned) and set(planned) <= set(ids)
            and (expected is None or expected in planned), "planned_focus")
    generation = observation.get("generation")
    require(uint(generation) and all(type(diagnostics.get(k)) is int and diagnostics[k] == generation
                                    for k in ("generation", "sampledGeneration")), "generation")
    require(uint(diagnostics.get("sampleCount")) and diagnostics["sampleCount"] > 0
            and number(diagnostics.get("sampleAgeMilliseconds"))
            and 0 <= diagnostics["sampleAgeMilliseconds"] < 1000, "stale_sample")
    require(diagnostics.get("reason") == "ready" and diagnostics.get("nativeFocusResolved") is True
            and diagnostics.get("requestedID") == expected and diagnostics.get("observedID") == expected,
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
    return generation


def validate(meta, row, size, hashes):
    """Returns raw evidence only after validating all four endpoint scenes."""
    require(meta.get("bounds_semantics") == "measured_view_bounds; not_focus_effect_segmentation", "bounds_semantics")
    require((meta.get("scene_width"), meta.get("scene_height")) == size, "dimensions")
    generations = {}
    for role, key, scene_key, expected in (
            ("unfocused", "reference_capture", "baseline_scene", None),
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
                ("recipe", "elements", "focus_observation")), "changed_bracket")
        require(after == meta.get(scene_key), "scene_alias_conflict")
        generations[role] = agen
    require(generations["focused"] > generations["unfocused"], "pair_generation")
    focused, baseline = meta["focused_scene"], meta["baseline_scene"]
    require(meta["reference_capture"]["after_scene_received_host_ns"] <=
            meta["focused_capture"]["before_scene_received_host_ns"], "pair_host_order")
    require(baseline["recipe"] == focused["recipe"], "pair_recipe")
    require(all(meta.get(k) == focused.get(k) for k in
                ("recipe", "elements", "focused_element_id", "is_settled", "scene_width", "scene_height")), "flat_alias_conflict")
    require(all(k not in meta or meta[k] == focused.get(v) for k, v in
                (("activeFocusId", "focused_element_id"), ("isSettled", "is_settled"))), "flat_alias_conflict")
    exclusions = meta.get("layout_exclusions")
    require(isinstance(exclusions, dict) and all(isinstance(k, str) and k and isinstance(v, str) and v
                                               for k, v in exclusions.items()), "layout_exclusions")
    require(not set(exclusions) & {e["element_id"] for e in focused["elements"]}, "excluded_annotation")
    probe = focused["observation_diagnostics"].get("nativeProbe") or {}
    require(exclusions == (probe.get("exclusionReasons") or {}), "exclusion_alias_conflict")
    target = row["expectedFocus"]
    require(any(e["element_id"] == target for e in baseline["elements"]), "reference_target_missing")
    return {"schemaVersion": 2, "correlation": "validated_capture_bracket",
            "baselineScene": baseline, "focusedScene": focused,
            "referenceCapture": meta["reference_capture"], "focusedCapture": meta["focused_capture"],
            "layoutExclusions": exclusions, "boundsSemantics": meta["bounds_semantics"]}
