import unittest
import tempfile
from pathlib import Path
import numpy as np
import reversal147 as r


class ReversalTests(unittest.TestCase):
    def test_exact_involution_and_source_unchanged(self):
        x=np.zeros((2,6,128,192),np.float32);x[:,3:]=1
        original=x.copy();reverse=r.reverse(x)
        np.testing.assert_array_equal(r.reverse(reverse),x)
        np.testing.assert_array_equal(x,original)
        self.assertTrue((reverse[:,:3]==1).all())

    def test_invalid_pixels(self):
        for x in (np.zeros((1,3,128,192),np.float32),np.zeros((1,6,128,192),np.float64),
                  np.full((1,6,128,192),np.nan,np.float32),np.full((1,6,128,192),2,np.float32)):
            with self.assertRaises(ValueError):r.reverse(x)

    def test_admission_excludes_unknown_and_rejects_duplicates(self):
        family=dict(within_screen=[0,3,6,8,10],screen_transition=[4,7],identical_control=[5,9])
        ids,labels=r.native_labels(family)
        self.assertEqual(set(ids),{0,3,4,5,6,7,8,9,10});self.assertEqual(labels.sum(),7)
        family['identical_control']=[5,5]
        with self.assertRaises(ValueError):r.native_labels(family)

    def test_abstention_is_not_correct(self):
        self.assertEqual(r.summary([.99,.01,.5,.99],[1,0,1,0]),dict(count=4,correct=2,wrong=1,abstain=1))

    def test_real_entrypoint_rejects_output_collision_before_inputs(self):
        with tempfile.TemporaryDirectory(dir=r.h.ROOT/'.build') as directory:
            with self.assertRaises(ValueError):r.run(Path(directory))
            self.assertEqual(list(Path(directory).iterdir()),[])


if __name__=='__main__':unittest.main()
