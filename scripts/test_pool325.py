"""Check independent size placement and cached pooling training."""
import unittest
from unittest.mock import patch
import numpy as np
import torch
from PIL import Image
import pool325 as p


class PoolTests(unittest.TestCase):
    def setUp(self):torch.set_num_threads(2)

    def model(self,blend=0.):
        return p.make(p.r.extend(p.r.s.c.model.extend(p.b.worker.make_model(torch,paired_context=True)),2),blend).eval()

    def test_spike_retention(self):
        v=torch.zeros(1,24,32,48);v[:,:,1,1]=1
        self.assertGreater(float(p.pool(v,.5).max()),float(p.pool(v,0.).max()))
        with self.assertRaises(ValueError):p.pool(v,1.)

    def test_independent_size_and_position(self):
        images=[Image.new('RGB',(1920,1080),c) for c in ('black','white')]
        for size in (3,6,12):
            tiles=p.patch(images,size)
            im,boxes=p.compose([tiles,tiles],[(180,180),(1140,180)],0)
            self.assertEqual(im.size,(1920,1080));self.assertEqual(boxes[1][0]-boxes[0][0],960)
        with self.assertRaises(ValueError):p.compose([tiles,tiles],[(0,0),(10,10)],0)

    def test_cached_image_and_average_parity(self):
        net=self.model();x=torch.rand(2,18,128,192)
        with torch.inference_mode():
            cache=net.change.cached(x)
            torch.testing.assert_close(net.change(x),net.change(cache[0.]),rtol=0,atol=0)
            torch.testing.assert_close(net.change(x),p.r.RegionChange.forward(net.change,x),rtol=0,atol=0)
            net.change.blend=.5
            torch.testing.assert_close(net.change(x),net.change(cache[.5]),rtol=0,atol=0)

    def test_training_freezes_convolutions(self):
        net=self.model();x=torch.randn(4,1185);y=torch.tensor([0.,1.,0.,1.])
        before={k:v.clone() for k,v in net.state_dict().items()}
        config=dict(epochs=1,lr=.001,batch=2,seed=42,threads=2,detailOnly=True,cachedDetailOnly=True)
        p.b.trainer.fit(net,x,y,config,auxiliary_inputs=x,auxiliary_weight=.25)
        changed=[]
        for key,value in net.state_dict().items():
            if not torch.equal(value,before[key]):changed.append(key)
        self.assertTrue(changed)
        self.assertTrue(all(k.startswith(('change.detail.8.','change.correction.')) for k in changed))
        with self.assertRaises(ValueError):p.b.trainer.fit(net,x[:,:10],y,config)
        with self.assertRaises(ValueError):p.b.trainer.fit(net,x*float('nan'),y,config)

    def test_unknown_checkpoint(self):
        with patch.object(p.t,'load',return_value={'representation':'unknown'}):
            with self.assertRaises(ValueError):p.load('unused')


if __name__=='__main__':unittest.main()
