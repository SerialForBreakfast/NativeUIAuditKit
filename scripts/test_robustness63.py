import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
import focus_direct_transition as d
import focus_translation_training as aug


class AugmentationTests(unittest.TestCase):
    def test_comparison_rejects_membership_label_and_duplicate_changes(self):
        import copy
        from compare_robustness63 import compare
        row=dict(id='a',split='train',condition='baseline',expectedChange=True,bothBoxesCorrect=True)
        a=dict(version='transfer-sensitivity-v1',corpusSHA256='same',conditions=['baseline'],rejected=[],results=[row])
        self.assertEqual(compare(a,a)[0]['lost'],0)
        for mutate in (lambda b:b.update(corpusSHA256='other'),lambda b:b['results'].append(row),
                       lambda b:b['results'][0].update(expectedChange=False)):
            b=copy.deepcopy(a);mutate(b)
            with self.assertRaises(ValueError):compare(a,b)

    def test_historical_condition_never_upgraded(self):
        from audit_stationary_coverage63 import classification
        raw=dict(specification=dict(condition='boundary_unchanged'),endpoints=[],cleanup='verified')
        row=classification(raw,True)
        self.assertIsNone(row['observedScrolled']);self.assertFalse(row['stationaryContractCandidate'])
        self.assertFalse(row['trainingEligible'])

    def test_bank_geometry_train_only_and_rejections(self):
        rows=[dict(id='a',split='train',images=[{},{}],size=[100,100],
            boxes=[[0,0,10,10],[20,20,10,10]],changed=True)]
        with patch.object(d,'pixels',return_value=Image.new('RGB',(100,100),'red')):
            x,y,options,entries,rejected=aug.bank(rows)
            self.assertEqual(x.shape,(3,6,64,96));self.assertEqual(len(rejected),2)
            self.assertEqual([r['condition'] for r in entries],['baseline','right','down'])
            np.testing.assert_allclose(y[1,:4],d.target_box([4,0,10,10],[100,100]))
            self.assertTrue(all(y[:,8]==1))
            rows[0]['split']='development'
            with self.assertRaisesRegex(ValueError,'train_only'):aug.bank(rows)

    def test_reproducible_independent_schedule(self):
        options=[[0,1,2],[3,4]]
        a=aug.schedule(options,120,42);b=aug.schedule(options,120,42)
        self.assertEqual(a,b)
        self.assertTrue(all(r[0] in options[0] and r[1] in options[1] for r in a))
        t=d.torch_runtime();t.manual_seed(42);before=t.get_rng_state().clone()
        aug.schedule(options,120,42);self.assertTrue(t.equal(before,t.get_rng_state()))
        entries=[dict(id='x',condition=c) for c in aug.TRAIN_CONDITIONS]
        receipt=aug.receipt(a,entries,[])
        self.assertEqual(sum(receipt['counts'].values()),240)
        self.assertEqual(receipt['scheduleSHA256'],d.digest(b))

    def test_architecture_and_inference_unchanged(self):
        t=d.torch_runtime();t.manual_seed(42);a=d.model(d.FULL_FIT_CONFIG)
        t.manual_seed(42);b=d.model(d.TRANSLATION_CONFIG)
        self.assertTrue(all(t.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))
        im=Image.new('RGB',(100,100),'gray')
        pa,pb=d.infer(a,im,im),d.infer(b,im,im)
        from evaluate_direct_transition import parity
        parity(pa,pb)
        with self.assertRaises(ValueError):d.model(dict(d.TRANSLATION_CONFIG,augmentation='unbounded'))

    def test_actual_training_uses_bank_without_development(self):
        # Mock numerical updates only; production code still chooses actual bank rows.
        rows=[dict(id=str(i),split='train',images=[{},{}],size=[100,100],
            boxes=[[10,10,20,20]]*2,changed=bool(i)) for i in range(2)]
        t=d.torch_runtime()
        with patch.object(d,'pixels',return_value=Image.new('RGB',(100,100),'red')),patch.object(t.optim.Adam,'step',return_value=None):
            net,history=d.fit(rows,d.TRANSLATION_CONFIG)
        self.assertEqual(len(history),120)
        self.assertEqual(net.training_augmentation['sampledPairs'],240)
        self.assertEqual(sum(sum(e['augmentationCounts'].values()) for e in history),240)


if __name__=='__main__':unittest.main()
