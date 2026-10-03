import copy
import unittest
import evaluate_direct_transition as e


class EvaluationTests(unittest.TestCase):
    def test_checkpoint_parity_rejects_decisions_probabilities_and_boxes(self):
        p=dict(decision='changed',changeProbability=.9,boxes=[[10,20,30,40],None])
        e.parity(p,copy.deepcopy(p))
        for kind in ('decision','probability','box','missing','count'):
            bad=copy.deepcopy(p)
            if kind=='decision':bad['decision']='unknown'
            if kind=='probability':bad['changeProbability']=.7
            if kind=='box':bad['boxes'][0][0]=11
            if kind=='missing':bad['boxes'][1]=[1,2,3,4]
            if kind=='count':bad['boxes'].pop()
            with self.assertRaises(ValueError):e.parity(p,bad)

    def test_joint_metric_requires_boxes_and_nonabstained_change(self):
        row=dict(prediction={'decision':'changed'},expectedChange=True,baseline=None,
                 rawChangeCorrect=True,bothBoxesCorrect=False)
        summary=e.d.summarize([row])['all']
        self.assertEqual(summary['rawChangeCorrect'],1);self.assertEqual(summary['jointCorrect'],0)
        row.update(bothBoxesCorrect=True,prediction={'decision':'unknown'})
        self.assertEqual(e.d.summarize([row])['all']['jointCorrect'],0)


if __name__=='__main__':unittest.main()
