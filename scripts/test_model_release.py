"""Test release preparation without network, real weights, or publication."""
import copy
import json
from pathlib import Path
import stat
import tempfile
import sys
import unittest
import zipfile
import model_release as m


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        root = m.ROOT / '.build/debug-output'
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        (self.source / 'Detector.mlpackage').mkdir(parents=True)
        (self.source / 'Detector.mlpackage/Manifest.json').write_text('{}')
        (self.source / 'LICENSE.txt').write_text('Test fixture. No model license is granted.')
        (self.source / 'contract.json').write_text('{}')
        self.files = m.inventory(self.source)
        self.archive = self.root / 'model.zip'
        receipt = m.pack(self.source, self.archive, self.files)
        self.entry = dict(modelID='nativeui-tvos-v3.0', artifactVersion='1.0.0-rc.1',
            task='element_detection', screenshotDomain='tvOS', modelRoot='Detector.mlpackage', files=self.files,
            expandedBytes=sum(f['bytes'] for f in self.files), **receipt,
            url='https://github.com/example/models/releases/download/1.0.0-rc.1/model.zip',
            hosts=[dict(platform='macOS', minimumVersion='15.0', evidence='test fixture only')],
            runtimeContract='nuiak-model-v1', preprocessing='test-only', tensorContractSHA256=m.digest(b'{}'),
            licensePath='LICENSE.txt', qualification='scorer fixture, not a model', sourceRevision='fixture-v1',
            releaseStatus='review-only', approvalReference='')

    def test_deterministic_archive_and_roundtrip(self):
        second = self.root / 'second.zip'
        receipt = m.pack(self.source, second, self.files)
        self.assertEqual(receipt['archiveSHA256'], self.entry['archiveSHA256'])
        self.assertTrue(m.verify_archive(self.archive, self.entry)['verified'])
        m.validate_catalog(dict(schemaVersion=1, models=[self.entry]))

    def test_publication_requires_explicit_record(self):
        with self.assertRaisesRegex(ValueError, 'approval_required'):
            m.validate_entry(self.entry, publication=True)

    @unittest.skipUnless(sys.platform == 'darwin', 'Native macOS extraction test')
    def test_native_ditto_roundtrip_and_rejection(self):
        destination = self.root/'native-extraction'
        result = m.native_extract_probe(self.archive, self.entry, destination)
        self.assertTrue(result['verified'])
        self.assertFalse(result['installed'])
        self.assertEqual(m.inventory(destination/'payload'), self.files)
        with self.assertRaisesRegex(ValueError, 'output_exists'):
            m.native_extract_probe(self.archive, self.entry, destination)
        self.archive.write_bytes(b'corrupt')
        missing = self.root/'must-not-exist'
        with self.assertRaises(ValueError): m.native_extract_probe(self.archive, self.entry, missing)
        self.assertFalse(missing.exists())

    def test_versions_and_task_mapping(self):
        for key, value in [('modelID', 'latest'), ('task', 'transition'), ('runtimeContract', 'v2'),
                           ('screenshotDomain', 'macOS'), ('artifactVersion', 'latest')]:
            entry = copy.deepcopy(self.entry); entry[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): m.validate_entry(entry)
        with self.assertRaises(ValueError):
            m.validate_catalog(dict(schemaVersion=2, models=[self.entry]))
        with self.assertRaisesRegex(ValueError, 'duplicate_artifact'):
            m.validate_catalog(dict(schemaVersion=1, models=[self.entry, self.entry]))

    def test_no_unsafe_urls(self):
        for url in ['http://github.com/e/r/releases/download/1/model.zip',
                    'https://github.com.evil.test/e/r/releases/download/1/model.zip',
                    'https://user@github.com/e/r/releases/download/1/model.zip',
                    'https://github.com/e/r/releases/download/latest/model.zip',
                    'https://github.com/e/r/releases/download/1/model.zip?token=secret']:
            entry = copy.deepcopy(self.entry); entry['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError): m.validate_entry(entry)

    def test_paths_and_duplicate_names(self):
        for name in ['../x', '/x', 'a//b', 'a/./b', 'a\\b', 'a/%2e%2e/b', 'a/'+'x'*513]:
            with self.subTest(name=name), self.assertRaises(ValueError): m.relative_name(name)
        entry = copy.deepcopy(self.entry); entry['files'].append(entry['files'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate_member'): m.validate_entry(entry)

    def test_limits_and_missing_notices(self):
        for key, value in [('archiveBytes', m.MAX_ARCHIVE+1), ('expandedBytes', 0), ('archiveSHA256', ''),
                           ('tensorContractSHA256', ''), ('licensePath', 'absent.txt'), ('hosts', [])]:
            entry = copy.deepcopy(self.entry); entry[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): m.validate_entry(entry)

    def test_changed_source_and_output_collision(self):
        with self.assertRaisesRegex(ValueError, 'output_exists'): m.pack(self.source, self.archive, self.files)
        with self.assertRaisesRegex(ValueError, 'output_inside_source'):
            m.pack(self.source, self.source/'result.zip', self.files)
        (self.source/'contract.json').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source_inventory_mismatch'):
            m.pack(self.source, self.root/'new.zip', self.files)

    def test_links_and_case_collisions(self):
        (self.source/'link').symlink_to(self.source/'contract.json')
        with self.assertRaisesRegex(ValueError, 'linked_member'): m.inventory(self.source)
        with self.assertRaisesRegex(ValueError, 'linked_path'): m.inventory(self.source/'link')

    def test_corrupt_archive(self):
        data = bytearray(self.archive.read_bytes()); data[-1] ^= 1
        self.archive.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'archive_hash_mismatch'):
            m.verify_archive(self.archive, self.entry)

    def test_archive_links_rejected_even_with_matching_hash(self):
        bad = self.root/'bad.zip'
        with zipfile.ZipFile(bad, 'w') as archive:
            for file in self.files:
                info = zipfile.ZipInfo(file['path']); info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, (self.source/file['path']).read_bytes())
        entry = copy.deepcopy(self.entry)
        entry.update(archiveBytes=bad.stat().st_size, archiveSHA256=m.digest(bad.read_bytes()))
        with self.assertRaisesRegex(ValueError, 'archive_member_type'): m.verify_archive(bad, entry)

    def test_json_duplicates_and_nonfinite(self):
        path = self.root/'input.json'
        for text in ['{"x":1,"x":2}', '{"x":NaN}']:
            path.write_text(text)
            with self.assertRaises(ValueError): m.read_json(path)

    def test_unexpected_host_and_fields(self):
        entry = copy.deepcopy(self.entry); entry['hosts'][0]['platform'] = 'tvOS'
        with self.assertRaisesRegex(ValueError, 'unsupported_host'): m.validate_entry(entry)
        entry = copy.deepcopy(self.entry); entry['unknown'] = True
        with self.assertRaisesRegex(ValueError, 'entry_fields'): m.validate_entry(entry)


if __name__ == '__main__': unittest.main()
