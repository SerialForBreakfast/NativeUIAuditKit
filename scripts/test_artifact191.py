import tarfile
import unittest
from unittest.mock import patch
import artifact191 as a


def member(name='handoff/a',size=1,kind=tarfile.REGTYPE):
    m=tarfile.TarInfo(name);m.size=size;m.type=kind;return m


class Tests(unittest.TestCase):
    def test_regular(self):
        self.assertIsNone(a.headers([member()])[0]['extractionError'])

    def test_hardlink_and_oversize_remain_rejected(self):
        rows=a.headers([member(kind=tarfile.LNKTYPE,size=0),member('handoff/b',36_190_870)])
        self.assertEqual(rows[0]['kind'],'hardlink')
        self.assertIsNotNone(rows[0]['extractionError'])
        self.assertIsNotNone(rows[1]['extractionError'])

    def test_path_duplicate_limits(self):
        for values in ([member('../outside')],[member('/outside')], [member(),member()],
                       [member(size=65*1024**2)], [member(str(i)) for i in range(1001)]):
            with self.assertRaises(Exception):a.headers(values)

    def test_selection(self):
        cases=[dict(metadata=str(i),metadata_sha256=str(i),training_admission='pending',
                    disposition='pilot_review_accepted' if i<15 else 'retained_geometry_calibration' if i<20 else 'superseded_render_review' if i<25 else 'superseded_baseline_geometry') for i in range(28)]
        manifest={str(i):dict(sha256=str(i)) for i in range(28)}
        self.assertEqual(a.selection(dict(version=1,cases=cases),manifest)['pilot_review_accepted'],15)
        for rows in (cases[:-1],cases+[cases[0]]):
            with self.assertRaises(Exception):a.selection(dict(version=1,cases=rows),manifest)
        manifest['0']['sha256']='wrong'
        with self.assertRaisesRegex(Exception,'selection_hash'):a.selection(dict(version=1,cases=cases),manifest)

    def test_collision(self):
        with patch('pathlib.Path.exists',return_value=True),patch.object(a.h,'sha') as sha:
            with self.assertRaisesRegex(Exception,'output_collision'):a.run()
            sha.assert_not_called()

    def test_archive_hash_before_read(self):
        with patch('pathlib.Path.exists',return_value=False),patch.object(a.h,'sha',return_value='wrong'),patch.object(a.tarfile,'open') as opened:
            with self.assertRaisesRegex(Exception,'archive_hash'):a.run()
            opened.assert_not_called()


if __name__=='__main__':unittest.main()
