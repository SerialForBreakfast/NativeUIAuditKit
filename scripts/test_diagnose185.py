import unittest
from unittest.mock import patch
import diagnose185 as d


class Tests(unittest.TestCase):
    def test_changes_and_order(self):
        a=dict(id='a',fp=1,hitIndices=[0],falsePredictions=[dict(xyxyPixels=[0,0,10,10],score=.9)])
        b=dict(id='a',fp=0,hitIndices=[],falsePredictions=[])
        result=d.changes([a],[b]);self.assertEqual(result['totals']['resolved'],1);self.assertEqual(result['totals']['lostHits'],1)
        with self.assertRaisesRegex(Exception,'case_order'):d.changes([a],[dict(b,id='b')])

    def test_geometry(self):
        c=dict(sourceBox=[0,0,10,2],bestIoU=.5,bestIoUCandidate=dict(xyxyPixels=[0,-1,10,3],score=.9))
        got=d.geometry(c);self.assertEqual(got['heightRatio'],2);self.assertEqual(got['centerYErrorInHeights'],0)
        self.assertIsNone(d.geometry(dict(c,bestIoUCandidate=None)))
        with self.assertRaisesRegex(Exception,'truth_geometry'):d.geometry(dict(c,sourceBox=[0,0,0,2]))

    def test_collision_before_reads(self):
        with patch.object(d,'OUT',d.h.ROOT),patch.object(d.f.d,'inputs') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):d.run()
            read.assert_not_called()

    def test_legacy_fit_contract(self):
        meta={str(i):dict(family='toy') for i in range(216)}
        rows=[dict(id=str(i)) for i in range(432)]
        args=dict(epochs=20,batch=8,imgsz=640,rect=True)
        ref=dict(rows=rows,metadata=meta)
        self.assertEqual(len(d.fit_protocol(dict(metadata=meta),ref,args)['rows']),216)
        with self.assertRaisesRegex(Exception,'fit_membership'):d.fit_protocol(dict(metadata=meta),dict(ref,rows=rows[:200]),args)
        with self.assertRaisesRegex(Exception,'fit_settings'):d.fit_protocol(dict(metadata=meta),ref,dict(args,epochs=10))


if __name__=='__main__':unittest.main()
