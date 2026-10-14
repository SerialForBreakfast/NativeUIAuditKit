import unittest
from hcf_resume_review import assess
from hcf_complete_training import validate_completion


class ResumeTests(unittest.TestCase):
    def test_retained_shape_rejects_resume(self):
        result = assess(dict(epoch=8, optimizer={}, scaler={}))
        self.assertEqual(result['completedEpochs'], 9)
        self.assertEqual(result['missing'], ['scheduler', 'random_state'])
        self.assertFalse(result['resumeQualified'])

    def test_state_presence_does_not_claim_parity(self):
        result = assess(dict(epoch=8, optimizer={}, scheduler={}, random_state={}))
        self.assertEqual(result['decision'], 'requires-resume-parity-test')

    def test_invalid_epoch_rejects_resume(self):
        self.assertIn('epoch', assess(dict(epoch=-1))['missing'])

    def test_early_stop_cannot_complete_fixed_comparison(self):
        for epoch in (None, 9, 29, 31):
            with self.assertRaisesRegex(ValueError, 'detector_epochs_incomplete'):
                validate_completion(dict(epochs=epoch))
        validate_completion(dict(epochs=30))


if __name__ == '__main__':
    unittest.main()
