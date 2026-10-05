import unittest
from unittest.mock import patch
import diagnose181 as d


class AuditTests(unittest.TestCase):
    def box(self,x=0,score=.9):return dict(xyxyPixels=[x,0,x+10,10],score=score)

    def test_duplicate_detections_and_threshold(self):
        r=d.detailed([[0,0,10,10]],[self.box(),self.box(score=.8),self.box(30,.24)])
        self.assertEqual((r['tp'],r['fp'],r['fn']),(1,1,0))
        d.reconcile([r],dict(support=1,tp=1,fp=1,fn=0))
        with self.assertRaisesRegex(Exception,'count_reconciliation'):d.reconcile([r],dict(support=1,tp=1,fp=0,fn=0))

    def test_spatial_association_not_count_cancellation(self):
        r=d.associate([self.box(),self.box(40)],[self.box(1),self.box(80)])
        self.assertEqual(r,dict(spatiallyRetained=[[0,0]],introduced=[1],resolved=[1]))

    def test_missing_truth_and_empty_success(self):
        self.assertEqual(d.detailed([],[])['fp'],0)
        self.assertEqual(d.detailed([],[self.box()])['fp'],1)
        self.assertEqual(d.detailed([[0,0,10,10]],[])['fn'],1)

    def test_collision_precedes_inputs(self):
        with patch.object(d,'OUT',d.h.ROOT),patch.object(d.r,'ready') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):d.run()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
