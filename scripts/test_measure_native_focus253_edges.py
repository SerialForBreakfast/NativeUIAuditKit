import unittest
from unittest.mock import patch
import numpy as np
from measure_native_focus253_edges import rectangle,rounded,shadow_field,strength,composite,run,size_scale


class EdgeTests(unittest.TestCase):
    def test_background_and_repeat(self):
        before=np.full((80,100,3),.6);body=np.full_like(before,.9)
        alpha=rounded(before.shape[:2],[30,25,30,25],5);field=shadow_field(alpha,2,3)
        result=composite(before,body,alpha,field,.3)
        untouched=(alpha==0)&(field==0)
        self.assertGreater(untouched.sum(),0)
        np.testing.assert_array_equal(result[untouched],before[untouched])
        np.testing.assert_array_equal(result,composite(before,body,alpha,field,.3))

    def test_clipping(self):
        alpha=rounded((30,40),[-10,-5,30,25],4)*rectangle((30,40),[0,0,18,19])
        self.assertEqual(alpha[:,18:].sum(),0)
        self.assertEqual(alpha[19:,:].sum(),0)

    def test_shadow_strength_recovery_and_bounds(self):
        x=np.random.default_rng(4).random((80,3))
        self.assertAlmostEqual(strength([(x,x*.37)]),.37)
        self.assertEqual(strength([(x,-x)]),0)
        self.assertEqual(strength([(x,2*x)]),.8)
        self.assertEqual(strength([(x*0,x)]),0)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):rectangle((20,20),[0,0,0,4])
        with self.assertRaises(ValueError):rounded((20,20),[0,0,5,4],8)
        with self.assertRaises(ValueError):shadow_field(np.zeros((20,20)),0,0)
        with self.assertRaises(ValueError):shadow_field(np.zeros((20,20)),2,-1)

    def test_collision(self):
        with patch('pathlib.Path.exists',return_value=True):
            with self.assertRaisesRegex(ValueError,'output_collision'):run()

    def test_size_conditioned_growth(self):
        self.assertAlmostEqual(size_scale([0,0,400,500],80),1.16)
        self.assertAlmostEqual(size_scale([0,0,500,400],80),1.16)
        self.assertAlmostEqual(size_scale([0,0,400,1000],80),1.08)
        with self.assertRaises(ValueError):size_scale([0,0,400,0],80)
        with self.assertRaisesRegex(ValueError,'geometry_mode'):run(False,'observed')


if __name__=='__main__':unittest.main()
