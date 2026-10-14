"""Test suite integrity and recovery with explicit test-only predictions."""
import copy
import fcntl
import tempfile
import subprocess
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

import evaluation_suite391 as s
from test_standard390 import document


class SuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=s.q.ROOT / '.build', prefix='suite391-test-')
        self.root = Path(self.temp.name)
        self.out = self.root / 'out'
        control, candidate = document(.99), document(.1)
        self.write('control.json', control)
        self.write('candidate.json', candidate)
        self.write('expected.json', dict(comparisons=[dict(controlJob='c', candidateJob='n', **s.standard390.compare(control, candidate))]))
        self.manifest = dict(version=s.VERSION, evidence=[self.pin('control.json')], slices=[dict(id='first',
            control=self.pin('control.json'), candidate=self.pin('candidate.json'), expected=self.pin('expected.json'),
            controlJob='c', candidateJob='n', cases=1)])

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, doc):
        s.q.save(self.root / name, doc, replace=(self.root / name).exists())

    def pin(self, name):
        return dict(path=name, sha256=s.q.digest(self.root / name))

    def run_suite(self, **kwargs):
        return s.execute(self.manifest, self.out, root=self.root, **kwargs)

    def test_exact_comparison_and_resume(self):
        first = self.run_suite()
        original = (self.out / 'suite.json').read_bytes()
        second = self.run_suite()
        self.assertEqual(first['computed'], 1)
        self.assertEqual(second['resumed'], 1)
        self.assertEqual(second['computed'], 0)
        self.assertEqual(original, (self.out / 'suite.json').read_bytes())
        self.assertFalse(second['modelAccepted'])

    def test_changed_input_on_resume(self):
        self.run_suite()
        self.write('candidate.json', document(.8))
        with self.assertRaisesRegex(ValueError, 'input_changed'):
            self.run_suite()

    def test_changed_output_on_resume(self):
        self.run_suite()
        s.q.save(self.out / 'first.json', {}, replace=True)
        with self.assertRaisesRegex(ValueError, 'resume_output_changed'):
            self.run_suite()

    def test_resume_contract_change(self):
        self.run_suite()
        self.manifest['slices'][0]['cases'] = 2
        with self.assertRaisesRegex(ValueError, 'resume_contract_changed'):
            self.run_suite()

    def test_interruption_between_output_and_receipt(self):
        original = s.q.save
        def fail_receipt(path, doc, **kwargs):
            if str(path).endswith('.receipt.json'):
                raise OSError('test interruption')
            return original(path, doc, **kwargs)
        with patch.object(s.q, 'save', side_effect=fail_receipt), self.assertRaises(OSError):
            self.run_suite()
        result = self.run_suite()
        self.assertEqual(result['computed'], 1)
        self.assertTrue(result['complete'])

    def test_duplicate_slice(self):
        self.manifest['slices'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate_or_invalid_slice'):
            self.run_suite()

    def test_duplicate_comparison(self):
        item = copy.deepcopy(self.manifest['slices'][0]); item['id'] = 'second'
        self.manifest['slices'].append(item)
        with self.assertRaisesRegex(ValueError, 'duplicate_comparison'):
            self.run_suite()

    def test_missing_expected_slice(self):
        self.write('expected.json', dict(comparisons=[]))
        self.manifest['slices'][0]['expected'] = self.pin('expected.json')
        with self.assertRaisesRegex(ValueError, 'expected_slice_missing'):
            self.run_suite()

    def test_wrong_expected_result(self):
        doc = s.q.load(self.root / 'expected.json'); doc['comparisons'][0]['modelAccepted'] = True
        self.write('expected.json', doc)
        self.manifest['slices'][0]['expected'] = self.pin('expected.json')
        with self.assertRaisesRegex(ValueError, 'comparison_parity_failed'):
            self.run_suite()

    def test_unknown_version_and_zero_support(self):
        self.manifest['version'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'suite_version'): self.run_suite()
        self.manifest['version'] = s.VERSION; self.manifest['slices'][0]['cases'] = 0
        with self.assertRaisesRegex(ValueError, 'zero_support'): self.run_suite()

    def test_unsafe_input_path(self):
        self.manifest['evidence'][0]['path'] = '../secret'
        with self.assertRaisesRegex(ValueError, 'unsafe_path'): self.run_suite()

    def test_symlink_output_refused(self):
        self.out.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink_refused'): self.run_suite()

    def test_parallel_start_refused(self):
        self.out.mkdir()
        with (self.out / 'suite.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'suite_busy'): self.run_suite()

    def test_limits(self):
        with self.assertRaisesRegex(ValueError, 'suite_timeout'): self.run_suite(timeout=0)
        with self.assertRaisesRegex(ValueError, 'output_size_limit'): self.run_suite(maximum=1)

    def test_cache(self):
        cache = s.Documents(self.root)
        self.assertEqual(cache.get(self.pin('control.json')), cache.get(self.pin('control.json')))
        self.assertEqual((cache.reads, cache.hits), (1, 1))

    def test_cross_role_and_unknown_role(self):
        doc = document(.9)
        doc['sets']['copy'] = copy.deepcopy(doc['sets']['native'])
        doc['sets']['copy']['rows'][0]['role'] = 'train'
        with self.assertRaisesRegex(ValueError, 'cross_role_group'): s.check_roles(doc)
        doc['sets']['native']['rows'][0]['role'] = 'final-audit'
        with self.assertRaisesRegex(ValueError, 'unknown_or_audit_role'): s.check_roles(doc)

    def test_queue_callable(self):
        # Exercise the actual staged callable without touching the live queue.
        self.out.mkdir()
        s.q.save(self.out / 'config.json', self.manifest)
        with patch.object(s.q, 'ROOT', self.root), patch.object(s, 'OUT', self.out):
            # execute's explicit root is supplied by the queue wrapper.
            s.run()
        self.assertTrue((self.out / 'sources.json').exists())

    def test_actual_queue_child(self):
        # Test the real worker interface in isolation. Do not start a scheduler.
        manifest = copy.deepcopy(self.manifest)
        for ref in manifest['evidence']:
            ref['path'] = s.q.relative(self.root / ref['path'])
        for item in manifest['slices']:
            for key in ('control', 'candidate', 'expected'):
                item[key]['path'] = s.q.relative(self.root / item[key]['path'])
        job = self.root / 'jobs/test-suite391'
        attempt = job / 'attempts/1'
        out = attempt / 'out'
        out.mkdir(parents=True)
        s.q.save(out / 'config.json', manifest)
        spec = dict(version='research-spec-v2', id='test-suite391', task='TEST391', owner='Test-NUIAK',
            kind='screen', authority='diagnostic', jobKind='aggregation',
            question='Does the real worker preserve the test comparison?', hypothesis='The result matches.',
            controlledComparison='Fixed test predictions and their independently retained result.',
            decisionRule='Require exact comparison parity.',
            nextActionByOutcome=dict(supported='Keep the interface.', contradicted='Repair the interface.'),
            inputs=manifest['evidence'], evidence=dict(citations='sources.json', reads=[manifest['evidence'][0]['path']]),
            dependencies=[dict(job='test-producer', specSHA256='a'*64, outputs=['expected.json'])],
            adapter=dict(type='python-callable', steps=['evaluation_suite391.run'], outputAttributes=['evaluation_suite391.OUT']),
            limits=dict(timeoutSeconds=20, maxOutputBytes=1000000, maxAttempts=1))
        s.q.validate(spec)
        s.q.save(job / 'spec.json', spec)
        result = subprocess.run([sys.executable, str(s.q.ROOT / 'scripts/research_queue.py'),
            '_execute', str(attempt), str(s.q.MODULES)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(s.q.load(out / 'suite/suite.json')['complete'])
        self.assertTrue((attempt / 'reads.json').exists())


if __name__ == '__main__':
    unittest.main()
