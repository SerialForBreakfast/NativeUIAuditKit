import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import migrate_artifact_storage as m


class MigrationTests(unittest.TestCase):
    def setUp(self):
        parent=m.s.ROOT/'.build/debug-output/migration-tests';parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'repo';self.root.mkdir();self.base=Path(self.tmp.name)/'external';self.base.mkdir()
        self.source=self.root/'reports/work/example/artifacts';self.source.mkdir(parents=True)
        (self.source/'raw.bin').write_bytes(b'evidence');(self.source/'review.md').write_text('tracked')
        self.receipt=self.root/'reports/work/migration/receipt.json'
        for obj,key,val in ((m.s,'ROOT',self.root),(m.c,'ROOT',self.root),(m.s,'BASE',self.base),(m.s,'VOLUME',self.base)):
            ctx=patch.object(obj,key,val);ctx.start();self.addCleanup(ctx.stop)
        ctx=patch.object(m.s,'mounted');ctx.start();self.addCleanup(ctx.stop)
        self.destination=self.base/'live/reports/work/example/artifacts'

    def test_copy_reclaim_preserves_tracked_and_verified_archive(self):
        m.run(self.source,self.receipt,'copy')
        with patch.object(m.s,'resolve_input',return_value=self.destination),patch.object(m.subprocess,'check_output',return_value=b'reports/work/example/artifacts/review.md\0'):
            m.run(self.source,self.receipt,'reclaim')
        self.assertFalse((self.source/'raw.bin').exists());self.assertTrue((self.source/'review.md').exists())
        self.assertEqual((self.destination/'raw.bin').read_bytes(),b'evidence')

    def test_changed_copy_blocks_deletion_and_collision_rejected(self):
        m.run(self.source,self.receipt,'copy');(self.destination/'raw.bin').write_bytes(b'altered')
        with patch.object(m.s,'resolve_input',return_value=self.destination):
            with self.assertRaises(ValueError):m.run(self.source,self.receipt,'reclaim')
        self.assertTrue((self.source/'raw.bin').exists())
        with self.assertRaises(ValueError):m.run(self.source,self.receipt,'copy')

    def test_unregistered_mapping_blocks_reclaim(self):
        m.run(self.source,self.receipt,'copy')
        with patch.object(m.s,'resolve_input',return_value=self.source):
            with self.assertRaisesRegex(ValueError,'not_active'):m.run(self.source,self.receipt,'reclaim')


if __name__=='__main__':unittest.main()
