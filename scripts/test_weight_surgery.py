import unittest
import torch
from torch import nn
from weight_surgery import edit_parameters, restore_batchnorm_buffers

class SurgeryTests(unittest.TestCase):
    def setUp(self):
        self.model = nn.Module()
        self.model.bn = nn.BatchNorm1d(2)
        self.model.classifier = nn.Linear(2, 1)
        self.base = self.model.state_dict()
        self.donor = {k: v.clone() for k, v in self.base.items()}
        self.donor['classifier.weight'] += 2
        self.donor['bn.running_mean'] += 7

    def test_edit_preserves_buffers_and_sources(self):
        out, receipt = edit_parameters(self.model, self.base, self.donor, ['classifier.weight'], .5)
        torch.testing.assert_close(out['classifier.weight'], self.base['classifier.weight'] + 1)
        self.assertTrue(torch.equal(out['bn.running_mean'], self.base['bn.running_mean']))
        self.assertFalse(receipt['modelAccepted'])
        self.assertTrue(torch.equal(self.donor['bn.running_mean'], torch.full((2,), 7.)))

    def test_noop_is_exact(self):
        out, receipt = edit_parameters(self.model, self.base, self.donor, ['classifier.weight'], 0)
        self.assertEqual(receipt['changedParameters'], [])
        self.assertTrue(all(torch.equal(out[k], v) for k, v in self.base.items()))

    def test_batchnorm_restore_keeps_donor_parameters_exact(self):
        self.donor['bn.weight'] += .1234567
        self.donor['bn.num_batches_tracked'] += 19
        before = {k: v.clone() for k, v in self.donor.items()}
        out, receipt = restore_batchnorm_buffers(self.model, self.base, self.donor)
        for key, _ in self.model.named_parameters():
            self.assertTrue(torch.equal(out[key], self.donor[key]))
        for key, _ in self.model.named_buffers():
            self.assertTrue(torch.equal(out[key], self.base[key]))
        self.assertTrue(all(torch.equal(before[k], self.donor[k]) for k in before))
        self.assertIn('bn.num_batches_tracked', receipt['changedFromDonor'])
        self.assertFalse(receipt['modelAccepted'])

    def test_unknown_buffers_and_bad_donor_fail(self):
        self.model.register_buffer('unknown', torch.ones(1))
        a = self.model.state_dict(); b = {k: v.clone() for k, v in a.items()}
        with self.assertRaisesRegex(ValueError, 'non_batchnorm'):
            restore_batchnorm_buffers(self.model, a, b)
        del self.model._buffers['unknown']
        self.donor['classifier.weight'][0, 0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            restore_batchnorm_buffers(self.model, self.base, self.donor)
        self.donor['classifier.weight'] = torch.zeros(3, 3)
        with self.assertRaisesRegex(ValueError, 'checkpoint_tensor'):
            restore_batchnorm_buffers(self.model, self.base, self.donor)

    def test_rejections(self):
        for allowed, coefficient, offset in [(['bn.running_mean'], .5, 0), (['classifier.weight'], float('nan'), 0), (['classifier.weight'], .5, .5)]:
            with self.assertRaises(ValueError):
                edit_parameters(self.model, self.base, self.donor, allowed, coefficient, offset)
        self.donor['classifier.weight'][0, 0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            edit_parameters(self.model, self.base, self.donor, ['classifier.weight'], .5)

if __name__ == '__main__':
    unittest.main()
