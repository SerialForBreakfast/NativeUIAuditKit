"""Tests for RESET604 T3.1 / T3.2 training script guards and dataset preparation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import research_execution_policy as policy
import research_queue as q
import train_detector604 as td


class TrainDetector604Tests(unittest.TestCase):
    def test_rejects_non_pretrained_weights_by_default(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='td604-w-') as tmp:
            fake_pt = Path(tmp) / 'shipped_synthetic.pt'
            fake_pt.write_bytes(b'stub')
            with self.assertRaisesRegex(ValueError, 'train604_must_start_from_pretrained'):
                td.validate_config(fake_pt, 100, 640, 371)

    def test_validates_imgsz_and_epochs(self):
        with self.assertRaisesRegex(ValueError, 'train604_invalid_imgsz'):
            td.validate_config(q.ROOT / 'yolo11n.pt', 100, 320, 371)
        td.validate_config(q.ROOT / 'yolo11n.pt', 100, 640, 371)
        td.validate_config(q.ROOT / 'yolo11n.pt', 100, 960, 372)

    def test_run_training_prepares_dataset_and_writes_receipt(self):
        doc = q.load(q.ROOT / 'reports/work/RESET604/membership/membership-d1.json')
        train_sub = [r for r in doc['rows'] if r['role'] == 'train'][:3]
        cal_sub = [r for r in doc['rows'] if r['role'] == 'calibration'][:1]
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='td604-run-') as tmp:
            root = Path(tmp)
            mem_path = root / 'mem.json'
            q.save(mem_path, dict(doc, rows=train_sub + cal_sub))
            out_dir = root / 'run'
            fake_model = MagicMock()
            with patch('ultralytics.YOLO', return_value=fake_model) as mock_yolo:
                def _fake_train(**kw):
                    (out_dir / 'detector').mkdir(parents=True, exist_ok=True)
                    (out_dir / 'detector/args.yaml').write_text("optimizer: auto\nlr0: 0.01\namp: false\nseed: 371\n")
                fake_model.train.side_effect = _fake_train
                receipt = td.run_training(mem_path, out_dir, weights=q.ROOT / 'yolo11n.pt', epochs=100, imgsz=640, seed=371)
            mock_yolo.assert_called_once()
            fake_model.train.assert_called_once()
            kwargs = fake_model.train.call_args.kwargs
            self.assertTrue(Path(kwargs['project']).is_absolute())
            self.assertEqual(kwargs['epochs'], 100)
            self.assertEqual(kwargs['imgsz'], 640)
            self.assertEqual(kwargs['lr0'], 0.01)
            self.assertFalse(kwargs['amp'])
            self.assertEqual(receipt['policyMaxSeconds'], policy.TRAINING_SECONDS)
            self.assertEqual(receipt['resolvedTrainArgs']['optimizer'], 'auto')
            self.assertEqual(receipt['counts'], {'train': 3, 'calibration': 1})
            self.assertTrue((out_dir / 'train-receipt.json').is_file())
            with self.assertRaisesRegex(ValueError, 'train604_(output|receipt)_exists'):
                td.run_training(mem_path, out_dir, weights=q.ROOT / 'yolo11n.pt', epochs=100, imgsz=640, seed=371)

    def test_augmentation_profiles(self):
        doc = q.load(q.ROOT / 'reports/work/RESET604/membership/membership-d1.json')
        rows = [r for r in doc['rows'] if r['role'] == 'train'][:2] + [r for r in doc['rows'] if r['role'] == 'calibration'][:1]
        for name, expected in (('none', dict(rect=True, mosaic=0)), ('mosaic', dict(rect=False, mosaic=1.0, close_mosaic=10))):
            with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='td604-aug-') as tmp:
                root = Path(tmp); mem_path = root / 'mem.json'; q.save(mem_path, dict(doc, rows=rows))
                fake_model = MagicMock()
                with patch('ultralytics.YOLO', return_value=fake_model):
                    receipt = td.run_training(mem_path, root / 'run', epochs=1, imgsz=640, seed=371, augmentation=name)
                kwargs = fake_model.train.call_args.kwargs
                for key, value in expected.items():
                    self.assertEqual(kwargs[key], value)
                self.assertEqual((kwargs['fliplr'], kwargs['flipud'], kwargs['degrees']), (0, 0, 0))
                self.assertEqual(receipt['augmentation'], name)
        with self.assertRaisesRegex(ValueError, 'train604_invalid_augmentation'):
            td.run_training(mem_path, q.ROOT / '.build/td604-never', epochs=1, augmentation='flip')

    def test_training_watchdog_times_out_slow_fit(self):
        with self.assertRaisesRegex(TimeoutError, 'train604_timeout'):
            with td._training_watchdog(0.05):
                import time
                time.sleep(0.3)

    def test_t107_template_compiles_with_policy_limit_and_queue_run(self):
        import hcf_templates395 as ht
        from template_inputs398 import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='td604-t107-') as tmp:
            root = Path(tmp)
            init_pt = root / 'yolo11n.pt'
            init_pt.write_bytes(b'weights')
            cfg_path = root / 'config.json'
            init_pin = pin(init_pt)
            q.save(cfg_path, dict(initialization=init_pin, epochs=100, imgsz=640, seed=371, lr0=0.01, batch=8))
            doc = q.load(q.ROOT / 'reports/work/RESET604/membership/v2-d1/membership.json')
            mem_path = root / 'mem.json'
            q.save(mem_path, dict(doc, rows=[r for r in doc['rows'] if r['role'] == 'train'][:2] + [r for r in doc['rows'] if r['role'] == 'calibration'][:1]))
            mem_pin = pin(mem_path)
            spec = ht.build(dict(
                version='hcf-template-description-v1',
                id='reset604-d1-test-371',
                task='RESET604',
                owner='Maximum-mini-NUIAK',
                template='T107',
                question='Does v2-d1 improve TVBench dev detection across matched seeds?',
                decision='Report dev recall and AP50 vs matched baseline; do not promote.',
                inputs=dict(configuration=pin(cfg_path), initialization=init_pin, membership=mem_pin),
                parameters={},
                dependencies=[],
                training=dict(expectedScoreboardChange='Both seeds improve localization recall on frozen TVBench development beyond the measured noise floor.', 
                    experimentLogRunId='RESET604-TEST-371',
                    initialization=init_pin,
                    membership=[mem_pin],
                    epochs=100,
                    storageBudgetBytes=2 << 30,
                    acceptanceEvidence='tvbench-v2 dev matched control vs v2-d1 across seeds 371 and 372',
                    resume='restart',
                ),
            ))
            self.assertEqual(spec['limits']['timeoutSeconds'], policy.TRAINING_SECONDS)
            self.assertEqual(spec['adapter']['steps'], ['train_detector604.queue_run'])

            job_out = root / 'jobs/reset604-d1-test-371/attempts/001/output'
            job_out.mkdir(parents=True)
            q.save(job_out.parents[2] / 'spec.json', spec)
            fake_model = MagicMock()
            def _fake_train(**kw):
                (job_out / 'detector/weights').mkdir(parents=True, exist_ok=True)
                (job_out / 'detector/weights/last.pt').write_bytes(b'last')
                (job_out / 'detector/args.yaml').write_text("optimizer: auto\nlr0: 0.01\namp: false\nseed: 371\n")
                (job_out / 'detector/results.csv').write_text("epoch,train/box_loss,train/cls_loss,train/dfl_loss\n1,1.0,0.5,0.5\n")
            fake_model.train.side_effect = _fake_train
            prev_out = td.OUT
            td.OUT = job_out
            try:
                with patch('ultralytics.YOLO', return_value=fake_model):
                    receipt = td.queue_run()
            finally:
                td.OUT = prev_out
            self.assertEqual(receipt['epochs'], 100)
            self.assertTrue((job_out / 'final.pt').is_file())
            self.assertTrue((job_out / 'fit.json').is_file())
            self.assertTrue((job_out / 'history.json').is_file())


if __name__ == '__main__':
    unittest.main()
