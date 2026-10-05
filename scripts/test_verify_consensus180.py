import unittest
import numpy as np
from verify_consensus180 import counts

class ConsensusTests(unittest.TestCase):
    def test_consensus_and_abstention(self):
        r=counts(np.array([[.15,.85,.1,.5],[.1,.9,.9,.5],[0,1,.9,.5]]),np.array([0,0,1,0]))
        self.assertEqual((r['unchanged'],r['changed'],r['abstain'],r['confidentFlips'],r['modelDisagreements']),(1,1,2,1,1))
    def test_invalid(self):
        for data in [np.zeros((2,1)),np.full((3,1),np.nan),np.full((3,1),1.1)]:
            with self.assertRaises(Exception):counts(data,np.array([0]))

if __name__=='__main__':unittest.main()
