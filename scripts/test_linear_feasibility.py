import unittest
import numpy as np
import linear_feasibility as f


class FeasibilityTests(unittest.TestCase):
    def test_feasible_minimum_norm_and_scale(self):
        x=np.array([[0,1,0],[0,0,-2],[3,0,0]],float);y=np.ones(3)
        r,w=f.solve(x,y)
        self.assertTrue(r['feasibleWitness']);self.assertAlmostEqual(r['infinityNorm'],f.TARGET,places=6)
        self.assertTrue(np.all(x[:,0]+x[:,1:]@w>=f.TARGET-1e-6))
        scaled=x.copy();scaled[:,1:]*=1e5;r2,w2=f.solve(scaled,y)
        self.assertTrue(r2['feasibleWitness']);np.testing.assert_allclose(w2*1e5,w,atol=1e-6)

    def test_contradiction_and_zero_feature(self):
        r,w=f.solve(np.array([[0,1],[0,1]]),np.array([0,1]))
        self.assertEqual(r['status'],2);self.assertIsNone(w)
        r,w=f.solve(np.array([[-3,0]]),np.array([0]))
        self.assertTrue(r['feasibleWitness']);np.testing.assert_array_equal(w,0)

    def test_invalid_contract(self):
        for x,y in [(np.array([[np.nan,1]]),[1]),(np.array([[0,1]]),[None]),(np.zeros((0,2)),[])]:
            with self.assertRaises(ValueError):f.solve(x,y)
        with self.assertRaises(ValueError):f.solve([[0,1]],[1],time_limit=61)


if __name__=='__main__':unittest.main()
