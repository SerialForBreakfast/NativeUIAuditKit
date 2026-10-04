import unittest
from diagnose_proposals73 import select,valid,vision_candidates


class ProposalTests(unittest.TestCase):
    def test_vision_source_binding_and_bounds(self):
        import copy
        r=dict(sha256='abc',width=100,height=100,errors=[],rectangles=[dict(bounds=[0,0,20,20],confidence=.8)])
        self.assertEqual(vision_candidates(r,{'sha256':'abc'},[100,100]),[dict(id='0',bounds=[0,0,20,20])])
        for mutate in (lambda x:x.update(sha256='other'),lambda x:x.update(errors=['failed']),
            lambda x:x.update(width=50),lambda x:x['rectangles'][0].update(bounds=[90,0,20,20]),
            lambda x:x['rectangles'][0].update(confidence=float('nan'))):
            bad=copy.deepcopy(r);mutate(bad)
            with self.assertRaises(ValueError):vision_candidates(bad,{'sha256':'abc'},[100,100])
    def test_geometry_selection_and_ties(self):
        pool=[dict(id='b',bounds=[40,10,20,20]),dict(id='a',bounds=[0,10,20,20])]
        self.assertEqual(select([1,10,20,20],pool,'center')['id'],'a')
        self.assertEqual(select([41,10,20,20],pool,'iou')['id'],'b')
        self.assertEqual(select([20,10,20,20],pool,'center')['id'],'a')
        self.assertEqual(select([20,10,20,20],pool[::-1],'center')['id'],'a')

    def test_missing_predictions_and_proposals_remain_unavailable(self):
        self.assertIsNone(select([0,0,1,1],[],'center'))
        self.assertIsNone(select(None,[dict(id='a',bounds=[0,0,1,1])],'center'))

    def test_labels_and_invalid_geometry_rejected(self):
        for extra in ('state','expected','focused','class'):
            with self.assertRaisesRegex(ValueError,'geometry_only'):
                select([0,0,1,1],[dict(id='a',bounds=[0,0,1,1],**{extra:True})],'center')
        for box in ([0,0,0,1],[-1,0,1,1],[0,0,float('nan'),1],[0,0,True,1]):
            self.assertFalse(valid(box))
            with self.assertRaises(ValueError):select(box,[dict(id='a',bounds=[0,0,1,1])],'center')
        with self.assertRaisesRegex(ValueError,'duplicate_candidate'):
            select([0,0,1,1],[dict(id='a',bounds=[0,0,1,1])]*2,'iou')


if __name__=='__main__':unittest.main()
