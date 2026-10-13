import unittest
import numpy as np
from study358 import pixels, trend, blocked


class StudyTests(unittest.TestCase):
    def test_identical(self):
        a=np.zeros((4,5,3),dtype=np.uint8)
        self.assertEqual(pixels(a,a)['changedPixels'],0)
        self.assertIsNone(pixels(a,a)['changeBounds'])

    def test_bounds(self):
        a=np.zeros((4,5,3),dtype=np.uint8); b=a.copy(); b[2,3]=255
        self.assertEqual(pixels(a,b)['changeBounds'],[3,2,4,3])
        self.assertEqual(pixels(a,b)['changedPixels'],1)

    def test_invalid(self):
        with self.assertRaises(ValueError):pixels(np.zeros((1,2,3)),np.zeros((2,2,3)))
        with self.assertRaises(ValueError):trend([])
        with self.assertRaises(ValueError):trend([{'loss':float('nan')}]*4)
        with self.assertRaises(ValueError):blocked()

    def test_trends(self):
        self.assertTrue(trend([{'loss':v} for v in (4,3,2,1)])['continuationSignal'])
        self.assertFalse(trend([{'loss':v} for v in (1,2,3,4)])['continuationSignal'])


if __name__=='__main__':unittest.main()
