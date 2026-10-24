"""Software qualification of the resident detector freeze path. No native training."""
import copy
import os
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q

os.environ.setdefault('YOLO_CONFIG_DIR', str(q.ROOT/'NativeUITrainer/.ultralytics'))
os.environ.setdefault('MPLCONFIGDIR', str(q.ROOT/'NativeUITrainer/.mplconfig'))
os.environ['YOLO_OFFLINE'] = 'true'
import torch
from ultralytics import YOLO
from ultralytics.engine.trainer import BaseTrainer
from train_yolo import FrozenYOLOBackbone, train_native_hcf
from detector_training419 import learning_rate


class FreezeTests(unittest.TestCase):
    def test_actual_backbone_and_head_update(self):
        torch.set_num_threads(2)
        model = YOLO(str(q.ROOT/'NativeUITrainer/yolo_runs/phase6a_r013/weights/best.pt')).model.float()
        guard = FrozenYOLOBackbone(model)
        for name, parameter in model.named_parameters():
            parameter.requires_grad_(not name.startswith(guard.prefixes) and '.dfl' not in name)
        trainer = SimpleNamespace(model=model, freeze_layer_names=list(guard.prefixes),
                                  ema=SimpleNamespace(ema=copy.deepcopy(model)))
        BaseTrainer._model_train(trainer)
        guard.verify(trainer)
        original = {k: p.detach().clone() for k, p in model.named_parameters() if p.requires_grad}
        optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad], lr=.001)
        output = model(torch.rand(2, 3, 64, 64))
        def tensors(value):
            if isinstance(value, torch.Tensor): return [value]
            if isinstance(value, dict): value = value.values()
            return [t for item in value for t in tensors(item)]
        loss = sum(t.square().mean() for t in tensors(output))
        loss.backward(); optimizer.step()
        guard.verify(trainer)
        self.assertTrue(any(not torch.equal(p, original[k]) for k,p in model.named_parameters() if k in original))
        self.assertTrue(all(not module.training for name,module in model.named_modules()
                            if name.startswith(guard.prefixes) and isinstance(module,torch.nn.BatchNorm2d)))
        key = next(k for k in guard.reference if k.endswith('running_mean'))
        model.state_dict()[key].add_(1)
        with self.assertRaisesRegex(ValueError, 'backbone_changed'): guard.verify(trainer)

    def test_wrong_architecture_and_config(self):
        with self.assertRaisesRegex(ValueError,'architecture'):
            FrozenYOLOBackbone(SimpleNamespace(yaml={'backbone':[]}))
        initial={'path':'unused','sha256':'a'*64}
        base=dict(initialization=initial, selection='fixed-last', patience=0)
        for invalid in ('true',1,None):
            with self.assertRaisesRegex(ValueError,'boolean'):
                learning_rate(dict(base,freezeBackbone=invalid),initial)
        self.assertEqual(learning_rate(dict(base,freezeBackbone=True),initial),.001)
        with self.assertRaisesRegex(ValueError,'boolean'):
            train_native_hcf(None,None,None,freeze_backbone=1)


if __name__ == '__main__': unittest.main()
