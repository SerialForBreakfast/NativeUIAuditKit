import unittest
import numpy as np
from replay_spatial163 import region

class RegionTests(unittest.TestCase):
    def test_odd_partitions_and_padding(self):
        mask=np.zeros((3,9,13),dtype=bool);mask[:,1:8,2:11]=True
        for a,b in [('left','right'),('top','bottom')]:
            x,y=region(mask,a),region(mask,b)
            self.assertFalse((x&y).any());self.assertTrue(np.array_equal(x|y,mask))
        center=region(mask,'center');self.assertEqual(center.sum(),3*4*4)
        self.assertFalse((center&~mask).any())
    def test_invalid_masks(self):
        mask=np.ones((3,7,9),dtype=bool)
        with self.assertRaisesRegex(ValueError,'unknown_arm'):region(mask,'bad')
        with self.assertRaisesRegex(ValueError,'empty_mask'):region(mask&False,'full')
        mask[:,3,3]=False
        with self.assertRaisesRegex(ValueError,'mask_rectangle'):region(mask,'full')

if __name__=='__main__':unittest.main()
