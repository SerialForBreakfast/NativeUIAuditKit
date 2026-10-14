"""Check independent authored effect controls."""
import unittest
import numpy as np
from PIL import Image
import effect326 as e


class EffectTests(unittest.TestCase):
    def test_independent_axes(self):
        art=Image.new('RGB',(40,60),(80,100,120))
        for size in (3,6):
            _,box,params=e.tile(art,size,3,.75,True,'independent')
            self.assertEqual(params['borderPixels'],30)
            self.assertEqual(params['contrast'],.75)
            self.assertEqual(box[2],round(size*10*1.14))
        _,_,coupled=e.tile(art,3,3,.75,True,'coupled')
        self.assertEqual(coupled['borderPixels'],15)
        self.assertEqual(coupled['contrast'],.375)

    def test_unfocused_invariant(self):
        art=Image.new('RGB',(40,60),(80,100,120))
        a=e.tile(art,3,1,.25,False,'coupled')[0]
        b=e.tile(art,3,3,.75,False,'independent')[0]
        self.assertTrue(np.array_equal(a,b))

    def test_pixel_effect_and_repeatability(self):
        art=Image.new('RGB',(40,60),(80,100,120))
        a,box,_=e.tile(art,3,1,.25,True,'independent')
        b,box2,_=e.tile(art,3,3,.75,True,'independent')
        self.assertEqual(box,box2)
        self.assertFalse(np.array_equal(a,b))
        self.assertTrue(np.array_equal(b,e.tile(art,3,3,.75,True,'independent')[0]))

    def test_invalid_parameters(self):
        art=Image.new('RGB',(40,60))
        for args in [(0,1,.25,True,'independent'),(3,0,.25,True,'coupled'),(3,1,2,True,'independent'),(3,1,.25,True,'unknown')]:
            with self.assertRaises(ValueError):e.tile(art,*args)

    def test_contrast_changes_pixels_without_geometry(self):
        art=Image.new('RGB',(40,60),(80,100,120))
        low,lb,_=e.tile(art,3,1,.25,True,'independent')
        high,hb,_=e.tile(art,3,1,.75,True,'independent')
        self.assertEqual(lb,hb)
        self.assertGreater(np.asarray(high).sum(),np.asarray(low).sum())

    def test_width_changes_extent_without_body(self):
        art=Image.new('RGB',(40,60),(80,100,120))
        narrow,nb,_=e.tile(art,3,1,.75,True,'independent')
        wide,wb,_=e.tile(art,3,3,.75,True,'independent')
        self.assertEqual(nb,wb)
        bg=np.array([20,20,25]);n=np.any(np.asarray(narrow)!=bg,2);w=np.any(np.asarray(wide)!=bg,2)
        self.assertGreater(w.sum(),n.sum())
        self.assertFalse(w[[0,-1]].any());self.assertFalse(w[:,[0,-1]].any())


if __name__=='__main__':unittest.main()
