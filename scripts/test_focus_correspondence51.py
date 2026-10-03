"""Offline tests of experimental correspondence; no model/data admission."""
import copy
import unittest
from unittest.mock import patch
from PIL import Image,ImageDraw
import focus_transition_verifier as v
import focus_correspondence_comparison as comparison
import focus_corrected_transition_audit as audit
import focus_recorded_transition_eval as evaluate


class CorrespondenceTests(unittest.TestCase):
    def test_policy_is_explicit_isolated_and_defaults_unchanged(self):
        old=dict(v.POLICY);wide=v.tracker_policy('wide-template-v1')
        self.assertEqual(wide['templateFraction'],.9);self.assertEqual(wide['maxBodyWidth'],512)
        wide['minPeakGap']=0
        self.assertEqual(v.POLICY,old)
        with self.assertRaisesRegex(ValueError,'unsupported_tracker'):v.tracker_policy('invented')

    def test_wide_translation_and_duplicate_rejection(self):
        # Distinguishing peripheral text is outside the original central template.
        before=Image.new('RGB',(900,500),'black');d=ImageDraw.Draw(before)
        d.text((140,213),'Q123X',fill='white')
        after=Image.new('RGB',before.size,'black');after.paste(before.crop((100,200,800,250)),(100,100))
        bounds=[100,200,700,50]
        self.assertEqual(v.track(before,after,bounds)['status'],'unavailable')
        tracked=v.track(before,after,bounds,tracker='wide-template-v1')
        self.assertEqual(tracked['status'],'matched',tracked)
        self.assertLess(abs(tracked['dy']+100),2)
        self.assertEqual(tracked['afterBounds'][2:],bounds[2:])
        after.paste(before.crop((100,200,800,250)),(100,200))
        self.assertEqual(v.track(before,after,bounds,tracker='wide-template-v1')['status'],'unavailable')

    def test_wide_blank_missing_and_viewport(self):
        a=Image.new('RGB',(400,300),'black');b=Image.new('RGB',a.size,'white')
        self.assertEqual(v.track(a,b,[40,40,300,60],tracker='wide-template-v1')['reason'],'low_texture')
        self.assertEqual(v.track(a,a,[40,40,300,60],tracker='wide-template-v1')['status'],'identical')
        self.assertEqual(v.track(a,b.resize((200,200)),[40,40,300,60],tracker='wide-template-v1')['reason'],'viewport_changed')

    def document(self):
        c=dict(id='x',expected='arrival',afterControl='x',trackingAgreesWithSemanticTarget=False,
               prediction=dict(tracking=dict(status='matched')))
        return dict(version='reference-transition-audit-v1',partition='development',trainingEligible=False,
                    independentEvaluationEligible=False,summaries={},
                    pairs=[dict(id='p',inputs=['same-pixels'],controls=[c])])

    def test_wrong_match_counted_even_if_classifier_abstains(self):
        doc=self.document();r=comparison.compare(doc,copy.deepcopy(doc))
        self.assertEqual(r['candidate']['counts']['wrong'],1)
        self.assertFalse(r['candidateAdopted'])
        self.assertEqual(r['identityDelta']['wrong'],0)

    def test_comparison_rejects_changed_truth_pixels_roles_membership(self):
        original=self.document()
        for mutation in ('truth','pixels','role','membership'):
            c=copy.deepcopy(original)
            if mutation=='truth':c['pairs'][0]['controls'][0]['expected']='unchanged'
            if mutation=='pixels':c['pairs'][0]['inputs']=['different-pixels']
            if mutation=='role':c['trainingEligible']=True
            if mutation=='membership':c['pairs'][0]['controls']=[]
            with self.assertRaises(ValueError):comparison.compare(original,c)

    def test_after_truth_not_forwarded_to_candidate(self):
        before=dict(image='before',controls=[dict(id='b',bounds=[1,2,3,4],state='unfocused')])
        after=dict(image='after',controls=[dict(id='secret',bounds=[8,9,3,4],state='focused')])
        with patch.object(evaluate,'predict',side_effect=RuntimeError('boundary')) as predictor:
            with self.assertRaisesRegex(RuntimeError,'boundary'):audit.score_pair(before,after,tracker='wide-template-v1')
        predictor.assert_called_once_with('before','after',[dict(id='b',bounds=[1,2,3,4])],tracker='wide-template-v1')


if __name__=='__main__':unittest.main()
