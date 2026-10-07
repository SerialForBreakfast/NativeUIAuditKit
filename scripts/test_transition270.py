"""Check the fixed training-only gate for the initialization comparison."""
import unittest
from transition270 import qualifies, CONFIG


class SelectionTests(unittest.TestCase):
    def result(self, correct, loss):
        return dict(summary=dict(correct=correct), meanBCE=loss)

    def test_requires_complete_confident_fit(self):
        self.assertFalse(qualifies(self.result(32, 1), self.result(63, .01)))

    def test_requires_low_loss(self):
        self.assertFalse(qualifies(self.result(32, 1), self.result(64, .1)))

    def test_rejects_tie_or_worse(self):
        self.assertFalse(qualifies(self.result(64, .01), self.result(64, .01)))
        self.assertFalse(qualifies(self.result(64, .01), self.result(64, .02)))

    def test_accepts_training_fit_improvement(self):
        self.assertTrue(qualifies(self.result(63, .001), self.result(64, .05)))
        self.assertTrue(qualifies(self.result(64, .05), self.result(64, .01)))

    def test_fixed_update_budget(self):
        self.assertEqual(CONFIG['epochs'] * (64 // CONFIG['batch']), 12480)


if __name__ == '__main__':
    unittest.main()
