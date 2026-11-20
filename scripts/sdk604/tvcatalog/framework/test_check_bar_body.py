"""Regression cases for the TVCatalog floating-strip geometry policy."""
import unittest

import numpy as np
from check_bar_body import native_candidates, painted_reference


class BarBodyTests(unittest.TestCase):
    full = [0, 92, 3840, 136]
    ref = [1073, 91, 1695, 138]
    transform = [2, 0, 0, 2, 0, 0]

    def snapshot(self, children):
        def node(ident, parent, left, width):
            return dict(id=ident, parent=parent, clippedBounds=dict(x=left,y=46,width=width,height=68))
        return dict(layout=dict(coordinateSpace='window_points',
            captureGeometry=dict(toScreenPoints=[1,0,0,1,0,0]),
            nodes=[node('bar', None, 0, 1920)] + [node(*child) for child in children]))

    def test_duplicate_nodes_with_same_rectangle(self):
        rect, ids = native_candidates(self.snapshot([('first','bar',537,846.5),
            ('second','first',537,846.5)]),self.transform,self.full,self.ref)
        self.assertEqual(rect,(1074,92,1693,136))
        self.assertEqual(ids,['first','second'])

    def test_missing_or_unrelated_body(self):
        for children in [[], [('candidate',None,537,846.5)]]:
            with self.assertRaisesRegex(ValueError,'missing or ambiguous'):
                native_candidates(self.snapshot(children),self.transform,self.full,self.ref)

    def test_distinct_passing_rectangles(self):
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            native_candidates(self.snapshot([('a','bar',537,846.5),('b','bar',536.5,847)]),
                              self.transform,self.full,self.ref)

    def test_no_painted_reference(self):
        with self.assertRaisesRegex(ValueError,'no closed painted strip'):
            painted_reference(np.zeros((1080,1920),dtype=np.uint8))
