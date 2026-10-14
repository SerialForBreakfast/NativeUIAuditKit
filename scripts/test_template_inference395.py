"""Test inference adapter contracts with explicit stubs, not model evidence."""
import base64
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import template_adapters395 as adapter
from experiment_templates import pin


class InferenceContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='inference395-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / 'out'
        self.out.mkdir()

    def record(self, name, value):
        path = self.root / name
        q.save(path, value)
        return pin(path)

    def test_export_success_and_command_failure(self):
        weights = self.root / 'weights'
        weights.write_bytes(b'explicit software fixture')
        candidate = self.record('candidate.json', dict(version='template-candidate-v1', eligibleForExport=True,
            architecture='mobilenetv4_conv_small', checkpoint=pin(weights)))
        environment = self.record('environment.json', dict(interpreter='.venv-coreml/bin/python', configuration=pin(weights)))
        def command(argv, output, name, timeout):
            folder = output / 'export'
            folder.mkdir(exist_ok=True)
            if name == 'conversion':
                package = folder / 'FocusRingDetector.mlpackage'
                package.mkdir()
                (package / 'data').write_bytes(b'not a model')
                q.save(folder / 'focus_ring_detector_training_report.json',
                       dict(checkpointSHA256=pin(weights)['sha256'], size_gate_pass=True))
            else:
                compiled = folder / 'FocusRingDetector.mlmodelc'
                compiled.mkdir()
                (compiled / 'data').write_bytes(b'not a model')
        inputs = dict(candidate=candidate, environment=environment)
        parameters = dict(precision='fp16', experimentalID='software-test')
        with patch.object(adapter, 'command', side_effect=command):
            adapter.export(inputs, parameters, self.out)
        self.assertFalse(q.load(self.out / 'export.json')['modelAccepted'])
        with patch.object(adapter, 'command', side_effect=ValueError('command_failed:conversion')):
            with self.assertRaisesRegex(ValueError, 'command_failed:conversion'):
                adapter.export(inputs, parameters, self.out)

    def test_parity_pass_and_mismatch(self):
        import torch
        from PIL import Image
        import focus_runtime
        import train_focus_ring_detector as trainer
        class FixedNetwork(torch.nn.Module):
            def load_state_dict(self, state):
                pass
            def forward(self, values):
                return torch.full((len(values), 1), 2.1972246)
        stream = io.BytesIO()
        Image.new('RGB', (8, 8)).save(stream, format='PNG')
        crops = dict(results=[dict(png=base64.b64encode(stream.getvalue()).decode())])
        file = self.root / 'checkpoint'
        file.write_bytes(b'software fixture')
        export = dict(checkpoint=pin(file))
        rows = [dict(id='case', label=1)]
        inputs = dict(export={}, membership={})
        with patch.object(adapter, 'verified_export', return_value=(export, self.root)), \
             patch.object(adapter, 'runtime_items', return_value=(rows, rows)), \
             patch.object(focus_runtime, 'invoke', return_value=crops), \
             patch.object(trainer, 'load_mobilenetv4_conv_small', return_value=lambda **kw: FixedNetwork()), \
             patch.object(torch, 'load', return_value={'state_dict': {}}):
            with patch.object(adapter, 'vision', return_value=dict(results=[dict(probability=.9)])):
                adapter.parity(inputs, {}, self.out)
            self.assertTrue(q.load(self.out / 'parity.json')['comparison']['passed'])
            failed = self.root / 'failed'
            failed.mkdir()
            with patch.object(adapter, 'vision', return_value=dict(results=[dict(probability=.1)])):
                with self.assertRaisesRegex(ValueError, 'parity_failed'):
                    adapter.parity(inputs, {}, failed)
            self.assertFalse(q.load(failed / 'parity.json')['comparison']['passed'])

    def test_runtime_pass_and_invalid_repetitions(self):
        export = {}
        parity = self.record('parity.json', dict(export=export, comparison=dict(passed=True)))
        inputs = dict(export=export, membership={}, parity=parity)
        reply = dict(results=[dict(inferenceMilliseconds=2)], modelLoadMilliseconds=1)
        with patch.object(adapter, 'verified_export', return_value=({}, self.root)), \
             patch.object(adapter, 'runtime_items', return_value=([{}], [{}])), \
             patch.object(adapter, 'vision', return_value=reply):
            adapter.runtime(inputs, dict(repetitions=3), self.out)
            self.assertEqual(q.load(self.out / 'runtime.json')['samples'], 3)
            with self.assertRaisesRegex(ValueError, 'runtime_repetitions'):
                adapter.runtime(inputs, dict(repetitions=0), self.out)


if __name__ == '__main__':
    unittest.main()
