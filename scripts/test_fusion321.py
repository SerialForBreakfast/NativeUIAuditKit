"""Check frozen image branches and the score combination."""
import copy
import unittest
from unittest.mock import patch
import numpy as np
import torch
import fusion321 as f


class FusionTests(unittest.TestCase):
    def test_unknown_checkpoint(self):
        with patch.object(f.t,'load',return_value={'representation':'unknown'}):
            with self.assertRaisesRegex(ValueError,'fusion_checkpoint'):f.load_candidate('unused')

    def test_identity(self):
        layer=f.PositiveFusion();x=torch.tensor([[-20.,25.],[40.,-10.]])
        torch.testing.assert_close(layer(x).flatten(),x.sum(1))
        self.assertTrue((torch.nn.functional.softplus(layer.raw)>0).all())

    def test_margins(self):
        result=f.margins(np.array([[-3.,6.],[3.,-6.]],np.float32),np.array([1.,0.]))
        self.assertEqual(result['helpfulDetailButWrongContext'],2)
        self.assertEqual(result['summary']['correct'],2)
        for x,y in [(np.empty((0,2)),np.empty(0)),(np.ones((2,3)),np.ones(2)),
                    (np.array([[np.nan,1.]]),np.ones(1)),(np.ones((1,2)),np.array([2.]))]:
            with self.assertRaises(ValueError):f.margins(x,y)

    def test_training_and_image_parity(self):
        torch.manual_seed(42);torch.set_num_threads(2)
        base=f.r.extend(f.r.s.c.model.extend(f.b.worker.make_model(torch,paired_context=True)),2)
        images=torch.rand(4,6,128,192);detail=f.r.encoded_details(images,2)
        scores=f.branch_scores(base,images.numpy(),detail.numpy())
        net=f.extend(base);x=torch.from_numpy(scores);y=torch.tensor([0.,1.,0.,1.])
        with torch.inference_mode():
            torch.testing.assert_close(net.change(x),net.change(torch.cat((images,detail),1)),rtol=1e-5,atol=1e-6)
        frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.fusion.')}
        cfg=dict(f.b.trainer.CONFIG,epochs=2,batch=2,lr=.01,fusionOnly=True)
        second=copy.deepcopy(net)
        net,h=f.b.trainer.fit(net,x,y,cfg,auxiliary_inputs=x,auxiliary_weight=.25)
        second,j=f.b.trainer.fit(second,x,y,cfg,auxiliary_inputs=x,auxiliary_weight=.25)
        self.assertEqual([v['loss'] for v in h],[v['loss'] for v in j])
        self.assertEqual(sum(p.numel() for p in net.parameters() if p.requires_grad),3)
        for key,value in frozen.items():torch.testing.assert_close(value,net.state_dict()[key],rtol=0,atol=0)
        self.assertNotEqual(float(net.change.fusion.bias.detach()[0]),0.)
        for bad in [dict(fusionOnly=1),dict(fusionOnly=True,detailOnly=True),dict(fusionOnly=True,linearOnly=True)]:
            with self.assertRaises(ValueError):f.b.trainer.fit(net,x,y,dict(cfg,**bad))
        with self.assertRaises(ValueError):f.b.trainer.fit(net,x*float('nan'),y,cfg)
        with self.assertRaises(ValueError):f.b.trainer.fit(net,x,y,dict(cfg,fusionOnly=False))


if __name__=='__main__':unittest.main()
