import unittest
import numpy as np
import torch
import copy
import residual154 as r
from test_native_adapt152 import Toy
from page_style154 import proposal


class ResidualTests(unittest.TestCase):
    def test_conflicts(self):
        x=np.array([[1,2],[1,2],[2,3]],np.float32)
        self.assertEqual(r.conflicts(x,np.array([0,1,1])),[[0,1]])
        self.assertEqual(r.conflicts(x,np.array([0,0,1])),[])
    def test_balance_partition(self):
        w=r.balanced({'a':[0],'b':[1,2,3]},4)
        self.assertAlmostEqual(float(w.mean()),1)
        self.assertAlmostEqual(float(w[0]),float(w[1:].sum()))
        with self.assertRaises(ValueError):r.balanced({'a':[0],'b':[0,1]},2)
    def test_weight_validation(self):
        with self.assertRaisesRegex(ValueError,'weights'):
            r.n.fit(Toy(),torch.zeros(2,6,128,192),torch.zeros(2),r.n.CONFIG,weights=torch.tensor([1.,0.]))
    def test_weighted_loss_matches_manual_update(self):
        torch.manual_seed(7);a=Toy();b=copy.deepcopy(a)
        x=torch.rand(2,6,128,192);y=torch.tensor([0.,1.]);w=torch.tensor([1.5,.5])
        cfg=dict(r.n.CONFIG,epochs=1,batch=2)
        a,history=r.n.fit(a,x,y,cfg,weights=w)
        opt=torch.optim.Adam(b.change.parameters(),lr=cfg['lr'])
        ids=torch.randperm(2,generator=torch.Generator().manual_seed(cfg['seed']))
        loss=torch.nn.functional.binary_cross_entropy_with_logits(b.change(b.change_inputs(x[ids])).flatten(),y[ids],weight=w[ids])
        loss.backward();opt.step()
        self.assertEqual(history[0]['loss'],float(loss.detach()))
        for key,v in a.state_dict().items():self.assertTrue(torch.equal(v,b.state_dict()[key]))
    def test_style_proposal_rejects_unsupported(self):
        row=dict(prominent=False,scale=2,frame=[1,2,3,4])
        self.assertEqual(proposal(row,375,[73,26]),row['frame'])
        self.assertEqual(proposal(dict(row,prominent=True),375,[73,26]),[151,151,73,26])
        with self.assertRaises(ValueError):proposal(dict(row,scale=4),375,[73,26])


if __name__=='__main__':unittest.main()
