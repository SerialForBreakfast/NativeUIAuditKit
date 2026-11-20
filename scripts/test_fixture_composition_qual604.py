"""Tests for Fixture composition pre-capture expectation & reconciliation (`fixture_composition_qual604.py`)."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

import fixture_composition_qual604 as fcq
import research_queue as q


class FixtureCompositionQualTests(unittest.TestCase):
    def _sample_recipe(self):
        return {
            'schema_version': 1,
            'archetype': 'grid_matrix',
            'appearance': {
                'version': 1,
                'composition': {
                    'version': 5,
                    'definitions': {
                        'card': {'kind': 'composite_card', 'width': 500, 'height': 300},
                        'btn': {'kind': 'button', 'width': 300, 'height': 80},
                        'desc': {'kind': 'text', 'width': 600, 'height': 60},
                    },
                    'regions': [
                        {
                            'id': 'row_r',
                            'axis': 'row',
                            'frame': [100, 100, 1800, 340],
                            'gap': 40,
                            'content_insets': [10, 20, 10, 20],
                            'items': [
                                {'id': 'card_0', 'component': 'card'},
                                {'id': 'card_1', 'component': 'card'},
                                {'id': 'card_offscreen', 'component': 'card'},
                            ],
                        },
                        {
                            'id': 'text_btn_r',
                            'axis': 'column',
                            'frame': [100, 500, 800, 300],
                            'gap': 20,
                            'content_insets': [0, 0, 0, 0],
                            'items': [
                                {'id': 'synopsis_text', 'component': 'desc'},
                                {'id': 'action_btn', 'component': 'btn'},
                            ],
                        },
                    ],
                },
            },
            'capture_selection': {'version': 1, 'target_element_ids': ['card_0'], 'max_targets': 1},
        }

    def test_expected_from_composition_detects_offscreen_and_static_text(self):
        exp = fcq.expected_from_composition(self._sample_recipe(), scene_width=3840, scene_height=2160)
        # card_offscreen starts at x = 160 + (120 + 540 + 540) * 16/9 = 2293.33, clipped inside 3840 -> adjust to truly offscreen > 1920 pts
        recipe = self._sample_recipe()
        recipe['appearance']['composition']['regions'][0]['items'].append({'id': 'card_far', 'component': 'card'})
        recipe['appearance']['composition']['regions'][0]['items'].append({'id': 'card_offscreen_x', 'component': 'card'})
        exp2 = fcq.expected_from_composition(recipe, scene_width=3840, scene_height=2160)
        self.assertIn('card_offscreen_x', exp2['offscreenControls'])
        self.assertEqual(exp['staticTextIDs'], ['synopsis_text'])
        self.assertEqual(exp['targetFocusID'], 'card_0')

    def test_reconcile_catches_missing_and_static_text_button_errors(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as td:
            img_path = Path(td) / 'scene.png'
            im = Image.new('RGB', (3840, 2160), (20, 20, 30))
            draw = ImageDraw.Draw(im)
            exp = fcq.expected_from_composition(self._sample_recipe(), 3840, 2160)
            for _, item in exp['visibleControls'].items():
                x, y, w, h = item['box']
                draw.rectangle([x + 4, y + 4, x + w - 4, y + h - 4], fill=(220, 120, 80))
            im.save(img_path)

            good_scene = {
                'elements': [
                    {'element_id': 'card_0', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_0']['box'], 'is_focused': True},
                    {'element_id': 'card_1', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_1']['box'], 'is_focused': False},
                    {'element_id': 'card_offscreen', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_offscreen']['box'], 'is_focused': False},
                    {'element_id': 'synopsis_text', 'taxonomy_class': 'label', 'pixel_bounds': [160, 1000, 1000, 100], 'is_focused': False},
                    {'element_id': 'action_btn', 'taxonomy_class': 'secondaryButton', 'pixel_bounds': exp['visibleControls']['action_btn']['box'], 'is_focused': False},
                ],
                'semantic_inventory': {'coverage': 'complete_declared_composition', 'exclusions': {}, 'focus_known': True},
                'focused_element_id': 'card_0',
            }
            res_ok = fcq.reconcile_frame(good_scene, exp, 'card_0', image_path=img_path, focus_frame=True)
            self.assertTrue(res_ok['passed'])
            self.assertEqual(res_ok['exactMatches'], 4)

            bad_elements = list(good_scene['elements'])
            bad_elements[3] = {'element_id': 'synopsis_text', 'taxonomy_class': 'secondaryButton', 'pixel_bounds': [160, 1000, 1000, 100], 'is_focused': False}
            bad_scene = dict(good_scene, elements=bad_elements)
            res_bad = fcq.reconcile_frame(bad_scene, exp, 'card_0', image_path=img_path, focus_frame=True)
            self.assertFalse(res_bad['passed'])
            self.assertEqual(res_bad['extraControls'][0]['reason'], 'static_text_emitted_as_control')

    def test_shelf_axis_horizontal_and_occluded_elements_excluded(self):
        recipe = self._sample_recipe()
        recipe['appearance']['composition']['regions'][0]['axis'] = 'shelf'
        exp = fcq.expected_from_composition(recipe, 3840, 2160)
        # card_0 and card_1 must share y coordinate when axis == 'shelf'
        self.assertEqual(exp['visibleControls']['card_0']['box'][1], exp['visibleControls']['card_1']['box'][1])
        self.assertGreater(exp['visibleControls']['card_1']['box'][0], exp['visibleControls']['card_0']['box'][0])
        occluded_scene = {
            'elements': [
                {'element_id': 'card_0', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_0']['box'], 'is_focused': True},
                {'element_id': 'card_1', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_1']['box'], 'is_focused': False},
                {'element_id': 'card_offscreen', 'taxonomy_class': 'collectionItem', 'pixel_bounds': exp['visibleControls']['card_offscreen']['box'], 'is_focused': False},
                {'element_id': 'action_btn', 'taxonomy_class': 'secondaryButton', 'pixel_bounds': exp['visibleControls']['action_btn']['box'], 'is_focused': False},
                {'element_id': 'hidden_under_modal', 'taxonomy_class': 'secondaryButton', 'pixel_bounds': [160, 120, 200, 80], 'is_occluded': True},
            ],
            'semantic_inventory': {'coverage': 'complete_declared_composition', 'exclusions': {}, 'focus_known': True},
            'focused_element_id': 'card_0',
        }
        res = fcq.reconcile_frame(occluded_scene, exp, 'card_0', focus_frame=True)
        self.assertTrue(res['passed'])
        self.assertEqual(res['extraControls'], [])


if __name__ == '__main__':
    unittest.main()
