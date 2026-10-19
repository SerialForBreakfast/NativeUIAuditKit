"""Check bounded review, evidence failures, and duplicate counting."""
import copy
import unittest
from unittest.mock import patch
import workflow_review437 as review


class ReviewTests(unittest.TestCase):
    def request(self):
        return dict(version='workflow-review-v1', batches=[dict(path='a', sha256='1'), dict(path='b', sha256='2')])

    def report(self, digest='1'):
        return dict(rows=[dict(job='same', expectedSHA256=digest, generated=True, dispatch='waiting')], counts={'waiting': 1})

    def run_review(self, results):
        with patch.object(review, 'checked', side_effect=lambda r: r['path']), patch.object(review.q, 'load', side_effect=lambda p: p), patch.object(review.workflow, 'inspect', side_effect=results):
            return review.review(self.request())

    def test_shared_jobs_count_once(self):
        result = self.run_review([self.report(), self.report()])
        self.assertEqual(result['uniqueGeneratedJobs'], 1)
        self.assertEqual(result['counts'], {'waiting': 1})
        self.assertFalse(result['executionChanged'])
        self.assertFalse(result['modelAccepted'])

    def test_bad_batch_does_not_hide_next_batch(self):
        result = self.run_review([ValueError('changed_hash'), self.report()])
        self.assertTrue(result['incomplete'])
        self.assertEqual(result['batches'][1]['status'], 'inspected')
        self.assertEqual(result['batches'][0]['reason'], 'changed_hash')

    def test_conflicting_specs_are_blocked(self):
        result = self.run_review([self.report(), self.report('2')])
        self.assertTrue(result['incomplete'])
        self.assertEqual(result['conflicts'], ['same'])
        self.assertEqual(result['counts'], {'blocked': 1})

    def test_duplicate_and_unbounded_requests_fail(self):
        request = self.request()
        request['batches'][1] = copy.deepcopy(request['batches'][0])
        with self.assertRaisesRegex(ValueError, 'review_duplicate_batch'):
            review.review(request)
        request['batches'] *= 7
        with self.assertRaisesRegex(ValueError, 'review_batch_limit'):
            review.review(request)

    def test_changed_manifest_is_not_inspected(self):
        with patch.object(review, 'checked', side_effect=ValueError('changed_hash')), patch.object(review.workflow, 'inspect') as inspect:
            result = review.review(self.request())
        self.assertTrue(result['incomplete'])
        inspect.assert_not_called()

    def test_summary_exposes_losses_outside_raw_proposals(self):
        slices = [dict(profile='standard', arm=arm, gains=0, losses=losses, newWrongSelections=0, observations=8, groups=2)
                  for arm, losses in [('raw-proposal', 0), ('known-box', 3)]]
        batch = dict(manifest={'path':'test'},status='inspected',report=dict(counts={'finished':1}, eta='ETA unavailable',
                     etaReason='No comparable history.', rows=[dict(job='decision', blockers=[], dispatch='finished',
                     decision=dict(outcome='contradicted', slices=slices, report='case-linked.json'))]))
        result = dict(uniqueGeneratedJobs=1, counts={'finished':1}, eta='ETA unavailable', incomplete=False, batches=[batch])
        text = review.summary(result)
        self.assertIn('| standard | known-box | 0 | 3 |', text)
        self.assertIn('case-linked.json', text)
        self.assertIn('Do not add these rows as independent trials', text)


if __name__ == '__main__':
    unittest.main()
