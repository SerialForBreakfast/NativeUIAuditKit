"""Initialization verification tests. These tests do not establish model accuracy."""
import copy
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
import torch
import research_queue as q
from detector_initializer567 import InitializerGuard
from detector_training419 import learning_rate


class InitializerTests(unittest.TestCase):
    def test_guard_rejects_reset_weights_and_seed(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='init567-') as temp:
            model=torch.nn.Linear(2,1);guard=InitializerGuard(model,42,Path(temp))
            trainer=SimpleNamespace(model=copy.deepcopy(model),args=SimpleNamespace(seed=42))
            guard.verify(trainer)
            trainer.args.seed=371
            with self.assertRaisesRegex(ValueError,'initializer_seed'):guard.verify(trainer)
            trainer.args.seed=42
            with torch.no_grad():trainer.model.bias.add_(1)
            with self.assertRaisesRegex(ValueError,'initializer_changed'):guard.verify(trainer)

    def test_config_preserves_defaults(self):
        pin=dict(path='unused',sha256='a'*64);base=dict(initialization=pin,selection='fixed-last',patience=0)
        self.assertEqual(learning_rate(base,pin),.001)
        self.assertEqual(learning_rate(dict(base,seed=42,verifyInitialization=True),pin),.001)
        with self.assertRaisesRegex(ValueError,'detector_seed'):learning_rate(dict(base,seed=0),pin)

    def test_resident_trainer_preserves_both_role_heads(self):
        import os
        os.environ.setdefault('YOLO_CONFIG_DIR',str(q.ROOT/'NativeUITrainer/.ultralytics'))
        os.environ.setdefault('MPLCONFIGDIR',str(q.ROOT/'NativeUITrainer/.mplconfig'))
        os.environ['YOLO_OFFLINE']='true'
        from ultralytics import YOLO
        from ultralytics.models.yolo.detect.train import DetectionTrainer
        torch.set_num_threads(2)
        for arm in ('random','projected'):
            source=q.ROOT/'reports/work/research-queue/jobs/surgery562-detector-heads/attempts/1/out'/(arm+'.pt')
            model=YOLO(str(source)).model.float()
            trainer=DetectionTrainer.__new__(DetectionTrainer)
            trainer.data=dict(nc=13,channels=3,names=model.names)
            trainer.args=SimpleNamespace(cls_remap=True)
            with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='reload567-') as temp:
                guard=InitializerGuard(model,42,Path(temp))
                rebuilt=trainer.get_model(cfg=model.yaml,weights=model,verbose=False)
                guard.verify(SimpleNamespace(model=rebuilt,args=SimpleNamespace(seed=42)))
