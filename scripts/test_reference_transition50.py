"""Deterministic temporal reference integration; no device/model execution."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import focus_corrected_transition_audit as audit
import focus_transition_learning as learn
from test_focus_transition_learning import TransitionTests, prediction


class ReferenceLearningTests(TransitionTests):
    def reference(self):
        source=self.source('reference',50)
        old=learn.h.read(learn.h.checked(learn.h.ROOT,source['report']))
        action=old['actions'][0]
        controls=action['guardedControls']
        for control in controls:control['arms']['guardedStability']=control['arms'].pop('combined')
        row=dict(id='reference',status='diagnostic',controls=controls,inputs=source['endpointImages'],
            condition='scroll_moved',family='native-test',sourceRole='calibration',
            sourceAncestry=dict(renderer='fixture_procedural_renderer_v1'))
        doc=dict(version='reference-transition-audit-v1',**learn.h.FLAGS,pairs=[row])
        p=self.write('reference-audit.json',doc,True)
        return dict(report=learn.h.ref(p),group='fixture-procedural-renderer-v1')

    def test_reference_version_roles_and_group(self):
        source=self.reference();corpus=learn.collect([source])
        self.assertEqual(corpus['counts']['featureReady'],3)
        self.assertTrue(all(r['sourceRole']=='calibration' for r in corpus['records']))
        self.assertEqual(corpus['baseline']['actions']['fullScene']['scorable'],0)
        source['group']='invented-independent-family'
        with self.assertRaisesRegex(ValueError,'renderer_group'):learn.collect([source])

    def test_feasibility_is_not_admission(self):
        a=self.source('a',70);b=self.source('b',80)
        corpus=learn.collect([a,b]);report=learn.feasibility(corpus)
        self.assertTrue(report['necessaryTwoGroupSupportPresent'])
        self.assertFalse(report['trainingEligible']);self.assertFalse(report['splitAssigned'])
        for row in corpus['records']:row['group']='same-renderer'
        self.assertFalse(learn.feasibility(corpus)['necessaryTwoGroupSupportPresent'])

    def test_experimental_tracker_cannot_enter_default_learner(self):
        source=self.reference();doc=learn.h.read(learn.h.checked(learn.h.ROOT,source['report']))
        doc.pop('seal');doc['tracker']='wide-template-v1'
        path=self.write('experimental-audit.json',doc,True)
        with self.assertRaisesRegex(ValueError,'experimental_tracker_not_admitted'):
            learn.collect([dict(source,report=learn.h.ref(path))])

    def test_shared_pixels_invalidate_two_group_support(self):
        a=self.source('a',90);b=self.source('b',90)
        report=learn.feasibility(learn.collect([a,b]))
        self.assertEqual(len(report['crossGroupDuplicatePixels']),1)
        self.assertFalse(report['necessaryTwoGroupSupportPresent'])


class ScoringTests(unittest.TestCase):
    def test_scoring_keeps_after_truth_out_of_prediction(self):
        import focus_recorded_transition_eval as evaluate
        import settings_focus_stability as stability
        p=dict(prediction(.4),id='e',decision='arrival',brightness='arrival',growth='arrival')
        p['tracking']['afterBounds']=[1,2,10,20]
        before=dict(image={'path':'before'},controls=[dict(id='e',bounds=[1,2,10,20],state='unfocused')])
        after=dict(image={'path':'after'},controls=[dict(id='e',bounds=[1,2,10,20],state='focused')])
        with patch.object(evaluate,'predict',return_value=([p],{'runtime':'fixture'})) as predict, \
             patch.object(stability,'crop_metrics',return_value=({'e':p['stability']['metrics']},{'runtime':'fixture'})):
            rows,_=audit.score_pair(before,after)
        predict.assert_called_once_with(before['image'],after['image'],[dict(id='e',bounds=[1,2,10,20])])
        self.assertEqual(rows[0]['expected'],'arrival')
        self.assertEqual(rows[0]['prediction']['stability']['metrics'],p['stability']['metrics'])
        self.assertIn('guardedStability',rows[0]['arms'])

    def test_reference_wrong_membership_fails_before_pixels(self):
        import audit_reference43
        base=learn.h.ROOT/'.build/debug-output/transition50-tests';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as name:
            root=Path(name);learn.h.write(root/'artifact-manifest.json',{})
            with patch.object(audit_reference43,'verify_files',return_value=1), \
                 patch.object(audit_reference43,'accepted_cases',return_value=[]), \
                 patch.object(audit,'score_pair') as scorer:
                with self.assertRaisesRegex(ValueError,'condition_membership'):audit.reference_run(root,root/'output')
                scorer.assert_not_called()


if __name__=='__main__':unittest.main()
