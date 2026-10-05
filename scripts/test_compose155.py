import unittest
import numpy as np
from compose155 import bounds,catalog


class ComposeTests(unittest.TestCase):
    def test_catalog(self):
        rows=catalog();self.assertEqual(len(rows),96);self.assertEqual(len({r['id'] for r in rows}),96)
        self.assertEqual(rows,catalog())
    def test_controlled_difference(self):
        a=np.zeros((20,20,3),np.uint8);b=a.copy();a[4:8,5:9]=255
        self.assertEqual(bounds(a,b,[2,1,4,4],2),[2.5,2.,2.,2.])
        a[18,18]=255
        with self.assertRaisesRegex(ValueError,'outside'):bounds(a,b,[2,1,4,4],2)
        with self.assertRaisesRegex(ValueError,'empty'):bounds(b,b,[2,1,4,4],2)


if __name__=='__main__':unittest.main()
