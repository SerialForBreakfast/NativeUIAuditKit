import unittest
from prepare_artwork213 import slots

class SlotTests(unittest.TestCase):
    def test_equal_budget_preserves_old_membership(self):
        old=[f'old{i}' for i in range(512)];new=[f'new{i}' for i in range(60)]
        result=slots(old,new);self.assertEqual(result,slots(old,new))
        self.assertEqual(len(result['control']),572);self.assertEqual(len(result['treatment']),572)
        self.assertEqual(result['control'][:512],old);self.assertEqual(result['treatment'][:512],old)
        self.assertEqual(result['treatment'][512:],new);self.assertTrue(set(result['control'][512:])<=set(old))
    def test_duplicates_overlap_and_partial_reject(self):
        old=[f'o{i}' for i in range(512)];new=[f'n{i}' for i in range(60)]
        for a,b in [(old[:-1],new),(old,new[:-1]),(old,new[:-1]+['o1']),(old,new[:-1]+new[:1])]:
            with self.assertRaises(ValueError):slots(a,b)

if __name__=='__main__':unittest.main()
