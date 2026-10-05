import tarfile
import unittest
import receive_worker180 as w


class Tests(unittest.TestCase):
    def test_larger_numeric_return(self):
        rows=[tarfile.TarInfo('scores/'+str(i)) for i in range(1322)]
        self.assertEqual(len(w.bounded_members(rows)[0]),1322)
        with self.assertRaisesRegex(Exception,'archive_member_limit'):w.bounded_members([tarfile.TarInfo(str(i)) for i in range(2001)])

    def test_global_duplicates_paths_links_and_sizes(self):
        for rows in ([tarfile.TarInfo('a'),tarfile.TarInfo('A')],[tarfile.TarInfo('../a')],[tarfile.TarInfo('/a')]):
            with self.assertRaises(Exception):w.bounded_members(rows)
        link=tarfile.TarInfo('link');link.type=tarfile.SYMTYPE;link.linkname='a'
        with self.assertRaises(Exception):w.bounded_members([link])
        big=tarfile.TarInfo('big');big.size=33*1024**2
        with self.assertRaises(Exception):w.bounded_members([big])
        rows=[tarfile.TarInfo(str(i)) for i in range(3)]
        for row in rows:row.size=30_000_000
        with self.assertRaises(Exception):w.bounded_members(rows)


if __name__=='__main__':unittest.main()
