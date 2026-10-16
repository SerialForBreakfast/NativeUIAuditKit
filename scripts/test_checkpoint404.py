"""Check restoration comparison failures without claiming model qualification."""
import unittest
import torch
from checkpoint404 import tensor_difference


class RestorationTests(unittest.TestCase):
    def test_equal_and_changed_tensors(self):
        self.assertEqual(tensor_difference({'a':torch.ones(2)},{'a':torch.ones(2)}),0)
        self.assertEqual(tensor_difference(torch.ones(2),torch.zeros(2)),1)

    def test_missing_state(self):
        with self.assertRaisesRegex(ValueError,'state_keys'):tensor_difference({'optimizer':{}},{})

    def test_nonfinite(self):
        with self.assertRaisesRegex(ValueError,'nonfinite'):tensor_difference(torch.tensor([float('nan')]),torch.ones(1))

    def test_shape_and_scheduler_changes(self):
        with self.assertRaisesRegex(ValueError,'shape'):tensor_difference(torch.ones(2),torch.ones(3))
        with self.assertRaisesRegex(ValueError,'state_value'):tensor_difference({'epoch':12},{'epoch':11})


if __name__=='__main__':unittest.main()
