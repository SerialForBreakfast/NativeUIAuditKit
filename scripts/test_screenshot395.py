"""Check caller-owned screenshot output without operating a Simulator."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import direct_tvos_capture as capture


class ScreenshotTests(unittest.TestCase):
    def test_staged_copy_and_failure(self):
        with tempfile.TemporaryDirectory(dir=capture.ROOT / '.build') as folder:
            root = Path(folder)
            payload = b'\x89PNG\r\n\x1a\nsoftware-test-only'
            def success(argv, **kwargs):
                Path(argv[-1]).write_bytes(payload)
                return ''
            with patch.object(capture, 'ROOT', root), patch.object(capture, 'run', side_effect=success):
                capture.capture_screenshot('test-target', root / 'frame.png')
            self.assertEqual((root / 'frame.png').read_bytes(), payload)
            self.assertFalse(list((root / '.build/debug-output/native-screenshots').glob('*.png')))
            with patch.object(capture, 'ROOT', root), patch.object(capture, 'run', side_effect=ValueError('controlled failure')):
                with self.assertRaisesRegex(ValueError, 'controlled failure'):
                    capture.capture_screenshot('test-target', root / 'failed.png')
            self.assertFalse((root / 'failed.png').exists())


if __name__ == '__main__':
    unittest.main()
