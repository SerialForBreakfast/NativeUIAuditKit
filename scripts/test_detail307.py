"""Test aligned region selection without label access."""
import unittest
import numpy as np
from PIL import Image
import detail307 as d
import exposure307 as e


class DetailTests(unittest.TestCase):
    def test_empty_retains_model(self):
        self.assertEqual(d.windows([]), [])
        self.assertEqual(d.aggregate([], .91), .91)

    def test_order_and_limit(self):
        regions = [[x, 10, 2, 2] for x in range(6)]
        self.assertEqual(d.windows(regions), d.windows(list(reversed(regions))))
        self.assertEqual(len(d.windows(regions)), 4)

    def test_bad_geometry(self):
        for box in ([0, 0, -1, 2], [0, 0, float('nan'), 2]):
            with self.assertRaises(ValueError): d.windows([box])
        with self.assertRaisesRegex(ValueError, 'empty_region'):
            d.source_window([0, 0, 1, 1], (1920, 1080))

    def test_inverse_letterbox(self):
        self.assertEqual(d.source_window([0, 10, 192, 118], (1920, 1080)), (0, 0, 1920, 1080))
        self.assertEqual(d.source_window([10, 20, 20, 30], (1920, 1080)), (100, 100, 200, 200))

    def test_aligned_crop_keeps_unchanged(self):
        image = Image.fromarray(np.random.default_rng(42).integers(0, 256, (1080, 1920, 3), dtype=np.uint8))
        value = d.crop_pair([image, image], [0, 10, 32, 42])
        self.assertEqual(value.shape, (6, 128, 192))
        np.testing.assert_array_equal(value[:3], value[3:])

    def test_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'size_mismatch'):
            d.crop_pair([Image.new('RGB', (10, 10)), Image.new('RGB', (20, 20))], [0, 0, 10, 10])

    def test_invalid_score(self):
        with self.assertRaisesRegex(ValueError, 'invalid_score'): d.aggregate([float('nan')], .2)

    def test_losses_are_not_hidden_by_gains(self):
        rows = [dict(set='test', role='development', changed=y,
                     scores={'model': dict(whole=a, enlarged=b, source=b)})
                for y, a, b in [(1, 0, 1), (0, 0, 1)]]
        result = d.summarize(rows)[2]
        self.assertEqual((result['gains'], result['losses']), (1, 1))

    def test_exposure_reconciles_weights(self):
        rows = [dict(group='a', changed=1, condition='focus')]*2
        rows += [dict(group='b', changed=0, condition='content')]
        result = e.totals(rows, np.array([1., 1., 2.]))
        self.assertEqual([r['fraction'] for r in result], [.5, .5])
        self.assertEqual([r['entries'] for r in result], [2, 1])

    def test_exposure_rejects_invalid_weights(self):
        rows = [dict(group='a', changed=1, condition='focus')]
        for weights in (np.array([]), np.array([0.]), np.array([float('nan')])):
            with self.assertRaisesRegex(ValueError, 'weights'): e.totals(rows, weights)


if __name__ == '__main__': unittest.main()
