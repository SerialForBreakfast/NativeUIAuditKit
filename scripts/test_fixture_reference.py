"""Generated reference contracts: identity, exclusions and native navigation."""
import copy
import unittest
from fixture_reference import resolve
from harvest_sidecar_v2 import require, recipe_hash, scene_check
from test_ttr_sidecar_v2 import scene
from test_fixture_semantic_inventory import inventory


def reference_recipe(version=1, screen='native_controls'):
    pack = dict(version=version, screen=screen, mode='instrumented', seed=83,
                variant=0, frozenEpoch=1759435200)
    if version == 2: pack.update(viewportHeight=600, artworkStyle='city', backdrop='dark')
    count = 3 if screen == 'native_controls' else (24 if version == 2 and screen == 'nostalgex_guide'
            else 30 if version == 2 else 12 if screen == 'stingray_catalog' else 10)
    r = dict(schema_version=1, archetype='grid_matrix', element_count=count, theme='dark',
             density='regular', seed=83, step_index=0,
             appearance=dict(version=1, preset='artwork', layout='standard', referencePack=pack))
    r['recipe_hash'] = recipe_hash(r)
    return r


def reference_scene():
    s = scene('e', 4)
    s['recipe'] = reference_recipe()
    s['focused_element_id'] = 'ref-0'
    s['elements'][0]['element_id'] = 'ref-0'
    s['focus_observation'].update(observedID='ref-0', requestedID='ref-0',
                                  plannedFocusIDs=['ref-0', 'ref-1', 'ref-2'])
    d = s['observation_diagnostics']
    d.update(requestedID='ref-0', observedID='ref-0', requiredIDs=['ref-0'], measuredIDs=['ref-0'])
    excluded = {'ref-1': 'clipped_or_zero_bounds', 'ref-2': 'clipped_or_zero_bounds'}
    d['nativeProbe']['exclusionReasons'] = excluded
    inv = inventory(s)
    inv.update(expected_control_ids=['ref-0', 'ref-1', 'ref-2'], visible_control_ids=['ref-0'],
               exclusions=excluded.copy(), control_exclusions=excluded.copy())
    for eid in excluded:
        e = copy.deepcopy(inv['elements'][0])
        e.update(id=eid, input_focused=False, clipping='fully_clipped',
                 visible_pixel_bounds=None, visible_normalized_bounds=None)
        inv['elements'].append(e)
    s['semantic_inventory'] = inv
    return s


class ReferenceTests(unittest.TestCase):
    def test_producer_known_v2_digest(self):
        r = reference_recipe(2, 'nostalgex_guide')
        self.assertEqual(r['recipe_hash'], '1d32c0a6eb62d3ac777bf3ad218c9798884085854c6323ccad8ec3f6c7044893')
        self.assertEqual(len(resolve(r, require)[0]), 24)

    def test_v1_legacy_and_rich_variants(self):
        for version in (1, 2):
            for screen in ('stingray_catalog', 'nostalgex_guide'):
                r = reference_recipe(version, screen)
                self.assertEqual(len(resolve(r, require)[0]), r['element_count'])

    def test_closed_identity_rejects_changes(self):
        for mutate in (lambda r:r['appearance']['referencePack'].update(mode='reference'),
                       lambda r:r['appearance']['referencePack'].update(version=True),
                       lambda r:r['appearance']['referencePack'].update(viewportHeight=float('nan')),
                       lambda r:r['appearance']['referencePack'].update(unknown=1),
                       lambda r:r['appearance'].update(family_id='invented'),
                       lambda r:r.update(element_count=11)):
            r = reference_recipe(2, 'stingray_catalog'); mutate(r)
            with self.assertRaises(ValueError): recipe_hash(r)

    def test_visible_and_excluded_inventory(self):
        s = reference_scene(); original = copy.deepcopy(s)
        self.assertEqual(scene_check(s, (64, 48), 'ref-0'), 4)
        self.assertEqual(s, original)

    def test_unaccounted_clipped_stale_conflicting_rejected(self):
        for mutate in (lambda s:s['focus_observation']['plannedFocusIDs'].append('invented'),
                       lambda s:s['observation_diagnostics']['nativeProbe']['exclusionReasons'].pop('ref-1'),
                       lambda s:s['semantic_inventory']['elements'][1].update(clipping=None),
                       lambda s:s['semantic_inventory'].update(truncated=True),
                       lambda s:s['semantic_inventory']['elements'][0].update(input_focused=False),
                       lambda s:s['observation_diagnostics'].update(sampleAgeMilliseconds=1000)):
            s = reference_scene(); mutate(s)
            with self.assertRaises(ValueError): scene_check(s, (64, 48), 'ref-0')

    def test_navigation_scoped_and_keeps_initial_request(self):
        s = reference_scene(); o = s['focus_observation']; d = s['observation_diagnostics']
        o.pop('requestedID'); d.pop('requestedID')
        o.update(verificationMode='native_navigation', initialRequestedID='ref-2')
        self.assertEqual(scene_check(s, (64, 48), 'ref-0', transition_visibility=True), 4)
        with self.assertRaisesRegex(ValueError, 'verification_mode'): scene_check(s, (64, 48), 'ref-0')
        o['initialRequestedID'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'initial_request'):
            scene_check(s, (64, 48), 'ref-0', transition_visibility=True)


if __name__ == '__main__': unittest.main()
