"""Check image-change measurements and decision grouping."""
import unittest
import numpy as np
import signal286 as s


class SignalTests(unittest.TestCase):
    def setUp(self):
        self.x=np.zeros((6,4,6),np.float32)
        self.mask=np.zeros((4,6),bool)
        self.mask[:2]=True

    def test_identical(self):
        r=s.measure(self.x,np.zeros((4,6)),self.mask)
        self.assertTrue(r['identical'])
        self.assertIsNone(r['retainedAbsoluteDifference'])
        self.assertIsNone(r['focusRegionFraction'])

    def test_inside_and_reverse(self):
        self.x[3:,:2]=1
        r=s.measure(self.x,np.ones((4,6)),self.mask)
        self.assertEqual(r['focusRegionFraction'],1)
        self.assertEqual(r['retainedAbsoluteDifference'],.5)
        self.assertEqual(r,s.measure(np.concatenate((self.x[3:],self.x[:3])),np.ones((4,6)),self.mask))

    def test_outside(self):
        self.x[3:,2:]=1
        self.assertEqual(s.measure(self.x,np.ones((4,6)),self.mask)['focusRegionFraction'],0)

    def test_invalid(self):
        with self.assertRaisesRegex(ValueError,'region_support'):
            s.measure(self.x,np.zeros((4,6)),np.ones((4,6),bool))
        with self.assertRaisesRegex(ValueError,'finite'):
            s.measure(self.x,np.full((4,6),np.nan),self.mask)

    def test_decisions(self):
        self.assertEqual(s.outcome(.5,1),'uncertain')
        self.assertEqual(s.outcome(.99,1),'correct')
        self.assertEqual(s.outcome(.99,0),'wrong')


if __name__=='__main__': unittest.main()
