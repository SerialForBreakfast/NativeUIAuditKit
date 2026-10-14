"""Check matched seed comparisons without training."""
import copy
import unittest
from seed_review384 import compare


class SeedReviewTests(unittest.TestCase):
    def documents(self):
        row = dict(id='a', changed=1, group='g', role='development', images=['same'], baselineProbability=.9)
        return [dict(seed=seed, rows=[dict(**row, probability=probability)])
                for seed, probability in ((42, .9), (43, .8), (44, .91))]

    def test_variation_does_not_change_gate(self):
        result = compare(self.documents())
        self.assertTrue(result['rows'][0]['varied'])
        self.assertEqual(result['slices'][0]['losses'], {'42': 0, '43': 1, '44': 0})
        self.assertFalse(result['productionGateChanged'])

    def test_changed_identity_fails(self):
        docs = self.documents()
        docs[1]['rows'][0]['images'] = ['other']
        with self.assertRaises(ValueError):
            compare(docs)

    def test_missing_seed_fails(self):
        with self.assertRaises(ValueError):
            compare(self.documents()[:2])

    def test_duplicate_case_fails(self):
        docs = self.documents()
        docs[0]['rows'].append(copy.deepcopy(docs[0]['rows'][0]))
        with self.assertRaises(ValueError):
            compare(docs)


if __name__ == '__main__':
    unittest.main()
