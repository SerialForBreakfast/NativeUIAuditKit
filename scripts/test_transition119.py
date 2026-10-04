import unittest
import numpy as np
from audit_transition119 import endpoint_bank


class EndpointTests(unittest.TestCase):
    def test_shared_endpoint_unique_and_all_origins_retained(self):
        a={'sha256':'a'};b={'sha256':'b'}
        x=np.zeros((2,6,128,192),dtype=np.float32);x[0,3:]=1;x[1,:3]=1
        rows=endpoint_bank([[a,b],[b,a]],x)
        self.assertEqual(len(rows),2);self.assertEqual(rows[0]['origins'],[[0,0],[1,1]])
        self.assertEqual(rows[1]['origins'],[[0,1],[1,0]])

    def test_conflicting_tensor_or_membership_rejected(self):
        x=np.zeros((1,6,128,192),dtype=np.float32);x[:,3:]=1
        with self.assertRaisesRegex(ValueError,'same_image_different_tensor'):endpoint_bank([[{'sha256':'a'}]*2],x)
        with self.assertRaisesRegex(ValueError,'endpoint_membership'):endpoint_bank([],x)


if __name__=='__main__':unittest.main()
