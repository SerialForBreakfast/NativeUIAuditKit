"""Offline interruption evidence failures; all temporary files stay in project."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import audit_fixture_interruptions as a
from test_fixture_rendered_body import body


def sample(overlay=False):
    scene = dict(scene_width=100, scene_height=100, monotonic_nanoseconds=1,
                 is_settled=not overlay, focused_element_id=None if overlay else 'a',
                 elements=[dict(element_id='a', rendered_body_geometry=body())])
    if overlay:
        scene['interruption'] = dict(event_id='abc', geometry_source='uikit_presentation_layer_window_pixels',
            overlay_bounds=[0,0,100,100], action_bounds=[10,10,80,30],
            observed_focus_id='interruption.continue', phase='failed', recovery='dismissal_failed',
            underlay_visibility={'a':'fully_covered'})
    else:
        scene['focus_observation'] = dict(generation=7, observedID='a', requestedID='a', verified=True)
    return dict(before=scene, after=copy.deepcopy(scene),
                capture=dict(state='delivered', effectStatus='unverified'))


class InterruptionTests(unittest.TestCase):
    def check(self, d):
        return a.audit_frame(d, (100,100), 'abc')

    def test_normal(self):
        r=self.check(sample()); self.assertEqual(r['proposals'][0]['state'],'focused')
        self.assertTrue(r['settled']); self.assertEqual(r['generationBinding'],'native_focus')

    def test_overlay_and_failure_not_reclassified(self):
        r=self.check(sample(True)); self.assertFalse(r['settled'])
        self.assertEqual(r['recovery'],'dismissal_failed')
        self.assertEqual(r['generationBinding'],'body_records_only')
        self.assertEqual([p['id'] for p in r['proposals']],['interruption.continue'])
        self.assertEqual(r['excluded'][0]['reason'],'fully_covered')

    def test_partially_covered_excluded_and_visible_unknown(self):
        for state, count in [('partially_covered',1),('visible',2)]:
            d=sample(True)
            for s in ('before','after'): d[s]['interruption']['underlay_visibility']['a']=state
            r=self.check(d); self.assertEqual(len(r['proposals']),count)
            if count==2:self.assertEqual(r['proposals'][0]['state'],'unknown')

    def test_removed_body_not_negative(self):
        d=sample()
        for s in ('before','after'):
            b=d[s]['elements'][0]['rendered_body_geometry']
            for k in ('full_pixel_bounds','visible_pixel_bounds','visible_normalized_bounds'):b.pop(k)
            b.update(availability='unavailable', unavailable_reason='not_rendered')
        r=self.check(d); self.assertEqual(r['proposals'],[])
        self.assertEqual(r['excluded'][0]['reason'],'body_unavailable')

    def test_geometry_focus_and_event_drift(self):
        for key,value in [('focused_element_id','b'),('is_settled',False),('elements',[])]:
            d=sample();d['after'][key]=value
            with self.assertRaisesRegex(ValueError,'bracket_drift'):self.check(d)
        d=sample(True)
        for s in ('before','after'):d[s]['interruption']['event_id']='wrong'
        with self.assertRaisesRegex(ValueError,'event_mismatch'):self.check(d)

    def test_focus_generation_mismatch(self):
        d=sample()
        for s in ('before','after'):d[s]['focus_observation']['generation']=8
        with self.assertRaisesRegex(ValueError,'focus_binding'):self.check(d)

    def test_missing_visibility_and_invalid_action(self):
        for change,reason in [('visibility','visibility_membership'),('bounds','bounds_range')]:
            d=sample(True)
            for s in ('before','after'):
                i=d[s]['interruption']
                if change=='visibility':i['underlay_visibility']={}
                else:i['action_bounds']=[90,0,80,30]
            with self.assertRaisesRegex(ValueError,reason):self.check(d)

    def test_terminal_without_geometry(self):
        d=sample()
        for s in ('before','after'):
            d[s]['interruption']=dict(event_id='abc',phase='ended',recovery='restoration_unverified')
        self.assertEqual(self.check(d)['recovery'],'restoration_unverified')

    def test_member_integrity_protected_and_paths(self):
        base=a.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as tmp:
            root=Path(tmp);f=root/'data.json';f.write_text('{}')
            manifest={'schema_version':1,'files':[dict(path='data.json',bytes=2,sha256=a.sha(f))]}
            (root/'manifest.json').write_text(json.dumps(manifest))
            self.assertEqual(len(a.integrity(root,set())['files']),1)
            with self.assertRaisesRegex(ValueError,'protected_bytes'):a.integrity(root,{a.sha(f)})
            with self.assertRaisesRegex(ValueError,'unsafe_member'):a.member(root,'../data.json')
            f.write_text('[]')
            with self.assertRaisesRegex(ValueError,'member_integrity'):a.integrity(root,set())
            (root/'extra').write_text('x')
            with self.assertRaisesRegex(ValueError,'manifest_membership'):a.integrity(root,set())


if __name__=='__main__':unittest.main()
