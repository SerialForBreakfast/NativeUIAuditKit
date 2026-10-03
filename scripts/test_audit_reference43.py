import copy
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import human_annotation_review as h
import audit_reference43 as audit


class ReferenceAuditTests(unittest.TestCase):
    def setUp(self):
        parent = h.ROOT / '.build/debug-output'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self):
        p = self.root / 'frame.png'
        Image.new('RGB', (12, 8)).save(p)
        entry = dict(path=p.name, bytes=p.stat().st_size, sha256=h.sha(p))
        self.manifest([entry])
        return p, entry

    def manifest(self, entries):
        (self.root / 'artifact-manifest.json').write_text(json.dumps(dict(schema_version=1, files=entries)))

    def test_exact_integrity(self):
        self.fixture()
        self.assertEqual(audit.verify_files(self.root), 1)

    def test_changed_bytes(self):
        p, _ = self.fixture()
        p.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'member_integrity'):
            audit.verify_files(self.root)

    def test_unlisted_file(self):
        self.fixture()
        (self.root / 'extra').write_text('x')
        with self.assertRaisesRegex(ValueError, 'unlisted_member'):
            audit.verify_files(self.root)

    def test_duplicate_casefold(self):
        _, entry = self.fixture()
        self.manifest([entry, dict(entry, path='FRAME.PNG')])
        with self.assertRaisesRegex(ValueError, 'duplicate_member'):
            audit.verify_files(self.root)

    def test_traversal(self):
        _, entry = self.fixture()
        self.manifest([dict(entry, path='../frame.png')])
        with self.assertRaises(ValueError):
            audit.verify_files(self.root)

    def scene(self):
        return dict(scene_width=12, scene_height=8, is_settled=True, focused_element_id='a',
                    focus_observation=dict(verified=True, observedID='a'),
                    elements=[dict(element_id='a', is_focused=True)])

    def test_image_and_observed_focus(self):
        p, entry = self.fixture()
        self.assertEqual(audit.inspect_image(p, self.scene()), entry['sha256'])

    def test_bad_dimensions_and_unverified_focus(self):
        p, _ = self.fixture()
        for change in ('dimensions', 'verified', 'membership'):
            scene = copy.deepcopy(self.scene())
            if change == 'dimensions': scene['scene_width'] = 13
            elif change == 'verified': scene['focus_observation']['verified'] = False
            else: scene['elements'][0]['is_focused'] = False
            with self.subTest(change=change), self.assertRaises(ValueError):
                audit.inspect_image(p, scene)


if __name__ == '__main__':
    unittest.main()
