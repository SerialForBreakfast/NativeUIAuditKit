import unittest
from native_coverage_intent import intent,validate


class IntentTests(unittest.TestCase):
    def test_balanced(self):
        value=validate(intent());self.assertEqual(len(value['cases']),48)
        self.assertEqual(sum(c['proposedRole']=='development' for c in value['cases']),12)
    def test_duplicate(self):
        v=intent();v['cases'][1]=v['cases'][0]
        with self.assertRaises(Exception):validate(v)
    def test_dispatch_not_allowed(self):
        v=intent();v['dispatchable']=True
        with self.assertRaises(Exception):validate(v)
    def test_not_training_admission(self):
        v=intent();v['trainingEligible']=True
        with self.assertRaises(Exception):validate(v)


if __name__=='__main__':unittest.main()
