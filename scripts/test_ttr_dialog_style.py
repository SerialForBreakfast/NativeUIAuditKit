"""Source-contract dialog styles through real ingest/normalization/crop entrypoints.

Generated images are explicitly test-only, never visual/runtime qualification.
"""
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from focus_dataset_contract import ROOT, validate_manifest
from harvest_bundle_validation import HarvestValidationError, validate_bundle
from harvest_sidecar_v2 import SidecarError, recipe_hash
from simulator_focus_manifest import SimulatorManifestError, build
from test_ttr_appearance import replace_recipes
from test_ttr_sidecar_v2 import write_bundle, reindex


class DialogStyleTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(dir=ROOT/".build/debug-output", prefix="dialog-style-"))
        self.bundle = self.root/"bundle"
        self.meta = write_bundle(self.bundle)
        self.recipe = copy.deepcopy(self.meta["recipe"])
        self.recipe["dialog_style"] = dict(version=1, size="large", shape="pill", palette="warm", content="badge")

    def tearDown(self):
        shutil.rmtree(self.root)

    def publish(self, recipe=None, meta=None):
        m = copy.deepcopy(self.meta if meta is None else meta)
        if recipe is not None:
            r = copy.deepcopy(recipe); r["recipe_hash"] = recipe_hash(r)
            replace_recipes(m, r)
        (self.bundle/"m.json").write_text(json.dumps(m))
        reindex(self.bundle)
        return m

    def test_all_144_combinations_preserved_in_normalization(self):
        hashes = set()
        for size, shape, palette, content in itertools.product(
                ("small", "medium", "large"), ("standard", "rounded", "pill"),
                ("system", "warm", "cool", "high_contrast"), ("short_label", "long_label", "icon", "badge")):
            r = copy.deepcopy(self.recipe)
            r["dialog_style"] = dict(version=1, size=size, shape=shape, palette=palette, content=content)
            canonical = (f"1:action_dialog:2:high_contrast:regular:7:0:"
                         f"identity@1:system:regular:0:false:false:false:false:"
                         f"dialog-style@1:{size}:{shape}:{palette}:{content}")
            self.assertEqual(recipe_hash(r), hashlib.sha256(canonical.encode()).hexdigest())
            hashes.add(recipe_hash(r)); self.publish(r)
            contract = validate_bundle(self.bundle)
            self.assertFalse(contract["usableRows"][0]["eligibleForTraining"])
            pair = build(contract, "test-only", "12105bc-dirty-contract", None)["pairs"][0]
            self.assertEqual(pair["observationBinding"]["focusedScene"]["recipe"]["dialog_style"], r["dialog_style"])
        self.assertEqual(len(hashes), 144)

    def test_absent_null_legacy_identity_and_invalid_styles(self):
        base = copy.deepcopy(self.meta["recipe"])
        expected = recipe_hash(base); base["dialog_style"] = None
        self.assertEqual(recipe_hash(base), expected)
        self.publish(base); self.assertEqual(validate_bundle(self.bundle)["acceptedRowCount"], 1)
        bad = [False, [], "style", {}, {**self.recipe["dialog_style"], "extra": 1}]
        for key in self.recipe["dialog_style"]:
            missing = copy.deepcopy(self.recipe["dialog_style"]); missing.pop(key); bad.append(missing)
            for value in (None, True, [], {}, "future", 1.0):
                bad.append({**self.recipe["dialog_style"], key: value})
        for style in bad:
            r = {**self.recipe, "dialog_style": style}
            with self.subTest(style=style), self.assertRaisesRegex(SidecarError, "dialog_style"):
                recipe_hash(r)
        r = {**self.recipe, "archetype": "grid_matrix"}
        with self.assertRaisesRegex(SidecarError, "dialog_style_archetype"): recipe_hash(r)

    def test_changed_alias_old_hash_and_legacy_sidecar_rejected(self):
        valid = self.publish(self.recipe)
        for mutate in ("alias", "old_hash", "legacy"):
            m = copy.deepcopy(valid)
            if mutate == "alias": m["focused_capture"]["after_scene"]["recipe"]["dialog_style"]["size"] = "small"
            elif mutate == "old_hash":
                r = copy.deepcopy(m["recipe"]); r["recipe_hash"] = self.meta["recipe"]["recipe_hash"]; replace_recipes(m, r)
            else: m.pop("schema_version")
            self.publish(meta=m)
            with self.subTest(mutate=mutate), self.assertRaises(HarvestValidationError): validate_bundle(self.bundle)

    def test_styles_do_not_create_independent_splits(self):
        self.publish(self.recipe); contract = validate_bundle(self.bundle)
        sibling = copy.deepcopy(contract["usableRows"][0]); sibling["id"] = "sibling"
        sibling["recipe"]["dialog_style"]["size"] = "small"
        sibling["recipe"]["recipe_hash"] = recipe_hash(sibling["recipe"])
        contract["usableRows"].append(sibling)
        self.assertEqual([p["recipeGroup"] for p in build(contract, "test-only", "contract", None)["pairs"]], ["seed:7"]*2)
        sibling["split"] = "held-out"
        with self.assertRaisesRegex(SimulatorManifestError, "group_split_leakage"): build(contract, "test-only", "contract", None)

    def test_actual_crop_cli_remains_test_only(self):
        self.publish(self.recipe)
        output = self.root/"crops"
        command = [sys.executable, str(ROOT/"scripts/ttr_focus_manifest.py"), "--bundle", str(self.bundle),
                   "--output", str(output), "--corpus-id", "test-only", "--producer-reference", "contract12105bc", "--test-only"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        manifest = json.loads((output/"focus_dataset_manifest.json").read_text())
        self.assertEqual(len(validate_manifest(manifest, output)), 1)
        self.assertEqual(manifest["pairs"][0]["observationBinding"]["focusedScene"]["recipe"]["dialog_style"], self.recipe["dialog_style"])


if __name__ == "__main__": unittest.main()
