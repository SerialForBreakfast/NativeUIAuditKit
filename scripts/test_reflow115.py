import unittest
import numpy as np
import diagnose_reflow115 as a


class AuditTests(unittest.TestCase):
    def test_decision_boundaries(self):
        self.assertEqual(a.decisions([0,.15,.5,.85,1]).tolist(),[0,0,-1,1,1])
        for p in ([float('nan')],[-.1],[1.1]):
            with self.assertRaises(ValueError):a.decisions(p)

    def test_contribution_reconstruction(self):
        rng=np.random.default_rng(42);f=rng.normal(size=(3,576));w=rng.normal(size=576)
        self.assertTrue(np.allclose(a.contribution_grid(f,w).sum((1,2)),f@w))
        with self.assertRaises(ValueError):a.contribution_grid(f[:,:5],w)

    def test_support_excludes_zero_and_respects_membership(self):
        f=np.array([[1.,0.],[0.,0.],[-1.,0.],[1.,0.]])
        self.assertEqual([r['index'] for r in a.nearest(f[0],f,[1,2,3])],[3,2])
        self.assertEqual(a.nearest(f[1],f,[0,2]),[])


if __name__=='__main__':unittest.main()
