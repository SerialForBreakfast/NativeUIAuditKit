"""Verify real crop encoder parameters and buffers, not a synthetic feature adapter."""
import unittest
import torch
from focus_ring_backbone import mobilenetv4_conv_small
from train_focus_ring_detector import freeze_crop_encoder, verify_crop_encoder
from hcf_factor_train376 import validate_config


class CropFreezeTests(unittest.TestCase):
    def test_real_encoder_and_buffers_stay_fixed_while_head_updates(self):
        torch.set_num_threads(2)
        torch.manual_seed(493)
        model = mobilenetv4_conv_small(num_classes=1)
        frozen = freeze_crop_encoder(model)
        before = model.classifier.bias.detach().clone()
        optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=3e-4)
        for _ in range(2):
            optimizer.zero_grad()
            logits = model(torch.rand(2, 3, 256, 256))
            torch.nn.functional.binary_cross_entropy_with_logits(logits, torch.ones_like(logits)).backward()
            optimizer.step()
        verify_crop_encoder(model, frozen)
        self.assertFalse(torch.equal(before, model.classifier.bias))
        self.assertEqual({n for n,p in model.named_parameters() if p.requires_grad},
                         {'classifier.weight', 'classifier.bias'})
        self.assertTrue(all(not m.training for m in model.modules() if isinstance(m, torch.nn.BatchNorm2d)))
        name = next(n for n in frozen if n.endswith('running_mean'))
        model.state_dict()[name].add_(1)
        with self.assertRaisesRegex(ValueError, 'crop_frozen_encoder_changed'):
            verify_crop_encoder(model, frozen)

    def test_wrong_head_and_bad_flags_fail(self):
        with self.assertRaisesRegex(ValueError, 'crop_freeze_classifier_contract'):
            freeze_crop_encoder(torch.nn.Linear(2, 1))
        base = dict(profile='balanced', deduplicate=False, seed=371)
        for flag in ('true', 1, None):
            with self.assertRaisesRegex(ValueError, 'freeze_encoder_invalid'):
                validate_config(dict(base, freezeEncoder=flag))
        for flag in (True, False):
            validate_config(dict(base, freezeEncoder=flag))
        validate_config(base)


if __name__ == '__main__':
    unittest.main()
