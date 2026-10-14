"""Check spatial attribution without Simulator access or image output."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from hcf_spatial_audit import audit, rectangle_mask, spatial_metrics, read_image


class SpatialTests(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((100, 200, 3), dtype=np.uint8)
        self.boxes = {'left': [[10, 10, 20, 20]], 'right': [[150, 10, 20, 20]]}

    def test_difference_moves_with_focus(self):
        for focus in self.boxes:
            changed = self.image.copy()
            changed[rectangle_mask(changed.shape[:2], self.boxes[focus])] = 100
            self.assertTrue(spatial_metrics(self.image, changed, self.boxes, focus, 5)['followsFocus'])
            other = 'right' if focus == 'left' else 'left'
            self.assertFalse(spatial_metrics(self.image, changed, self.boxes, other, 5)['followsFocus'])

    def test_global_change_does_not_pass(self):
        result = spatial_metrics(self.image, self.image+100, self.boxes, 'left', 5)
        self.assertFalse(result['followsFocus'])
        self.assertGreater(result['outsideDifference'], 0)

    def test_zero_difference_is_not_evidence(self):
        result = spatial_metrics(self.image, self.image, self.boxes, 'left', 5)
        self.assertFalse(result['followsFocus'])
        self.assertIsNone(result['controls']['left']['fractionOfDifference'])

    def test_overlap_fails(self):
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            spatial_metrics(self.image, self.image, self.boxes, 'left', 100)

    def test_negative_coordinates_do_not_wrap(self):
        mask = rectangle_mask((20, 20), [[-5, -5, 10, 10]])
        self.assertEqual(int(mask.sum()), 25)

    def test_invalid_box_fails(self):
        with self.assertRaisesRegex(ValueError, 'empty_rectangle'):
            rectangle_mask((20, 20), [[0, 0, -1, 3]])


class ManifestTests(unittest.TestCase):
    def document(self):
        frames = []
        for profile in ('standard', 'hcf'):
            for target in ('left', 'right'):
                for repeat in (0, 1):
                    elements = [dict(element_id=identity, is_focused=identity == target,
                        rendered_body_geometry=dict(availability='measured',
                            coordinate_space='image_top_left_pixels', source='native_body_presentation_layer',
                            visible_pixel_bounds=[x, 100, 20, 20])) for identity, x in (('left', 100), ('right', 400))]
                    scene = dict(elements=elements, is_settled=True, focused_element_id=target, recipe={'seed': 1},
                        focus_observation=dict(verified=True, source='uikit_focus_system', observedID=target))
                    frames.append(dict(profile=profile, focus=target, repeat=repeat, path=f'{profile}-{target}-{repeat}.png',
                        before=dict(scene=copy.deepcopy(scene)), after=dict(scene=copy.deepcopy(scene)),
                        profileReceipt=dict(receipt=dict(hcf=dict(status='completed', desiredVerified=True,
                            requested=profile, observed=profile)))))
        return dict(version='native-hcf362-v1', complete=True, cleanup=True, role='development',
                    trainingEligible=False, group='test-family', frames=frames)

    def evaluate(self, document):
        def image(_root, frame):
            array = np.zeros((250, 600, 3), dtype=np.uint8)
            if frame['profile'] == 'hcf':
                x = 100 if frame['focus'] == 'left' else 400
                array[100:120, x:x+20] = 200
            return array
        raw = json.dumps(document)
        with patch.object(Path, 'read_text', return_value=raw), \
             patch.object(Path, 'read_bytes', return_value=raw.encode()), \
             patch('hcf_spatial_audit.read_image', side_effect=image):
            return audit(Path('capture.json'))

    def test_complete_manifest(self):
        result = self.evaluate(self.document())
        self.assertTrue(result['followsFocus'])
        self.assertFalse(result['trainingEligible'])

    def test_duplicate_missing_and_unknown_version(self):
        for mutation in ('duplicate', 'missing', 'version'):
            document = self.document()
            if mutation == 'duplicate': document['frames'].append(document['frames'][0])
            if mutation == 'missing': document['frames'].pop()
            if mutation == 'version': document['version'] = 'unknown'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.evaluate(document)

    def test_false_observation_and_changed_recipe(self):
        for mutation in ('focus', 'recipe', 'geometry', 'profile'):
            document = self.document()
            frame = document['frames'][0]
            if mutation == 'focus': frame['after']['scene']['focus_observation']['verified'] = False
            if mutation == 'recipe': frame['after']['scene']['recipe']['seed'] = 2
            if mutation == 'geometry':
                frame['after']['scene']['elements'][0]['rendered_body_geometry']['visible_pixel_bounds'][0] += 1
            if mutation == 'profile': frame['profileReceipt']['receipt']['hcf']['desiredVerified'] = False
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.evaluate(document)

    def test_image_integrity_and_path(self):
        with self.assertRaisesRegex(ValueError, 'image_outside_capture'):
            read_image(Path('capture'), {'path': '../outside.png'})
        with patch.object(Path, 'read_bytes', return_value=b'changed'), self.assertRaisesRegex(ValueError, 'image_hash'):
            read_image(Path('capture'), {'path': 'frame.png', 'sha256': '0'*64})


if __name__ == '__main__':
    unittest.main()
