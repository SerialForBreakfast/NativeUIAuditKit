"""Check review sampling without capture or training."""
import unittest
from unittest.mock import patch
import failure_review_sampling493 as review


def rows():
    return [dict(id=str(i), group='g'+str(i//2), profile='standard', arm='raw-proposal',
                 candidate='wrong' if i == 0 else 'miss', baseline='correct', noFocus=False,
                 gain=False, loss=True, newWrong=i == 0) for i in range(50)]


class ReviewTests(unittest.TestCase):
    def test_equal_size_and_reproducibility(self):
        a, b = review.sample(rows(), 'standard'), review.sample(rows()[::-1], 'standard')
        self.assertEqual(a['sampleSize'], 20)
        self.assertEqual(a['diverse']['groups'], 20)
        self.assertEqual(a['random'], b['random'])
        self.assertTrue(all(r['cases'] == 20 for r in a['random']))

    def test_sparse_and_empty(self):
        self.assertEqual(review.sample(rows()[:4], 'standard')['sampleSize'], 2)
        result = review.sample(rows(), 'hcf')
        self.assertEqual(result['sampleSize'], 0)
        self.assertEqual(result['outcome'], 'inconclusive')

    def test_successes_stay_in_summary_not_failure_pool(self):
        data=rows(); data[0]['candidate']='correct'
        self.assertEqual(review.sample(data, 'standard')['poolCases'], 49)
        self.assertEqual(review.summary(data)[0]['observations'], 50)

    def test_bad_version(self):
        with self.assertRaisesRegex(ValueError, 'review_input_version'):
            review.rebuild({'version':'invalid'})

    def test_recorded_outcome_cannot_override_recomputed_truth(self):
        row=rows()[0]
        pair=dict(rows=[dict(row, candidate='correct')], pair='one', sources={'baseline':{},'candidate':{}})
        with patch.object(review,'verified_report',return_value=dict(version='model-comparison-set-v1',comparisons=[pair])), \
             patch.object(review,'load_source',return_value=({}, {'model':{}})), \
             patch.object(review,'compare',return_value={'rows':[row]}):
            with self.assertRaisesRegex(ValueError,'review_outcome_changed'):
                review.rebuild(dict(version='failure-review-input-v1',source={}))
