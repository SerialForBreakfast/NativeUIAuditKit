"""Keep region diagnostics separate from labels and original pixels."""
import unittest
import numpy as np
import spatial297 as s


class SpatialTests(unittest.TestCase):
    def test_clipping_and_empty(self):
        self.assertEqual(s.region_mask([]).sum(),0)
        self.assertEqual(s.region_mask([[-2,-2,4,4]]).sum(),4)
        with self.assertRaisesRegex(ValueError,'invalid_box'):s.region_mask([[0,0,-1,3]])

    def test_control_area_and_seed(self):
        mask=s.region_mask([[0,0,10,20]])
        a=s.control_mask(mask,42)
        self.assertEqual(a.sum(),mask.sum())
        np.testing.assert_array_equal(a,s.control_mask(mask,42))
        self.assertFalse(np.array_equal(a,mask))

    def test_interventions_do_not_change_source(self):
        value=np.zeros((6,128,192),np.float32);value[3:]=1
        mask=s.region_mask([[0,0,10,20]])
        keep=s.intervene(value,mask,True);remove=s.intervene(value,mask,False)
        self.assertEqual(keep[3:].sum(),600)
        self.assertEqual(remove[3:].sum(),3*(128*192-200))
        self.assertTrue((value[3:]==1).all())
        np.testing.assert_array_equal(keep[:3],value[:3])


if __name__=='__main__':unittest.main()
