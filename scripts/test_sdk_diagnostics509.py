import unittest
from unittest.mock import patch
from sdk_diagnostics509 import expanded, comparison


class DiagnosticTests(unittest.TestCase):
    def test_grayscale_reader_preserves_source_and_restores_after_error(self):
        from types import SimpleNamespace
        from PIL import Image
        from sdk_diagnostics509 import grayscale_inputs
        original = Image.new('RGB', (2, 2), (0, 0, 255))
        reader = lambda *args: original
        module = SimpleNamespace(image=reader)
        with self.assertRaisesRegex(ValueError, 'deliberate'):
            with grayscale_inputs(module):
                pixel = module.image('path', 'hash').getpixel((0, 0))
                self.assertEqual(pixel[0], pixel[1]); self.assertEqual(pixel[1], pixel[2])
                raise ValueError('deliberate')
        self.assertIs(module.image, reader)
        self.assertEqual(original.getpixel((0, 0)), (0, 0, 255))

    def test_context_keeps_center_and_preserves_original(self):
        box = [10, 20, 80, 24]
        self.assertEqual(expanded(box, 1.5), [-10, 14, 120, 36])
        self.assertEqual(box, [10, 20, 80, 24])
        self.assertEqual(expanded(box, 1.), box)
        with self.assertRaisesRegex(ValueError, 'context_scale'):
            expanded(box, 2.)
        self.assertEqual(expanded(box, 1.5, (100, 60)), [0, 14, 100, 36])
        with self.assertRaisesRegex(ValueError, 'outside_image'):
            expanded([120, 120, 20, 20], 1., (100, 100))

    def test_no_focus_and_temporal_regressions_are_not_hidden(self):
        for old, new in [('correct-abstention', 'false-selection'), ('correct', 'false-change')]:
            result = comparison(old, new)
            self.assertTrue(result['loss']); self.assertTrue(result['newWrong'])
        self.assertTrue(comparison('missed-change', 'correct')['gain'])

    def test_maximum_can_recover_departure_and_break_a_negative(self):
        from temporal_pairs414 import decision, outcome
        self.assertEqual(outcome(decision(max(.01, .99)), 1), 'correct')
        self.assertEqual(outcome(decision(max(.01, .99)), 0), 'false-change')

    def test_incomplete_source_cannot_enter_diagnostic(self):
        from pathlib import Path
        from sdk_diagnostics509 import completed
        with patch('sdk_diagnostics509.checked', return_value=Path('/a/attempt/out/report.json')), \
             patch('sdk_diagnostics509.q.load', return_value={'status': 'failed'}):
            with self.assertRaisesRegex(ValueError, 'source_incomplete'):
                completed({'path': 'unused', 'sha256': '0'*64})

    def test_report_requires_distinct_dependencies(self):
        from sdk_diagnostics509 import report_spec
        with self.assertRaisesRegex(ValueError, 'report_ids'):
            report_spec([{'id': 'same'}, {'id': 'same'}], 'report')
