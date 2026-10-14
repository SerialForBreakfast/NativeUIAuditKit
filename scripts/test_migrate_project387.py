"""Check migration safety using isolated temporary project folders."""
import contextlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import migrate_project387 as m


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'.build/debug-output')
        self.root = Path(self.temp.name)
        self.source = self.root/'source'
        self.target = self.root/'target'
        self.evidence = self.root/'evidence'
        (self.source/'dataset').mkdir(parents=True)
        (self.source/'dataset/image').write_bytes(b'original pixels')
        (self.source/'dataset/link').symlink_to(self.source/'dataset/image')
        (self.source/'reports/work/CHAT-288').mkdir(parents=True)
        (self.source/'reports/work/CHAT-288/profile').write_bytes(b'keep local')
        (self.source/'source.swift').write_bytes(b'keep source')
        shutil.copytree(self.source,self.target,symlinks=True)
        self.stack = contextlib.ExitStack()
        for name,value in [('SOURCE',self.source),('TARGET',self.target),('EVIDENCE',self.evidence),('VOLUME',self.root)]:
            self.stack.enter_context(patch.object(m,name,value))
        self.stack.enter_context(patch.object(m,'volume'))
        self.stack.enter_context(patch.object(Path,'is_mount',return_value=True))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
    def tearDown(self):
        self.stack.close()
        self.temp.cleanup()
    def test_verified_move_preserves_source_and_credentials(self):
        m.verify();m.repair();m.reclaim()
        self.assertFalse((self.source/'dataset/image').exists())
        self.assertEqual((self.target/'dataset/link').read_bytes(),b'original pixels')
        self.assertTrue((self.source/'source.swift').exists())
        self.assertTrue((self.source/'reports/work/CHAT-288/profile').exists())
    def test_changed_copy_blocks_removal(self):
        m.verify();m.repair()
        (self.target/'dataset/image').write_bytes(b'altered')
        with self.assertRaisesRegex(AssertionError,'Target changed'):m.reclaim()
        self.assertTrue((self.source/'dataset/image').exists())
    def test_verification_rejects_bad_copy(self):
        (self.target/'dataset/image').write_bytes(b'altered')
        with self.assertRaises(AssertionError):m.verify()
        self.assertFalse((self.evidence/'verification.json').exists())
    def test_reclaim_recovers_after_partial_removal(self):
        m.verify();m.repair()
        (self.source/'dataset/image').unlink()
        m.reclaim()
        self.assertTrue((self.evidence/'reclamation.json').exists())


if __name__ == '__main__':
    unittest.main()
