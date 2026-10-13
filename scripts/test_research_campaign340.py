"""Check retained diagnostics without model execution."""
import unittest
from research_campaign340 import boundaries, reversal, TESTS


class CampaignTests(unittest.TestCase):
    def test_distinct_contracts(self):
        self.assertEqual(len(TESTS),20)
        self.assertEqual(len({t[0] for t in TESTS}),20)
        self.assertEqual([sum(t[0][0]==b for t in TESTS) for b in 'ABCD'],[5]*4)

    def test_reversal_counts(self):
        doc={'conditions':{k:{'probabilities':v} for k,v in {
            'native.npy':[.9,.1],'reverse_native.npy':[.5,.1],
            'replay.npy':[.9],'reverse_replay.npy':[.1]}.items()}}
        member={'rows':[{'changed':1,'group':'g'},{'changed':0,'group':'g'}],'replayLabels':[1]}
        r=reversal(doc,member)['comparisons']
        self.assertEqual(r['native.npy']['lostCorrect'],1)
        self.assertEqual(r['native.npy']['disagreements'],1)
        self.assertEqual(len(r['native.npy']['groups']),1)

    def test_reversal_missing_members(self):
        with self.assertRaises(ValueError):
            reversal({'conditions':{'native.npy':{'probabilities':[]},'reverse_native.npy':{'probabilities':[]}}},
                     {'rows':[{'changed':1}],'replayLabels':[]})

    def test_missing_boundary_measurement_stays_unavailable(self):
        row={'group':'g','measurements':{p:{'coverage':None,'purity':None} for p in ('old','boundary','retain_first')}}
        r=boundaries({'rows':[row]})
        self.assertEqual(r['unavailableRows'],1)
        self.assertEqual(r['measuredRows'],0)


if __name__=='__main__':unittest.main()
