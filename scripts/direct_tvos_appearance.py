"""Closed appearance pilot specification; source/file checks only, no device I/O."""
import hashlib
from pathlib import Path
from focus_dataset_contract import FocusDataError, digest
from direct_tvos_targets import SOURCE_HASHES, expected_targets

VERSION = "direct-tvos-appearance-catalog-v1"
PINS = {"Models/FixtureRecipe.swift":SOURCE_HASHES["FixtureRecipe.swift"],
        "Models/ProceduralSceneBuilder.swift":SOURCE_HASHES["ProceduralSceneBuilder.swift"],
        "Models/DomainRandomizationPack.swift":"a690642fcee539d669124d6a4090261f66bdd014dc5203896571031de1473a40",
        "Views/ProceduralSceneView.swift":"292b8f16519f844f5cdeb2b340ce2db46edf55352e9a4a8cb2d5ad369c48393c"}


def catalog():
    recipes=[{"schema_version":1,"archetype":family,"element_count":2 if family=="action_dialog" else 4,
              "theme":theme,"density":density,"seed":seed,"step_index":0}
             for family in ("media_shelf","grid_matrix","action_dialog","hero_carousel")
             for theme in ("light","dark") for seed in (101,211)
             for density in (("compact","spacious") if family in ("media_shelf","grid_matrix") else ("regular",))]
    targets=[expected_targets(r) for r in recipes]
    doc={"version":VERSION,"purpose":"development-pilot","recipes":recipes,
         "sourceHashes":dict(PINS),"expectedTargets":targets,"expectedPairs":sum(map(len,targets)),
         "expectedFrames":len(recipes)+sum(map(len,targets)),"partition":"development",
         "maxRecipeSeconds":120,"maxRequestSeconds":5,"maxSettlingSeconds":10}
    doc["sha256"]=digest(doc)
    return doc


def validate(value):
    if value != catalog(): raise FocusDataError("unsupported_appearance_catalog")


def check_source(root):
    if root is None: raise FocusDataError("appearance_producer_source_required")
    root=Path(root).absolute()
    if any(p.is_symlink() for p in (root,*root.parents)): raise FocusDataError("symlink_producer_source")
    for name,expected in PINS.items():
        path=root/name
        if any(p.is_symlink() for p in (path,*path.parents)): raise FocusDataError("symlink_producer_source")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise FocusDataError("changed_appearance_source:"+name)
    return dict(PINS)
