import unittest
import numpy as np
import diagnose_focus116 as f


class LocalTests(unittest.TestCase):
    def test_letterbox_and_union(self):
        m=f.mask([[0,0,1920,1080]]*2,[1920,1080])
        self.assertEqual(int(m.sum()),192*108)
        self.assertFalse(m[:10].any());self.assertTrue(m[10:118].all())
        n=f.mask([[0,0,960,540],[960,540,960,540]],[1920,1080])
        self.assertEqual(int(n.sum()),192*108//2)

    def test_bad_bounds(self):
        for b in (None,[-1,0,2,2],[0,0,0,2],[0,0,1921,1080],[0,float('nan'),2,2]):
            with self.assertRaises(ValueError):f.mask([b,b],[1920,1080])

    def test_complement_and_false_change(self):
        m=f.mask([[1,2,30,40]]*2,[192,128]);x=np.ones((128,192))
        self.assertTrue(np.array_equal(x*m+x*~m,x))
        s=f.summary(np.array([1.,.5,0.]),np.array([0.,1.,0.]),np.array([False,True,False]),[0,1,2])
        self.assertEqual((s['falseChanges'],s['lostSuccesses'],s['abstentions']),(1,2,1))


if __name__=='__main__':unittest.main()
