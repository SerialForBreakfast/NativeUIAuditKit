import unittest
import numpy as np
from PIL import Image,ImageDraw
import diagnose_signal95 as s


class SignalTests(unittest.TestCase):
    def test_source_coverage_does_not_conflate_roles_or_labels(self):
        rows=[dict(id='a:1',split='train',changed=True),dict(id='a:2',split='development',changed=False)]
        self.assertEqual(s.source_coverage(rows,{'native':{'sha256':'a'}}),[
            dict(source='native',split='development',changed=False,pairs=1),
            dict(source='native',split='train',changed=True,pairs=1)])
        with self.assertRaisesRegex(ValueError,'source_identity'):s.source_coverage(rows,{'wrong':{'sha256':'b'}})

    def test_default_parity_and_identity(self):
        image=Image.new('RGB',(200,120),(40,80,120))
        x,t=s.encoded(image,image,(96,64))
        self.assertTrue(np.array_equal(x,s.d.encode(image,image)))
        stats=s.metrics(x,[[10,10,30,30]],image.size,t)
        self.assertTrue(stats['identical']);self.assertEqual(stats['meanAbsolute'],0)

    def test_sparse_detail_and_resolution(self):
        before=Image.new('RGB',(768,512));after=before.copy()
        ImageDraw.Draw(after).rectangle((300,200,303,203),fill='white')
        maxima=[]
        for size in s.SIZES:
            x,t=s.encoded(before,after,size);v=s.metrics(x,[[290,190,30,30]],before.size,t)
            self.assertFalse(v['identical']);self.assertGreater(v['truthRegionMean'],v['meanAbsolute'])
            maxima.append(v['maximum'])
        self.assertGreater(maxima[-1],maxima[0])

    def test_invalid_dimensions_and_boxes(self):
        image=Image.new('RGB',(40,30))
        with self.assertRaises(ValueError):s.encoded(image,Image.new('RGB',(41,30)),(96,64))
        with self.assertRaises(ValueError):s.encoded(image,image,(999,999))
        x,t=s.encoded(image,image,(96,64))
        with self.assertRaises(ValueError):s.metrics(x,[[-1,0,10,10]],image.size,t)


if __name__=='__main__':unittest.main()
