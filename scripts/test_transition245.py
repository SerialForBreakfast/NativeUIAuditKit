"""Verify diagnostic masks and preservation checks without model training."""
import unittest
from unittest.mock import patch
import numpy as np
import transition245 as t


class RegionTests(unittest.TestCase):
    def test_union_keeps_all_controls(self):
        mask=t.union_mask([[2,2,4,4],[12,12,4,4]],(1,1,0,0),(20,20))
        self.assertTrue(mask[3,3]);self.assertTrue(mask[13,13])
        self.assertFalse(mask[9,9])

    def test_empty_regions_rejected(self):
        with self.assertRaisesRegex(ValueError,'empty_mask'):
            t.union_mask([],(1,1,0,0))

    def test_shift_does_not_wrap(self):
        mask=np.ones((2,4,8),dtype=bool)
        self.assertFalse(t.shifted(mask,2)[...,:2].any())
        self.assertFalse(t.shifted(mask,-2)[...,-2:].any())
        self.assertTrue(np.array_equal(mask,t.shifted(mask,0)))

    def test_same_mask_preserves_pair_reversal(self):
        x=np.arange(6*4*8).reshape(1,6,4,8)
        mask=np.zeros((1,1,4,8));mask[:,:,:,:4]=1
        self.assertTrue(np.array_equal(t.reverse(x*mask),t.reverse(x)*mask))

    def test_old_correct_cases_remain_required(self):
        before={'left8':{'probabilities':[.01,.99,.5]},'seal':'metadata'}
        after={'left8':{'probabilities':[.5,.01,.01]}}
        self.assertEqual(t.preservation(before,after),[dict(condition='left8',previousCorrectLost=1)])

    def test_collision_blocks_training(self):
        with patch.object(t,'OUT') as path,patch.object(t,'prepare') as prepare:
            path.exists.return_value=True
            with self.assertRaisesRegex(ValueError,'output_collision'):t.run()
            prepare.assert_not_called()


if __name__=='__main__':unittest.main()
