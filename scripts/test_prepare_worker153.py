import unittest
import numpy as np
from prepare_worker153 import validate


class MaskTests(unittest.TestCase):
    def fixture(self):
        x=np.zeros((108,6,128,192),dtype=np.float32)
        m=np.zeros(x.shape,dtype=bool);m[:,:,1:3,1:3]=True
        for i in range(216):x[i//2,(i%2)*3:(i%2+1)*3,1:3,1:3]=(i%178+1)/255
        return x,m

    def test_valid_and_binding(self):
        x,m=self.fixture();self.assertEqual(len(validate(x,m,x.copy())),178)
        other=x.copy();other[0,0,1,1]=0
        with self.assertRaisesRegex(ValueError,'binding'):validate(x,m,other)

    def test_padding_shape_and_conflict(self):
        x,m=self.fixture()
        with self.assertRaisesRegex(ValueError,'shape'):validate(x,m[:1],x)
        bad=m.copy();bad[0,0,1,1]=False
        with self.assertRaisesRegex(ValueError,'padding'):validate(x,bad,x)
        bad=m.copy();bad[0,:,4,4]=True
        with self.assertRaisesRegex(ValueError,'conflict'):validate(x,bad,x)


if __name__=='__main__':unittest.main()
