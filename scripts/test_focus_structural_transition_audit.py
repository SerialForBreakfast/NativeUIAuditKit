"""Retained transition endpoint validation rejects stale or contradictory evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
import human_annotation_review as h
import focus_structural_transition_audit as a
from test_ttr_sidecar_v2 import scene


class EndpointTests(unittest.TestCase):
    def setUp(self):
        base=h.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=base,prefix='transition22-')
        self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        Image.new('RGB',(64,48),(10,20,30)).save(self.root/'frame.png')
        s=scene('e',4);e=s['elements'][0]
        e['rendered_body_geometry']=dict(version=1,role='rendered_control_body',
            coordinate_space='image_top_left_pixels',element_id='e',generation=4,
            source='native_body_presentation_layer',availability='measured',
            full_pixel_bounds=e['pixel_bounds'],visible_pixel_bounds=e['pixel_bounds'],
            visible_normalized_bounds=e['normalized_bounds'],clipping=None)
        self.capture=dict(before_scene=copy.deepcopy(s),after_scene=copy.deepcopy(s),
            before_scene_received_host_ns=1,frame_received_host_ns=2,after_scene_received_host_ns=3,
            image='frame.png',sha256=h.sha(self.root/'frame.png'),
            action_capture_receipt=dict(state='delivered',sequence=1,operationID='op',
                                       simulatorID='sim',screenshotReference='capture.png'))

    def endpoint(self):
        return a.endpoint(self.root,self.root/'summary.json',self.capture,'frame.png')

    def test_valid_endpoint_preserves_measured_body(self):
        r=self.endpoint();self.assertEqual(r['focus'],'e')
        self.assertEqual(r['controls'][0]['bounds'],[12,8,28,20])

    def test_hash_order_receipt_and_bracket_fail_closed(self):
        original=copy.deepcopy(self.capture)
        for mutate,reason in [
            (lambda c:c.update(sha256='0'*64),'image_hash'),
            (lambda c:c.update(frame_received_host_ns=4),'host_order'),
            (lambda c:c['action_capture_receipt'].update(state='failed'),'capture_receipt'),
            (lambda c:c['before_scene']['focus_observation'].update(generation=5),'generation')]:
            with self.subTest(reason=reason):
                self.capture=copy.deepcopy(original);mutate(self.capture)
                with self.assertRaisesRegex(ValueError,reason):self.endpoint()

    def test_missing_focused_body_is_not_layout_fallback(self):
        for k in ('before_scene','after_scene'):
            del self.capture[k]['elements'][0]['rendered_body_geometry']
        with self.assertRaisesRegex(ValueError,'focused_body_missing'):self.endpoint()

    def test_source_observations_do_not_repair_duplicates_or_offscreen_ids(self):
        s=self.capture['after_scene'];s['semantic_inventory']=dict(elements=[dict(id='film'),dict(id='film')])
        s['focus_observation']['plannedFocusIDs'].append('offscreen')
        original=copy.deepcopy(s);r=a.contract_observations(s)
        self.assertEqual(r,dict(duplicateSemanticIDs={'film':2},plannedIDsAbsentFromVisibleElements=['offscreen']))
        self.assertEqual(s,original)

    def test_real_comparison_cli_rejects_unsealed_input_without_output(self):
        source=self.root/'bad.json';source.write_text(json.dumps(dict(version='focus-recorded-semantics-v1')))
        output=self.root/'output'
        r=subprocess.run([sys.executable,str(h.ROOT/'scripts/focus_recorded_comparison.py'),
            '--semantics',str(source),'--output',str(output)],capture_output=True,text=True,timeout=30)
        self.assertNotEqual(r.returncode,0);self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
