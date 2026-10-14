import io
import tarfile
import unittest
from test_research_queue import QueueTests
import hcf357 as h


class ArchiveTests(QueueTests):
    def archive(self, name, link=False):
        p=self.base/'test.tar'
        with tarfile.open(p,'w') as stream:
            root=tarfile.TarInfo('./');root.type=tarfile.DIRTYPE;stream.addfile(root)
            entry=tarfile.TarInfo(name)
            if link:
                entry.type=tarfile.SYMTYPE;entry.linkname='/etc/passwd';stream.addfile(entry)
            else:
                entry.size=1;stream.addfile(entry,io.BytesIO(b'x'))
        return p

    def test_root_directory(self):
        h.unpack(self.archive('./safe.txt'),self.base/'out')
        self.assertEqual((self.base/'out/safe.txt').read_bytes(),b'x')

    def test_traversal(self):
        with self.assertRaises(ValueError):h.unpack(self.archive('../bad'),self.base/'out')

    def test_link(self):
        with self.assertRaises(ValueError):h.unpack(self.archive('link',True),self.base/'out')


if __name__=='__main__':unittest.main()
