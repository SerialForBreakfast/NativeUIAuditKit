import unittest
import numpy as np
import spatial135 as s


class SpatialTests(unittest.TestCase):
    def test_rounded_letterbox_and_empty(self):
        empty = s.proposal_mask([], [100,200])
        self.assertFalse(empty.any())
        full = s.proposal_mask([dict(id='a',bounds=[0,0,100,200])], [100,200])
        self.assertEqual(int(full.sum()),64*128)
        self.assertTrue(full[:,64:128].all())
        self.assertFalse(full[:,:64].any())
        partial=s.proposal_mask([dict(id='b',bounds=[0,0,50,100])],[100,200])
        self.assertEqual(int(partial.sum()),32*64)

    def test_invalid_geometry_and_labels(self):
        for candidate in (dict(id='a',bounds=[-1,0,1,1]),dict(id='a',bounds=[0,0,101,1]),
                          dict(id='a',bounds=[0,0,1,1],focused=True)):
            with self.assertRaises(ValueError):s.proposal_mask([candidate],[100,200])
        with self.assertRaises(ValueError):s.proposal_mask([dict(id='a',bounds=[0,0,1,1])]*2,[100,200])

    def test_support_identity_and_local_energy(self):
        x=np.zeros((2,6,128,192),dtype=np.float32)
        m=np.zeros((2,128,192),dtype=bool);m[:,4:8,4:8]=True
        x[0,3:,4:8,4:8]=1
        before=x.copy()
        rows=s.support(x,m)
        self.assertEqual(rows[0]['insideDifferenceFraction'],1.)
        self.assertIsNone(rows[1]['insideDifferenceFraction'])
        np.testing.assert_array_equal(x,before)

    def test_real_scorer_empty_and_full_masks(self):
        torch=s.d.a.r.d.torch_runtime();torch.manual_seed(42)
        base=s.d.a.r.d.model(s.d.a.r.d.PAIRED_TEMPORAL_CONFIG)
        net=s.d.a.r.model(base)
        x=np.random.default_rng(2).random((2,6,128,192),dtype=np.float32)
        x[1,3:]=x[1,:3]
        full=s.score_modes(net,x,np.ones((2,128,192),dtype=bool))
        empty=s.score_modes(net,x,np.zeros((2,128,192),dtype=bool))
        np.testing.assert_array_equal(full['inside'],full['baseline'])
        np.testing.assert_array_equal(empty['outside'],empty['baseline'])
        for mode in full:
            self.assertEqual(full[mode][1],full['baseline'][1])


if __name__=='__main__':unittest.main()
