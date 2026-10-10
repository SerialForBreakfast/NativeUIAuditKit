"""Check which examples change in each fixed comparison."""
import unittest
from unittest.mock import patch
import numpy as np
import condition292 as run


class FactorialTests(unittest.TestCase):
    def test_only_selected_class_changes(self):
        old=np.arange(24).reshape(4,6,1,1).astype(np.float32)
        new=old+100
        labels=np.array([1,0,1,0])
        for positive in (True,False):
            result=run.mix(old,new,labels,positive)
            mask=labels==int(positive)
            np.testing.assert_array_equal(result[mask],new[mask])
            np.testing.assert_array_equal(result[~mask],old[~mask])
            np.testing.assert_array_equal(run.base.reporting.reverse(result)[:,:3],result[:,3:])
        np.testing.assert_array_equal(old,np.arange(24).reshape(4,6,1,1))

    def test_invalid_shapes_and_labels(self):
        old=np.zeros((2,6,1,1),np.float32)
        with self.assertRaisesRegex(ValueError,'mix_shape'):
            run.mix(old,old[:1],np.array([0,1]),True)
        with self.assertRaisesRegex(ValueError,'mix_labels'):
            run.mix(old,old,np.array([0,-1]),True)

    def test_report_keeps_interaction_and_losses(self):
        probabilities={'DTM083':[.1,.9], 'DTM084':[.9,.5],
                       'DTM085':[.1,.5], 'DTM086':[.1,.9]}
        def read(path):
            if path.name=='registration.json':
                return dict(addedRows=[dict(changed=0,condition='identity'),dict(changed=1,condition='focus')])
            p=probabilities[path.parent.name]
            if path.name=='result.json':return dict(addedFit=dict(probabilities=p))
            correct=int(p[0]<=.15)+int(p[1]>=.85)
            return dict(conditions={'native.npy':dict(probabilities=p,summary=dict(correct=correct))},strengths=[])
        membership=dict(rows=[dict(id='a',group='g',role='reserved',changed=0),
                              dict(id='b',group='g',role='train',changed=1)])
        with patch.object(run.base,'read',side_effect=read), patch.object(run.base,'ref',return_value={}), \
             patch.object(run.base,'write') as write:
            result=run.report(membership)
        item=result['native.npy']
        self.assertEqual(item['positiveEffectOldNegatives'],-1)
        self.assertEqual(item['positiveEffectIdentityNegatives'],-2)
        self.assertEqual(item['interaction'],-1)
        report=write.call_args.args[1]
        self.assertEqual(len(report['contrasts']),4)
        self.assertEqual(report['contrasts']['negative_with_new_positives']['conditions']['native.npy']['lostCorrect'],1)
        self.assertFalse(report['productionEligible'])
        self.assertFalse(report['independentEvaluation'])


if __name__=='__main__':unittest.main()
