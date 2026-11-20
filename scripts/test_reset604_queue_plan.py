"""Tests for RESET604 T107 matched detector experiment queue specs."""
import tempfile
import unittest
from pathlib import Path

import research_execution_policy as policy
import research_queue as q
import reset604_queue_plan as rqp


class Reset604QueuePlanTests(unittest.TestCase):
    def test_builds_four_valid_matched_specs_with_policy_timeout(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='rqp-') as tmp:
            specs = rqp.build_matched_specs(out_dir=Path(tmp), seeds=(371, 372))
            self.assertEqual(len(specs), 4)
            ids = [s['id'] for s in specs]
            self.assertEqual(ids, [
                'reset604-v2d1-e100-s371',
                'reset604-v2d1-e100-s372',
                'reset604-v2f1-e100-s371',
                'reset604-v2f1-e100-s372',
            ])
            for s in specs:
                self.assertEqual(s['authority'], 'training')
                self.assertEqual(s['limits']['timeoutSeconds'], policy.TRAINING_SECONDS)
                self.assertEqual(s['adapter']['steps'], ['train_detector604.queue_run'])


if __name__ == '__main__':
    unittest.main()
