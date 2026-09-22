"""Fail-closed normalization for simulator-only TVTestRig FocusRing intake."""
from __future__ import annotations

import hashlib
from typing import Any


class SimulatorManifestError(ValueError):
    pass


FAMILY_MAP = {
    "grid_matrix": "gridMatrix", "gridMatrix": "gridMatrix",
    "media_shelf": "mediaShelf", "mediaShelf": "mediaShelf",
    "settings_list": "settingsList", "settingsList": "settingsList",
    "action_dialog": "actionDialog", "actionDialog": "actionDialog",
    "hero_carousel": "heroCarousel", "heroCarousel": "heroCarousel",
    "focus_maze": "focusMaze", "focusMaze": "focusMaze",
    "kitchen_sink": "kitchenSink", "kitchenSink": "kitchenSink",
}
THEME_MAP = {"light": "light", "dark": "dark", "high_contrast": "highContrast", "highContrast": "highContrast"}
SPLIT_MAP = {"training": "train", "calibration": "validation", "held-out": "test"}


def _mapped(value: Any, mapping: dict[str, str], label: str) -> tuple[str, str]:
    if not isinstance(value, str) or value not in mapping:
        raise SimulatorManifestError(f"unsupported_{label}")
    return value, mapping[value]


def build(contract: dict[str, Any], corpus_id: str, producer_reference: str, requested_target: dict[str, Any] | None, source_kind: str = "simulatorFixture") -> dict[str, Any]:
    if source_kind not in {"simulatorFixture", "physicalFixture"}:
        raise SimulatorManifestError("unsupported_source_kind")
    if not isinstance(corpus_id, str) or not corpus_id or not isinstance(producer_reference, str) or not producer_reference:
        raise SimulatorManifestError("missing_manifest_identity")
    pairs = []
    seen_ids: set[str] = set()
    groups: dict[str, str] = {}
    for row in contract.get("usableRows", []):
        recipe = row.get("recipe")
        if not isinstance(recipe, dict):
            raise SimulatorManifestError("missing_recipe_metadata")
        original_family, family = _mapped(recipe.get("archetype"), FAMILY_MAP, "family")
        original_theme, theme = _mapped(recipe.get("theme"), THEME_MAP, "theme")
        seed = recipe.get("seed")
        recipe_hash = recipe.get("recipe_hash") or recipe.get("recipeHash")
        if type(seed) is not int or seed < 0 or not isinstance(recipe_hash, str) or not recipe_hash:
            raise SimulatorManifestError("missing_recipe_group")
        pair_id = row.get("id")
        if not isinstance(pair_id, str) or not pair_id or pair_id in seen_ids:
            raise SimulatorManifestError("duplicate_pair_id")
        seen_ids.add(pair_id)
        split = SPLIT_MAP.get(row.get("split"))
        if split is None:
            raise SimulatorManifestError("unsupported_split")
        # Related theme/density/step variants must not become independent groups.
        group = f"seed:{seed}"
        if group in groups and groups[group] != split:
            raise SimulatorManifestError("group_split_leakage")
        groups[group] = split
        pairs.append({
            "pairID": pair_id, "recipeGroup": group, "split": split,
            "originalFamily": original_family, "family": family,
            "originalTheme": original_theme, "theme": theme,
            "unfocused": {"path": row["unfocusedPath"], "sha256": row["unfocusedSHA256"]},
            "focused": {"path": row["focusedPath"], "sha256": row["focusedSHA256"]},
            "elements": row["elements"],
        })
    if not pairs:
        raise SimulatorManifestError("no_usable_pairs")
    return {
        "schemaVersion": "1.0", "corpusID": corpus_id, "sourceKind": source_kind,
        "producer": {"name": contract.get("producer"), "buildReference": producer_reference, "producerBuild": contract.get("producerBuild")},
        "requestedTarget": requested_target, "observedSource": contract.get("sourceDescription"),
        "eligibility": {"inspection": "passed", "simulatorUse": "pending-corpus-review" if source_kind == "simulatorFixture" else "not-applicable", "physicalQualification": "not-established", "generalTrainingApproval": False},
        "pairs": pairs,
    }


def fingerprint(manifest: dict[str, Any]) -> str:
    import json
    return hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
