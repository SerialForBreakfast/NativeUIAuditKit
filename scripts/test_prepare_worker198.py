import unittest
from types import SimpleNamespace
import hashlib
from PIL import Image
from prepare_worker198 import select, pixel_sha, check_bounds


class SelectionTests(unittest.TestCase):
    def test_pixel_encoding(self):
        image=Image.new('RGB',(1,1),(1,2,3))
        self.assertEqual(pixel_sha(image),hashlib.sha256(b'(1, 1)\x01\x02\x03').hexdigest())
        self.assertEqual(pixel_sha(image.convert('RGBA')),pixel_sha(image))
        self.assertNotEqual(pixel_sha(image),hashlib.sha256(image.tobytes()).hexdigest())

    def test_exact_member_exception_and_totals(self):
        check_bounds([dict(path='initializer.pt',bytes=40539244)])
        for rows in ([dict(path='other.pt',bytes=40539244)],
                     [dict(path='initializer.pt',bytes=41000001)],
                     [dict(path='x',bytes=1)]*1101,
                     [dict(path='x',bytes=31000000)]*2):
            with self.assertRaises(ValueError):check_bounds(rows)

    def test_deterministic_complete_membership(self):
        images=[SimpleNamespace(image_id=str(i)) for i in range(600)]
        lineage=[dict(id=str(i)) for i in range(600)]
        a=select(images,lineage);b=select(list(reversed(images)),lineage)
        self.assertEqual([i.image_id for i in a],[i.image_id for i in b])
        self.assertEqual(len({i.image_id for i in a}),512)

    def test_missing_and_duplicate_membership(self):
        images=[SimpleNamespace(image_id=str(i)) for i in range(600)]
        lineage=[dict(id=str(i)) for i in range(600)]
        for im,lin in [(images[:20],lineage),(images,lineage[:20]),
                       (images+[images[0]],lineage),(images,lineage+[lineage[0]])]:
            with self.assertRaises(ValueError):select(im,lin)


if __name__=='__main__':unittest.main()
