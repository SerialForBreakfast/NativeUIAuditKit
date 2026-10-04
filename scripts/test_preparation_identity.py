import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image, UnidentifiedImageError
import focus_direct_transition as d


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=d.h.ROOT/'.build')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def image(self, name='image.png', size=(24,20), alpha=17):
        path = self.root/name
        Image.new('RGBA', size, (40,80,120,alpha)).save(path)
        return d.h.ref(path)

    def test_historical_hash_and_alpha(self):
        ref = self.image()
        expected = hashlib.sha256(str((24,20)).encode()+bytes((40,80,120,17))*480).hexdigest()
        self.assertEqual(d.old.decoded_identity(ref), ((24,20),expected))
        self.assertEqual(d.old.decoded_hash(ref),expected)
        self.assertNotEqual(d.old.decoded_hash(self.image('opaque.png',alpha=255)),expected)

    def test_record_one_open_per_endpoint(self):
        ref = self.image()
        frame = dict(image=ref,controls=[dict(state='focused',bounds=[1,1,10,10])])
        with patch.object(Image,'open',wraps=Image.open) as opened:
            row=d.record('id','group','calibration',frame,frame,False,[],{})
            self.assertEqual(opened.call_count,2)
        self.assertEqual(row['size'],[24,20])
        self.assertEqual(row['decodedPixelHashes'],[d.old.decoded_hash(ref)]*2)
        other=dict(frame,image=self.image('other.png',size=(25,20)))
        with self.assertRaisesRegex(ValueError,'viewport_changed'):
            d.record('id','group','calibration',frame,other,False,[],{})

    def test_changed_bytes_and_corruption(self):
        ref=self.image()
        (self.root/'image.png').write_bytes(b'not a PNG')
        with self.assertRaises(ValueError):d.old.decoded_identity(ref)
        with self.assertRaises(UnidentifiedImageError):
            d.old.decoded_identity(d.h.ref(self.root/'image.png'))

    def test_non_png(self):
        path=self.root/'image.jpg';Image.new('RGB',(24,20)).save(path)
        with self.assertRaisesRegex(ValueError,'invalid_endpoint_image'):
            d.old.decoded_identity(d.h.ref(path))


if __name__=='__main__':unittest.main()
