import unittest
from unittest.mock import patch
import roi192 as r


class Tests(unittest.TestCase):
    def test_edge_clamping_keeps_size(self):
        for box in ([0,0,10,10],[90,190,100,200],[45,95,55,105]):
            x,y,u,v=r.window(100,200,box)
            self.assertEqual((u-x,v-y),(50,50))
            self.assertTrue(0<=x<u<=100 and 0<=y<v<=200)
            self.assertEqual(r.intersect([x,y,u,v],box),100)
    def test_scale(self):
        d=r.support([0,0,10,2],100,200,[0,0,50,50])
        self.assertAlmostEqual(d['full640']['height'],6.4)
        self.assertAlmostEqual(d['roi640']['height'],25.6)
    def test_invalid(self):
        for width,height,box in [(0,1,[0,0,1,1]),(100,200,[0,0,101,1]),(100,200,[0,0,float('nan'),1]),(100,20,[0,0,1,1])]:
            with self.assertRaises(Exception):r.window(width,height,box)
    def test_collision(self):
        with patch.object(r,'OUT',r.h.ROOT),patch.object(r.f,'inputs') as inputs:
            with self.assertRaisesRegex(Exception,'output_collision'):r.run()
            inputs.assert_not_called()


if __name__=='__main__':unittest.main()
