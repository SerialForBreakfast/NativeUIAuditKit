import unittest
from unittest.mock import patch
import focus_direct_transition as d
import prepare_fit61 as prep
from evaluate_direct_transition import fitted_summary


class FitTests(unittest.TestCase):
    def test_membership_and_legacy_summary(self):
        scores=[dict(id=str(i),split='train',prediction=dict(decision='unknown'),rawChangeCorrect=True,
            bothBoxesCorrect=False,baseline=None,expectedChange=bool(i%2)) for i in range(24)]
        report=fitted_summary(scores,['0','1','2','3'])
        self.assertEqual(report['fitted']['all']['pairs'],4)
        self.assertEqual(report['otherTrainRole']['all']['pairs'],20)
        self.assertFalse(fitted_summary(scores,None)['available'])
        for ids in (['0','0'],['missing'],[]):
            with self.assertRaises(ValueError):fitted_summary(scores,ids)
        scores[0]['split']='development'
        with self.assertRaisesRegex(ValueError,'membership_mismatch'):fitted_summary(scores,['0'])

    def test_same_model_full_membership(self):
        rows=[dict(id=str(i),changed=bool(i%2),split='train') for i in range(24)]
        self.assertEqual(len(d.training_rows(rows,d.FULL_FIT_CONFIG)),24)
        self.assertEqual(len(d.training_rows(rows,d.LOGIT_DIAGNOSTIC)),4)
        t=d.torch_runtime();t.manual_seed(42);a=d.model(d.LOGIT_CONFIG)
        t.manual_seed(42);b=d.model(d.FULL_FIT_CONFIG)
        self.assertTrue(all(t.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))

    def test_numerical_compatibility_rejection(self):
        # Synthetic baseline exercises rejection without touching historical artifacts.
        source=dict(path='scripts/focus_direct_transition.py',sha256='same')
        pins=dict(dependencies={},python='p',code=[source])
        baseline=dict(pins=pins,numerical={},configuration=d.LOGIT_DIAGNOSTIC,source=source)
        with patch.object(d.h,'checked'),patch.object(d.h,'sealed',return_value=baseline),patch.object(d,'pins',return_value=pins):
            with self.assertRaisesRegex(ValueError,'numerical_behavior_changed'):prep.verify_gate({}, {}, [])


if __name__=='__main__':unittest.main()
