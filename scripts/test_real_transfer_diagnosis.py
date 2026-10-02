import unittest
import numpy as np
from PIL import Image
from real_transfer_diagnosis import masks,apply_mask,luminance,diagnostic_window
from real_transfer_coverage import aspect


class MaskTests(unittest.TestCase):
    def test_aspect(self):
        self.assertEqual(aspect([0,0,100,10]),10)
        with self.assertRaises(Exception):aspect([0,0,1,0])

    def test_clipped_diagnostic(self):
        requested,actual,clipped=diagnostic_window([80,20,20,20],(100,100))
        self.assertTrue(clipped);self.assertEqual(actual,[76,16,24,28])
        self.assertEqual(requested,[76,16,28,28])

    def test_invalid_geometry_not_relaxed(self):
        with self.assertRaises(Exception):diagnostic_window([80,20,21,20],(100,100))

    def test_union_and_target_exclusion(self):
        result=masks([10,10,10,10],[[10,10,10,10]],[[8,8,14,14]])
        self.assertFalse(np.any(result['neighbor']&result['target']))
        self.assertTrue(np.all(result['neighbor']|result['target']))

    def test_no_neighbors(self):
        self.assertEqual(int(masks([10,10,10,10],[[10,10,10,10]],[])['neighbor'].sum()),0)

    def test_offscreen_mask(self):
        self.assertEqual(int(masks([10,10,10,10],[],[[100,100,10,10]])['neighbor'].sum()),0)

    def test_mask_preserves_source(self):
        im=Image.new('RGB',(256,256),'white');mask=np.zeros((256,256),bool);mask[0,0]=True
        out=apply_mask(im,mask)
        self.assertEqual(out.getpixel((0,0)),(128,128,128))
        self.assertEqual(im.getpixel((0,0)),(255,255,255))
        self.assertEqual(out.getpixel((1,0)),im.getpixel((1,0)))

    def test_invalid_shape(self):
        with self.assertRaises(Exception):apply_mask(Image.new('RGB',(256,256)),np.zeros((2,2),bool))

    def test_brightness_order(self):
        self.assertGreater(luminance(Image.new('RGB',(256,256),'white')),luminance(Image.new('RGB',(256,256),'black')))

    def test_union_order_invariant(self):
        a=[10,10,10,10];b=[12,12,10,10]
        self.assertTrue(np.array_equal(masks(a,[a,b],[])['target'],masks(a,[b,a],[])['target']))


if __name__=='__main__':unittest.main()
