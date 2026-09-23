"""Appearance-v1 source vectors and actual v2 intake/crop entrypoint regressions."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from focus_dataset_contract import ROOT, FocusDataError, validate_manifest
from harvest_bundle_validation import HarvestValidationError, validate_bundle
from harvest_sidecar_v2 import SidecarError, recipe_hash
from simulator_focus_manifest import SimulatorManifestError, build
from test_ttr_sidecar_v2 import write_bundle, reindex


# TTR e3d55d1 Scripts/fixture-appearance-vectors.json; not computed by this consumer.
VECTORS = {
    "artwork": "41be66c4bd4660731eb2139445f93545a95935b0448632eea5af75818d3a0384",
    "bright_unfocused": "21ccc1ec640bca298497f3645b9eaaa869741deb1ffd5bf54ff90ddcc96e170b",
    "gray_placeholder": "a1b289a83b9ad1864af4265c34ab1eaad4117a7ed28a98459b73df66957254e4",
}
LEGACY_HASH = "f472aed392a173003bbd4c653adbe3f65c9b92b1eee4bc37a0302926513af832"


def recipe(preset="artwork", archetype="media_shelf", layout="standard"):
    return {"schema_version": 1, "archetype": archetype, "element_count": 2,
            "theme": "light", "density": "regular", "seed": 7, "step_index": 0,
            "appearance": {"version": 1, "preset": preset, "layout": layout}}


def replace_recipes(meta, resolved):
    """Set each serialized alias/bracket independently, not shared Python references."""
    if isinstance(meta, dict):
        if "recipe" in meta:
            meta["recipe"] = copy.deepcopy(resolved)
        for value in meta.values():
            replace_recipes(value, resolved)
    elif isinstance(meta, list):
        for value in meta:
            replace_recipes(value, resolved)


class AppearanceTests(unittest.TestCase):
    def setUp(self):
        (ROOT/".build/debug-output").mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=ROOT/".build/debug-output", prefix="appearance-test-"))
        self.bundle = self.root/"bundle"
        self.meta = write_bundle(self.bundle)
        resolved = recipe()
        resolved["recipe_hash"] = VECTORS["artwork"]
        replace_recipes(self.meta, resolved)
        self.publish(self.meta)

    def tearDown(self):
        shutil.rmtree(self.root)

    def publish(self, meta):
        (self.bundle/"m.json").write_text(json.dumps(meta))
        reindex(self.bundle)

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT/"scripts"/script), *map(str, args)],
                              capture_output=True, text=True, timeout=120,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def test_pinned_producer_vectors_and_legacy_null(self):
        for preset, expected in VECTORS.items():
            with self.subTest(preset=preset):
                self.assertEqual(recipe_hash(recipe(preset)), expected)
        old = recipe()
        old.pop("appearance")
        self.assertEqual(recipe_hash(old), LEGACY_HASH)
        old["appearance"] = None
        self.assertEqual(recipe_hash(old), LEGACY_HASH)
        # Frozen pre-existing dialog fixture remains accepted with null appearances.
        old_meta = write_bundle(self.root/"legacy")
        resolved = old_meta["recipe"]
        resolved["appearance"] = None
        replace_recipes(old_meta, resolved)
        (self.root/"legacy/m.json").write_text(json.dumps(old_meta))
        reindex(self.root/"legacy")
        self.assertEqual(validate_bundle(self.root/"legacy")["acceptedRowCount"], 1)

    def test_all_supported_combinations_and_randomization_suffix(self):
        identities = set()
        for preset in VECTORS:
            for archetype, layout in (("media_shelf", "standard"), ("grid_matrix", "standard"),
                                      ("grid_matrix", "dock")):
                r = recipe(preset, archetype, layout)
                r["recipe_hash"] = recipe_hash(r)
                identities.add(r["recipe_hash"])
                meta = copy.deepcopy(self.meta)
                replace_recipes(meta, r)
                self.publish(meta)
                normalized = build(validate_bundle(self.bundle), "test-only", "e3d55d1", None)
                self.assertEqual(normalized["pairs"][0]["observationBinding"]["focusedScene"]["recipe"], r)
        self.assertEqual(len(identities), 9)
        r = recipe()
        r["randomization"] = {"pack_id": "test", "version": "1", "palette_name": "warm",
                              "typography_weight": "bold", "badge_count": 2, "gradient_overlay": True,
                              "simulate_voiceover_running": False, "simulate_reduce_motion": True,
                              "simulate_bold_text": False}
        canonical = "1:media_shelf:2:light:regular:7:0:test@1:warm:bold:2:true:false:true:false:appearance@1:artwork:standard"
        self.assertEqual(recipe_hash(r), hashlib.sha256(canonical.encode()).hexdigest())

    def test_closed_fields_versions_values_and_archetypes(self):
        bad_objects = [False, 1, "artwork", [], {},
                       {"version": 1, "preset": "artwork"},
                       {"version": 1, "layout": "standard"},
                       {"preset": "artwork", "layout": "standard"}]
        for field, values in {"version": [True, "1", 1.0, 0, 2, None],
                              "preset": [None, [], {}, "future"],
                              "layout": [None, [], {}, "future"]}.items():
            for value in values:
                a = copy.deepcopy(recipe()["appearance"])
                a[field] = value
                bad_objects.append(a)
        bad_objects.append({**recipe()["appearance"], "unbound_rendering": True})
        for appearance in bad_objects:
            with self.subTest(appearance=appearance):
                r = recipe(); r["appearance"] = appearance
                with self.assertRaisesRegex(SidecarError, "appearance_"):
                    recipe_hash(r)
                meta = copy.deepcopy(self.meta)
                replace_recipes(meta, {**r, "recipe_hash": VECTORS["artwork"]})
                self.publish(meta)
                with self.assertRaisesRegex(HarvestValidationError, "appearance_"):
                    validate_bundle(self.bundle)
        for archetype, layout in (("media_shelf", "dock"), ("action_dialog", "standard"),
                                  ("kitchen_sink", "standard"), ("unknown", "standard")):
            with self.assertRaisesRegex(SidecarError, "appearance_archetype_layout"):
                recipe_hash(recipe(archetype=archetype, layout=layout))

    def test_changed_dropped_unbound_or_legacy_appearance_rejected(self):
        def changed(r):
            r["appearance"]["preset"] = "bright_unfocused"
            r["recipe_hash"] = VECTORS["bright_unfocused"]
        def dropped(r):
            r.pop("appearance")
            r["recipe_hash"] = LEGACY_HASH
        paths = [("recipe",), ("baseline_scene", "recipe"), ("focused_scene", "recipe")]
        paths += [(role, endpoint, "recipe") for role in ("reference_capture", "focused_capture")
                  for endpoint in ("before_scene", "after_scene")]
        for path in paths:
            for change in (changed, dropped):
                with self.subTest(path=path, change=change.__name__):
                    meta = copy.deepcopy(self.meta)
                    r = meta
                    for key in path:
                        r = r[key]
                    change(r); self.publish(meta)
                    with self.assertRaises(HarvestValidationError):
                        validate_bundle(self.bundle)
        for mode in ("legacy_hash", "no_version", "pair_change"):
            meta = copy.deepcopy(self.meta)
            if mode == "legacy_hash":
                replace_recipes(meta, {**recipe(), "recipe_hash": LEGACY_HASH})
            elif mode == "no_version":
                meta.pop("schema_version")
            else:
                r = copy.deepcopy(meta["recipe"]); changed(r)
                replace_recipes(meta["focused_capture"], r)
                meta["focused_scene"]["recipe"] = copy.deepcopy(r)
                meta["recipe"] = r
            self.publish(meta)
            with self.assertRaises(HarvestValidationError):
                validate_bundle(self.bundle)

    def test_preset_and_layout_siblings_do_not_change_split_group(self):
        contract = validate_bundle(self.bundle)
        sibling = copy.deepcopy(contract["usableRows"][0])
        sibling.update(id="sibling", recipe=recipe("bright_unfocused", "grid_matrix", "dock"))
        sibling["recipe"]["recipe_hash"] = recipe_hash(sibling["recipe"])
        contract["usableRows"].append(sibling)
        same = build(contract, "test-only", "e3d55d1", None)
        self.assertEqual([p["recipeGroup"] for p in same["pairs"]], ["seed:7", "seed:7"])
        sibling["split"] = "held-out"
        with self.assertRaisesRegex(SimulatorManifestError, "group_split_leakage"):
            build(contract, "test-only", "e3d55d1", None)

    def test_actual_intake_crop_cli_lineage_and_preflight(self):
        from focus_training_preflight import preflight
        intake = self.root/"intake.json"
        args = ("--bundle", self.bundle, "--corpus-id", "test-only", "--producer-reference", "e3d55d1")
        result = self.cli("build_simulator_focus_manifest.py", *args, "--output", intake)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        document = json.loads(intake.read_text())
        self.assertEqual(document["pairs"][0]["observationBinding"]["baselineScene"]["recipe"]["appearance"], recipe()["appearance"])
        output = self.root/"crops"
        result = self.cli("harvest_focus_pairs.py", "--fixture-bundle", self.bundle,
                          "--output", output, "--corpus-id", "test-only", "--producer-reference", "e3d55d1",
                          "--ttr-sidecar-v2", "--test-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        derived = json.loads((output/"focus_dataset_manifest.json").read_text())
        self.assertEqual(len(validate_manifest(derived, output)), 1)
        self.assertEqual(derived["version"], "1.5")
        self.assertEqual(derived["evidenceKind"], "test-only")
        self.assertFalse(preflight(output, "appearance-test-only")["launchEligible"])
        binding = derived["pairs"][0]["observationBinding"]
        self.assertEqual(binding["focusedScene"]["recipe"]["recipe_hash"], VECTORS["artwork"])
        binding["focusedScene"]["recipe"]["appearance"]["preset"] = "gray_placeholder"
        with self.assertRaisesRegex(FocusDataError, "changed_ttr_membership"):
            validate_manifest(derived, output)


if __name__ == "__main__":
    unittest.main()
