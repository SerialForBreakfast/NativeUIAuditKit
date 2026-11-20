import unittest
from hcf_confidence574 import strict_index

class StrictObserverTests(unittest.TestCase):
    def test_strict_filter_never_resolves_prior_ambiguity(self):
        self.assertIsNone(strict_index([.99,.90]))
        self.assertIsNone(strict_index([.84]))
        self.assertIsNone(strict_index([]))
    def test_score_and_competitor_requirements(self):
        self.assertEqual(strict_index([.96,.70]),0)
        self.assertIsNone(strict_index([.94,.1]))
        self.assertIsNone(strict_index([.99,.71]))
    def test_invalid_scores_fail(self):
        for s in [float('nan'),float('inf'),-1,1.1]:
            with self.assertRaisesRegex(ValueError,'invalid_score'):strict_index([s])

if __name__=='__main__':unittest.main()
