import base64
import hashlib
import io
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from measure_native_focus253_mapping import decode_asset, map_asset, select_rows, color_upper_bound, frequency_scores, endpoint_scene, normalized_coordinates, run


class MappingTests(unittest.TestCase):
    def test_coordinate_reference_preserves_fit_and_scales(self):
        from measure_native_focus253 import coordinates
        shape = (40, 60); center = [30, 20]; box = [10, 10, 40, 20]
        reference = coordinates(shape, center)
        for mode, ratios in [('body', [.75, 1]), ('longest', [.75, .5])]:
            actual = normalized_coordinates(shape, center, box, ratios, mode)
            np.testing.assert_array_equal(actual, reference)
            scaled = normalized_coordinates((80, 120), [60, 40], [20, 20, 80, 40], ratios, mode)
            np.testing.assert_array_equal(scaled[0][::2, ::2], actual[0])
            np.testing.assert_array_equal(scaled[1][::2, ::2], actual[1])
        with self.assertRaisesRegex(ValueError, 'coordinate_parameters'):
            normalized_coordinates(shape, center, box, [0, 1], 'longest')

    def test_endpoint_binding_uses_image_not_filename(self):
        doc = dict(unfocused_sha256='a', focused_sha256='b',
                   baseline_scene={'focused_element_id': 'other'}, focused_scene={'focused_element_id': 'target'})
        self.assertEqual(endpoint_scene(doc, 'a')['focused_element_id'], 'other')
        self.assertEqual(endpoint_scene(doc, 'b')['focused_element_id'], 'target')
        with self.assertRaisesRegex(ValueError, 'endpoint_binding'): endpoint_scene(doc, 'c')
        with self.assertRaisesRegex(ValueError, 'endpoint_binding'):
            endpoint_scene({**doc, 'focused_sha256': 'a'}, 'a')
        with self.assertRaisesRegex(ValueError, 'output_name'): run('../escape')

    def test_identity_and_repeat(self):
        rgba = np.random.default_rng(4).random((20, 30, 4)); rgba[..., 3] = 1
        rgb, alpha = map_asset(rgba, (20, 30), [0, 0, 30, 20], 'fill', [.5, .5])
        np.testing.assert_array_equal(rgb, rgba[..., :3])
        np.testing.assert_array_equal(alpha, np.ones((20, 30)))
        np.testing.assert_array_equal(rgb, map_asset(rgba, (20, 30), [0, 0, 30, 20], 'fill', [.5, .5])[0])

    def test_fill_and_anchor(self):
        rgba = np.ones((4, 8, 4)); rgba[..., 0] = np.arange(8)/8
        left, _ = map_asset(rgba, (4, 4), [0, 0, 4, 4], 'fill', [0, .5])
        right, _ = map_asset(rgba, (4, 4), [0, 0, 4, 4], 'fill', [1, .5])
        np.testing.assert_array_equal(left[..., 0], rgba[:, :4, 0])
        np.testing.assert_array_equal(right[..., 0], rgba[:, 4:, 0])

    def test_fit_translation_and_clipping(self):
        rgba = np.ones((2, 4, 4))
        _, alpha = map_asset(rgba, (6, 6), [1, 1, 4, 4], 'fit', [.5, .5])
        self.assertEqual(int(alpha.sum()), 8)
        self.assertTrue(np.all(alpha[2:4, 1:5] == 1))
        _, clipped = map_asset(rgba, (4, 4), [-2, 1, 4, 2], 'fill', [.5, .5])
        self.assertEqual(int(clipped.sum()), 4)

    def test_premultiplied_alpha(self):
        rgba = np.array([[[1., 0, 0, 0], [0., 1, 0, 1]]])
        rgb, alpha = map_asset(rgba, (2, 4), [0, 0, 4, 2], 'fill', [.5, .5])
        self.assertTrue(np.all(rgb[..., 0] == 0))
        self.assertTrue(np.any((alpha > 0) & (alpha < 1)))

    def test_asset_identity_and_dimensions(self):
        output = io.BytesIO(); Image.new('RGB', (3, 2)).save(output, format='PNG')
        raw = output.getvalue()
        asset = dict(bytes=base64.b64encode(raw).decode(), sha256=hashlib.sha256(raw).hexdigest(), width=3, height=2)
        self.assertEqual(decode_asset(asset).shape, (2, 3, 4))
        with self.assertRaisesRegex(ValueError, 'asset_hash'):
            decode_asset({**asset, 'sha256': '0'*64})
        with self.assertRaisesRegex(ValueError, 'asset_dimensions'):
            decode_asset({**asset, 'width': 4})

    def test_bad_mapping(self):
        rgba = np.ones((3, 4, 4))
        for box, fit, anchor in [([0, 0, 0, 3], 'fill', [.5, .5]),
                                 ([0, 0, 4, 3], 'unknown', [.5, .5]),
                                 ([0, 0, 4, 3], 'fill', [float('nan'), .5])]:
            with self.assertRaisesRegex(ValueError, 'mapping_parameters'):
                map_asset(rgba, (3, 4), box, fit, anchor)

    def test_roles_duplicates_and_collision(self):
        rows = [dict(group='234:recipe-'+g, id=g+str(i), changed=1, conditions=['original_capture'], role='train')
                for g in ('00', '03') for i in range(4)]
        self.assertEqual(len(select_rows(rows)), 8)
        rows[0]['role'] = 'reserved'
        with self.assertRaisesRegex(ValueError, 'mapping_membership'): select_rows(rows)
        rows[0]['role'] = 'train'; rows[0]['id'] = rows[1]['id']
        with self.assertRaisesRegex(ValueError, 'mapping_membership'): select_rows(rows)
        with patch('pathlib.Path.exists', return_value=True):
            with self.assertRaisesRegex(ValueError, 'output_collision'): run()

    def test_color_oracle_and_frequency(self):
        rgb = np.random.default_rng(8).random((20, 20, 3)); mask = np.ones((20, 20), bool)
        target = rgb*.8+.1
        corrected, coefficients = color_upper_bound(rgb, target, mask)
        np.testing.assert_allclose(corrected, target, atol=1e-12)
        np.testing.assert_allclose(coefficients, [[.8, .1]]*3, atol=1e-12)
        self.assertEqual(frequency_scores(rgb, rgb, mask)['highFrequencyMAE255'], 0)
        with self.assertRaisesRegex(ValueError, 'mapping_support'):
            frequency_scores(rgb, target, np.zeros((20, 20), bool))


if __name__ == '__main__':
    unittest.main()
