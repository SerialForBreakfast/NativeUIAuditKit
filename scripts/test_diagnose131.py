import unittest
import numpy as np
import diagnose131 as d


class DiagnosticsTests(unittest.TestCase):
    def test_affine_identity_and_local_change(self):
        rng=np.random.default_rng(5);before=rng.uniform(.1,.8,(1,3,12,16)).astype('float32')
        x=np.concatenate([before,before*.8+.1],axis=1);mask=np.ones_like(x,dtype=bool)
        rows=d.residuals(x,mask)
        self.assertLess(rows[0]['maximum'],1e-5)
        x[0,3,5,5]+=.05
        self.assertGreater(d.residuals(x,mask)[0]['maximum'],1/255)

    def test_guard_only_abstains_changed_nonidentity(self):
        rows=[dict(exactIdentity=False,maximum=0),dict(exactIdentity=True,maximum=0),
              dict(exactIdentity=False,maximum=0),dict(exactIdentity=False,maximum=.1)]
        p=np.array([.95,.99,.1,.95],dtype='float32')
        after,_=d.abstain(p,rows,1e-5)
        np.testing.assert_array_equal(after,np.array([.5,.99,.1,.95],dtype='float32'))
        np.testing.assert_array_equal(p,np.array([.95,.99,.1,.95],dtype='float32'))

    def test_opposing_duplicates_and_degenerate_features(self):
        r=d.separation(np.zeros((4,3)),np.array([0,0,1,1]))
        self.assertEqual(len(r['exactConflicts']),4);self.assertEqual(r['numericalRank'],0)
        self.assertIsNone(r['relativeMedian'])

    def test_validation(self):
        with self.assertRaises(ValueError):d.separation(np.ones((4,2)),np.ones(4))
        with self.assertRaises(ValueError):d.abstain([float('nan')],[{}],1e-5)

    def test_padding_is_not_equivalence_evidence(self):
        rng=np.random.default_rng(7);x=rng.uniform(.1,.8,(1,6,10,12)).astype('float32')
        mask=np.zeros_like(x,dtype=bool);mask[:,:,2:8,2:10]=True
        x[:,3:,2:8,2:10]=x[:,:3,2:8,2:10]*.8+.1
        self.assertLess(d.residuals(x,mask)[0]['maximum'],1e-5)

    def test_distance_report_matches_hand_calculation(self):
        row=d.separation(np.array([[0.],[1.],[3.],[4.]]),[0,0,1,1])
        self.assertEqual(row['sameDistances'],[1.,1.,1.,1.])
        self.assertEqual(row['oppositeDistances'],[3.,2.,2.,3.])
        self.assertEqual(row['relativeMedian'],2.5)


if __name__=='__main__':unittest.main()
