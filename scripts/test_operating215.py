import copy
import unittest
from operating215 import rank


def fixture():
    report=dict(operating_confidence_threshold=.25,matching_IoU=.5,partitions=[])
    mapping=dict(plans={})
    for kind in ('fit','page','combined'):
        result=dict(TP=1,FP=2,FN=1,matched_GT_indices=[0],failures=dict(unmatched_FP=2,absent_same_class_FN=1))
        counts=dict(TP=1,FP=2,FN=1)
        case=dict(imageID=kind+'-roi',GT_count=2,operating_control=copy.deepcopy(result),
                  operating_treatment=copy.deepcopy(result),low_confidence_candidate_GT_indices=dict(treatment=[0,1]))
        report['partitions'].append(dict(partition=kind,role=kind,images=1,support=2,cases=[case],
            operating_control=counts.copy(),operating_treatment=counts.copy(),
            per_class=[dict(className='x',**{'class':'x'},support=2,operating_control=counts.copy(),operating_treatment=counts.copy())]))
        mapping['plans'][kind]=dict(records=[dict(cropID=kind+'-roi',imageID=kind+'-parent',window=[0,0,10,10])])
    return report,mapping


class RankTests(unittest.TestCase):
    def test_operating_not_floor_and_matched_exclusion(self):
        r,m=fixture();r['failure_categories']=[dict(count=99999)]
        d=rank(r,m)
        self.assertEqual(d,rank(r,m));self.assertEqual(d['topTen'][0]['count'],2)
        self.assertEqual(d['topTen'][0]['denominator'],3)
        self.assertEqual(d['partitions'][0]['unmatchedLowConfidence'][0]['indices'],[1])
        self.assertEqual(d['topTen'][0]['representatives'][0]['imageID'],'combined-parent')
        self.assertFalse(d['modelGatePassed'])
    def test_corrupt_accounting_membership_threshold(self):
        r,m=fixture()
        for mutate in (lambda x:x.update(operating_confidence_threshold=.001),
                       lambda x:x['partitions'][0]['cases'][0]['operating_treatment'].update(FP=99),
                       lambda x:x['partitions'][0]['cases'][0].update(imageID='unknown'),
                       lambda x:x['partitions'][0]['cases'][0]['operating_treatment'].update(matched_GT_indices=[1,1])):
            bad=copy.deepcopy(r);mutate(bad)
            with self.assertRaises(ValueError):rank(bad,m)
    def test_class_regression_visible(self):
        r,m=fixture()
        self.assertTrue(all(not p['regressions'] for p in rank(r,m)['partitions']))
        part=r['partitions'][0]
        part['cases'][0]['operating_treatment']['FP']=3
        part['cases'][0]['operating_treatment']['failures']['unmatched_FP']=3
        part['operating_treatment']['FP']=3
        part['per_class'][0]['operating_treatment']['FP']=3
        row=rank(r,m)['partitions'][0]['regressions'][0]
        self.assertEqual(row['className'],'x');self.assertEqual(row['treatment']['FP'],3)

if __name__=='__main__':unittest.main()
