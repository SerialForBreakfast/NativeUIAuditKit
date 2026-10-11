"""Check frozen feature extraction and constrained score correction."""
import unittest
from unittest.mock import patch
import numpy as np
import torch
import features324 as f


class FeatureTests(unittest.TestCase):
    def setUp(self):torch.set_num_threads(2)

    def base(self):
        return f.r.extend(f.r.s.c.model.extend(f.b.worker.make_model(torch,paired_context=True)),2)

    def test_normalization_checks(self):
        center,scale=f.normalization(np.zeros((3,64),np.float32))
        self.assertTrue(np.all(scale>=.001));self.assertTrue(np.all(center==0))
        for x in [np.empty((0,64)),np.zeros((4,32)),np.full((2,64),np.nan)]:
            with self.assertRaises(ValueError):f.normalization(x)
        with self.assertRaises(ValueError):f.FeatureChange(torch.nn.Identity(),np.zeros(64),np.zeros(64))

    def test_image_cache_and_frozen_parity(self):
        net=self.base().eval();images=torch.rand(2,18,128,192)
        with torch.inference_mode():
            features,scores=f.retained(net.change,images)
            torch.testing.assert_close(scores.sum(1,keepdim=True),net.change(images),rtol=0,atol=0)
        original={k:v.clone() for k,v in net.change.state_dict().items()}
        net=f.make(net,np.zeros(64),np.ones(64)).eval()
        with torch.no_grad():net.change.readout.weight.fill_(.01)
        with torch.inference_mode():
            torch.testing.assert_close(net.change(images),net.change(torch.cat((features,scores),1)),rtol=0,atol=0)
        for k,v in original.items():torch.testing.assert_close(v,net.change.base.state_dict()[k],rtol=0,atol=0)

    def test_fallback_and_shape(self):
        net=self.base().eval();images=torch.zeros(1,6,128,192)
        with torch.inference_mode():
            _,scores=f.retained(net.change,images)
            torch.testing.assert_close(scores.sum(1,keepdim=True),net.change(images),rtol=0,atol=0)
        with self.assertRaises(ValueError):f.retained(net.change,torch.zeros(1,12,128,192))
        net=f.make(net,np.zeros(64),np.ones(64))
        for x in [torch.zeros(1,65),torch.full((1,66),float('nan'))]:
            with self.assertRaises(ValueError):net.change(x)

    def test_features_can_resolve_equal_scores(self):
        scores=np.zeros((2,2));labels=np.array([0.,1.]);weights=np.ones(2)
        result=f.d.fixed_feature_bound(scores,labels,weights,np.array([[-2.,1.],[2.,1.]]))
        self.assertLess(result['minimumHinge'],1e-8)
        self.assertGreater(result['baselineHinge'],3)

    def test_unknown_checkpoint_version(self):
        with patch.object(f.t,'load',return_value={'representation':'unknown'}):
            with self.assertRaises(ValueError):f.load('unused')

    def test_features_do_not_require_labels_at_inference(self):
        base=self.base().change.eval();images=torch.rand(1,18,128,192)
        with torch.inference_mode():
            features,scores=f.retained(base,images)
        self.assertEqual(features.shape,(1,64));self.assertEqual(scores.shape,(1,2))
        self.assertTrue(torch.isfinite(features).all())


if __name__=='__main__':unittest.main()
