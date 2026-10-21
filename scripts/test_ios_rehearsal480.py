import copy
import unittest
from ios_rehearsal480 import eligible, interleave, mix


class RehearsalTests(unittest.TestCase):
    def row(self, name):
        return dict(role='train', trainingEligible=True, labelsComplete=True,
                    image=dict(sha256=name))

    def test_equal_counts_and_shared_membership(self):
        old=[self.row(str(i)) for i in range(4)]
        new=[self.row('native')]
        before=copy.deepcopy(old)
        control,mixed=mix(old,new,4)
        self.assertEqual(len(control),len(mixed))
        self.assertEqual(control[:3],mixed[:3])
        self.assertEqual(old,before)

    def test_role_and_duplicate_refusal(self):
        for key,value in [('role','development'),('trainingEligible',False),('labelsComplete',False)]:
            bad=self.row('new');bad[key]=value
            with self.assertRaisesRegex(ValueError,'rehearsal_role'):
                mix([self.row('a'),self.row('b')],[bad],2)
        with self.assertRaisesRegex(ValueError,'rehearsal_duplicate'):
            mix([self.row('a'),self.row('b')],[self.row('a')],2)

    def test_excludes_reserved_groups_and_pixels(self):
        rows=[dict(split=s,family=f,seed=n,pixelSHA256=p) for s,f,n,p in
              [('val','a',1,'x'),('train','a',1,'y'),('train','b',2,'x'),('train','c',3,'z')]]
        self.assertEqual(eligible(dict(integrityPassed=True,errors=[],members=rows)),[rows[-1]])

    def test_selection_is_order_independent(self):
        rows=[dict(family=f,imageID=str(i)) for i,f in enumerate(['b','a','b','a'])]
        self.assertEqual(list(interleave(rows)),list(interleave(rows[::-1])))

    def test_missing_inventory_and_short_population_fail(self):
        with self.assertRaisesRegex(ValueError,'rehearsal_inventory'):eligible({})
        with self.assertRaisesRegex(ValueError,'rehearsal_count'):mix([],[],64)


if __name__=='__main__':unittest.main()
