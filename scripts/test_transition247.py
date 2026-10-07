"""Test diagnostic labels, weighting, and representation behavior."""
import unittest
from unittest.mock import patch
import numpy as np
import transition247 as t
import transition247_diagnosis as diagnosis


class BatchTests(unittest.TestCase):
    def test_group_support_excludes_protected_rows(self):
        rows=[dict(group='a',role='train',changed=0,conditions=['identity']) for _ in range(3)]
        rows.append(dict(group='b',role='reserved',changed=1,conditions=['focus']))
        r=diagnosis.support(rows)
        self.assertEqual(r['rows'],3);self.assertEqual(r['effectiveGroups'],1)
        self.assertNotIn('focus',r['conditions'])

    def test_error_counts_separate_abstention(self):
        rows=[dict(id=str(i),group='a',role='train',changed=y,conditions=['test']) for i,y in enumerate([0,1,0])]
        r=diagnosis.errors(rows,[.9,.1,.5])['test']['summary']
        self.assertEqual((r['falseChange'],r['missedChange'],r['abstentions']),(1,1,1))

    def test_reversed_conflicting_labels(self):
        x=np.zeros((2,6,2,2),np.float32);x[0,3:]=1;x[1,:3]=1
        r=t.audit(x,np.array([0,1]),[{'group':'a'},{'group':'a'}])
        self.assertEqual(r['reversalUnique'],1);self.assertEqual(r['conflicts'],[[0,1]])

    def test_training_only_normalization(self):
        x=np.array([[0.],[1.],[2.],[3.]])
        model=t.ridge_fit(x,np.array([0,0,1,1]))
        self.assertEqual(model['mean'][0],1.5)
        before=model['mean'].copy();t.predict(model,np.array([[1000.]]))
        np.testing.assert_array_equal(before,model['mean'])

    def test_nonfinite_and_single_class_rejected(self):
        for x,y in [(np.array([[np.nan],[1.]]),np.array([0,1])),(np.ones((2,1)),np.ones(2))]:
            with self.assertRaises(ValueError):t.ridge_fit(x,y)

    def test_collision_before_input_work(self):
        with patch.object(t,'OUT') as path,patch.object(t.t,'prepare') as prepare:
            path.exists.return_value=True
            with self.assertRaisesRegex(ValueError,'output_collision'):t.run()
            prepare.assert_not_called()


if __name__=='__main__':unittest.main()
