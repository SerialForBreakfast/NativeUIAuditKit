"""Regression checks for the test-only cross-repository conformance handoff."""
import hashlib
import json
import unittest
import zipfile
import tempfile
import contextlib
import io
from pathlib import Path
from build_conformance124 import BASE, ROOT, build, verify_case


class ConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / '.build', prefix='conformance-test-')
        cls.base = Path(cls.temp.name) / 'generated'
        audit = Path(cls.temp.name) / 'audit.json'
        audit.write_text(json.dumps({'exposure': [dict(currentRole='training_exposed',
            finalEligible=False, ancestry='test-only', image={'sha256': 'a' * 64})]}))
        with contextlib.redirect_stdout(io.StringIO()):
            build(cls.base, exposure_audit=audit,
                  exposure_hash=hashlib.sha256(audit.read_bytes()).hexdigest(), expected_images=1)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_cases_replay_without_admission(self):
        contract = json.loads((self.base / 'pack/contract.json').read_text())
        self.assertEqual(len(contract['cases']), 11)
        self.assertTrue(contract['testOnly'])
        for case in contract['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(verify_case(self.base / 'pack' / case['id'],
                                            case['expected']['accepted']), case['expected'])

    def test_exposure_is_sanitized_and_not_independence(self):
        data = json.loads((self.base / 'pack/exposure.json').read_text())
        self.assertEqual(data['absentHashMeaning'], 'unknown_not_independent')
        self.assertEqual(data['independentFinalMembership'], [])
        self.assertEqual(len(data['knownImages']), 1)
        for row in data['knownImages']:
            self.assertEqual(set(row), {'sha256', 'ancestry', 'role', 'finalEligible'})
            self.assertEqual(row['role'], 'training_exposed')
            self.assertFalse(row['finalEligible'])
        self.assertNotIn('/Users/', json.dumps(data))

    def test_archive_exact_inventory_and_source_pins(self):
        report = json.loads((self.base / 'report.json').read_text())
        archive = self.base / 'nuiak-conformance-exposure-v1.zip'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), report['archiveSHA256'])
        with zipfile.ZipFile(archive) as z:
            members = json.loads(z.read('manifest.json'))['files']
            self.assertEqual(set(z.namelist()), {r['path'] for r in members} | {'manifest.json'})
            self.assertEqual(len(z.namelist()), len(set(z.namelist())))
            self.assertLess(sum(i.file_size for i in z.infolist()), 1_048_576)
            for row in members:
                payload = z.read(row['path'])
                self.assertEqual(len(payload), row['bytes'])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row['sha256'])
            for name, digest in json.loads(z.read('contract.json'))['sourceHashes'].items():
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_existing_destination_rejected(self):
        with self.assertRaises(AssertionError):
            build(self.base)

    def test_wrong_expectation_does_not_pass(self):
        with self.assertRaises(AssertionError):
            verify_case(self.base / 'pack/valid_v2', False)
        with self.assertRaises(AssertionError):
            verify_case(self.base / 'pack/corrupt_image', True)


if __name__ == '__main__':
    unittest.main()
