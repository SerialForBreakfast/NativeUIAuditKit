"""Verify retained recovery without any producer operation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import campaign_retained_review517 as adapter

class RetainedReviewTests(unittest.TestCase):
    def setUp(self):
        self.spec=q.load(q.ROOT/'reports/work/STREAM517/review-request.json')
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.out=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_retained_success_has_no_capture(self):
        with patch('ttr_campaign_queue493.Client',side_effect=AssertionError('No TTR calls permitted')):
            adapter.review(self.spec,self.out)
        self.assertFalse(q.load(self.out/'review.json')['newCapture'])
        self.assertEqual(q.load(self.out/'session-result.json')['acceptedFrames'],8)
    def test_corrupt_output_is_rejected(self):
        with patch.object(q,'outputs_intact',return_value=False):
            with self.assertRaisesRegex(ValueError,'review_outputs_changed'):adapter.review(self.spec,self.out)
    def test_incomplete_labels_are_rejected(self):
        with patch.object(adapter,'export_labels',return_value=([{}]*8,[])):
            with self.assertRaisesRegex(ValueError,'review_labels_changed'):adapter.review(self.spec,self.out)

if __name__=='__main__':unittest.main()
