import tempfile
import unittest
from pathlib import Path

from PIL import ImageDraw
import human_annotation_review as h
import focus_transition_stress as fixture
import settings_tracking_diagnosis as d


class TrackingDiagnosisTests(unittest.TestCase):
    def test_gallery_includes_changes_and_different_failures(self):
        rows = [dict(actionID='a', expected='unchanged', attribution='pixel_rule_abstained', id=i) for i in range(20)]
        rows += [dict(actionID='b', expected='arrival', attribution='tracking_unavailable', id=20),
                 dict(actionID='c', expected='unchanged', attribution='wrong_target_geometry', id=21)]
        selected = d.select_gallery(rows, 3)
        self.assertEqual(selected[0]['id'], 20)
        self.assertEqual({r['actionID'] for r in selected}, {'a','b','c'})

    def test_rounds_displacement_not_fractional_annotation(self):
        body = [200.3, 200.2, 160, 60]
        tracking = dict(status='matched', afterBounds=[202.6, 199.9, 160, 60])
        r = d.alignment(body, tracking, None, (640,480), 'roundedDisplacement')
        self.assertAlmostEqual(r['afterBounds'][0], 202.3)
        self.assertAlmostEqual(r['afterBounds'][1], 200.2)
        self.assertEqual(r['afterBounds'][2:], body[2:])

    def test_rounding_does_not_resurrect_rejected_tracking(self):
        tracking = dict(status='unavailable', reason='vision_confidence')
        r = d.alignment([200,200,160,60], tracking, [200,200,160,60], (640,480), 'roundedDisplacement')
        self.assertEqual(r, tracking)
        self.assertIsNot(r, tracking)

    def test_oracle_preserves_growth_and_missing_identity(self):
        body = [200,200,160,60]
        r = d.alignment(body, {}, [190,195,180,70], (640,480), 'reviewedCenterOracle')
        self.assertEqual(r['afterBounds'], body)
        self.assertTrue(r['oracleGeometry'])
        r = d.alignment(body, {}, None, (640,480), 'reviewedCenterOracle')
        self.assertEqual(r['status'], 'unavailable')

    def test_outside_and_unknown_arm(self):
        self.assertEqual(d.translated([200,200,160,60], [0,0], (640,480))['status'], 'unavailable')
        with self.assertRaises(ValueError): d.alignment([], {}, None, (640,480), 'other')

    def test_attribution_distinguishes_localization_and_rule(self):
        r = dict(expected='unchanged', prediction=dict(tracking=dict(status='unavailable')))
        self.assertEqual(d.attribution(r), 'tracking_unavailable')
        r.update(prediction=dict(tracking=dict(status='matched')), trackingAgreesWithSemanticTarget=False)
        self.assertEqual(d.attribution(r), 'wrong_target_geometry')
        r.update(trackingAgreesWithSemanticTarget=True, arms=dict(combined=dict(decision='unknown')))
        self.assertEqual(d.attribution(r), 'pixel_rule_abstained')
        r['expected'] = None
        self.assertEqual(d.attribution(r), 'unscorable_identity')

    def test_changed_stress_seal_rejected_before_output(self):
        base = h.ROOT/'.build/debug-output/tracking30'; base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as td:
            root=Path(td); p=root/'bad.json'; h.write(p,dict(version='settings-swift-stress-v1',seal='bad'))
            with self.assertRaisesRegex(ValueError,'stress_source_changed'): d.stress(p,root/'output')
            self.assertFalse((root/'output').exists())

    def test_actual_native_crop_rule_and_counterexamples(self):
        base = h.ROOT/'.build/debug-output/tracking30'; base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as td:
            root=Path(td); before=fixture.scene(); outline=fixture.scene()
            ImageDraw.Draw(outline).rectangle((198,198,361,261),outline='white',width=2)
            cases=[('identical',before,[200,200,160,60],'unchanged'),
                   ('scroll',fixture.scene(dy=-100),[200,100,160,60],'unchanged'),
                   ('highlight',fixture.scene(shade=235),[200,200,160,60],'arrival'),
                   ('outline',outline,[200,200,160,60],'unknown'),
                   ('illumination',before.point(lambda v:min(255,v+30)),[200,200,160,60],'unknown')]
            before.save(root/'before.png')
            for name, after, target, expected in cases:
                with self.subTest(name=name):
                    path=root/(name+'.png'); after.save(path)
                    t=d.alignment([200,200,160,60],{},target,before.size,'reviewedCenterOracle')
                    p,ims=d.predict(h.ref(root/'before.png'),h.ref(path),[200,200,160,60],t,'x',before.size)
                    self.assertEqual(p['decision'],expected)
                    self.assertEqual(ims[0].size,(256,256))


if __name__=='__main__': unittest.main()
