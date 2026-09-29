"""Competitor-v3 intake: source-shaped evidence, never training admission."""
import copy
import json
import subprocess
import unittest

from focus_dataset_contract import ROOT, validate_manifest
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from harvest_sidecar_v2 import appearance_digest_source, recipe_hash, SidecarError
from test_ttr_canvas import canvas_recipe
from test_ttr_appearance import replace_recipes
import test_ttr_appearance as fixtures


def focus_recipe(kind='native_image'):
    recipe = canvas_recipe()
    recipe['appearance']['canvas'].update(pairing='competitor_v1', showLabels=True)
    recipe['appearance']['focus'] = dict(version=1, kind=kind)
    if kind == 'custom':
        recipe['appearance']['focus']['custom'] = dict(scale=1.08, borderWidth=3.0,
            borderRGB=16777215, shadowOpacity=0.9, shadowRGB=0, cornerRadius=16.0)
    return recipe


def competitor_meta(meta):
    meta = copy.deepcopy(meta)
    def visit(value):
        if isinstance(value, dict):
            if 'focus_observation' in value:
                expected = 'e' if value['focused_element_id'] == 'e' else 'x'
                value['focused_element_id'] = expected
                value['elements'][0]['is_focused'] = expected == 'e'
                value['elements'].append(dict(element_id='x', taxonomy_class='collectionItem',
                    is_focused=expected == 'x', pixel_bounds=[44, 10, 12, 16],
                    normalized_bounds=[44/64, 10/48, 56/64, 26/48]))
                value['focus_observation'].update(requestedID=expected, observedID=expected,
                    plannedFocusIDs=['e', 'x'])
                value['observation_diagnostics'].update(requestedID=expected, observedID=expected,
                    requiredIDs=['e', 'x'], measuredIDs=['e', 'x'])
                value['observation_diagnostics']['nativeProbe']['referenceFocused'] = False
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
    visit(meta)
    recipe = focus_recipe(); recipe['recipe_hash'] = recipe_hash(recipe)
    replace_recipes(meta, recipe)
    meta.update(schema_version=3, pairing_mode='competitor_v1', competitor_element_id='x')
    return meta


class CompetitorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AppearanceTests(); self.fixture.setUp()
        self.meta = competitor_meta(self.fixture.meta)
        self.fixture.publish(self.meta)

    def tearDown(self): self.fixture.tearDown()

    def test_real_crop_cli_preserves_negative_focus_and_bounds(self):
        f = self.fixture
        contract = validate_bundle(f.bundle)
        self.assertEqual(contract['usableRows'][0]['sidecarVersion'], 3)
        output = f.root/'crops'
        result = f.cli('ttr_focus_manifest.py', '--bundle', f.bundle, '--output', output,
                       '--corpus-id', 'competitor-test', '--producer-reference', '0ef89d79', '--test-only')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        document = json.loads((output/'focus_dataset_manifest.json').read_text())
        self.assertEqual(len(validate_manifest(document, output)), 1)
        pair = document['pairs'][0]
        self.assertEqual(pair['observationBinding']['schemaVersion'], 3)
        self.assertEqual(pair['observationBinding']['competitorElementID'], 'x')
        self.assertEqual(pair['frames']['unfocused']['observedFocusID'], 'x')
        self.assertNotEqual(pair['frames']['focused']['bounds'], pair['frames']['unfocused']['bounds'])
        from focus_training_preflight import preflight
        self.assertFalse(preflight(output, 'competitor-test')['launchEligible'])
        pair['frames']['unfocused']['observedFocusID'] = None
        with self.assertRaises(ValueError): validate_manifest(document, output)

    def test_rejects_missing_wrong_and_downgraded_competitor(self):
        for change in (lambda m: m.pop('competitor_element_id'),
                       lambda m: m.update(competitor_element_id='e'),
                       lambda m: m.update(competitor_element_id='absent'),
                       lambda m: m.update(pairing_mode='unknown'),
                       lambda m: m.update(schema_version=2),
                       lambda m: m['reference_capture']['before_scene']['elements'][0].update(is_focused=True),
                       lambda m: m['baseline_scene']['focus_observation'].update(plannedFocusIDs=['x']),
                       lambda m: m['focused_capture']['after_scene']['recipe']['appearance']['focus'].update(kind='custom')):
            with self.subTest(change=change):
                meta = copy.deepcopy(self.meta); change(meta); self.fixture.publish(meta)
                with self.assertRaises(HarvestValidationError): validate_bundle(self.fixture.bundle)

    def test_recipe_pairing_cannot_downgrade(self):
        meta = copy.deepcopy(self.meta)
        r = copy.deepcopy(meta['recipe']); r['appearance']['canvas'].pop('pairing')
        r['recipe_hash'] = recipe_hash(r); replace_recipes(meta, r); self.fixture.publish(meta)
        with self.assertRaisesRegex(HarvestValidationError, 'pairing_recipe'): validate_bundle(self.fixture.bundle)


class FocusIdentityTests(unittest.TestCase):
    def test_emitted_producer_vectors(self):
        # Emitted by delivered 0ef89d79 FixtureAppearance.swift using the retained
        # identity-probe/main.swift; constants are not consumer-derived.
        vectors = {
            'native_image': 'eyJraW5kIjoibmF0aXZlX2ltYWdlIiwidmVyc2lvbiI6MX0=',
            'native_button': 'eyJraW5kIjoibmF0aXZlX2J1dHRvbiIsInZlcnNpb24iOjF9',
            'custom': 'eyJjdXN0b20iOnsiYm9yZGVyUkdCIjoxNjc3NzIxNSwiYm9yZGVyV2lkdGgiOjMsImNvcm5lclJhZGl1cyI6MTYsInNjYWxlIjoxLjA4LCJzaGFkb3dPcGFjaXR5IjowLjksInNoYWRvd1JHQiI6MH0sImtpbmQiOiJjdXN0b20iLCJ2ZXJzaW9uIjoxfQ=='
        }
        for kind, encoded in vectors.items():
            self.assertEqual(appearance_digest_source(focus_recipe(kind)),
                ':appearance@1:artwork:standard:canvas@1:4:32:80:2105376:true:competitor_v1:focus@' + encoded)

    def test_closed_fields_and_ranges(self):
        for key, values in {'scale':[0, 1.21, True, float('nan')], 'borderWidth':[-1, 9],
                            'shadowOpacity':[-0.1, 1.1], 'cornerRadius':[-1, 33],
                            'borderRGB':[-1, True, 16777216], 'tintRGB':[False, -1]}.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    r = focus_recipe('custom'); r['appearance']['focus']['custom'][key] = value
                    with self.assertRaises(SidecarError): recipe_hash(r)
        for focus in ({}, [], {'version': True, 'kind':'native_image'},
                      {'version':1, 'kind':'custom'}, {'version':1, 'kind':'native_image', 'custom':{}},
                      {'version':1, 'kind':'native_image', 'extra':True}):
            r = focus_recipe(); r['appearance']['focus'] = focus
            with self.assertRaises(SidecarError): recipe_hash(r)
        r = focus_recipe('native_button'); r['appearance']['canvas']['showLabels'] = False
        with self.assertRaises(SidecarError): recipe_hash(r)

    def test_identity_separates_focus_and_legacy_null(self):
        recipes = [focus_recipe(k) for k in ('native_image', 'native_button', 'custom')]
        self.assertEqual(len({recipe_hash(r) for r in recipes}), 3)
        old = canvas_recipe(); null = copy.deepcopy(old)
        null['appearance'].update(focus=None); null['appearance']['canvas']['pairing'] = None
        self.assertEqual(recipe_hash(old), recipe_hash(null))

    def test_optional_actual_producer_probe(self):
        probe = ROOT/'.build/debug-output/focus-identity-probe'
        if not probe.exists(): self.skipTest('compile retained Foundation producer probe to verify emitted vectors')
        recipes = [focus_recipe(k) for k in ('native_image', 'native_button', 'custom')]
        for number in (0, -0.0, 1, 0.000001, 1e-7, 1e-9, 1e-100, 0.1234567890123456):
            r = focus_recipe('custom'); r['appearance']['focus']['custom']['shadowOpacity'] = number
            recipes.append(r)
        result = subprocess.run([str(probe)], input=json.dumps([r['appearance'] for r in recipes]),
                                text=True, capture_output=True, check=True)
        for recipe, emitted in zip(recipes, json.loads(result.stdout)):
            self.assertEqual(appearance_digest_source(recipe), ':' + emitted['canonical'])
            recipe['appearance']['family_id'] = emitted['family']
            self.assertEqual(appearance_digest_source(recipe), ':' + emitted['canonical'])


if __name__ == '__main__': unittest.main()
