import unittest
import roi197 as r


class Tests(unittest.TestCase):
    def row(self, entries):
        return dict(status='ok', detections=[dict(classID=c, score=s, xyxyPixels=b) for c,s,b in entries])

    def test_cap_floor_and_tie(self):
        row=self.row([(2,.0009,[0,0,10,10]),(2,.1,[20,0,30,10]),(2,.1,[40,0,50,10]),(3,.2,[0,0,10,10])])
        self.assertEqual(r.candidate(row,2)[0][0],1)
        self.assertEqual(r.candidate(self.row([(2,.0009,[0,0,10,10])]),2),(None,'absent'))

    def test_duplicate_does_not_fallback(self):
        row=self.row([(2,.8,[0,0,10,10]),(2,.2,[0,0,10,10]),(2,.1,[20,0,30,10])])
        self.assertEqual(r.candidate(row,2),(None,'duplicate_operating'))

    def test_error_is_not_empty(self):
        with self.assertRaisesRegex(Exception,'failed_inference'):
            r.candidate(dict(status='error',detections=[]),2)

    def test_windows_deterministic_cover_edges(self):
        ws=r.windows(101,219)
        self.assertEqual(ws,r.windows(101,219))
        self.assertEqual(len(ws),len({tuple(w) for w in ws}))
        self.assertTrue(any(w[2:]==[101,219] for w in ws))
        self.assertTrue(all(w[2]-w[0]==51 and w[3]-w[1]==51 for w in ws))
        for y in range(219):
            for x in range(101):
                self.assertTrue(any(w[0]<=x<w[2] and w[1]<=y<w[3] for w in ws))

    def test_invalid_or_excessive_dimensions(self):
        for shape in [(100,50),(0,100),(100.0,200),(2,16384)]:
            with self.assertRaises(Exception):r.windows(*shape)

    def test_clipped_is_not_contained(self):
        self.assertFalse(r.contained([0,0,10,10],[1,0,11,10]))
        self.assertTrue(r.contained([0,0,10,10],[0,0,10,10]))


if __name__=='__main__':unittest.main()
