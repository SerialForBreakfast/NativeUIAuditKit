import unittest
import numpy as np
from ios_sheet_visibility610 import visible_body,footprint


class SheetMaskTests(unittest.TestCase):
    def test_hidden_partial_and_fragmented(self):
        mask=np.zeros((10,10),bool)
        mask[4:,2:8]=True
        self.assertEqual(visible_body([2,4,8,10],mask)['disposition'],'fully_hidden')
        self.assertEqual(visible_body([2,2,8,8],mask)['bounds'],[2,2,6,2])
        self.assertEqual(visible_body([0,6,10,10],mask)['fragments'],[[0,6,2,4],[8,6,2,4]])
        self.assertEqual(visible_body([0,0,10,2],mask)['disposition'],'visible')

    def test_invalid_geometry_rejects(self):
        with self.assertRaisesRegex(ValueError,'invalid_source_box'):
            visible_body([-1,0,8,10],np.zeros((10,10),bool))

    def test_unchanged_shadow_does_not_occlude(self):
        black=np.full((8,8,3),40,dtype=np.uint8)
        white=black.copy();white[2:6,2:6]=255
        self.assertEqual(footprint(white,black).sum(),16)
