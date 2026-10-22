"""Check bounded settings without starting model training."""
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
from checkpoint404 import repeat_value
from detector_training419 import learning_rate


class SettingsTests(unittest.TestCase):
    def test_repeat_defaults_and_supported_value(self):
        self.assertEqual(repeat_value({}),1)
        self.assertEqual(repeat_value({'repeat':9}),9)

    def test_repeat_rejects_wrong_types_and_fields(self):
        for cfg in ({'repeat':True},{'repeat':0},{'repeat':17},{'repeat':9.0},{'unknown':1}):
            with self.subTest(cfg=cfg), self.assertRaises(ValueError):repeat_value(cfg)

    def test_learning_rate_default_and_controlled_change(self):
        cfg=dict(initialization={'path':'fixed'},selection='fixed-last',patience=0)
        self.assertEqual(learning_rate(cfg,cfg['initialization']),.001)
        self.assertEqual(learning_rate(dict(cfg,learningRate=.0001),cfg['initialization']),.0001)
        for value in (True,0,-1,.1,float('nan')):
            with self.subTest(value=value),self.assertRaises(ValueError):
                learning_rate(dict(cfg,learningRate=value),cfg['initialization'])

    def test_learning_rate_rejects_configuration_drift(self):
        cfg=dict(initialization={},selection='best',patience=0)
        with self.assertRaises(ValueError):learning_rate(cfg,{})

    def test_resident_trainer_receives_only_changed_rate(self):
        import research_queue as q
        from train_yolo import train_native_hcf
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder);initial=root/'initial.pt';initial.write_bytes(b'test-only')
            with patch('ultralytics.YOLO') as model:
                train_native_hcf(root/'data.yaml',initial,root/'out',weights='last',patience=0)
                baseline=dict(model.return_value.train.call_args.kwargs)
                train_native_hcf(root/'data.yaml',initial,root/'out',weights='last',patience=0,learning_rate=.0001)
                candidate=dict(model.return_value.train.call_args.kwargs)
                self.assertEqual(baseline.pop('lr0'),.001)
                self.assertEqual(candidate.pop('lr0'),.0001)
                self.assertEqual(baseline,candidate)


if __name__=='__main__':unittest.main()
