import unittest
import hashlib
import numpy as np
import train_spatial135 as t


class SpatialFeaturesTests(unittest.TestCase):
    def test_features_identity_and_full_mask_control(self):
        torch=t.d.a.r.d.torch_runtime();torch.manual_seed(42)
        net=t.d.a.r.model(t.d.a.r.d.model(t.d.a.r.d.PAIRED_TEMPORAL_CONFIG))
        x=np.random.default_rng(7).random((3,6,128,192),dtype=np.float32)
        x[2,3:]=x[2,:3]
        f=t.features(net,x,np.ones((3,128,192),dtype=bool))
        self.assertEqual(f['raw'].shape,(3,1153))
        np.testing.assert_array_equal(f['raw'][:,1:577],f['raw'][:,577:])
        np.testing.assert_array_equal(f['raw'][:,1:577],f['spatial'][:,1:577])
        for z in f.values():np.testing.assert_array_equal(z[2,1:],0)
        # Zeroing only difference channels is not the same as ignoring RGB context.
        self.assertTrue(np.isfinite(f['spatial']).all())

    def test_source_bound_masks_missing_and_ambiguity(self):
        x=np.zeros((1,6,128,192),dtype=np.float32)
        key=hashlib.sha256(x[0,:3].tobytes()).hexdigest()
        frame=dict(encodedSHA256=key,size=[192,128],candidates=[dict(id='a',bounds=[1,2,10,10])])
        mask=t.pair_masks(x,{'a':frame})
        self.assertEqual(mask.sum(),100)
        with self.assertRaises(ValueError):t.pair_masks(x,{})
        with self.assertRaises(ValueError):t.pair_masks(x,{'a':frame,'b':dict(frame,candidates=[])})


if __name__=='__main__':unittest.main()
