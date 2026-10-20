import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import detector_retention478 as adapter
import research_queue as q


class RetentionTests(unittest.TestCase):
    def test_changes_only_snapshot_frequency(self):
        trainer = SimpleNamespace(save_period=1, args=SimpleNamespace(
            save_period=1, epochs=30, seed=371, lr0=.001))
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as directory:
            adapter.OUT = Path(directory)
            adapter.apply_retention(trainer)
            self.assertEqual(trainer.save_period, -1)
            self.assertEqual(vars(trainer.args),
                             dict(save_period=-1, epochs=30, seed=371, lr0=.001))
            self.assertTrue((adapter.OUT / 'checkpoint-retention.json').is_file())

    def test_unknown_trainer_policy_fails(self):
        trainer = SimpleNamespace(save_period=5, args=SimpleNamespace(save_period=5))
        with self.assertRaisesRegex(ValueError, 'source_changed'):
            adapter.apply_retention(trainer)
        self.assertEqual(trainer.save_period, 5)

    def test_callback_removed_after_failure(self):
        from ultralytics.utils.callbacks import default_callbacks
        before = list(default_callbacks['on_pretrain_routine_end'])
        with patch.object(adapter.training, 'run', side_effect=ValueError('expected')):
            with self.assertRaisesRegex(ValueError, 'expected'):
                adapter.run()
        self.assertEqual(default_callbacks['on_pretrain_routine_end'], before)


if __name__ == '__main__':
    unittest.main()
