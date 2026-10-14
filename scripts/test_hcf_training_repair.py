"""Test training preparation with a stub trainer. These are software tests, not model results."""
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import hcf_training375 as training
import research_queue as q


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.root = q.ROOT / '.build' / ('test-hcf-preparation-' + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root, True)
        self.out = self.root / 'out'
        self.out.mkdir()
        self.initial = self.root / 'initial.bin'
        self.initial.write_bytes(b'unit-test-initialization')
        self.source = self.root / 'source.png'
        self.source.write_bytes(b'unit-test-image-not-for-training')
        q.save(self.out / 'config.json', dict(datasetFolder='dataset',
            initialization=dict(path=q.relative(self.initial), sha256=q.digest(self.initial))))
        self.rows = [dict(id=role + '-' + profile, role=role, profile=profile, path=str(self.source),
                         sha256=q.digest(self.source), boxes={'focus': [0, 0, 10, 10]}, focus='focus', width=20, height=20)
                     for role in ('train', 'calibration') for profile in ('standard', 'hcf')]

    def trainer(self, dataset, initialization, out, progress, weights):
        import yaml
        value = yaml.safe_load(dataset.read_text())
        self.assertEqual(value['train'], 'images/train')
        self.assertEqual(value['val'], 'images/calibration')
        for role in ('train', 'calibration'):
            self.assertEqual(len(list((dataset.parent / 'images' / role).glob('*.png'))), 2)
        folder = out / 'detector'
        (folder / 'weights').mkdir(parents=True)
        (folder / 'results.csv').write_text('epoch,train/box_loss,train/cls_loss,train/dfl_loss\n1,1,2,3\n')
        path = folder / 'weights/best.pt'
        path.write_bytes(b'unit-test-output-not-a-model')
        return path

    def run_adapter(self):
        document = dict(rows=self.rows, cases=[], storage={}, trainingAdmitted=True)
        with patch.object(training, 'OUT', self.out), patch.object(training.study, 'dependency', return_value=[document]), \
             patch.object(training.study, 'verify_storage', return_value=self.root), \
             patch.object(training.study, 'validate_groups') as groups, \
             patch('train_yolo.train_native_hcf', side_effect=self.trainer):
            training.detector()
            groups.assert_called_once_with([])

    def test_roles_and_actual_history(self):
        self.run_adapter()
        self.assertEqual(q.load(self.out / 'fit.json')['epochs'], 1)
        self.assertEqual(q.load(self.out / 'history.json'), [dict(epoch=1, trainLoss=6.0)])

    def test_existing_directory_is_preserved(self):
        dataset = self.root / 'dataset'
        dataset.mkdir()
        original = dataset / 'keep.txt'
        original.write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'detector_dataset_exists'):
            self.run_adapter()
        self.assertEqual(original.read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
