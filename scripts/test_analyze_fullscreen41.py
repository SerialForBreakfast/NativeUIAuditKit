"""Offline checks for the final comparison's metric replay."""
import copy
import unittest
from unittest.mock import patch
import analyze_fullscreen41 as a


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.frame=dict(id='case-0',split='evaluation',group='group-8',
            image={'path':'image'},annotation={'path':'annotation'})
        self.row=dict(id='case-0',predictedBounds=[[0,0,10,10]],tp=1,fp=0,fn=0)
        self.doc=dict(frames=[self.row],totals=dict(tp=1,fp=0,fn=0),exactFrames=1)
        self.annotation=dict(controls=[dict(id='item-1',state='focused',bounds=[0,0,10,10])])

    def run_analysis(self):
        with patch.object(a.h,'read',side_effect=[self.doc,{'frames':[self.frame]},self.annotation]), \
             patch.object(a.h,'checked',return_value=a.h.ROOT/'annotation'), \
             patch.object(a.h,'ref',return_value={'path':'pinned'}), \
             patch.object(a.h,'write') as write:
            a.analyze('reports/work/analysis-test.json','reports/work/analysis-result.json')
            return copy.deepcopy(write.call_args.args[1])

    def test_replayed_group_counts(self):
        result=self.run_analysis()
        self.assertEqual(result['groups']['focused-item-1']['exact'],1)
        self.assertEqual(result['failures'],[])

    def test_incorrect_totals_rejected(self):
        self.doc['totals']['tp']=2
        with self.assertRaisesRegex(ValueError,'summary_mismatch'):self.run_analysis()

    def test_incorrect_frame_score_rejected(self):
        self.row['tp']=0
        with self.assertRaisesRegex(ValueError,'metric_mismatch'):self.run_analysis()

    def test_changed_membership_rejected(self):
        self.row['id']='another'
        with self.assertRaisesRegex(ValueError,'membership_changed'):self.run_analysis()


if __name__=='__main__':unittest.main()
