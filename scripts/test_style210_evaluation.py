import unittest
from unittest.mock import patch
import evaluate_style210_extra as extra


class EvaluationBoundary(unittest.TestCase):
    def test_incomplete_training_never_infers(self):
        with patch.object(extra.training,'configure'), \
             patch.object(extra.training.previous.runner,'ready',side_effect=ValueError('training_failed')), \
             patch.object(extra.e,'export_predictions') as inference:
            with self.assertRaisesRegex(ValueError,'training_failed'):extra.run('control')
            inference.assert_not_called()

    def test_output_collision_never_infers(self):
        with patch.object(extra.training,'configure'), \
             patch.object(extra.training.previous.runner,'ready',return_value=('unused',{})), \
             patch('pathlib.Path.exists',return_value=True), \
             patch.object(extra.e,'export_predictions') as inference:
            with self.assertRaisesRegex(Exception,'output_collision'):extra.run('control')
            inference.assert_not_called()


if __name__=='__main__':unittest.main()
