import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import research_queue as q
import ttr_evidence_compaction458 as worker


class CompactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.archive=self.root/'archive';self.receipt=self.root/'receipt.json'
        self.a=self.root/'a.png';self.b=self.root/'failed.png'
        self.a.write_bytes(b'unchanged evidence');self.b.write_bytes(self.a.read_bytes())

    def test_preserves_every_path_and_failed_bytes(self):
        result=worker.compact([self.a,self.b],self.archive,self.receipt)
        self.assertEqual(result['pathsRemoved'],0);self.assertEqual(result['linksReplaced'],1)
        self.assertEqual(self.a.stat().st_ino,self.b.stat().st_ino)
        self.assertEqual(self.b.read_bytes(),b'unchanged evidence')
        self.assertEqual((self.archive/(q.digest(self.a)+'.png')).read_bytes(),self.a.read_bytes())

    def test_restart_is_idempotent(self):
        worker.compact([self.a,self.b],self.archive,self.receipt)
        result=worker.compact([self.a,self.b],self.archive,self.root/'second.json')
        self.assertEqual(result['linksReplaced'],0)

    def test_linked_paths_count_once(self):
        self.b.unlink(); worker.os.link(self.a, self.b)
        with patch.object(worker, 'MAX_UNIQUE_INPUT', self.a.stat().st_size):
            result = worker.compact([self.a,self.b],self.archive,self.receipt)
        self.assertEqual(result['uniqueFileBytes'], self.a.stat().st_size)
        self.assertEqual(result['originalLogicalBytes'], 2*self.a.stat().st_size)

    def test_unique_input_budget_still_enforced(self):
        with patch.object(worker, 'MAX_UNIQUE_INPUT', 1):
            with self.assertRaisesRegex(ValueError, 'input_budget'):
                worker.compact([self.a,self.b],self.archive,self.receipt)

    def test_archive_reservation_enforced(self):
        with patch.object(worker, 'MAX_ARCHIVE', 1):
            with self.assertRaisesRegex(ValueError, 'archive_budget'):
                worker.compact([self.a,self.b],self.archive,self.receipt)

    def test_free_space_reserves_missing_bytes(self):
        from collections import namedtuple
        usage = namedtuple('Usage','total used free')(100, 80, 20)
        with patch.object(worker.shutil, 'disk_usage', return_value=usage):
            with self.assertRaisesRegex(ValueError, 'compaction_space'):
                worker.compact([self.a,self.b],self.archive,self.receipt)

    def test_unique_content_is_not_merged(self):
        self.b.write_bytes(b'different evidence')
        self.assertEqual(worker.compact([self.a,self.b],self.archive,self.receipt)['linksReplaced'],0)

    def test_bad_archive_preserves_originals(self):
        self.archive.mkdir();(self.archive/(q.digest(self.a)+'.png')).write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'backup_changed'):worker.compact([self.a,self.b],self.archive,self.receipt)
        self.assertNotEqual(self.a.stat().st_ino,self.b.stat().st_ino)

    def test_link_failure_preserves_original(self):
        with patch.object(worker.os,'link',side_effect=OSError('unsupported')):
            with self.assertRaises(OSError):worker.compact([self.a,self.b],self.archive,self.receipt)
        self.assertEqual(self.b.read_bytes(),self.a.read_bytes());self.assertFalse(self.receipt.exists())

    def test_links_and_non_png_are_rejected(self):
        link=self.root/'link.png';link.symlink_to(self.a)
        for path in (link,self.root/'journal.json'):
            with self.assertRaises(ValueError):worker.compact([path],self.archive,self.receipt)

    def test_active_route_is_rejected(self):
        map_root=self.root/'map';journal=map_root/'hcf-one/recovery.json';journal.parent.mkdir(parents=True)
        q.save(journal,dict(session='00000000-0000-0000-0000-000000000001',state=dict(status='running')))
        with self.assertRaisesRegex(ValueError,'route_active'):worker.retained_pngs(self.root,map_root)

if __name__=='__main__':unittest.main()
