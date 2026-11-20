import unittest
import numpy as np
from inspect_frames import sheet_pixels
from verify import strength,states

class VisibilityTests(unittest.TestCase):
    def test_tint_alone_does_not_verify_switch_outline(self):
        a=np.full((140,200,3),[180,70,70],dtype='uint8')
        self.assertEqual(strength(a,[20,20,50,50],True),0)
        a[20:70,20:70,1]=110
        self.assertEqual(strength(a,[20,20,50,50],True),40)
    def test_rectangular_surface_rejects_small_tinted_control(self):
        a=np.zeros((120,180,3),dtype='uint8')
        a[20:42,20:48,0]=220
        self.assertIsNone(sheet_pixels(a))
        a[60:110,10:170,0]=220
        self.assertEqual(sheet_pixels(a),[10,60,160,50])
    def test_no_settlement_without_observed_geometry(self):
        with self.assertRaisesRegex(ValueError,'incomplete_episode'):states([])
