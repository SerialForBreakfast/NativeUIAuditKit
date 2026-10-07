import unittest
import numpy as np
from native_focus_capture253 import matrix, background_contrast


class MatrixTests(unittest.TestCase):
    def test_background_contrast_and_geometry_veto(self):
        rgb = np.ones((40, 40, 3))*.4
        regions = {k: np.array([0., 0., 40., 40.]) for k in ('before','after','visible')}
        dark = (rgb, rgb, np.ones((40,40), bool), regions)
        self.assertEqual(background_contrast(dark, dark)['focusedInterior']['differingPixelFraction'], 0)
        light = (rgb, rgb+.1, dark[2], regions)
        self.assertAlmostEqual(background_contrast(dark, light)['focusedInterior']['meanAbsolute255'], 25.5)
        different = {**regions, 'after': regions['after']+1}
        self.assertFalse(background_contrast(dark, (rgb, rgb, dark[2], different))['comparableGeometry'])
        with self.assertRaisesRegex(ValueError, 'contrast_support'):
            background_contrast(dark, (rgb, rgb, np.zeros((40,40), bool), regions))

    def test_exact_cross_and_only_intended_changes(self):
        source = dict(appearance=dict(composition=dict(
            asset_pack=dict(assets=[dict(sha256='a'), dict(sha256='b')]),
            contents={'one': dict(title='fixed', asset=dict(sha256='b'))},
            definitions=dict(poster=dict(width=260, height=360)),
            background=dict(colors=[1, 2]))))
        entries = matrix(source)
        self.assertEqual(len(entries), 4)
        self.assertEqual({(e['factors']['widthPoints'], e['factors']['background']) for e in entries},
                         {(260, 'dark'), (260, 'light'), (360, 'dark'), (360, 'light')})
        for e in entries:
            c = e['recipe']['appearance']['composition']
            self.assertEqual(c['definitions']['poster']['height'], 360)
            self.assertEqual(c['contents']['one']['title'], 'fixed')
            self.assertEqual(c['contents']['one']['asset']['sha256'], 'a')
            self.assertEqual(e['role'], 'training')
            self.assertEqual(len(c['asset_pack']['assets']), 1)
        self.assertEqual(len(source['appearance']['composition']['asset_pack']['assets']), 2)


if __name__ == '__main__':
    unittest.main()
