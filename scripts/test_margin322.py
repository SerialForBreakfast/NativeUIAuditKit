"""Check score separation and training-only margin protection."""
import copy
import unittest
from unittest.mock import patch
import numpy as np
import torch
import margin322 as m
import nonlinear322 as n
import diagnose_guard322 as diagnostic


class MarginTests(unittest.TestCase):
    def test_feature_bound(self):
        x=np.array([[2.,0.],[0.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        result=diagnostic.fixed_feature_bound(x,y,np.ones(2),np.array([[0.],[1.]]))
        self.assertLess(result['minimumHinge'],result['baselineHinge'])
        self.assertGreaterEqual(result['minimumProtectedSlack'],-1e-7)
        with self.assertRaises(ValueError):diagnostic.fixed_feature_bound(x,y,np.ones(2),np.ones((1,2)))

    def test_separable_and_conflicting(self):
        x=np.array([[3.,0.],[-3.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        self.assertTrue(m.feasible(x,y)['feasible'])
        self.assertFalse(m.feasible(np.zeros((2,2)),y)['feasible'])
        z=m.separation(x,y,np.ones(2))
        self.assertEqual(z['protectedCount'],2)
        self.assertAlmostEqual(z['minimumHinge'],0.)
        with self.assertRaises(ValueError):m.separation(x,y,np.array([1.,-1.]))
        with self.assertRaises(ValueError):m.feasible(x,np.array([1.,2.]))

    def test_unrestricted_is_separate(self):
        x=np.array([[-3.,0.],[3.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        self.assertFalse(m.feasible(x,y)['feasible'])
        self.assertTrue(m.feasible(x,y,False)['feasible'])

    def test_guard_rejects_harmful_update(self):
        class Net(torch.nn.Module):
            def __init__(self):
                super().__init__();self.change=torch.nn.Module();self.change.fusion=n.Residual([0.,0.],[1.,1.])
        net=Net();x=np.array([[2.,0.],[-2.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        guard=n.Guard(net,x,y)
        with torch.no_grad():net.change.fusion.layers[2].bias.fill_(50.)
        guard(net)
        self.assertTrue(guard.valid(net));self.assertEqual(guard.limited,1)
        with self.assertRaises(ValueError):n.Guard(net,np.zeros((2,2),np.float32),y)

    def test_real_model_fit_freezes_branches(self):
        torch.manual_seed(42);torch.set_num_threads(2)
        base=m.r.extend(m.r.s.c.model.extend(m.b.worker.make_model(torch,paired_context=True)),2)
        net=n.make(base,[0.,0.],[1.,1.]);x=torch.tensor([[2.,0.],[-2.,0.],[0.,1.],[0.,-1.]])
        y=torch.tensor([1.,0.,1.,0.]);old={k:v.clone() for k,v in net.state_dict().items() if 'fusion.layers' not in k}
        cfg=dict(m.b.trainer.CONFIG,epochs=2,batch=2,fusionOnly=True,nonlinearFusion=True,marginLoss=True)
        initial=copy.deepcopy(net)
        guard=n.Guard(net,x.numpy(),y.numpy())
        net,h=m.b.trainer.fit(net,x,y,cfg,step_guard=guard)
        other,j=m.b.trainer.fit(initial,x,y,cfg,step_guard=n.Guard(initial,x.numpy(),y.numpy()))
        self.assertEqual([v['loss'] for v in h],[v['loss'] for v in j])
        self.assertEqual(sum(p.numel() for p in net.parameters() if p.requires_grad),33)
        for k,v in old.items():torch.testing.assert_close(v,net.state_dict()[k],rtol=0,atol=0)
        self.assertTrue(guard.valid(net));self.assertEqual(guard.calls,4)
        with self.assertRaises(ValueError):m.b.trainer.fit(net,x,y,dict(cfg,marginLoss=False),step_guard=guard)
        with self.assertRaises(ValueError):m.b.trainer.fit(net,x,y,dict(cfg,fusionOnly=False))

    def test_unknown_version_and_normalization(self):
        with patch.object(m.t,'load',return_value={'representation':'unknown'}):
            with self.assertRaisesRegex(ValueError,'nonlinear_checkpoint'):n.load('unused')
        with self.assertRaises(ValueError):n.Residual([0.,0.],[0.,1.])


if __name__=='__main__':unittest.main()
