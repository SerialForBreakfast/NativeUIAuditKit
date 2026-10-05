import unittest
import numpy as np
from residual160 import nearest_positive


class NearestTests(unittest.TestCase):
    def test_positive_only_and_exact_alias(self):
        x=np.zeros((3,6,2,2),np.float32);x[1]=.5
        self.assertEqual(nearest_positive(x[0],x,np.array([0,1,1])),dict(index=2,rms=0.,exactEncodedAlias=True))
    def test_no_positive(self):
        x=np.zeros((2,6,2,2),np.float32)
        with self.assertRaisesRegex(ValueError,'no_positive'):nearest_positive(x[0],x,np.zeros(2))
    def test_nonfinite(self):
        x=np.zeros((2,6,2,2),np.float32);x[1]=np.nan
        with self.assertRaisesRegex(ValueError,'distance_inputs'):nearest_positive(x[0],x,np.ones(2))


if __name__=='__main__':unittest.main()
