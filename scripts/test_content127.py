import unittest
import numpy as np
from content127 import intervene


class ContentTests(unittest.TestCase):
    def test_disjoint_controls_reconstruct_full_intervention(self):
        x=np.arange(24,dtype=np.float32).reshape(1,6,2,2)/24
        mask=np.zeros_like(x,dtype=bool);mask[:,:,:,1]=True
        original=x.copy();content=intervene(x,mask,.8,.1);padding=intervene(x,mask,.8,.1,False)
        np.testing.assert_array_equal(content[~mask],x[~mask])
        np.testing.assert_array_equal(padding[mask],x[mask])
        np.testing.assert_allclose(content+padding-x,x*.8+.1,atol=1e-7)
        np.testing.assert_array_equal(original,x)

    def test_identical_pair_remains_identical(self):
        x=np.ones((1,6,2,2),dtype=np.float32)*.5
        mask=np.zeros_like(x,dtype=bool);mask[:,:,:,1]=True
        for content in (True,False):
            out=intervene(x,mask,.8,.1,content)
            np.testing.assert_array_equal(out[:,:3],out[:,3:])

    def test_invalid_mask_rejected(self):
        x=np.zeros((1,6,2,2),dtype=np.float32)
        with self.assertRaises(ValueError):intervene(x,np.zeros((2,2),dtype=bool),.8,.1)
        with self.assertRaises(ValueError):intervene(x,np.zeros_like(x),.8,.1)


if __name__=='__main__':unittest.main()
