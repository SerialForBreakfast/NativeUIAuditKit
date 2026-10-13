"""Reject ambiguous observations and invalid native body bounds."""
import copy
import unittest
from native_receipt373 import scene_record

class NativeReceiptTests(unittest.TestCase):
    def scene(self):
        body=dict(version=1,availability='measured',role='rendered_control_body',element_id='a',generation=2,
                  coordinate_space='image_top_left_pixels',visible_pixel_bounds=[10,20,30,40],visible_normalized_bounds=[.1,.2,.4,.6])
        return dict(schema_version=1,is_settled=True,isSettled=True,focused_element_id='a',activeFocusId='a',
                    focus_observation=dict(observedID='a',verified=True,generation=2),observation_generation=2,
                    scene_width=100,scene_height=100,fixture_run_id='run',timestamp=1,
                    elements=[dict(id='a',is_focused=True,rendered_body_geometry=body)])

    def test_valid(self):self.assertEqual(scene_record(self.scene(),(100,100))['bounds'],[10,20,30,40])

    def test_missing_native_focus_is_not_false_label(self):
        s=self.scene();s['elements'][0].pop('is_focused')
        with self.assertRaisesRegex(ValueError,'selected_focus'):scene_record(s,(100,100))

    def test_stale_generation(self):
        s=self.scene();s['elements'][0]['rendered_body_geometry']['generation']=1
        with self.assertRaisesRegex(ValueError,'body_generation'):scene_record(s,(100,100))

    def test_bounds_and_normalized_coordinates(self):
        for key,value in [('visible_pixel_bounds',[10,20,100,40]),('visible_normalized_bounds',[.1,.2,.3,.4])]:
            s=self.scene();s['elements'][0]['rendered_body_geometry'][key]=value
            with self.assertRaises(ValueError):scene_record(s,(100,100))

    def test_ambiguous_focus(self):
        s=self.scene();s['elements'].append(copy.deepcopy(s['elements'][0]))
        with self.assertRaisesRegex(ValueError,'selected_focus'):scene_record(s,(100,100))

if __name__=='__main__':unittest.main()
