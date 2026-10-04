import unittest
import numpy as np
import margin_retention as m


class MarginTests(unittest.TestCase):
    def test_previously_zero_slack_is_positive(self):
        x=np.zeros((1,1153),np.float32);x[0,0]=1.75;x[0,1]=1
        net=m.model(x,np.ones(1,np.float32));self.assertGreater(float(net.change.slack[0]),0)
        torch=m.r.a.r.d.torch_runtime();net.change.linear.weight.data[0,0]=-.001
        loss=net.change(torch.from_numpy(x)).sum();loss.backward()
        self.assertEqual(float(net.change.effective()[1].detach()),1)
        self.assertGreater(float(net.change.linear.weight.grad.norm()),0)

    def test_extreme_mixed_sign_updates_preserve_gate(self):
        torch=m.r.a.r.d.torch_runtime();rng=np.random.default_rng(19)
        x=rng.normal(size=(8,1153)).astype(np.float32);y=np.arange(8)%2
        x[:,0]=(2*y-1)*np.linspace(1.75,5,8)
        net=m.model(x,y)
        for magnitude in (0,.01,1000):
            net.change.linear.weight.data.copy_(torch.from_numpy((rng.normal(size=(1,1152))*magnitude).astype(np.float32)))
            with torch.no_grad():
                logits=net.change(torch.from_numpy(x)).flatten().numpy()
                self.assertTrue(((2*y-1)*logits>m.BOUNDARY).all())
                weights,radius=net.change.effective();self.assertGreater(float(radius),0)
                expected=torch.from_numpy(x[:,:1])+torch.nn.functional.linear(torch.from_numpy(x[:,1:]),weights)
                np.testing.assert_array_equal(logits,expected.flatten().numpy())
                identity=x.copy();identity[:,1:]=0
                np.testing.assert_array_equal(net.change(torch.from_numpy(identity)).flatten().numpy(),identity[:,0])

    def test_boundary_and_corruption_reject(self):
        x=np.zeros((1,1153),np.float32);x[0,0]=m.BOUNDARY
        with self.assertRaises(ValueError):m.model(x,np.ones(1,np.float32))
        x[0,0]=float('nan')
        with self.assertRaises(ValueError):m.model(x,np.ones(1,np.float32))


if __name__=='__main__':unittest.main()
