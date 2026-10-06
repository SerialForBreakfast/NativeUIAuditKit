import unittest
from roi_style210 import paired_slots, precise_labels


class Slots(unittest.TestCase):
    def test_same_exposure_preserves_originals(self):
        old=['a','b','c'];new=['d','e','f','g']
        x=paired_slots(old,new)
        self.assertEqual(x,paired_slots(old,new))
        self.assertEqual(len(x['control']),len(x['treatment']))
        self.assertEqual(x['control'][:3],old)
        self.assertEqual(x['treatment'],old+new)
        self.assertEqual(set(x['control']),set(old))
        counts=[x['control'][3:].count(k) for k in old]
        self.assertLessEqual(max(counts)-min(counts),1)

    def test_ambiguous_membership_rejected(self):
        for old,new in [([],['a']),(['a'],[]),(['a','a'],['b']),(['a'],['a']),(['a'],['b','b'])]:
            with self.assertRaises(Exception):paired_slots(old,new)

    def test_precision_preserves_native_geometry_and_checks_export(self):
        ann={'elements':[{'elementType':'pageControl','boundsVisionNormalized':
            {'x':.123456789,'y':.25,'width':.1,'height':.03}}]}
        result=precise_labels(ann,['pageControl'],'0 0.173457 0.735000 0.100000 0.030000\n')
        self.assertAlmostEqual(float(result.split()[1]),.173456789,places=14)
        with self.assertRaises(Exception):
            precise_labels(ann,['pageControl'],'0 0.173457 0.736000 0.100000 0.030000\n')


if __name__=='__main__':unittest.main()
