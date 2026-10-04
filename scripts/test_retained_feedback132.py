import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from PIL import Image
import retained_feedback132 as r


class RetainedTests(unittest.TestCase):
    def fixture(self,root,kind='valid'):
        stream=io.BytesIO();Image.new('RGB',(3,2),'red').save(stream,format='PNG');raw=stream.getvalue()
        name=hashlib.sha256(raw).hexdigest()+'.png'
        archive=root/'bundle.tar.gz'
        with tarfile.open(archive,'w:gz') as t:
            info=tarfile.TarInfo('../escape' if kind=='traversal' else 'originals/'+name)
            if kind=='link':info.type=tarfile.SYMTYPE;info.linkname='/etc/passwd';t.addfile(info)
            else:
                payload=b'corrupt' if kind=='corrupt' else raw;info.size=len(payload);t.addfile(info,io.BytesIO(payload))
                if kind=='duplicate':t.addfile(info,io.BytesIO(payload))
        tx=root/'tx.json';tx.write_text(json.dumps(dict(requestID='test',localPath=str(archive.relative_to(r.t.ROOT)),
            bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())))
        return tx

    def test_exact_extraction_and_collision(self):
        with tempfile.TemporaryDirectory(dir=r.t.ROOT/'.build') as tmp:
            root=Path(tmp);tx=self.fixture(root);out=root/'out';r.extract(tx,out)
            report=json.loads((out/'extraction.json').read_text())
            self.assertFalse(report['trainingEligible']);self.assertEqual(report['inventory'][0]['dimensions'],[3,2])
            with self.assertRaises(ValueError):r.extract(tx,out)

    def test_unsafe_and_corrupt_rejected(self):
        for kind in ('traversal','link','duplicate','corrupt'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory(dir=r.t.ROOT/'.build') as tmp:
                root=Path(tmp);tx=self.fixture(root,kind)
                with self.assertRaises(ValueError):r.extract(tx,root/'out')

    def test_archive_changed_rejected(self):
        with tempfile.TemporaryDirectory(dir=r.t.ROOT/'.build') as tmp:
            root=Path(tmp);tx=self.fixture(root);(root/'bundle.tar.gz').write_bytes(b'changed')
            with self.assertRaises(ValueError):r.extract(tx,root/'out')


if __name__=='__main__':unittest.main()
