"""Check the fixed-feature dispatch without training."""
import unittest
from unittest.mock import patch
import transition246 as t


class DispatchTests(unittest.TestCase):
    def test_fixed_control_and_final_layers_only(self):
        original = t.trainer.OUT
        try:
            with patch.object(t.trainer, 'run') as run:
                t.run()
                run.assert_called_once_with(experiments=[('DTM065', False)],
                                            linear_only=True, matched_control=t.CONTROL)
                self.assertEqual(t.trainer.OUT, t.OUT)
                self.assertIn('TRANSITION-245/DTM063', str(t.CONTROL).replace('/artifacts', ''))
        finally:
            t.trainer.OUT = original


if __name__ == '__main__':
    unittest.main()
