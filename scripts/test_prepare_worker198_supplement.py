import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

import prepare_worker198_supplement as s


class SupplementTests(unittest.TestCase):
    def setUp(self):
        base = s.ROOT / '.build/debug-output'
        base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=base, prefix='worker198-supplement-'))
        self.source = self.root / 'retained.json'
        self.source.write_text('{}')
        entry = dict(path=self.source.name, bytes=2, sha256=s.digest(self.source))
        self.parent = self.root / 'manifest.json'
        self.parent.write_text(json.dumps(dict(version='worker198-eval-v1',
            purpose='frozen_inference_only', trainingEligible=False, files=[entry],
            settings=dict(device='0', imgsz=640, discard_degenerate=True),
            plans={k: dict(path=self.source.name, count=n, trainingEligible=False,
                          contentSHA256=k, role='retained-test')
                   for k, n in [('fit', 135), ('page', 37), ('combined', 413)]})))
        self.parent_sha = s.digest(self.parent)
        self.cp = self.root / 'last.pt'
        self.cp.write_bytes(b'fixture-checkpoint-not-a-model')
        self.sha = s.digest(self.cp)
        self.end = dict(exitCode=0, optimizerAt=[0, 3], checkpoint=dict(sha256=self.sha))
        self.schedule = dict(optimizerAt=[0, 3])

    def tearDown(self):
        shutil.rmtree(self.root)

    def package(self, **overrides):
        args = dict(output=self.root / 'out', parent=self.parent, parent_sha=self.parent_sha,
                    checkpoint=self.cp, checkpoint_sha=self.sha, completion=self.end,
                    schedule=self.schedule, evidence={'fixture': True}, root=self.root)
        args.update(overrides)
        return s.package(**args)

    def test_only_checkpoint_and_manifest_preserve_parent_contract(self):
        archive = self.package()
        with tarfile.open(archive) as stream:
            self.assertEqual(stream.getnames(), ['treatment028.pt', 'supplement.json'])
            self.assertEqual(stream.extractfile('treatment028.pt').read(), self.cp.read_bytes())
            doc = json.load(stream.extractfile('supplement.json'))
        parent = json.loads(self.parent.read_text())
        self.assertEqual(doc['plans'], parent['plans'])
        self.assertEqual(doc['settings'], parent['settings'])
        self.assertEqual(doc['parentManifestSHA256'], self.parent_sha)
        self.assertFalse(doc['trainingEligible'])
        self.assertTrue(all('eval028-' in name for name in doc['outputNames'].values()))
        with self.assertRaisesRegex(ValueError, 'collision'):
            self.package()

    def test_incomplete_failed_or_schedule_mismatch_before_output(self):
        for end in ({}, dict(self.end, exitCode=1), dict(self.end, optimizerAt=[0])):
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                self.package(completion=end)
            self.assertFalse((self.root / 'out').exists())

    def test_changed_parent_or_retained_data(self):
        with self.assertRaisesRegex(ValueError, 'parent_changed'):
            self.package(parent_sha='0' * 64)
        self.source.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'parent_input_changed'):
            self.package()
        self.assertFalse((self.root / 'out').exists())

    def test_changed_checkpoint_or_completion_binding(self):
        with self.assertRaisesRegex(ValueError, 'checkpoint_changed'):
            self.package(completion=dict(self.end, checkpoint=dict(sha256='0' * 64)))
        self.cp.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checkpoint_changed'):
            self.package()

    def test_escape_and_symlink_rejected(self):
        with self.assertRaisesRegex(ValueError, 'output_boundary'):
            self.package(output=self.root / '..' / 'escape')
        link = self.root / 'link.pt'
        link.symlink_to(self.cp)
        with self.assertRaisesRegex(ValueError, 'checkpoint_changed'):
            self.package(checkpoint=link)

    def test_parent_contract_cannot_change_roles_or_settings(self):
        original = json.loads(self.parent.read_text())
        for key, value in [('trainingEligible', True), ('settings', {'device': 'mps'})]:
            changed = dict(original, **{key: value})
            self.parent.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                self.package(parent_sha=s.digest(self.parent))


if __name__ == '__main__':
    unittest.main()
