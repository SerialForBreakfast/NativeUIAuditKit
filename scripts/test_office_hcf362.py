import unittest
import numpy as np
from office_hcf362 import change


class OfficeTests(unittest.TestCase):
    def test_unchanged_is_not_focus_truth(self):
        a=np.zeros((9,9,3),dtype=np.uint8)
        value=change(a,a)
        self.assertEqual(value['changedFraction'],0)
        self.assertTrue(all(r['fraction'] is None for r in value['regions']))

    def test_corner_energy(self):
        a=np.zeros((9,9,3),dtype=np.uint8);b=a.copy();b[:3,:3]=255
        value=change(a,b)
        self.assertAlmostEqual(value['changedFraction'],1/9)
        self.assertEqual(value['regions'][0]['fraction'],1)

    def test_dimensions(self):
        with self.assertRaises(ValueError):change(np.zeros((1,1,3)),np.zeros((2,2,3)))
