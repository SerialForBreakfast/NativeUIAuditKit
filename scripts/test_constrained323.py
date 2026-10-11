"""Check direct fitting and conversion of protected output scores."""
import unittest
import numpy as np
import torch
import constrained323 as c
import reachability323 as reach


class ConstrainedTests(unittest.TestCase):
    def test_development_bound_is_constrained(self):
        x=np.array([[2.,0.],[-2.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        phi=np.ones((2,1));query=np.array([[0.,0.]],np.float32)
        result=reach.upper_scores(x,y,phi,query,np.ones((1,1)))
        self.assertAlmostEqual(result[0],2-(c.m.H+.25),places=6)
        with self.assertRaises(ValueError):reach.upper_scores(x,y,phi,query,np.ones((2,1)))

    def test_coefficients_and_frozen_features(self):
        net=torch.nn.Module();net.change=torch.nn.Module();net.change.fusion=c.n.Residual([0.,0.],[1.,1.])
        saved={k:v.clone() for k,v in net.state_dict().items() if '.layers.2.' not in k}
        c.apply_coefficients(net,np.linspace(-1,1,9))
        for k,v in saved.items():torch.testing.assert_close(v,net.state_dict()[k],rtol=0,atol=0)
        for bad in [np.zeros(8),np.ones(9)*2,np.ones(9)*np.nan]:
            with self.assertRaises(ValueError):c.apply_coefficients(net,bad)

    def test_constraints_reject_lost_success(self):
        x=np.array([[2.,0.],[-2.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        self.assertEqual(c.check_margins(x,y,np.array([2.,-2.]))['lostProtectedDecisions'],0)
        with self.assertRaises(ValueError):c.check_margins(x,y,np.array([1.,-2.]))
        with self.assertRaises(ValueError):c.check_margins(x,y,np.array([np.nan,-2.]))

    def test_direct_solver_and_float_conversion(self):
        x=np.array([[2.,0.],[0.,0.]],np.float32);y=np.array([1.,0.],np.float32)
        features=np.zeros((2,9));features[1,0]=1
        result=c.diagnostic.fixed_feature_bound(x,y,np.ones(2),features)
        coefficients=np.asarray(result['diagnosticCoefficients'],np.float32)
        logits=x.sum(1)+features.astype(np.float32)@coefficients
        c.check_margins(x,y,logits)
        self.assertLess(result['minimumHinge'],result['baselineHinge'])


if __name__=='__main__':unittest.main()
