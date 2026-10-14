import unittest
from repair373 import decide


class RepairTests(unittest.TestCase):
    def test_missing_comparison_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,'missing_comparisons'):
            decide([dict(summaryRows=[],targetPredictions=[])],{'control':['required'],'notification':[]})

    def test_renamed_summary_does_not_drop_arm(self):
        docs=[];expected={}
        for arm in ('control','notification'):
            name='focus366-'+arm+'-test';expected[arm]=[name]
            targets=[dict(id=str(i),changed=1,probability=.9) for i in range(391)]
            targets.append(dict(id='artwork-s1-focus_maze-005',changed=1,probability=.9))
            docs.append(dict(summaryRows=[dict(job=name,counts={'lost':0})],targetPredictions=targets))
        result=decide(docs,expected)
        self.assertEqual(result['arms']['notification']['correct'],392)
        self.assertFalse(result['passesDevelopmentRule'])
        self.assertFalse(result['modelAccepted'])
