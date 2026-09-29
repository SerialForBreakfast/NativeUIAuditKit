"""Offline generated recording fixtures; never alter the human's review files."""
import json
import unittest
import human_annotation_review as h
import human_recording_review as r
import test_human_annotation_review as fixtures


class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests(); self.f.setUp()
        self.source = self.f.source
        (self.source/'images').mkdir()
        entries, inventory = [], []
        for n in range(2):
            p = self.source/f'frame-{n}.png'
            digest = h.sha(p)
            p.rename(self.source/'images'/f'frame-{digest}.png')
            entries.append({'frame': {'_0': dict(frameID=f'f{n}', sequenceNumber=n,
                sourceDeviceID='office', role='postInputSettled', sha256=digest)}})
            inventory.append(dict(sha256=digest, bytes=(self.source/'images'/f'frame-{digest}.png').stat().st_size))
        for name, rows in [('events.jsonl', entries), ('files.jsonl', inventory)]:
            (self.source/name).write_text('\n'.join(json.dumps(row) for row in rows))
        self.f.dump(self.source/'manifest.json', dict(schemaVersion=2, sessionID='session', targetDeviceID='office'))
        for name in ['delivery.json', 'manifest-receipt.json']:
            self.f.dump(self.source/name, {})

    def tearDown(self):
        self.f.tearDown()

    def prepare(self):
        return r.prepare(self.source, self.f.batch, [(0,'settings'),(1,'settings')])

    def test_dispatch_and_unconfirmed_editor(self):
        p = self.prepare()
        self.assertEqual(len(h.validate_batch(p)['frames']), 2)
        for editor in (p.parent/'editor').glob('*.json'):
            doc = h.read(editor)
            self.assertEqual(doc['shapes'], [])
            self.assertFalse(any(doc['flags'].values()))

    def test_changed_source_metadata(self):
        p = self.prepare()
        (p.parent/'raw/events.jsonl').write_text('{}')
        with self.assertRaises(ValueError): r.validate(p)

    def test_changed_image(self):
        p = self.prepare()
        (p.parent/'raw/recorded-0.png').write_bytes(b'broken')
        with self.assertRaises(ValueError): r.validate(p)

    def test_duplicate_selection(self):
        with self.assertRaises(ValueError):
            r.prepare(self.source, self.f.batch, [(0,'a'), (0,'b')])

    def test_wrong_target_and_role(self):
        p = self.source/'events.jsonl'
        rows = r.events(p)
        rows[0]['frame']['_0']['sourceDeviceID'] = 'wrong'
        p.write_text('\n'.join(json.dumps(row) for row in rows))
        with self.assertRaises(ValueError): self.prepare()

    def test_unsupported_schema(self):
        self.f.dump(self.source/'manifest.json', dict(schemaVersion=3))
        with self.assertRaises(ValueError): self.prepare()

    def test_unverified_requires_explicit_option_and_preserves_role(self):
        path = self.source/'events.jsonl'
        rows = r.events(path); rows[0]['frame']['_0']['role'] = 'postInputUnverified'
        path.write_text('\n'.join(json.dumps(row) for row in rows))
        with self.assertRaises(ValueError): self.prepare()
        p = r.prepare(self.source, self.f.root/'second', [(0,'home')], include_unverified=True)
        doc = h.validate_batch(p)
        self.assertEqual(doc['frames'][0]['recordingEvent']['role'], 'postInputUnverified')
        self.assertFalse(h.read(p.parent/'editor/001-recorded-0.json')['flags']['settled'])
        rows[0]['frame']['_0']['role'] = 'transition'
        path.write_text('\n'.join(json.dumps(row) for row in rows))
        with self.assertRaises(ValueError):
            r.prepare(self.source, self.f.root/'third', [(0,'home')], include_unverified=True)


if __name__ == '__main__':
    unittest.main()
