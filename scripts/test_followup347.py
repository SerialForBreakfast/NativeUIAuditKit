import unittest
import numpy as np
from PIL import Image
import followup347 as f


class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):f.a.t.set_num_threads(2)

    def test_black_content_is_not_padding(self):
        x=f.a.t.zeros(1,18,128,192)
        mask=f.masks(x)
        self.assertTrue(mask[0,:,10:118].all())
        self.assertFalse(mask[0,:,:10].any())
        y=f.alter(x,mask,'06-brightness','all-content')
        self.assertEqual(float(y[0,0,0,0]),0)
        self.assertAlmostEqual(float(y[0,0,64,0]),.1,places=6)

    def test_scope_and_originals(self):
        x=f.a.t.rand(2,18,128,192);old=x.clone();mask=f.masks(x)
        for factor in f.FACTORS:
            whole=f.alter(x,mask,factor,'whole-content')
            detail=f.alter(x,mask,factor,'detail-content')
            self.assertTrue(f.a.t.equal(whole[:,6:],x[:,6:]))
            self.assertTrue(f.a.t.equal(detail[:,:6],x[:,:6]))
            self.assertTrue(f.a.t.equal(whole[~mask],x[~mask]))
        self.assertTrue(f.a.t.equal(old,x))
        with self.assertRaises(ValueError):f.alter(x,mask,'bad','all-content')

    def test_source_preprocessing_parity(self):
        rows=f.q.load(f.prior.BASE/'inputs.json')['rows'][:2]
        factor='06-brightness';actual,_=f.source_views(rows,factor)
        for i,row in enumerate(rows):
            images=[f.source_image(f.a.r.s.image(v['path'],v['sha256']),factor) for v in row['images']]
            whole=f.a.r.s.encoded(*images,(192,128))[0]
            self.assertTrue(np.array_equal(actual[i,:6].numpy(),whole))
            boxes=f.a.r.windows(f.a.t.from_numpy(whole[None]))[0]
            for j in range(2):
                if not boxes:expected=whole
                else:
                    x,y=boxes[min(j,len(boxes)-1)]
                    expected=f.a.r.s.crop_pair(images,[x,y,x+32,y+32],preserve_padding=True)
                self.assertTrue(np.array_equal(actual[i,6+j*6:12+j*6].numpy(),expected))

    def test_image_transform_bounds(self):
        image=Image.new('RGB',(12,8),(20,80,240));old=image.tobytes()
        for factor in f.FACTORS:
            output=f.source_image(image,factor)
            self.assertEqual(output.size,image.size)
            self.assertEqual(output.mode,'RGB')
        self.assertEqual(image.tobytes(),old)


if __name__=='__main__':unittest.main()
