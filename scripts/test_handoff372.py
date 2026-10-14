import unittest
from handoff372 import receipt_audit


class HandoffTests(unittest.TestCase):
    def test_settled_does_not_supply_geometry(self):
        case=dict(case_id='a',pre_settled=True,post_settled=True,pre_observed_focus_id='x',
                  post_observed_focus_id='x',focused_element_geometry=dict(focused=False,id='x'))
        r=receipt_audit({'batch':{'cases':[case]}})
        self.assertEqual((r['settled'],r['matchingFocus'],r['bodyPresent'],r['selectedElementFalse']),(1,1,0,1))
        self.assertFalse(r['trainingAdmitted'])

    def test_missing_observation_does_not_agree(self):
        r=receipt_audit({'batch':{'cases':[dict(case_id='a')]}})
        self.assertEqual(r['matchingFocus'],0)

    def test_conflicting_observation_fails(self):
        case=dict(case_id='a',pre_observed_focus_id='x',post_observed_focus_id='y')
        self.assertEqual(receipt_audit({'batch':{'cases':[case]}})['matchingFocus'],0)
