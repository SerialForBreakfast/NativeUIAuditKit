import json
from pathlib import Path
import shutil
import tempfile
import unittest
from PIL import Image
import prediction_artifact as a
from prepare_worker198_eval import copy_request,check_limits


class Tests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parent.parent/'.build/debug-output'
        root.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=root,prefix='worker198-eval-'))
        Image.new('RGB',(8,8),'red').save(self.root/'source.png')
        (self.root/'source.txt').write_text('0 0.5 0.5 0.5 0.5\n')
        path=self.root/'input.json'
        path.write_text(json.dumps(dict(formatVersion=a.INPUT_FORMAT_VERSION,corpusID='frozen',
            images=[dict(imageID='original-id',imagePath='source.png',labelPath='source.txt')])) )
        self.request=a.load_request(path,41)

    def tearDown(self):shutil.rmtree(self.root)

    def test_relocation_preserves_identity_and_bytes(self):
        copied=a.load_request(copy_request(self.request,self.root/'out'),41)
        self.assertEqual(copied.content_sha256,self.request.content_sha256)
        self.assertEqual(copied.images[0].image_id,'original-id')
        self.assertNotEqual(copied.manifest_sha256,self.request.manifest_sha256)
        with self.assertRaises(FileExistsError):copy_request(self.request,self.root/'out')

    def test_changed_input_rejected(self):
        (self.root/'source.txt').write_text('0 0.1 0.1 0.1 0.1\n')
        with self.assertRaisesRegex(ValueError,'source_changed'):
            copy_request(self.request,self.root/'out')

    def test_limits(self):
        check_limits([dict(path='control027.pt',bytes=41000000)])
        for entries in ([dict(path='../x',bytes=1)], [dict(path='/x',bytes=1)],
                [dict(path='x',bytes=51*1024**2)], [dict(path='x',bytes=1)]*1301,
                [dict(path='x',bytes=1)]*2,
                [dict(path=str(i),bytes=50*1024**2) for i in range(5)]):
            with self.assertRaises(ValueError):check_limits(entries)


if __name__=='__main__':unittest.main()
