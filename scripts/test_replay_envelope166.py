import unittest
import numpy as np
import replay_envelope166 as e


class ReplayTests(unittest.TestCase):
    def test_sample_covers_cases_and_cells(self):
        ids=e.sample_indices()
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual({e.spec(i)[0] for i in ids},set(range(286)))
        self.assertEqual({i%768 for i in ids},set(range(768)))

    def test_geometry_odd_and_clipped(self):
        for y in range(8):
            for x in range(8):
                for z in range(3):
                    a,b,c,d=e.bounds([2,3,11,10],y,x,z)
                    self.assertTrue(2<=a<c<=11 and 3<=b<d<=10)
        with self.assertRaises(ValueError):e.bounds([0,0,0,1],0,0,0)
        for i in (-1,e.COUNT,True):
            with self.assertRaises(ValueError):e.spec(i)

    def test_missing_and_bad_scores(self):
        with self.assertRaisesRegex(ValueError,'incomplete_scores'):e.checked_scores([])
        for q in [dict(model=1,start=0,probabilities=[.5]*1024),
                  dict(model=0,start=0,probabilities=[float('nan')]*1024),
                  dict(model=0,start=0,probabilities=[1.1]*1024)]:
            with self.assertRaises(ValueError):e.checked_scores([q])

    def test_complete_count_and_order(self):
        chunks=[dict(model=m,start=i,probabilities=[.5]*min(1024,e.COUNT-i))
                for m in range(3) for i in range(0,e.COUNT,1024)]
        self.assertEqual(e.checked_scores(chunks).shape,(3,e.COUNT))
        with self.assertRaises(ValueError):e.checked_scores(chunks[::-1])

    def test_transformation_preserves_before_and_padding(self):
        torch=e.v.n.d.torch_runtime()
        pair=torch.full((6,11,13),.3);rect=[2,3,11,10];i=767
        out=e.transform(torch,pair,rect,i);a,b,c,d=e.bounds(rect,7,7,2)
        expected=pair.clone();expected[3:,b:d,a:c]=torch.round(torch.tensor(.18)*255)/255
        self.assertTrue(torch.equal(out,expected))
        self.assertTrue(torch.equal(out[:3],pair[:3]))


if __name__=='__main__':unittest.main()
