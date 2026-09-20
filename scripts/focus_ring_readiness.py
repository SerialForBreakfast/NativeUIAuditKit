"""Offline FR-A quota, split, and VoiceOver-alignment readiness validation."""

from collections import Counter
from typing import Any


class ReadinessError(ValueError):
    """Raised when a prospective FocusRing corpus cannot satisfy FR-A."""


MIN = {
    "gridMatrix": 2000,
    "mediaShelf": 1500,
    "settingsList": 1000,
    "actionDialog": 500,
    "heroCarousel": 500,
    "focusMaze": 500,
}
ALIGNMENT_CONTRACT_VERSION = "1.0"
INTERACTION_MODES = {
    "directionalNavigation",
    "voiceOverExploration",
    "voiceOverTraversal",
    "unknown",
}
EXPECTED_RELATIONS = {
    "aligned",
    "expectedDecoupled",
    "unexpectedMismatch",
    "notAssessable",
}
ALIGNMENT_SOURCES = {"fixtureGroundTruth", "trustedLiveMetadata"}
REQUIRED_ALIGNMENT_CASES = {
    "normalDirectional",
    "voiceOverExploration",
    "voiceOverTraversal",
    "intentionalFixtureFault",
    "missingProducerState",
}


def _required_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def alignment_case(alignment: dict[str, Any]) -> str:
    """Return the ADR-0007 matrix row represented by trusted metadata."""
    mode = alignment.get("interactionMode")
    relation = alignment.get("expectedRelation")
    navigation = _required_string(alignment.get("navigationFocusElementID"))
    voice_over = _required_string(alignment.get("voiceOverFocusElementID"))
    if mode == "directionalNavigation" and relation == "aligned" and navigation == voice_over:
        return "normalDirectional"
    if mode == "voiceOverExploration" and relation == "expectedDecoupled" and navigation != voice_over:
        return "voiceOverExploration"
    if mode == "voiceOverTraversal" and relation == "expectedDecoupled" and navigation != voice_over:
        return "voiceOverTraversal"
    if relation == "unexpectedMismatch" and navigation != voice_over:
        return "intentionalFixtureFault"
    if mode == "unknown" and relation == "notAssessable" and voice_over is None:
        return "missingProducerState"
    raise ReadinessError("invalid_alignment_relationship")


def validate_alignment(alignment: Any) -> str:
    if not isinstance(alignment, dict):
        raise ReadinessError("invalid_alignment")
    if alignment.get("version") != ALIGNMENT_CONTRACT_VERSION:
        raise ReadinessError("unsupported_alignment_version")
    if alignment.get("interactionMode") not in INTERACTION_MODES:
        raise ReadinessError("invalid_interaction_mode")
    if alignment.get("expectedRelation") not in EXPECTED_RELATIONS:
        raise ReadinessError("invalid_expected_relation")

    relation = alignment["expectedRelation"]
    source = alignment.get("source")
    navigation = _required_string(alignment.get("navigationFocusElementID"))
    voice_over = _required_string(alignment.get("voiceOverFocusElementID"))
    if relation != "notAssessable" and source not in ALIGNMENT_SOURCES:
        raise ReadinessError("untrusted_alignment_source")
    if relation == "notAssessable":
        if alignment.get("interactionMode") != "unknown" or source is not None:
            raise ReadinessError("invalid_not_assessable_alignment")
    elif not navigation or not voice_over:
        raise ReadinessError("missing_alignment_target")
    return alignment_case(alignment)


def validate(rows: list[dict[str, Any]], require_alignment_matrix: bool = False) -> dict[str, Any]:
    seen: set[str] = set()
    scene: Counter[str] = Counter()
    theme: Counter[tuple[str, str]] = Counter()
    hard: Counter[tuple[str, str]] = Counter()
    matrix: Counter[str] = Counter()
    for row in rows:
        if not row.get("focused") or not row.get("unfocused") or row.get("labelSource") == "modelPrediction":
            raise ReadinessError("invalid_pair")
        seed = _required_string(row.get("seed"))
        if not seed or seed in seen:
            raise ReadinessError("seed_leakage")
        seen.add(seed)
        scene_name = _required_string(row.get("scene"))
        theme_name = _required_string(row.get("theme"))
        element_class = _required_string(row.get("class"))
        if not scene_name or not theme_name or not element_class:
            raise ReadinessError("invalid_pair_metadata")
        scene[scene_name] += 1
        theme[(scene_name, theme_name)] += 1
        if row.get("hardNegative"):
            hard[(theme_name, element_class)] += 1
        if "alignment" in row:
            matrix[validate_alignment(row["alignment"])] += 1

    if any(scene[name] < count for name, count in MIN.items()) or any(
        theme[(scene_name, theme_name)] < 0.2 * MIN[scene_name]
        for scene_name in ("gridMatrix", "mediaShelf")
        for theme_name in ("light", "highContrast")
    ):
        raise ReadinessError("underfilled_quota")
    if sum(hard.values()) < 100 or any(
        not hard[(theme_name, element_class)]
        for theme_name in ("light", "highContrast")
        for element_class in ("imageView", "collectionItem")
    ):
        raise ReadinessError("empty_hard_negative_stratum")
    if require_alignment_matrix and any(matrix[case] == 0 for case in REQUIRED_ALIGNMENT_CASES):
        raise ReadinessError("missing_alignment_case")
    return {
        "pairs": len(rows),
        "sceneCounts": dict(scene),
        "hardNegativeCounts": {f"{theme}/{kind}": count for (theme, kind), count in hard.items()},
        "alignmentContractVersion": ALIGNMENT_CONTRACT_VERSION,
        "alignmentCaseCounts": dict(matrix),
    }
