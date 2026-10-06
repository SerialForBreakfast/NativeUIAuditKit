import unittest
import roi195 as r
import roi195_geometry as g


class Tests(unittest.TestCase):
    def test_bounds_are_not_occlusion_claims(self):
        self.assertEqual(g.bounds_state([0,0,10,10],10,10),'contained')
        self.assertEqual(g.bounds_state([-1,0,10,10],10,10),'outside')
        with self.assertRaises(Exception):g.bounds_state([0,0,0,10],10,10)
    def test_truth_association_stays_fixed(self):
        a=dict(classID=18,score=.7,xyxyPixels=[0,0,10,10]);b=dict(a,xyxyPixels=[20,0,30,10])
        row=r.compare_row(a,b,[[0,0,10,10],[20,0,30,10]])
        self.assertEqual(row['truthIndex'],0);self.assertEqual(row['after']['iou'],0)
        self.assertEqual(row['disposition'],'regressed')
    def test_conservation_and_no_truth(self):
        a=dict(classID=18,score=.1,xyxyPixels=[0,0,10,10])
        self.assertFalse(r.compare_row(a,a,[])['operating'])
        self.assertEqual(r.compare_row(a,a,[])['disposition'],'no_overlap_truth')
        with self.assertRaises(Exception):r.compare_row(a,dict(a,score=.2),[])
    def row(self,i,split='train'):
        return dict(id=str(i),split=split,sourceFamily='family',image=dict(sha256=str(i)),pixelSHA256=str(i))
    def test_selection_is_bounded_deterministic(self):
        rows=[self.row(i) for i in range(30)]
        chosen=r.choose(rows,{'0'},[])
        self.assertEqual(len(chosen),24);self.assertNotIn('0',[x['id'] for x in chosen])
        self.assertEqual(chosen,r.choose(list(reversed(rows)),{'0'},[]))
    def test_roles_and_pixels_cannot_leak(self):
        with self.assertRaisesRegex(Exception,'role'):r.choose([self.row(1,'test')],set(),[])
        with self.assertRaisesRegex(Exception,'overlap'):r.choose([self.row(1)],set(),[self.row(1,'test')])
        row=self.row(2);row['pixelSHA256']='1'
        with self.assertRaisesRegex(Exception,'overlap'):r.choose([row],set(),[self.row(1,'test')])
    def test_summary_has_all_predictions(self):
        a=dict(classID=18,score=.7,xyxyPixels=[0,0,10,10]);b=dict(a,xyxyPixels=[0,0,10,20])
        summary=r.summarize([r.compare_row(a,b,[[0,0,10,10]]),r.compare_row(a,a,[])])
        self.assertEqual(summary['predictions'],2);self.assertEqual(summary['changed'],1)
        self.assertEqual(summary['changedMedians']['after']['heightRatio'],2)


if __name__=='__main__':unittest.main()
