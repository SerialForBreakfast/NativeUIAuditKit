"""Test verified reclamation and restore with project-local temporary files."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import usb_archive386 as a


class ArchiveTests(unittest.TestCase):
    def test_archive_restore_and_conflict(self):
        with tempfile.TemporaryDirectory(dir=a.q.ROOT/'reports/work') as temp:
            root=Path(temp);source=root/'source';source.mkdir();(source/'data.bin').write_bytes(b'known bytes')
            volume=root/'usb';volume.mkdir();receipt=root/'receipt.json'
            with patch.object(a.u,'verify_volume'),patch.object(a.u,'VOLUME',volume),patch.object(Path,'is_mount',return_value=True),patch.object(a.shutil,'disk_usage',return_value=type('U',(),{'free':10**12,'total':10**12})()):
                doc=a.archive(source,receipt)
                self.assertFalse(doc['backup'])
                a.archive(source,receipt,reclaim=True)
                self.assertFalse((source/'data.bin').exists())
                a.archive(source,receipt,restore=True)
                self.assertEqual((source/'data.bin').read_bytes(),b'known bytes')
                (source/'data.bin').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'restore_existing_conflict'):a.archive(source,receipt,restore=True)
    def test_changed_archive_blocks_reclaim(self):
        with tempfile.TemporaryDirectory(dir=a.q.ROOT/'reports/work') as temp:
            root=Path(temp);source=root/'source';source.mkdir();(source/'data.bin').write_bytes(b'known')
            volume=root/'usb';volume.mkdir();receipt=root/'receipt.json'
            with patch.object(a.u,'verify_volume'),patch.object(a.u,'VOLUME',volume),patch.object(a.shutil,'disk_usage',return_value=type('U',(),{'free':10**12,'total':10**12})()):
                doc=a.archive(source,receipt);(Path(doc['destination'])/'data.bin').write_bytes(b'wrong')
                with self.assertRaises(ValueError):a.archive(source,receipt,reclaim=True)
                self.assertTrue((source/'data.bin').exists())

if __name__=='__main__':unittest.main()
