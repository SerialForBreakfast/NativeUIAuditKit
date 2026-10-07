"""Check fixed scores and threshold selection without native capture."""
import unittest
from unittest.mock import patch
import numpy as np
import transition244 as t


class DiagnosticTests(unittest.TestCase):
    def test_output_collision_stops_before_input_read(self):
        with patch.object(t,'OUT') as output, patch.object(t.p,'load_inputs') as load:
            output.exists.return_value=True
            with self.assertRaisesRegex(ValueError,'output_collision'):t.run()
            load.assert_not_called()

    def test_nominal_bounds_ignore_focus_effect(self):
        scene={'elements':[dict(element_id='a',is_accessibility_element=True,
            pixel_bounds=[0,0,20,20],artwork_geometry={'pixel_bounds':[2,2,10,10]},
            rendered_body_geometry={'pixel_bounds':[0,0,30,30]})]}
        self.assertEqual(t.boxes(scene),{'a':[2,2,10,10]})
        self.assertEqual(t.common_boxes(t.boxes(scene),t.boxes(scene)),[[2,2,10,10]])

    def test_conflicting_regions_fail(self):
        with self.assertRaisesRegex(ValueError,'nominal_geometry_changed'):
            t.common_boxes({'a':[0,0,10,10]},{'a':[1,0,10,10]})
        with self.assertRaisesRegex(ValueError,'candidate_membership_changed'):
            t.common_boxes({'a':[0,0,10,10]}, {})

    def test_offscreen_rectangle_is_empty(self):
        self.assertFalse(t.rect([-50,0,10,10],(1,1,0,0),(20,20),1).any())

    def test_identity_and_border_signal(self):
        a=np.zeros((3,40,40),dtype=np.float32)
        box=[10,10,20,20];transform=(1,1,0,0)
        same=t.scores(a,a,[box],transform)
        self.assertTrue(same['identical'])
        self.assertEqual(same['whole'],0)
        b=a.copy()
        ring=t.rect(box,transform,(40,40),1.2)&~t.rect(box,transform,(40,40),.8)
        b[:,ring]=1
        score=t.scores(a,b,[box],transform)
        self.assertEqual(score['border'],1)
        self.assertFalse(score['identical'])

    def test_threshold_and_fixed_audit(self):
        chosen=t.choose_threshold([0,1,2,3],[0,0,1,1])
        self.assertEqual(chosen['threshold'],1)
        self.assertEqual(chosen['trainingBalancedError'],0)
        result=t.counts([3,0],[0,1],chosen['threshold'])
        self.assertEqual(result['falseChange'],1)
        self.assertEqual(result['missedChange'],1)

    def test_invalid_threshold_support(self):
        for values,labels in [([],[]),([1],[0]),([float('nan'),1],[0,1])]:
            with self.assertRaisesRegex(ValueError,'threshold_support'):
                t.choose_threshold(values,labels)

    def test_empty_counts(self):
        self.assertEqual(t.counts([],[],0)['count'],0)


if __name__=='__main__':unittest.main()
