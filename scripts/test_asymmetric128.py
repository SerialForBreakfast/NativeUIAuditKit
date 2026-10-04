import unittest
import numpy as np
from asymmetric128 import intensity,shift


class AsymmetricTests(unittest.TestCase):
    def setUp(self):
        self.x=np.zeros((1,6,4,8),dtype=np.float32)
        self.x[:,:,1:3,1:7]=np.arange(6,dtype=np.float32)/6
        self.mask=np.zeros_like(self.x,dtype=bool);self.mask[:,:,1:3,1:7]=True

    def test_intensity_only_requested_endpoint_and_content(self):
        original=self.x.copy()
        for ep in (0,1):
            out=intensity(self.x,self.mask,.8,.1,ep)
            np.testing.assert_array_equal(out[:,3*(1-ep):3*(1-ep)+3],self.x[:,3*(1-ep):3*(1-ep)+3])
            np.testing.assert_array_equal(out[~self.mask],self.x[~self.mask])
        np.testing.assert_array_equal(original,self.x)

    def test_shifts_no_wrap_and_identity_for_common_motion(self):
        for dx in (-2,2):
            out=shift(self.x,self.mask,dx,True)
            np.testing.assert_array_equal(out[:,:3],out[:,3:])
            np.testing.assert_array_equal(out[~self.mask],self.x[~self.mask])
            empty=slice(1,3) if dx>0 else slice(5,7)
            self.assertTrue((out[:,:,1:3,empty]==0).all())
            one=shift(self.x,self.mask,dx,False)
            np.testing.assert_array_equal(one[:,:3],self.x[:,:3])

    def test_invalid_contract(self):
        with self.assertRaises(ValueError):intensity(self.x,self.mask,.8,.1,2)
        with self.assertRaises(ValueError):shift(self.x,self.mask,0,False)


if __name__=='__main__':unittest.main()
