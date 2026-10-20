"""Test recovery publication repair without Simulator operations."""
import unittest
from unittest.mock import patch
import research_queue as q
import recovery_receipt_review as review
from experiment_templates import pin
from test_recovery_capture_gate437 import GateTests


class ReviewTests(GateTests):
    def review_spec(self):
        receipt = self.root/'retention.json'; q.save(receipt, dict(verified=True))
        result = q.load(self.attempt/'result.json')
        result.update(status='failed', reason='evidence_not_read:'+q.relative(receipt))
        q.save(self.attempt/'result.json',result,replace=True)
        return dict(reviewResult=pin(self.attempt/'result.json'), reviewSpec=pin(self.recovery/'spec.json'),
                    retentionReceipt=pin(receipt), expectedFailure=result['reason'])

    def test_reuses_verified_recovery_without_navigation(self):
        spec = self.review_spec()
        review.review(spec, self.output)
        receipt = q.load(self.output/'recovery.json')
        self.assertEqual(receipt['qualification'],pin(self.output/'qualification/qualification.json'))
        self.assertFalse(q.load(self.output/'review.json')['newCapture'])

    def test_rejects_other_failure(self):
        spec=self.review_spec();spec['expectedFailure']='process_failed'
        with self.assertRaisesRegex(ValueError,'review_failure_changed'):
            review.review(spec,self.output)

    def test_rejects_changed_outputs(self):
        spec=self.review_spec()
        (self.out/'restored-fixture.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'review_outputs_changed'):
            review.review(spec,self.output)

    def test_existing_dispatcher_selects_review_without_native_run(self):
        import hcf_recovery367 as dispatcher
        spec=dict(recoveryReview=True, capture=dict(plan=dict(path='unused.json',sha256='pinned')))
        with patch.object(dispatcher,'OUT',self.output), patch.object(q,'load',side_effect=[spec,dict(version='native-capture-recovery-v2')]), \
                patch.object(q,'digest',return_value='pinned'), patch.object(review,'review') as invoke:
            dispatcher.run()
        invoke.assert_called_once_with(spec,self.output)


if __name__ == '__main__':unittest.main()
