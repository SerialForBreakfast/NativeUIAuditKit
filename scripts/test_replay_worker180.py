import unittest
from unittest.mock import patch
import replay_worker180 as w


class Tests(unittest.TestCase):
    def test_scores_complete_and_failures(self):
        rows=[dict(model=m,placement=p,start=0,probabilities=[.5]*3) for m in range(3) for p in range(2)]
        self.assertEqual(w.scores(rows,3).shape,(3,2,3))
        for bad in (rows[:-1],rows[::-1],[dict(rows[0],probabilities=[float('nan')]*3)], [dict(rows[0],probabilities=[2.]*3)],
                    [dict(rows[0],probabilities=['.5']*3)],[dict(rows[0],probabilities=[True]*3)],[dict(rows[0],model=False)]):
            with self.assertRaises(Exception):w.scores(bad,3)

    def test_chunk_boundaries_and_resume_prefix(self):
        rows=[dict(model=m,placement=p,start=start,probabilities=[.5]*min(1024,1027-start)) for m in range(3) for p in range(2) for start in (0,1024)]
        self.assertEqual(w.scores(rows,1027).shape,(3,2,1027))
        with self.assertRaisesRegex(Exception,'chunk_order'):w.scores(rows[:2]+rows[1:],1027)
        with self.assertRaisesRegex(Exception,'incomplete_scores'):w.scores(rows[:2],1027)

    def test_transform_sides_and_padding(self):
        torch=w.v.n.d.torch_runtime();pair=torch.empty(6,11,13);pair[:3]=.3;pair[3:]=.7;rect=[2,3,11,10]
        for mode in (0,1):
            out=w.placed(torch,pair,rect,767,mode);a,b,c,d=w.a.bounds(rect,7,7,2);expected=pair.clone()
            expected[:3,b:d,a:c]=torch.round(torch.tensor(.18)*255)/255
            if mode==1:expected[3:,b:d,a:c]=torch.round(torch.tensor(.58)*255)/255
            self.assertTrue(torch.equal(out,expected));self.assertTrue(torch.equal(pair[:3],torch.full_like(pair[:3],.3)))
        with self.assertRaisesRegex(Exception,'placement'):w.placed(torch,pair,rect,0,2)

    def test_paths_and_collision(self):
        with self.assertRaisesRegex(Exception,'outside_project'):w.local('/etc')
        with patch.object(w.h,'read') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):w.run(w.h.ROOT/'reports',w.h.ROOT/'Tasks.md')
            read.assert_not_called()


if __name__=='__main__':unittest.main()
