"""Check explicit staging and compression boundaries without device operations."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import direct_tvos_capture as capture
import template_bridge395 as bridge
import template_adapters395 as adapter
from experiment_templates import pin


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='hcf396-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_internal_staging_copy_preserves_usb_destination(self):
        internal = self.root / 'internal'
        destination = self.root / 'usb/frame.png'
        payload = b'\x89PNG\r\n\x1a\nsoftware-test'
        def produce(args, **kwargs):
            self.assertEqual(Path(args[-1]).parent, internal)
            Path(args[-1]).write_bytes(payload)
        with patch.object(capture, 'SCREENSHOT_STAGING', internal), patch.object(capture, 'run', side_effect=produce):
            capture.capture_screenshot('test-target', destination)
        self.assertEqual(destination.read_bytes(), payload)
        self.assertEqual(list(internal.iterdir()), [])

    def test_staging_rejects_path_outside_declared_project_before_capture(self):
        project = self.root / 'NativeUIAuditKit'
        project.mkdir()
        config = self.root / 'staging.json'
        q.save(config, dict(version='simulator-staging-v1', projectRoot=str(project), directory=str(self.root/'elsewhere')))
        out = self.root / 'out'
        out.mkdir()
        with patch.object(bridge, 'OUT', out), patch.object(bridge, 'contract', return_value=dict(inputs=dict(staging=pin(config)))), \
             patch.object(capture, 'capture_screenshot') as operation:
            with self.assertRaisesRegex(ValueError, 'staging_path'):
                bridge.capture()
            operation.assert_not_called()

    def test_compression_rejects_changed_source_before_conversion(self):
        weights = self.root / 'weights'
        weights.write_bytes(b'not a model')
        package = self.root / 'model.mlpackage'
        package.mkdir()
        (package / 'data').write_bytes(b'not a model')
        def doc(name, value):
            path = self.root / name
            q.save(path, value)
            return pin(path)
        inputs = dict(
            candidate=doc('candidate.json', dict(version='template-candidate-v1', eligibleForExport=True,
                architecture='mobilenetv4_conv_small', checkpoint=pin(weights))),
            environment=doc('environment.json', dict(interpreter='.venv-coreml/bin/python', configuration=pin(weights))),
            sourcePackage=doc('source.json', dict(path=q.relative(package), digestAlgorithm='focus-artifact-v1', sha256='0'*64)),
            sourceReport=doc('report.json', dict(checkpointSHA256=pin(weights)['sha256'])))
        with patch.object(adapter, 'command') as operation:
            with self.assertRaisesRegex(ValueError, 'compression_source_changed'):
                adapter.export(inputs, dict(precision='int8weights'), self.root)
            operation.assert_not_called()


if __name__ == '__main__':
    unittest.main()
