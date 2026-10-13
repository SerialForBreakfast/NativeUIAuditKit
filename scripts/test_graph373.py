"""Check cached comparisons without model execution."""
import unittest
from graph373 import decision, summarize, compare, records


class GraphTests(unittest.TestCase):
    def row(self, ident, group, truth, old, new):
        return dict(id=ident, group=group, changed=truth, predictions=dict(control=old,gamma=new))

    def test_abstention_is_a_lost_success(self):
        rows=[self.row('a','g',1,True,None)]
        self.assertEqual(compare(rows)['losses'],['a'])
        report=summarize(rows,'gamma')
        self.assertEqual(report['missedChanges']['value'],1)
        self.assertEqual(report['falseStableAmongChanged']['value'],0)
        self.assertIsNone(report['errorAmongStable']['value'])

    def test_groups_do_not_change_raw_counts(self):
        rows=[self.row(str(i),'large',1,True,True) for i in range(9)]
        rows.append(self.row('last','small',1,True,False))
        result=summarize(rows,'gamma')
        self.assertEqual(result['rowAccuracy']['value'],.9)
        self.assertEqual(result['equalGroupAccuracy'],.5)
        self.assertIsNone(result['binomialUpper95'])

    def test_invalid_probabilities(self):
        for value in (float('nan'),-1,2,True):
            with self.assertRaises(ValueError):decision(value)

    def test_thresholds_and_duplicates(self):
        self.assertIs(decision(.15),False)
        self.assertIs(decision(.85),True)
        self.assertIsNone(decision(.5))
        row=self.row('a','g',0,False,False)
        with self.assertRaisesRegex(ValueError,'duplicate_case'):compare([row,row])

    def test_role_and_prediction_length(self):
        row=dict(id='a',role='calibration',group='g',changed=0,sourceDomain='authored')
        doc={'sets':{'s':dict(rows=[row],probabilities={'control':[.1],'gamma':[.1]},originalProbabilities=[.1])}}
        with self.assertRaisesRegex(ValueError,'development_role'):records(doc)
        row['role']='development'
        doc['sets']['s']['probabilities']['gamma']=[]
        with self.assertRaisesRegex(ValueError,'prediction_length'):records(doc)

    def test_one_group_has_no_bootstrap_interval(self):
        report=compare([self.row('a','g',1,False,True)])
        self.assertIsNone(report['descriptiveGroupInterval95'])
        self.assertFalse(report['independentSafetyClaim'])
