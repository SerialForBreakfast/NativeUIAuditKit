"""Pinned expected targets for the frozen direct development catalog, not live labels.

Source: TVTestRig Fixture Models/ProceduralSceneBuilder.swift and
KitchenSinkCatalog.swift, FocusMazeGraph.swift, FixtureRecipe.swift.
Hashes are recorded below; changing producer planning requires review, never adapting
expected membership to an incomplete observed scene. This does not authenticate pixels.
"""
SOURCE_HASHES = {
    "FixtureRecipe.swift": "6b7eaa81084f27440a2af1ef9b418e8df147a87fadad96d92d9b6e55d7b8ed77",
    "ProceduralSceneBuilder.swift": "454e42b0e0430ad228cdfbab250f2cd65cd6b424ce40bdf6769b92ecf058992a",
    "KitchenSinkCatalog.swift": "79834e00b646132bcdd62b5831165bfb84b45746ad724feefc9140f450e9ac85",
    "FocusMazeGraph.swift": "be9e2d2455d1a7bd2e3598b0f70a0081b274eb61db7f4d1912ed97a96f34aaca",
}


def expected_targets(recipe):
    """Mirror only the frozen catalog's source rules; labels still require native truth."""
    family = recipe["archetype"]
    if family == "action_dialog": return ["dialog_btn_0", "dialog_btn_1"]
    if family == "media_shelf": return [f"media_card_{i}" for i in range(4)]
    if family == "settings_list": return [f"settings_row_{i}" for i in range(4)]
    if family == "hero_carousel": return ["hero_btn_watch", "hero_btn_details"]
    if family == "focus_maze":
        return [f"maze_{r}_{c}" for r in range(3) for c in range(3) if (r, c) != (2, 1)]
    if family == "kitchen_sink":
        return ["sink_" + name for name in (
            "cancelAction", "collectionItem", "colorWell", "contextMenu", "destructiveButton",
            "disclosureGroup", "listRow", "menuButton", "picker", "primaryButton", "refreshControl",
            "secondaryButton", "segmentedControl", "sidebar", "tabBar", "textField", "toggle", "toolbar")]
    if family == "grid_matrix":
        # Source SplitMix64 consumes one nextDouble per item, including item zero.
        mask = (1 << 64) - 1
        state = recipe["seed"]
        result = []
        for i in range(4):
            state = (state + 0x9E3779B97F4A7C15) & mask
            z = ((state ^ (state >> 30)) * 0xBF58476D1CE4E5B9) & mask
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & mask
            z ^= z >> 31
            if i == 0 or (z >> 11) / float(1 << 53) >= .1:
                result.append(f"grid_cell_{i // 2}_{i % 2}")
        return result
    raise ValueError("unsupported_target_plan")
