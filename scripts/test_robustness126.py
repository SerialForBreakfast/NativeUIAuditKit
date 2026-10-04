import unittest
import numpy as np
from robustness126 import transform,summarize


class RobustnessTests(unittest.TestCase):
    def test_common_transform_preserves_identity_order_and_input(self):
        image=np.linspace(0,1,24,dtype=np.float32).reshape(1,3,2,4)
        pair=np.concatenate([image,image],axis=1);saved=pair.copy()
        for offset in (0,.1,.2):
            changed=transform(pair,.8,offset)
            np.testing.assert_array_equal(changed[:,:3],changed[:,3:])
            self.assertGreaterEqual(float(changed.min()),0)
            self.assertLessEqual(float(changed.max()),1)
            self.assertTrue(np.all(np.diff(changed[0,0].flatten())>0))
        np.testing.assert_array_equal(pair,saved)

    def test_invalid_transform_rejected(self):
        for x,g,b in [(np.array([np.nan]),.8,0),(np.array([1.1]),.8,0),
                      (np.array([0.]),.8,.3),(np.array([0.]),0,0)]:
            with self.assertRaises(ValueError): transform(x,g,b)

    def test_abstentions_are_not_correct_or_confident_errors(self):
        result=summarize(np.array([.1,.5,.9]),np.array([0,1,0]),
                         {'all':[0,1,2]},np.array([.1,.9,.1]))['all']
        self.assertEqual((result['correct'],result['abstentions'],result['confidentWrong']),(1,1,1))
        self.assertEqual(result['lostCorrect'],2)
        self.assertEqual(result['failureIndices'],[1,2])


if __name__=='__main__':unittest.main()
