import unittest
from pathlib import Path
from unittest.mock import patch

import control_eligibility39 as c
import prepare_native_fullscreen as f


class EligibilityTests(unittest.TestCase):
    def test_supported_whole_body(self):
        self.assertTrue(c.eligible([0,0,100,30],[[0,0,100,30]]))

    def test_text_fragment_rejected(self):
        self.assertFalse(c.eligible([10,5,25,10],[[0,0,100,30]]))

    def test_unanchored_rejected(self):
        self.assertFalse(c.eligible([200,0,100,30],[[0,0,100,30]]))

    def test_panel_spanning_disjoint_anchors_rejected(self):
        self.assertFalse(c.eligible([0,0,100,55],[[0,0,100,30],[0,40,100,10]]))

    def test_duplicate_anchors_do_not_reject(self):
        self.assertTrue(c.eligible([0,0,100,30],[[0,0,100,30],[1,0,100,30]]))

    def test_empty_abstains(self):
        self.assertEqual(c.outcome([],[],[])['outcome'],'no_candidates')

    def test_geometry_diagnosis(self):
        r=c.geometry_diagnosis([10,10,20,10],[dict(score=.4,xyxyPixels=[10,10,50,20])])
        self.assertEqual(r['widthRatio'],2);self.assertEqual(r['bestIoU'],.5)

    def test_no_predictions_not_zero_score(self):
        self.assertIsNone(c.geometry_diagnosis([0,0,10,10],[])['score'])


class FullscreenPreparationTests(unittest.TestCase):
    def scene(self):
        return dict(is_settled=True,observation_generation=1,elements=[
            dict(element_id=f'item-{i}',is_focused=i==1,is_hidden=False,rendered_body_geometry={}) for i in range(3)])

    def test_baseline_competitor_retained(self):
        with patch.object(f,'body_validate',return_value=[1,2,30,40]):
            controls=f.annotate(self.scene(),[100,100])
        self.assertEqual([c['state'] for c in controls],['unfocused','focused','unfocused'])

    def test_nonunique_unknown_and_unsettled_rejected(self):
        for edit in ('duplicate','unknown','unsettled','hidden','missing'):
            scene=self.scene()
            if edit=='duplicate':scene['elements'][0]['is_focused']=True
            if edit=='unknown':scene['elements'][0]['is_focused']=None
            if edit=='unsettled':scene['is_settled']=False
            if edit=='hidden':scene['elements'][0]['is_hidden']=True
            if edit=='missing':scene['elements'].pop()
            with patch.object(f,'body_validate',return_value=[1,2,30,40]),self.assertRaises(ValueError):
                f.annotate(scene,[100,100])

    def test_geometry_unavailable_rejected(self):
        with patch.object(f,'body_validate',return_value=None),self.assertRaises(ValueError):
            f.annotate(self.scene(),[100,100])

    def test_split_preserved(self):
        groups={};f.check_group(groups,8,'evaluation')
        with self.assertRaises(ValueError):f.check_group(groups,8,'train')
        with self.assertRaises(ValueError):f.check_group({},8,'development')

    def test_dot_source_capture_order_guard(self):
        # Static regression guard only; live rendering remains separately qualified.
        for name in ('MediaCardGridTemplate.swift','ProgressActivityTemplate.swift'):
            text=(c.h.ROOT/'NativeUIDatasetGenerator/Templates'/name).read_text()
            view=text[text.index('NativeUIPageDotsView('):]
            self.assertLess(view.index('.fixedSize()'),view.index('.captureFrame(id: "pageControl_0")'))
            self.assertLess(view.index('.captureFrame(id: "pageControl_0")'),view.index('.frame(maxWidth: .infinity)'))


if __name__=='__main__':unittest.main()
