"""B405-128: check the 6-bit palette option of T10 and its Vision parity on the HCF396 membership."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import hcf_templates395 as templates
import template_adapters395 as adapter

JOBS = q.QUEUE / 'jobs'
SOURCE = JOBS / 'hcf396-10-compress/spec.json'
MEMBERSHIP = dict(path='reports/work/TEMPLATE395/revision2/runtime-membership.json',
                  sha256='2003692898ab02c9da827ec1ef840cc8d25730eda045563cb229336ec7ef1433')
TOOL = q.ROOT / '.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'


def hcf396_description(precision):
    spec = q.load(SOURCE)
    return dict(version='hcf-template-description-v1', id='palette6-test', owner='Maximum-mini-NUIAK', template='T10',
                question='Does the 6-bit palette option compile into a valid export job?', decision='Accept the export only when every Vision parity decision matches.',
                inputs=spec['template']['inputs'], dependencies=spec['dependencies'],
                parameters=dict(experimentalID='palette6-test', precision=precision))


def resolved_inputs():
    inputs = dict(q.load(SOURCE)['template']['inputs'])
    candidate = JOBS / 'template395r2-09-candidate/attempts/1/out/candidate.json'
    inputs['candidate'] = dict(path=q.relative(candidate), sha256=q.digest(candidate))
    return inputs


@unittest.skipUnless(SOURCE.is_file(), 'HCF396 queue evidence is not present')
class Palette6Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='palette6-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_description_requires_compression_inputs(self):
        spec = templates.build(hcf396_description('palette6weights'))
        self.assertEqual(spec['authority'], 'export')
        self.assertEqual(spec['limits']['timeoutSeconds'], 1800)
        doc = hcf396_description('palette6weights')
        del doc['inputs']['sourceReport']
        with self.assertRaisesRegex(ValueError, 'compression_inputs'):
            templates.build(doc)

    def test_int8_command_is_unchanged_and_palette6_adds_method(self):
        calls = []
        def stop(argv, output, name, timeout=180):
            calls.append(argv)
            raise RuntimeError('stop_after_command')
        for precision in ('int8weights', 'palette6weights'):
            with patch.object(adapter, 'command', side_effect=stop):
                with self.assertRaisesRegex(RuntimeError, 'stop_after_command'):
                    adapter.export(resolved_inputs(), dict(experimentalID='t', precision=precision), self.root)
        self.assertNotIn('--method', calls[0])
        self.assertEqual(calls[1][-2:], ['--method', 'palette6'])
        self.assertEqual(calls[0], calls[1][:-2])

    def test_unknown_precision_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'export_precision'):
            adapter.export(resolved_inputs(), dict(experimentalID='t', precision='int4weights'), self.root)

    @unittest.skipUnless(TOOL.is_file(), 'FocusRingTool is not built')
    def test_palette6_package_keeps_vision_parity_on_hcf396_membership(self):
        export = self.root / 'export-job'; export.mkdir()
        adapter.export(resolved_inputs(), dict(experimentalID='palette6-test', precision='palette6weights'), export)
        report = q.load(export / 'export/focus_ring_detector_training_report.json')
        self.assertTrue(report['size_gate_pass'])
        self.assertIn('6-bit-palette', report['method'])
        parity = self.root / 'parity-job'; parity.mkdir()
        adapter.parity(dict(export=dict(path=q.relative(export / 'export.json'), sha256=q.digest(export / 'export.json')),
                            membership=MEMBERSHIP), {}, parity)
        self.assertTrue(q.load(parity / 'parity.json')['comparison']['passed'])


if __name__ == '__main__':
    unittest.main()
