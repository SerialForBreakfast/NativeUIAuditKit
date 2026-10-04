import unittest
from diagnose_native88 import combine,rank_summary


class FrozenTests(unittest.TestCase):
    def test_confidence_is_required_for_joint(self):
        rows=[dict(id='a',split='train',changed=True),dict(id='b',split='development',changed=False)]
        boxes={v['id']:dict(bothBoxesCorrect=True) for v in rows}
        values,summary=combine(rows,[.7,.01],boxes,{'a'})
        self.assertTrue(values[0]['correct']);self.assertTrue(values[0]['abstained'])
        self.assertFalse(values[0]['joint']);self.assertTrue(values[1]['joint'])
        self.assertEqual(summary['addedNativeTrain']['joint'],0)
        with self.assertRaises(ValueError):combine(rows,[.7],boxes,{'a'})
        with self.assertRaises(ValueError):combine(rows,[float('nan'),.1],boxes,{'a'})

    def test_rank_and_size_describe_not_filter(self):
        rows=[dict(split='development',bestPositiveRank=rank,
            selected=dict(candidate=dict(bounds=[0,0,w,h]))) for rank,w,h in ((1,20,20),(2,15,15),(3,800,400))]
        result=rank_summary(rows)
        self.assertEqual(result['wrong'],2);self.assertEqual(result['wrongWithPositiveSecond'],1)
        self.assertEqual(result['wrongSmallSelection'],1)


if __name__=='__main__':unittest.main()
