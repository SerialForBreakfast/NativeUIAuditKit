import unittest
import json
import numpy as np
from nuisance129 import affine,align,normalize,h


class NuisanceTests(unittest.TestCase):
    def test_trimmed_constant_support_keeps_identifiable_fit(self):
        x=np.full((3,10,20),.5,dtype=np.float32);x[:,0,:10]=.9
        actual,_=affine(x,.8*x+.1)
        np.testing.assert_allclose(actual,x,atol=2e-7)

    def test_affine_recovers_known_photometry(self):
        x=np.random.default_rng(2).uniform(.1,.9,(3,10,20)).astype(np.float32)
        actual,params=affine(x,.8*x+.1)
        np.testing.assert_allclose(actual,x,atol=2e-7)

    def test_horizontal_alignment_sign_and_zero_fill(self):
        x=np.random.default_rng(2).random((3,10,20),dtype=np.float32)
        y=np.zeros_like(x);y[:,:,2:]=x[:,:,:-2]
        actual,record=align(x,y);self.assertEqual(record['dx'],2)
        self.assertEqual(h.digest(record),h.digest(json.loads(json.dumps(record))))
        np.testing.assert_array_equal(actual[:,:,:-2],x[:,:,:-2])
        self.assertTrue((actual[:,:,-2:]==0).all())

    def test_identity_and_padding(self):
        x=np.zeros((1,6,8,12),dtype=np.float32);x[:,:,1:7,1:11]=.4
        mask=np.zeros_like(x,dtype=bool);mask[:,:,1:7,1:11]=True
        for mode in ('affine','align','combined'):
            actual,_=normalize(x,mask,mode);np.testing.assert_allclose(actual,x,atol=1e-7)
        with self.assertRaises(ValueError):normalize(x,mask,'invalid')


if __name__=='__main__':unittest.main()
