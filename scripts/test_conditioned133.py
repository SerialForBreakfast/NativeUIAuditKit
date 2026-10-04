import unittest
import numpy as np
import conditioned133 as c


class ScaleTests(unittest.TestCase):
    def test_train_scale_and_zero_anchor(self):
        z=np.zeros((4,1153),dtype='float32');z[:,0]=[1,2,3,4];z[:,1]=[0,2,4,6]
        scale=c.scale_for(z);self.assertAlmostEqual(float(scale[0]),np.sqrt(5),places=6)
        self.assertEqual(scale[1],np.float32(.001))
        out=c.scaled(z,scale);np.testing.assert_array_equal(out[:,0],z[:,0])
        np.testing.assert_array_equal(out[0,1:],0)
        self.assertEqual(z[3,1],6)
        probe=z*100;c.scaled(probe,scale);np.testing.assert_array_equal(scale,c.scale_for(z))

    def test_invalid_scale(self):
        with self.assertRaises(ValueError):c.scale_for(np.ones((1,2)))
        with self.assertRaises(ValueError):c.scaled(np.zeros((1,1153)),np.zeros(1152))
        with self.assertRaises(ValueError):c.scale_for(np.full((2,1153),np.nan))


if __name__=='__main__':unittest.main()
